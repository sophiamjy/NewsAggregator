"""翻译模块 v3.0 — Google (deep-translator) 并发版"""
import logging, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

TRANSLATE_DELAY = 0.5   # 单次请求间隔
MAX_WORKERS = 4         # 并发线程数


class TranslationEngine:
    def __init__(self, preferred="google"):
        self.available = False
        try:
            GoogleTranslator(source="en", target="zh-CN").translate("test")
            self.available = True
            logger.info("deep-translator (Google) 就绪")
        except Exception as e:
            logger.warning(f"Google 翻译不可用: {e}")


def _translate_one(text):
    """翻译单条文本，失败返回原文"""
    if not text or not text.strip():
        return text
    time.sleep(TRANSLATE_DELAY)
    for attempt in range(3):
        try:
            return GoogleTranslator(source="en", target="zh-CN").translate(text)
        except Exception:
            if attempt < 2:
                time.sleep(2)
    return text


def _translate_field(items, field_name, target_attr):
    """并发翻译某个字段"""
    texts = [(i, getattr(item, field_name, "") or "") for i, item in enumerate(items) if getattr(item, field_name, "") or ""]
    total = len(texts)
    logger.info("  翻译 %s: %d 条 (workers=%d)...", field_name, total, MAX_WORKERS)
    completed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_translate_one, text): idx for idx, text in texts}
        for future in as_completed(futures):
            idx = futures[future]
            setattr(items[idx], target_attr, future.result())
            completed += 1
    logger.info("  翻译 %s: 完成 %d 条", field_name, completed)


def translate_news_items(data, engine):
    if not engine.available:
        logger.warning("翻译引擎不可用，跳过翻译")
        return data

    all_items = []
    for cn in data:
        for dn in data[cn]:
            all_items.extend(data[cn][dn])

    total = len(all_items)
    logger.info("正在翻译 %d 条新闻 (并发 workers=%d)...", total, MAX_WORKERS)

    _translate_field(all_items, "title", "title_zh")
    _translate_field(all_items, "summary", "summary_zh")
    _translate_field(all_items, "content", "content_zh")

    logger.info("翻译完成: %d 条新闻", total)
    return data
