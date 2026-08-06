"""正文抓取模块 v3.0"""
import logging, re
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from config import CONTENT_FETCH_WORKERS, CONTENT_FETCH_TIMEOUT, CONTENT_MIN_LENGTH

logger = logging.getLogger(__name__)


def _clean_html(raw):
    """去除 HTML 标签、脚本、样式，提取纯文本"""
    if not raw:
        return ""
    text = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</li>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def _fetch_single(item):
    try:
        resp = requests.get(item.url, timeout=CONTENT_FETCH_TIMEOUT, headers={
            "User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200 and len(resp.text) > CONTENT_MIN_LENGTH:
            cleaned = _clean_html(resp.text)
            return cleaned[:3000]
    except Exception:
        pass
    return ""


def fetch_contents_for_items(items):
    if not items:
        return
    logger.info("开始抓取 %d 篇文章正文 (workers=%d)...", len(items), CONTENT_FETCH_WORKERS)
    success = 0
    with ThreadPoolExecutor(max_workers=CONTENT_FETCH_WORKERS) as executor:
        futures = {executor.submit(_fetch_single, item): item for item in items}
        for future in as_completed(futures):
            content = future.result()
            if content:
                futures[future].content = content
                success += 1
    logger.info("正文抓取完成: 成功 %d 篇, 失败 %d 篇", success, len(items) - success)
