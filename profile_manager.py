"""配置方案管理模块 v3.0"""
import json, os, sys

def _app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

PROFILE_PATH = os.path.join(_app_dir(), "profiles.json")


def load_profiles():
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"default": "", "profiles": {}}


def save_profiles(data):
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _g(gui, attr, default=None):
    if hasattr(gui, attr):
        return getattr(gui, attr).get()
    return default


def gather_settings(gui):
    rss = {}
    for cn, domain_vars in gui._rss_vars.items():
        from config import COUNTRY_RSS_FEEDS
        config_domains = COUNTRY_RSS_FEEDS.get(cn, {})
        rss[cn] = {}
        for domain, vl in domain_vars.items():
            domain_feeds = config_domains.get(domain, [])
            rss[cn][domain] = {}
            for i, feed in enumerate(domain_feeds):
                if i < len(vl):
                    rss[cn][domain][feed["name"]] = vl[i].get()
    return {
        "fetch": gui.var_fetch.get(),
        "translate": gui.var_trans.get(),
        "bilingual": _g(gui, "var_bilingual", False),
        "html": _g(gui, "var_html", False),
        "content": gui.var_content.get(),
        "progress": gui.var_progress.get(),
        "engine": "google",
        "window_mode": gui.var_winmode.get(),
        "google_rss": gui.var_rss.get(),
        "war_topic": _g(gui, "var_war_topic", False),
        "country_rss": rss,
        "rss_threshold": int(gui.var_rss_threshold.get()),
        "rss_domain_max": int(gui.var_domain_max.get()),
        "pipeline_order": gui._get_pipeline_order() if hasattr(gui, '_get_pipeline_order') else None,
        "keywords": {dn: list(d["keywords_en"])
                     for dn, d in [(d["name_zh"], d) for d in __import__("config").DOMAINS]},
    }


def apply_settings(gui, settings):
    for k, attr in [
        ("fetch", "var_fetch"), ("translate", "var_trans"),
        ("bilingual", "var_bilingual"), ("content", "var_content"),
        ("progress", "var_progress"), ("google_rss", "var_rss"),
    ]:
        if k in settings and hasattr(gui, attr):
            getattr(gui, attr).set(settings[k])
    if "html" in settings and hasattr(gui, 'var_html'):
        gui.var_html.set(settings["html"])
    if "war_topic" in settings and hasattr(gui, 'var_war_topic'):
        gui.var_war_topic.set(settings["war_topic"])
    if "window_mode" in settings:
        gui.var_winmode.set(settings["window_mode"])
        if hasattr(gui, '_update_win_label'): gui._update_win_label()
    if "country_rss" in settings:
        from config import COUNTRY_RSS_FEEDS
        for cn, saved_data in settings["country_rss"].items():
            cn_vars = gui._rss_vars.get(cn, {})
            config_domains = COUNTRY_RSS_FEEDS.get(cn, {})
            if isinstance(saved_data, dict):
                first_val = next(iter(saved_data.values()), None) if saved_data else None
                if isinstance(first_val, dict):
                    for domain, feed_states in saved_data.items():
                        vl = cn_vars.get(domain, [])
                        domain_feeds = config_domains.get(domain, [])
                        for i, feed in enumerate(domain_feeds):
                            if i < len(vl) and feed["name"] in feed_states:
                                vl[i].set(feed_states[feed["name"]])
                else:
                    vl = cn_vars.get("综合", [])
                    domain_feeds = config_domains.get("综合", [])
                    for i, feed in enumerate(domain_feeds):
                        if i < len(vl) and feed["name"] in saved_data:
                            vl[i].set(saved_data[feed["name"]])
    if "rss_threshold" in settings:
        gui.var_rss_threshold.set(str(settings["rss_threshold"]))
    if "rss_domain_max" in settings:
        gui.var_domain_max.set(str(settings["rss_domain_max"]))
    if "pipeline_order" in settings and settings["pipeline_order"]:
        if hasattr(gui, '_init_pipeline_stages') and hasattr(gui, '_rebuild_pipeline_rows'):
            gui._init_pipeline_stages(order=settings["pipeline_order"])
            gui._rebuild_pipeline_rows()
    if "keywords" in settings:
        from config import DOMAINS as _D
        for domain in _D:
            dn = domain["name_zh"]
            if dn in settings["keywords"]:
                domain["keywords_en"] = list(settings["keywords"][dn])


def profile_summary(settings):
    p = []
    if settings.get("fetch"): p.append("抓取")
    if settings.get("translate"): p.append("翻译")
    p.append(settings.get("window_mode", "?"))
    if settings.get("bilingual"): p.append("对照")
    if settings.get("content"): p.append("正文")
    return " | ".join(p)
