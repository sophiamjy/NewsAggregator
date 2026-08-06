"""新闻抓取模块 v3.0 — Google RSS + 各国RSS + 战争专题"""
import hashlib, logging, time, urllib.parse, feedparser, requests
from calendar import timegm
from datetime import datetime, timedelta, timezone

from config import (
    ARTICLES_PER_QUERY, COUNTRIES, DOMAINS, MAX_RETRIES, REQUEST_DELAY,
    REQUEST_TIMEOUT, LOG_LEVEL, ENABLE_GOOGLE_RSS, ENABLE_PROGRESS_DETAIL,
    TIME_WINDOW_START_HOUR, TIME_WINDOW_START_MINUTE, TIME_WINDOW_START_SECOND,
    TIME_WINDOW_OFFSET_DAYS, COUNTRY_RSS_FEEDS, COUNTRY_RSS_DISAMBIGUATION,
    RSS_DOMAIN_THRESHOLD, RSS_DOMAIN_MAX, PIPELINE_ORDER,
    WAR_TOPIC_ENABLED, WAR_TOPIC_KEYWORDS, WAR_TOPIC_ARTICLES,
)

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                    format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

BEIJING_TZ = timezone(timedelta(hours=8))
_active_window_mode = None


def set_window_mode(mode):
    global _active_window_mode
    _active_window_mode = mode


def now_beijing():
    return datetime.now(BEIJING_TZ)


def get_time_window_start(mode=None):
    if mode is None: mode = _active_window_mode
    t = now_beijing().replace(hour=TIME_WINDOW_START_HOUR, minute=TIME_WINDOW_START_MINUTE,
                              second=TIME_WINDOW_START_SECOND, microsecond=0)
    return t + timedelta(days=TIME_WINDOW_OFFSET_DAYS)


def get_time_window_end(mode=None):
    if mode is None: mode = _active_window_mode
    if mode == "yesterday_only":
        t = now_beijing().replace(hour=0, minute=0, second=0, microsecond=0)
        return t - timedelta(seconds=1)
    return now_beijing()


def is_within_window(dt):
    if dt is None: return True
    if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
    dt_bj = dt.astimezone(BEIJING_TZ)
    return get_time_window_start() <= dt_bj <= get_time_window_end()


def now_utc():
    return datetime.now(timezone.utc)


def article_id(title, source, url=""):
    return hashlib.md5(title.strip().lower().encode()).hexdigest()[:12]


def extract_domain(url):
    if not url: return ""
    return urllib.parse.urlparse(url).netloc.replace("www.", "")


def safe_request(url, params=None, headers=None, timeout=REQUEST_TIMEOUT):
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.exceptions.Timeout:
            logger.warning("请求超时 (尝试 %d/%d): %s", attempt + 1, MAX_RETRIES + 1, url[:80])
        except requests.exceptions.HTTPError as e:
            logger.warning("HTTP 错误 (尝试 %d/%d): %s", attempt + 1, MAX_RETRIES + 1, url[:80])
        except requests.exceptions.RequestException as e:
            logger.warning("请求异常 (尝试 %d/%d): %s", attempt + 1, MAX_RETRIES + 1, e)
        if attempt < MAX_RETRIES: time.sleep(2 * (attempt + 1))
    return None


# ── NewsItem ──
class NewsItem:
    def __init__(self, title, url, source, published=None, summary="", content="",
                 country="", domain="", source_label=""):
        self.title = title; self.url = url; self.source = source
        self.published = published or now_utc()
        self.summary = summary; self.content = content
        self.country = country; self.domain = domain
        self.aid = article_id(title, source, url)
        self.title_zh = ""; self.summary_zh = ""; self.content_zh = ""; self.tags = ""
        self.source_label = source_label


# ── Google News RSS ──
class GoogleNewsRSSSource:
    BASE_URL = "https://news.google.com/rss/search"

    def __init__(self):
        self.available = True

    def fetch(self, query, language="en", max_results=99):
        params = {"q": query, "hl": language, "gl": "US", "ceid": f"US:{language}"}
        resp = safe_request(self.BASE_URL, params=params)
        if resp is None: return []
        fd = feedparser.parse(resp.text)
        if fd.bozo and not fd.entries: return []
        window_matched = []
        for e in fd.entries:
            pub = None
            if hasattr(e, "published_parsed") and e.published_parsed:
                pub = datetime.fromtimestamp(timegm(e.published_parsed), tz=timezone.utc)
            if pub and not is_within_window(pub): continue
            title = e.get("title", ""); src = ""
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0].strip(); src = parts[1].strip()
            window_matched.append(NewsItem(title, e.get("link", ""),
                src or extract_domain(e.get("link", "")), pub,
                e.get("summary", e.get("description", "")), source_label="Google RSS"))
        items = window_matched[:max_results]
        logger.info("GoogleRSS [%s]: %d条 -> 窗口内%d条 (截取前%d)",
                    query[:60], len(fd.entries), len(window_matched), len(items))
        return items


