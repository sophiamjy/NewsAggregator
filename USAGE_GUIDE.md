# 每日中东中亚新闻聚合 — 使用指南

> 版本: 3.0.0 | 更新: 2026-06-14

## 快速开始

```bash
pip install feedparser deep-translator markdown requests python-dateutil
python gui_app.py
```

## GUI 界面

### 运行设置

- **运行阶段**：勾选 ①抓取 ②翻译
- **抓取选项**：正文开关 / 详细进度 / 达标阈值 / 域上限
- **输出选项**：对照版 / HTML 版 / 以色列-伊朗战争专题
- **时间窗口**：昨日 00:00 ~ 当前 / 仅前一天
- **邮件设置**：是否发送原文/翻译/对照 + 附件模式 + 收件邮箱
- **配置方案**：保存/加载/设默认

### 新闻源选择

- **Google News RSS**：免费，需 VPN
- **各国专属 RSS**：按政治/经济/科技/综合四领域分组展示，空领域自动隐藏
- **查询顺序**：↑↓ 调整 3 阶段执行顺序，勾选启用/禁用

### 关键词管理

编辑三个领域的英文搜索关键词，保存后重新抓取生效。

## 输出文件

| 文件 | 说明 |
|------|------|
| `新闻聚合输出/每日中东中亚新闻_{date}_原文.md` | 英文原文 |
| `新闻聚合输出/每日中东中亚新闻_{date}_翻译.md` | 中文翻译 |
| `新闻聚合输出/每日中东中亚新闻_{date}_对照.md` | 中英对照 |
| `新闻聚合输出/*.html` | HTML 版（可复制粘贴到邮件） |

## GitHub Actions 自动运行

1. 确保 `.github/workflows/daily.yml` 已推送到仓库
2. 仓库 Settings → Secrets → Actions 设置 4 个 Secret：
   - `EMAIL_USER`（发件邮箱）
   - `EMAIL_AUTH`（QQ 授权码）
   - `EMAIL_TO`（收件人）
   - `EMAIL_CC`（抄送）
3. 定时 cron：UTC 00:30 = 北京时间 08:30
4. 手动触发：Actions → Daily News → Run workflow

## GitHub Pages

Actions 自动将翻译版 HTML 部署到 `https://用户名.github.io/仓库名/`，每天更新。

仓库 Settings → Pages → Source 选 **GitHub Actions**。

## 隐私安全

| 文件 | 推送到 GitHub | 说明 |
|------|:--:|------|
| `config.py` | ✅ | EMAIL_CONFIG 已清空 |
| `api_keys.json` | ❌ | gitignored, 存真实密钥 |
| `profiles.json` | ❌ | gitignored, 含邮箱地址 |
| `运行日志/` | ❌ | gitignored |
| Actions 控制台日志 | ✅ | 无敏感信息 |

## CLI

```bash
python main.py                  # 完整运行
python main.py --no-translate   # 跳过翻译
python main.py --no-content     # 跳过正文
python main.py --no-html        # 跳过 HTML
```

## 常见问题

- **战争专题新闻数少**：可在 `config.py` 的 `WAR_TOPIC_KEYWORDS` 增减关键词
- **邮件 550 错误**：QQ 邮箱内容过滤，改用附件模式
- **HTML 乱码**：v3.0 已修复翻译残留标签
- **翻译限流 429**：v3.0 已加 0.3s 延时 + 分批
- **某国 RSS 抓取为空**：查看运行日志，大部分 RSS 需 VPN
- **同一文章在不同国家出现**：跨国家文章正常，同国不同领域已通过 AID 去重消除
