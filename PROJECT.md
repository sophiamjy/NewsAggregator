# 每日中东中亚新闻聚合 — 项目文档

> 版本: 3.0.0 | 更新: 2026-06-14 | Python 3

## 项目概述

从 Google News RSS 和各国本地 RSS 抓取中东 12 国 + 中亚及高加索 9 国（共 21 国）最新英文新闻，按政治/经济/科技/综合四类组织，Google 翻译为中文，生成 Markdown + HTML 报告，通过 QQ SMTP 邮件投递 + GitHub Pages 网页展示。

### 核心功能

- **3 阶段查询流水线**：各国 RSS → Google RSS 宽泛 → Google RSS 定向，可自由排序 + 启用/禁用
- **以色列-伊朗战争专题**：46 组关键词分 10 批查询，虚拟国家混入主输出
- **纯标题 AID 去重**：跨 API/跨 URL/跨领域不重复
- **领域专属 RSS**：直接归类 + 本地分类兜底，多领域命中归入综合/其它 + 多标签
- **来源标签**：每条新闻标注 `[Google RSS]` / 具体 RSS 源名
- **HTML 输出**：蓝白配色，可复制粘贴到邮件
- **邮件正文 + 附件**：附件模式正文仅一句"请查看附件"
- **GitHub Actions 自动化**：每日定时抓取 + 邮件投递 + Pages 部署
- **隐私安全**：密钥存于本地 `api_keys.json`（gitignored），仓库公开零泄露

### 技术栈

| 层 | 技术 |
|----|------|
| GUI | tkinter |
| 新闻源 | Google News RSS + 各国本地 RSS（领域分组） |
| 翻译 | Google (deep-translator)，分批 + 0.3s 延时防限流 |
| 正文 | requests + HTML 清洗（去 script/style/标签） |
| 输出 | Markdown + HTML |
| 投递 | QQ SMTP SSL:465 |
| 定时 | GitHub Actions (cron) |
| 网页 | GitHub Pages (Actions 部署) |

### 架构

```
config.py (配置: 21国/RSS/关键词/邮件/战争专题/流水线)
    ├── news_fetcher.py   (GoogleRSS + CountryRSS + 分批战争专题 + 消歧)
    ├── translator.py     (Google deep-translator, 分批 + 限流)
    ├── content_fetcher.py (正文抓取 + HTML清洗)
    ├── markdown_writer.py (Markdown + HTML 生成)
    ├── email_sender.py   (SMTP 正文 + 附件, 日志脱敏)
    ├── profile_manager.py (配置方案保存/加载)
    ├── gui_app.py        (tkinter GUI)
    └── main.py           (CLI, GitHub Actions 用)
.github/workflows/daily.yml
.gitignore (api_keys.json / profiles.json / 运行日志/)
```

### 去重设计

AID = 纯标题 MD5，`all_aids[cn]` 全局字典跨阶段共享。领域专属 RSS 先查重再本地分类。`_strip_html` 清洗畸形标签（`<一href=`、`href="..."` 等翻译残留）。

### 翻译设计 (v3.0)

`_translate_field` 按 BATCH_SIZE=5 分批，每条翻译间隔 0.3s，避免触发 Google 429 限流。标题/摘要/正文三个字段依次串行处理。

### 正文抓取 (v3.0)

`_clean_html` 先剥离 `<script>`/`<style>` 块，再去除所有标签，解 HTML 实体，截取前 3000 字符。

### 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 3.0.0 | 2026-06-14 | 精简架构(仅Google RSS+国家RSS+Google翻译), 战争专题分批查询, 翻译分批限流, 正文HTML清洗, 邮件附件, GitHub Pages, 全链路脱敏, PIPELINE_ORDER 清理, SUMMARY_MAX_LENGTH 去重, ENABLE_GOOGLE_RSS 配置化 |

### 运行

```bash
python gui_app.py     # GUI
python main.py        # CLI (GitHub Actions)
```

### 输出

`新闻聚合输出/` 目录：原文.md、翻译.md、对照.md + 对应 .html

### 安全

- `api_keys.json` — 本地密钥，.gitignore 保护
- `profiles.json` — 配置方案，.gitignore 保护（含邮箱）
- `config.py` EMAIL_CONFIG — 已清空为占位符
- 邮件日志 — 只显示"邮件发送成功"，不泄露邮箱
- 运行日志 — .gitignore 保护，不提交到仓库