# ── Country RSS Fetcher ──
class CountryRSSFetcher:
    def __init__(self, feed_configs_by_domain):
        self.feeds_by_domain = {}
        for domain, feeds in feed_configs_by_domain.items():
            enabled = [f for f in feeds if f.get("enabled", True)]
            if enabled: self.feeds_by_domain[domain] = enabled
        self.stats = {"fetched": 0, "failed": 0}

    def has_any(self):
        return any(len(v) > 0 for v in self.feeds_by_domain.values())

    def domains(self):
        return list(self.feeds_by_domain.keys())

    def fetch_domain(self, domain):
        feeds = self.feeds_by_domain.get(domain, [])
        if not feeds: return []
        all_items = []; seen_ids = set()
        total_entries = 0; window_matched = 0
        for feed in feeds:
            resp = safe_request(feed["url"], timeout=REQUEST_TIMEOUT)
            if resp is None:
                self.stats["failed"] += 1
                logger.warning("RSS feed 请求失败: %s (%s)", feed["name"], feed["url"][:80])
                continue
            fd = feedparser.parse(resp.text)
            if fd.bozo and not fd.entries:
                self.stats["failed"] += 1
                logger.warning("RSS feed 解析失败: %s (%s)", feed["name"], feed["url"][:80])
                continue
            fc = 0
            for e in fd.entries[:15]:
                total_entries += 1
                pub = None
                if hasattr(e, "published_parsed") and e.published_parsed:
                    pub = datetime.fromtimestamp(timegm(e.published_parsed), tz=timezone.utc)
                if pub and not is_within_window(pub): continue
                window_matched += 1
                title = e.get("title", "").strip()
                if not title: continue
                link = e.get("link", "")
                aid = article_id(title, feed["name"], link)
                if aid in seen_ids: continue
                seen_ids.add(aid)
                all_items.append(NewsItem(title, link, feed["name"], pub,
                    e.get("summary", e.get("description", "")), source_label=feed["name"]))
                fc += 1
            self.stats["fetched"] += fc
            logger.info("RSS[%s]: %s -> %d条获取 / %d条窗口内 / %d条去重后",
                        domain, feed["name"], len(fd.entries), window_matched, fc)
            time.sleep(0.5)
        return all_items


# ── 本地分类 ──
def _fuzzy_match(text, keyword):
    parts = keyword.lower().split()
    return all(p in text for p in parts)


def classify_article_locally(item, domains):
    text = ((item.title or "") + " " + (item.summary or "") + " " + (item.source or "")).lower()
    matched = []
    for d in domains:
        for kw in d["keywords_en"]:
            if _fuzzy_match(text, kw):
                matched.append(d["name_zh"]); break
    if len(matched) == 1: return matched[0], ""
    elif len(matched) > 1: return "综合/其它", ", ".join(matched)
    else: return "综合/其它", "其它"


def build_query_with_keywords(country, keywords):
    country_terms = country.get("search_keywords", {}).get("en", [country["name_en"]])
    disambig = COUNTRY_RSS_DISAMBIGUATION.get(country["name"])
    if disambig: country_terms = country.get("search_keywords", {}).get("en", [country["name_en"]])
    country_str = " OR ".join('"' + t + '"' for t in country_terms)
    kw_str = " OR ".join('"' + k + '"' for k in keywords)
    q = '(' + country_str + ') AND (' + kw_str + ')'
    ws = get_time_window_start(); we = get_time_window_end()
    q += f" after:{(ws - timedelta(days=1)).strftime('%Y-%m-%d')}"
    if _active_window_mode == "yesterday_only":
        q += f" before:{(we + timedelta(days=1)).strftime('%Y-%m-%d')}"
    return q


