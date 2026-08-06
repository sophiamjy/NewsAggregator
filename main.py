#!/usr/bin/env python3
"""每日中东中亚新闻聚合 CLI v3.0 — GitHub Actions 自动化"""
import logging, os, sys
from datetime import datetime

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _APP_DIR)

from config import (OUTPUT_DIR, LOG_DIR, ENABLE_CONTENT_FETCH, ENABLE_GOOGLE_RSS, TIME_WINDOW_MODE,
                    COUNTRY_RSS_FEEDS, WAR_TOPIC_ENABLED)
from news_fetcher import (NewsAggregator, get_time_window_start, get_time_window_end,
                          now_beijing, set_window_mode)
from markdown_writer import (generate_markdown, write_markdown_file,
                             generate_markdown_bilingual, write_html_file)
from translator import TranslationEngine, translate_news_items
from email_sender import send_email, send_email_attachment

LOG_DIR_PATH = os.path.join(_APP_DIR, LOG_DIR)
os.makedirs(LOG_DIR_PATH, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S",
                    handlers=[logging.StreamHandler(sys.stdout),
                              logging.FileHandler(os.path.join(LOG_DIR_PATH,
                                  f"运行日志{datetime.now().strftime('%Y%m%d%H%M%S')}.log"), encoding="utf-8")])
logger = logging.getLogger(__name__)

O_ORIG = "每日中东中亚新闻_{date}_原文.md"
O_TRANS = "每日中东中亚新闻_{date}_翻译.md"
O_BI = "每日中东中亚新闻_{date}_对照.md"


def _fn(ds, is_trans):
    return (O_TRANS if is_trans else O_ORIG).replace("{date}", ds)


def run(no_translate=False, no_content=False, no_html=False):
    if not no_content: no_content = not ENABLE_CONTENT_FETCH
    mode = TIME_WINDOW_MODE; set_window_mode(mode)
    ws = get_time_window_start(mode); we = get_time_window_end(mode)
    ds = ws.strftime("%Y-%m-%d") if mode == "yesterday_only" else ws.strftime("%Y-%m-%d") + "起"

    logger.info("=" * 50)
    logger.info("每日中东中亚新闻聚合 v3.0")
    logger.info("时间窗口: %s ~ %s (北京)", ws.strftime("%Y-%m-%d %H:%M"), we.strftime("%Y-%m-%d %H:%M"))

    agg = NewsAggregator(enable_google_rss=ENABLE_GOOGLE_RSS, country_rss_config=COUNTRY_RSS_FEEDS, window_mode=mode)
    data = agg.fetch_all(fetch_content=not no_content)
    stats = agg.stats
    logger.info("抓取完成: %d 条 (R=%d RSS=%d)", stats["total_fetched"], stats["google_rss"], stats["country_rss"])

    orig_md = generate_markdown(data, generation_time=now_beijing(), is_translated=False,
                                window_mode=mode, stats=stats, has_content=not no_content)
    orig_file = write_markdown_file(orig_md, _APP_DIR, output_dir=OUTPUT_DIR, output_file=_fn(ds, False), prepend=True)
    logger.info("原文: %s", orig_file)
    if not no_html: write_html_file(orig_md, _APP_DIR, output_dir=OUTPUT_DIR, output_file=_fn(ds, False), data=data)

    trans_file = None
    if not no_translate:
        logger.info("翻译 (Google)...")
        engine = TranslationEngine(preferred="google")
        if engine.available:
            data_t = translate_news_items(data, engine)
            trans_md = generate_markdown(data_t, generation_time=now_beijing(), is_translated=True,
                                         window_mode=mode, stats=stats, has_content=not no_content)
            trans_file = write_markdown_file(trans_md, _APP_DIR, output_dir=OUTPUT_DIR, output_file=_fn(ds, True), prepend=True)
            logger.info("翻译: %s", trans_file)
            if not no_html: write_html_file(trans_md, _APP_DIR, output_dir=OUTPUT_DIR, output_file=_fn(ds, True), data=data_t)
            bi_md = generate_markdown_bilingual(data_t, generation_time=now_beijing(),
                                                window_mode=mode, stats=stats, has_content=not no_content)
            write_markdown_file(bi_md, _APP_DIR, output_dir=OUTPUT_DIR, output_file=O_BI.replace("{date}", ds), prepend=True)
            if not no_html: write_html_file(bi_md, _APP_DIR, output_dir=OUTPUT_DIR, output_file=O_BI.replace("{date}", ds), data=data_t)
        else: logger.warning("Google 翻译不可用")
    logger.info("全部完成！")
    return {"orig": orig_file, "trans": trans_file, "stats": stats}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="每日中东中亚新闻聚合 CLI")
    p.add_argument("--no-translate", action="store_true")
    p.add_argument("--no-content", action="store_true")
    p.add_argument("--no-html", action="store_true")
    args = p.parse_args()
    result = run(no_translate=args.no_translate, no_content=args.no_content, no_html=args.no_html)

    trans_file = result.get("trans")
    if trans_file and os.path.exists(trans_file):
        with open(trans_file, "r", encoding="utf-8") as f: content = f.read()
        if send_email(content, subject=f"每日中东中亚新闻-翻译",
                sender_email=os.environ.get("EMAIL_USER", ""),
                auth_code=os.environ.get("EMAIL_AUTH", ""),
                to_email=os.environ.get("EMAIL_TO", ""),
                to_email2=os.environ.get("EMAIL_CC", "")):
            logger.info("邮件已发送")
        else: logger.warning("邮件发送失败")
    else:
        logger.info("无翻译文件, 跳过邮件")
