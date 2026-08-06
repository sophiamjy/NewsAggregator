"""Markdown/HTML 生成模块 v3.0"""
import logging, os, re
from datetime import datetime
from config import COUNTRIES, DOMAINS, OUTPUT_DIR, OUTPUT_FILE, SUMMARY_MAX_LENGTH
from news_fetcher import get_time_window_start, now_beijing, get_time_window_end

logger = logging.getLogger(__name__)


def _strip_html(text):
    if not text: return text
    text = re.sub(r'<br\s*/?>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<li[^>]*>', ' - ', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</?(ol|ul)[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?p[^>]*>?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def _get_country_config(name):
    for c in COUNTRIES:
        if c['name'] == name: return c
    return {'flag': '🌍', 'name': name, 'name_en': name}


def generate_markdown(data, generation_time=None, is_translated=False,
                      window_mode=None, stats=None, has_content=False):
    if generation_time is None: generation_time = datetime.now()
    time_str = generation_time.strftime("%Y-%m-%d %H:%M:%S")
    date_str = generation_time.strftime("%Y年%m月%d日")
    lines = []
    lines.append("# 每日中东中亚新闻信息聚合")
    lines.append("")
    lines.append(f"> 生成时间：{time_str}")
    lines.append("> 覆盖区域：中东12国 + 中亚及高加索9国")
    lines.append(f"> 覆盖领域：{', '.join(d['name_zh'] for d in DOMAINS)}")
    ws = get_time_window_start(window_mode)
    we = get_time_window_end(window_mode) if window_mode else now_beijing()
    lines.append(f"> 收录窗口：{ws.strftime('%Y-%m-%d %H:%M')} ~ {we.strftime('%Y-%m-%d %H:%M')} (北京时间)")
    lang_label = "中文翻译" if is_translated else "英文原文"
    lines.append(f"> 语言：{lang_label} | 正文：{'含正文' if has_content else '仅标题摘要'}")
    if stats:
        src_info = []
        if stats.get("google_rss", 0) > 0: src_info.append(f"GoogleRSS({stats['google_rss']}条)")
        if stats.get("country_rss", 0) > 0: src_info.append(f"各国RSS({stats['country_rss']}条)")
        if src_info: lines.append(f"> 新闻源：{' | '.join(src_info)}")
        cat_counts = {}
        for cn in data:
            for dn in data[cn]:
                cat_counts[dn] = cat_counts.get(dn, 0) + len(data[cn][dn])
        lines.append(f"> 分类统计：{'  |  '.join(f'{dn}: {cnt}' for dn, cnt in cat_counts.items())}")
    lines.append(""); lines.append("---"); lines.append("")
    total = sum(len(data[cn][dn]) for cn in data for dn in data[cn])
    lines.append(f"## {date_str} 新闻概览")
    lines.append("")
    lines.append(f"共收录 **{total}** 条新闻，覆盖 **{len(COUNTRIES)}** 个国家、**{len(DOMAINS)}** 个领域。")
    lines.append("")
    lines.append("| 国家 | 政治 | 经济 | 科技 | 综合 | 合计 |")
    lines.append("|------|:----:|:----:|:----:|:----:|:----:|")
    for cn in data:
        cfg = _get_country_config(cn)
        counts = []
        cn_total = 0
        for dn in [d["name_zh"] for d in DOMAINS] + ["综合/其它"]:
            cnt = len(data[cn].get(dn, []))
            counts.append(str(cnt)); cn_total += cnt
        lines.append(f"| {cfg.get('flag','🌍')} {cn} | {' | '.join(counts)} | **{cn_total}** |")
    lines.append(""); lines.append("---"); lines.append("")

    for cn in data:
        cfg = _get_country_config(cn)
        lines.append(f"## {cfg.get('flag','🌍')} {cn} ({cfg.get('name_en', cn)})")
        lines.append("")
        all_cats = [(d["name_zh"], d.get("icon","📌"), d.get("name_en",d["name_zh"])) for d in DOMAINS]
        all_cats.append(("综合/其它", "📋", "General/Other"))
        for dn, di, de in all_cats:
            articles = data[cn].get(dn, [])
            lines.append(f"### {di} {dn} ({de})")
            lines.append("")
            if not articles:
                lines.append(f"> 暂无收录窗口内的{dn}相关新闻"); lines.append(""); continue
            for i, item in enumerate(articles, 1):
                te = item.title.strip(); url = item.url.strip()
                src = item.source.strip(); pt = item.published.strftime("%Y-%m-%d %H:%M") if item.published else "未知"
                se = _strip_html(item.summary.strip()) if item.summary else ""
                tz = getattr(item, "title_zh", "") or ""
                sz = _strip_html(getattr(item, "summary_zh", "")) if getattr(item, "summary_zh", "") else ""
                if tz and tz != te:
                    lines.append(f"**{i}. {tz}**"); lines.append("")
                    lines.append(f"> 原文：[{te}]({url})")
                else:
                    lines.append(f"**{i}. [{te}]({url})**")
                lines.append("")
                sl = getattr(item, "source_label", "") or src
                lines.append(f"来源：{src}  `[{sl}]` | {pt}" if sl != src else f"来源：{src} | {pt}")
                tags = getattr(item, "tags", "")
                if tags: lines.append(f"标签：{tags}")
                lines.append("")
                ds = sz if sz else se
                if ds:
                    if len(ds) > SUMMARY_MAX_LENGTH: ds = ds[:SUMMARY_MAX_LENGTH] + "..."
                    lines.append(f"摘要：{ds}"); lines.append("")
                lines.append("---"); lines.append("")
    lines.append("---"); lines.append("")
    lines.append("*本报告由自动新闻聚合系统生成，数据来源于 Google News RSS 及各国本地 RSS。*")
    lines.append(f"*生成时间：{time_str}*"); lines.append("")
    return "\n".join(lines)


def generate_markdown_bilingual(data, generation_time=None, window_mode=None, stats=None, has_content=False):
    if generation_time is None: generation_time = datetime.now()
    time_str = generation_time.strftime("%Y-%m-%d %H:%M:%S")
    date_str = generation_time.strftime("%Y年%m月%d日")
    lines = []
    lines.append("# 每日中东中亚新闻信息聚合（中英对照）")
    lines.append("")
    lines.append(f"> 生成时间：{time_str}")
    ws = get_time_window_start(window_mode)
    we = get_time_window_end(window_mode) if window_mode else now_beijing()
    lines.append(f"> 收录窗口：{ws.strftime('%Y-%m-%d %H:%M')} ~ {we.strftime('%Y-%m-%d %H:%M')} (北京时间)")
    lines.append(f"> 语言：中英对照 | 正文：{'含正文' if has_content else '仅标题摘要'}")
    if stats:
        si = []
        if stats.get("google_rss",0)>0: si.append(f"GoogleRSS({stats['google_rss']}条)")
        if stats.get("country_rss",0)>0: si.append(f"各国RSS({stats['country_rss']}条)")
        if si: lines.append(f"> 新闻源：{' | '.join(si)}")
        cat_counts = {}
        for cn in data:
            for dn in data[cn]:
                cat_counts[dn] = cat_counts.get(dn, 0) + len(data[cn][dn])
        lines.append(f"> 分类统计：{'  |  '.join(f'{dn}: {cnt}' for dn, cnt in cat_counts.items())}")
    lines.append(""); lines.append("---"); lines.append("")

    total = sum(len(data[cn].get(dn,[])) for cn in data for dn in data[cn])
    lines.append(f"## {date_str} 新闻概览")
    lines.append("")
    lines.append(f"共收录 **{total}** 条新闻，覆盖 **{len(COUNTRIES)}** 个国家。")
    lines.append("")
    lines.append("| 国家 | 政治 | 经济 | 科技 | 综合 | 合计 |")
    lines.append("|------|:----:|:----:|:----:|:----:|:----:|")
    for cn in data:
        cfg = _get_country_config(cn)
        counts = []; cn_total = 0
        for dn in [d["name_zh"] for d in DOMAINS] + ["综合/其它"]:
            cnt = len(data[cn].get(dn,[])); counts.append(str(cnt)); cn_total += cnt
        lines.append(f"| {cfg.get('flag','🌍')} {cn} | {' | '.join(counts)} | **{cn_total}** |")
    lines.append(""); lines.append("---"); lines.append("")

    for cn in data:
        cfg = _get_country_config(cn)
        lines.append(f"## {cfg.get('flag','🌍')} {cn} ({cfg.get('name_en',cn)})")
        lines.append("")
        all_cats = [(d["name_zh"], d.get("icon","📌")) for d in DOMAINS] + [("综合/其它","📋")]
        for dn, di in all_cats:
            articles = data[cn].get(dn, [])
            lines.append(f"### {di} {dn}"); lines.append("")
            if not articles:
                lines.append(f"> 暂无收录窗口内的{dn}相关新闻"); lines.append(""); continue
            for i, item in enumerate(articles, 1):
                te = item.title.strip(); url = item.url.strip(); src = item.source.strip()
                pt = item.published.strftime("%Y-%m-%d %H:%M") if item.published else ""
                tz = getattr(item,"title_zh","") or ""
                sz = _strip_html(getattr(item,"summary_zh","")) if getattr(item,"summary_zh","") else ""
                se = _strip_html(item.summary.strip()) if item.summary else ""
                tags = getattr(item,"tags","")
                display = tz if tz else te
                lines.append(f"**{i}. [{display}]({url})**"); lines.append("")
                if tz and tz != te:
                    lines.append(f"> 英文标题：{te}"); lines.append("")
                sl = getattr(item,"source_label","") or src
                lines.append(f"> 来源：{src}  `[{sl}]` | {pt}" if sl != src else f"> 来源：{src} | {pt}")
                if tags: lines.append(f"> 标签：{tags}")
                lines.append("")
                if sz:
                    ds = sz[:SUMMARY_MAX_LENGTH] + ("..." if len(sz)>SUMMARY_MAX_LENGTH else "")
                    lines.append(f"> **中文摘要：** {ds}"); lines.append("")
                if se:
                    ds = se[:SUMMARY_MAX_LENGTH] + ("..." if len(se)>SUMMARY_MAX_LENGTH else "")
                    lines.append(f"> 英文摘要：{ds}"); lines.append("")
                lines.append("---"); lines.append("")
    lines.append("---"); lines.append("")
    lines.append("*本报告由自动新闻聚合系统生成，数据来源于 Google News RSS 及各国本地 RSS。*")
    lines.append(f"*生成时间：{time_str}*"); lines.append("")
    return "\n".join(lines)


def write_markdown_file(content, base_dir, output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE, prepend=True):
    full_dir = os.path.join(base_dir, output_dir)
    os.makedirs(full_dir, exist_ok=True)
    file_path = os.path.join(full_dir, output_file)
    if prepend and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f: existing = f.read()
        combined = content + "\n\n" + "=" * 60 + "\n\n" + existing
        with open(file_path, "w", encoding="utf-8") as f: f.write(combined)
    else:
        with open(file_path, "w", encoding="utf-8") as f: f.write(content)
    logger.info(f"输出: {file_path}")
    return file_path


_HTML_CSS = """<style>
body{font-family:'Segoe UI','Microsoft YaHei',sans-serif;max-width:800px;margin:0 auto;padding:20px;color:#333}
h1{color:#1a5276;border-bottom:2px solid #2980b9;padding-bottom:10px}
h2{color:#2471a3;border-bottom:1px solid #aed6f1;padding-bottom:6px;margin-top:30px}
h3{color:#2e86c1;margin-top:20px}
a{color:#2980b9;text-decoration:none}
table{border-collapse:collapse;width:100%;margin:15px 0}
th,td{border:1px solid #d4e6f1;padding:8px 12px;text-align:center}
th{background:#2980b9;color:white}
tr:nth-child(even){background:#f2f8fc}
hr{border:none;border-top:1px solid #d4e6f1;margin:20px 0}
strong{color:#1a5276}
blockquote{border-left:3px solid #aed6f1;margin:10px 0;padding:5px 15px;color:#555;background:#f7fafc}
.footer{color:#999;font-size:.85em;margin-top:40px;border-top:1px solid #eee;padding-top:15px}
.nav{position:fixed;top:0;left:0;right:0;background:#1a5276;padding:8px 20px;z-index:999;display:flex;flex-wrap:wrap;gap:4px;max-height:40vh;overflow-y:auto}
.nav a{color:#fff;text-decoration:none;font-size:12px;padding:3px 8px;border-radius:3px;white-space:nowrap}
.nav a:hover,.nav a:focus{background:#2980b9}
.nav-toggle{display:none;position:fixed;top:5px;right:10px;z-index:1000;background:#1a5276;color:#fff;border:none;padding:6px 12px;border-radius:4px;font-size:14px;cursor:pointer}
@media(max-width:600px){.nav{display:none}.nav.open{display:flex}.nav-toggle{display:block}}
body{padding-top:50px}
</style>"""


def _generate_nav(data):
    """生成导航栏HTML"""
    links = ['<div class="nav" id="topNav"><a href="#top">📊 概览</a>']
    for cn in data:
        anchor = cn.replace(" ", "-").replace("⚔️", "war")
        links.append(f'<a href="#{anchor}">{cn}</a>')
    links.append('</div><button class="nav-toggle" onclick="document.getElementById(\'topNav\').classList.toggle(\'open\')">☰ 导航</button>')
    return "".join(links)


def _inject_nav(html_body, data):
    """在 HTML body 中注入导航栏和锚点"""
    # 先给每个 h2 加 id（h2 格式: <h2>🇸🇦 沙特阿拉伯 (Saudi Arabia)</h2>）
    for cn in data:
        anchor = cn.replace(" ", "-").replace("⚔️", "war")
        import re as _re2
        pattern = _re2.compile(r'<h2>[^\n]*' + _re2.escape(cn) + r'[^\n]*</h2>')
        m = pattern.search(html_body)
        if m:
            old_h2 = m.group(0)
            new_h2 = old_h2.replace('<h2>', f'<h2 id="{anchor}">')
            html_body = html_body.replace(old_h2, new_h2)
    # html_body 是 markdown 渲染后的纯内容（无 <body> 标签），直接在前面拼接导航
    nav = _generate_nav(data)
    # 给概览的 h2 加锚点（标题格式: "2026年08月05日 新闻概览"）
    import re as _re
    html_body = _re.sub(r'<h2>([^<]*)新闻概览</h2>', r'<h2 id="top">\1新闻概览</h2>', html_body)
    return nav + html_body


def generate_html(md_content, data=None):
    try:
        import markdown as _md
        html_body = _md.markdown(md_content, extensions=['extra'])
    except ImportError:
        html_body = md_content.replace('\n', '<br>\n')
    if data:
        html_body = _inject_nav(html_body, data)
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{_HTML_CSS}</head>
<body>{html_body}<div class="footer">本报告由自动新闻聚合系统生成</div></body></html>"""


def write_html_file(md_content, base_dir, output_dir=OUTPUT_DIR, output_file="news.html", data=None):
    full_dir = os.path.join(base_dir, output_dir)
    os.makedirs(full_dir, exist_ok=True)
    if output_file.endswith('.md'): output_file = output_file[:-3] + '.html'
    file_path = os.path.join(full_dir, output_file)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(generate_html(md_content, data=data))
    logger.info(f"HTML: {file_path}")
    return file_path