# ── NewsAggregator ──
class NewsAggregator:
    STAGE_LABELS = {
        "broad_google_rss": "宽泛查询(Google RSS)",
        "country_rss": "各国专属RSS查询",
        "targeted_google_rss": "定向域搜索(Google RSS)",
    }

    def __init__(self, enable_google_rss=True, country_rss_config=None, window_mode=None,
                 stop_check=None):
        self.google_rss = GoogleNewsRSSSource() if enable_google_rss else None
        if not enable_google_rss and self.google_rss:
            self.google_rss.available = False
        self.country_rss_config = country_rss_config or COUNTRY_RSS_FEEDS
        self._country_rss_fetchers = {}
        for cn, feeds_by_domain in self.country_rss_config.items():
            fetcher = CountryRSSFetcher(feeds_by_domain)
            if fetcher.has_any(): self._country_rss_fetchers[cn] = fetcher
        self.stats = {"google_rss": 0, "country_rss": 0, "total_fetched": 0}
        self._stop_check = stop_check
        if window_mode: set_window_mode(window_mode)
        self._progress_detail = ENABLE_PROGRESS_DETAIL

    def _check_stop(self):
        return self._stop_check and self._stop_check()

    def _ensure_country_init(self, results, all_aids, cn):
        if cn not in results:
            results[cn] = {d["name_zh"]: [] for d in DOMAINS}
            results[cn]["综合/其它"] = []
            all_aids[cn] = set()

    def _trim_domain_max(self, country_results):
        for dn in list(country_results.keys()):
            items = country_results[dn]
            if len(items) <= RSS_DOMAIN_MAX: continue
            if dn == "综合/其它":
                tagged = [i for i in items if i.tags and i.tags != "其它"]
                other = [i for i in items if i.tags == "其它" or not i.tags]
                country_results[dn] = (tagged + other)[:RSS_DOMAIN_MAX]
            else:
                country_results[dn] = items[:RSS_DOMAIN_MAX]

    def _disambiguate_rss(self, items, country_name):
        disambig = COUNTRY_RSS_DISAMBIGUATION.get(country_name)
        if not disambig: return items
        country_signals = [s.lower() for s in disambig.get("country_signals", [])]
        noise_signals = [s.lower() for s in disambig.get("noise_signals", [])]
        kept = []; discarded = 0
        for item in items:
            text = f"{item.title or ''} {item.summary or ''} {item.source or ''}".lower()
            if sum(1 for s in country_signals if s in text) > 0:
                kept.append(item)
            elif sum(1 for s in noise_signals if s in text) > 0:
                discarded += 1
            else:
                kept.append(item)
        if discarded:
            logger.info("  [消歧] %s: 移除 %d 条, 保留 %d 条", country_name, discarded, len(kept))
        return kept

    def _broad_fetch_and_classify(self, country, cn, results, all_aids, source_name,
                                  disambig, broad_ex):
        if disambig:
            terms = country.get("search_keywords", {}).get("en", [country["name_en"]])
        else:
            terms = [country["name_en"]]
        country_str = " OR ".join('"' + t + '"' for t in terms)
        ws = get_time_window_start(); we = get_time_window_end()
        q = '(' + country_str + ')'
        q += f" after:{(ws - timedelta(days=1)).strftime('%Y-%m-%d')}"
        if _active_window_mode == "yesterday_only":
            q += f" before:{(we + timedelta(days=1)).strftime('%Y-%m-%d')}"
        if broad_ex:
            q += " " + " ".join('-' + ('"' + t + '"' if ' ' in t else t) for t in broad_ex)
        items = self.google_rss.fetch(q, language="en", max_results=99)
        self.stats["google_rss"] += len(items)
        if disambig: items = self._disambiguate_rss(items, cn)
        for item in items:
            if item.aid in all_aids[cn]: continue
            dn_local, tags = classify_article_locally(item, DOMAINS)
            item.country = cn; item.domain = dn_local; item.tags = tags
            results[cn][dn_local].append(item); all_aids[cn].add(item.aid)
            self.stats["total_fetched"] += 1

    # ── Pipeline Stages ──
    def _stage_broad(self, results, all_aids, source_name, progress_callback=None,
                     stage_idx=0, total_stages=0):
        label = self.STAGE_LABELS.get(source_name, source_name)
        logger.info("[阶段 %d/%d] %s", stage_idx, total_stages, label)
        total = len(COUNTRIES); cur = 0
        for country in COUNTRIES:
            if self._check_stop(): break
            cn = country["name"]; cur += 1
            self._ensure_country_init(results, all_aids, cn)
            disambig = COUNTRY_RSS_DISAMBIGUATION.get(cn)
            broad_ex = disambig.get("broad_exclude") if disambig else None
            if self._progress_detail:
                logger.info("[%d/%d] 宽泛查询: %s", cur, total, cn)
                if progress_callback: progress_callback(f"[{cur}/{total}] {cn}")
            if source_name == "google_rss" and not self.google_rss.available: continue
            self._broad_fetch_and_classify(country, cn, results, all_aids, source_name,
                                           disambig, broad_ex)
            if RSS_DOMAIN_MAX > 0: self._trim_domain_max(results[cn])
            counts = {dn: len(results[cn][dn]) for dn in results[cn]}
            logger.info("  %s: %s", cn, " | ".join(f"{dn}:{cnt}" for dn, cnt in counts.items()))

    def _stage_country_rss_pipeline(self, results, all_aids):
        if not self._country_rss_fetchers:
            logger.info("各国RSS: 无可用源, 跳过"); return
        logger.info("各国专属RSS查询...")
        for cn, fetcher in self._country_rss_fetchers.items():
            if self._check_stop(): break
            self._ensure_country_init(results, all_aids, cn)
            disambig_cn = COUNTRY_RSS_DISAMBIGUATION.get(cn)
            # 领域专属 RSS
            for domain_name in ["政治", "经济", "科技"]:
                if domain_name not in fetcher.domains(): continue
                items = fetcher.fetch_domain(domain_name)
                if disambig_cn: items = self._disambiguate_rss(items, cn)
                added = 0
                for item in items:
                    if item.aid in all_aids[cn]: continue
                    dn_local, tags = classify_article_locally(item, DOMAINS)
                    if tags and dn_local == "综合/其它":
                        item.country = cn; item.domain = "综合/其它"; item.tags = tags
                        results[cn]["综合/其它"].append(item)
                    elif dn_local != domain_name and dn_local != "综合/其它":
                        item.country = cn; item.domain = dn_local
                        results[cn][dn_local].append(item)
                    else:
                        item.country = cn; item.domain = domain_name
                        results[cn][domain_name].append(item)
                    all_aids[cn].add(item.aid); self.stats["country_rss"] += 1; added += 1
                if added: logger.info("  RSS[%s/%s]: +%d条", cn, domain_name, added)
                else: logger.info("  RSS[%s/%s]: 无有效条目", cn, domain_name)
                if RSS_DOMAIN_MAX > 0: self._trim_domain_max(results[cn])
            # 综合 RSS
            needed = [dn for dn in results[cn] if len(results[cn][dn]) < RSS_DOMAIN_THRESHOLD]
            if not needed:
                logger.info("  RSS: %s (所有领域已达标)", cn); continue
            general_added = 0
            rss_items = fetcher.fetch_domain("综合")
            if disambig_cn: rss_items = self._disambiguate_rss(rss_items, cn)
            for item in rss_items:
                if item.aid in all_aids[cn]: continue
                dn_local, tags = classify_article_locally(item, DOMAINS)
                if dn_local not in needed and dn_local != "综合/其它": continue
                item.country = cn; item.domain = dn_local; item.tags = tags
                results[cn][dn_local].append(item); all_aids[cn].add(item.aid)
                self.stats["country_rss"] += 1; general_added += 1
            if general_added: logger.info("  RSS[%s/综合]: +%d条", cn, general_added)
            else: logger.info("  RSS[%s/综合]: 无有效条目", cn)
            if RSS_DOMAIN_MAX > 0: self._trim_domain_max(results[cn])

    def _targeted_search_single(self, country, domain, keyword_batch, source_name):
        cn_name = country["name"]; dn_name = domain["name_zh"]
        all_items = []; seen_ids = set()
        if source_name == "google_rss" and self.google_rss.available:
            rss_q = build_query_with_keywords(country, keyword_batch)
            for item in self.google_rss.fetch(rss_q, language="en", max_results=99):
                if item.aid not in seen_ids:
                    seen_ids.add(item.aid)
                    item.country = cn_name; item.domain = dn_name
                    all_items.append(item)
            self.stats["google_rss"] += len(all_items); time.sleep(REQUEST_DELAY)
        return all_items

    def _stage_targeted(self, results, all_aids, source_name, progress_callback=None,
                        stage_idx=0, total_stages=0):
        label = self.STAGE_LABELS.get(source_name, source_name)
        logger.info("[阶段 %d/%d] %s (仅不达标领域)", stage_idx, total_stages, label)
        for country in COUNTRIES:
            if self._check_stop(): break
            cn = country["name"]
            self._ensure_country_init(results, all_aids, cn)
            disambig = COUNTRY_RSS_DISAMBIGUATION.get(cn)
            for domain in DOMAINS:
                if self._check_stop(): break
                dn = domain["name_zh"]
                if len(results[cn][dn]) >= RSS_DOMAIN_THRESHOLD: continue
                if self._progress_detail:
                    logger.info("  域搜索: %s/%s (当前%d)", cn, dn, len(results[cn][dn]))
                all_kw = domain["keywords_en"]
                for batch_start in range(0, len(all_kw), 3):
                    if len(results[cn][dn]) >= RSS_DOMAIN_THRESHOLD: break
                    batch = all_kw[batch_start:batch_start + 3]
                    new_items = self._targeted_search_single(country, domain, batch, source_name)
                    if disambig: new_items = self._disambiguate_rss(new_items, cn)
                    added = 0
                    for item in new_items:
                        if item.aid not in all_aids[cn]:
                            item.domain = dn
                            results[cn][dn].append(item); all_aids[cn].add(item.aid); added += 1
                            self.stats["total_fetched"] += 1
                    if added:
                        logger.info("    批次%d +%d条", batch_start // 3 + 1, added)
                    if RSS_DOMAIN_MAX > 0: self._trim_domain_max(results[cn])

    def fetch_all(self, fetch_content=False, progress_callback=None, pipeline_order=None):
        if pipeline_order is None: pipeline_order = PIPELINE_ORDER
        results = {}; all_aids = {}
        enabled_stages = [s for s in pipeline_order if s.get("enabled", True)]
        total_enabled = len(enabled_stages)
        logger.info("流水线: %d 个阶段 -> %s", total_enabled,
                    " -> ".join(self.STAGE_LABELS.get(s["id"], s["id"]) for s in enabled_stages))
        for stage_idx, stage_def in enumerate(enabled_stages, 1):
            if self._check_stop(): break
            stage_id = stage_def["id"]
            if stage_id == "broad_google_rss":
                self._stage_broad(results, all_aids, "google_rss", progress_callback, stage_idx, total_enabled)
            elif stage_id == "country_rss":
                self._stage_country_rss_pipeline(results, all_aids)
            elif stage_id == "targeted_google_rss":
                self._stage_targeted(results, all_aids, "google_rss", progress_callback, stage_idx, total_enabled)
            else:
                logger.warning("未知流水线阶段: %s, 跳过", stage_id)
        # 最终消歧
        for cn in list(results.keys()):
            if cn not in COUNTRY_RSS_DISAMBIGUATION: continue
            for dn in list(results[cn].keys()):
                before = len(results[cn][dn])
                results[cn][dn] = self._disambiguate_rss(results[cn][dn], cn)
                if before != len(results[cn][dn]):
                    logger.info("  [最终消歧] %s/%s: %d->%d", cn, dn, before, len(results[cn][dn]))

        # 战争专题
        if WAR_TOPIC_ENABLED and self.google_rss.available:
            self._fetch_war_topic(results)

        total_kept = sum(len(results[cn][dn]) for cn in results for dn in results[cn])
        self.stats["total_fetched"] = total_kept
        logger.info("全部完成: %d 条", total_kept)
        if fetch_content and not self._check_stop():
            logger.info("抓取正文...")
            from content_fetcher import fetch_contents_for_items
            all_items = [item for cn in results for dn in results[cn] for item in results[cn][dn]]
            fetch_contents_for_items(all_items)
        return results

    def _fetch_war_topic(self, results):
        logger.info("以伊专题 (Google RSS)...")
        war_raw = []; seen_war = set()
        ws = get_time_window_start(); we = get_time_window_end()
        batch_size = 5
        for batch_start in range(0, len(WAR_TOPIC_KEYWORDS), batch_size):
            batch_kw = WAR_TOPIC_KEYWORDS[batch_start:batch_start + batch_size]
            kw_str = " OR ".join(f'"{kw}"' for kw in batch_kw)
            q = f'({kw_str}) after:{(ws - timedelta(days=1)).strftime("%Y-%m-%d")}'
            if _active_window_mode == "yesterday_only":
                q += f' before:{(we + timedelta(days=1)).strftime("%Y-%m-%d")}'
            items = self.google_rss.fetch(q, language="en", max_results=50)
            for item in items:
                if item.aid in seen_war: continue
                seen_war.add(item.aid)
                item.country = "⚔️ 以伊专题"; item.domain = "综合/其它"; item.tags = "战争专题"
                war_raw.append(item)
            if self._check_stop(): break
            time.sleep(0.8)
        war_raw = war_raw[:WAR_TOPIC_ARTICLES]
        if war_raw:
            cn = "⚔️ 以伊专题"
            if cn not in results: results[cn] = {d["name_zh"]: [] for d in DOMAINS}
            results[cn]["综合/其它"] = war_raw
        logger.info("战争专题: %d 条", len(war_raw))
