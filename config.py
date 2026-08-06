"""
每日中东中亚新闻聚合 - 配置文件
==================================
包含国家定义、领域分类、新闻源配置、邮件配置等。
覆盖中东12国 + 中亚及高加索9国 = 共21国

版本: 3.0.0 | 更新: 2026-06-14
新增: 精简架构(仅Google RSS+国家RSS+Google翻译)、战争专题、HTML输出、邮件附件、GitHub Pages
"""

# ============================================================
# 目标国家定义
# 中东地区 12 国 + 中亚及高加索 9 国 = 共 21 国
# ============================================================
COUNTRIES = [
    # ========================
    # 中东地区 (12国)
    # ========================
    {
        "name": "沙特阿拉伯",
        "name_en": "Saudi Arabia",
        "flag": "🇸🇦",
        "code": "sa",
        "region": "中东",
        "search_keywords": {
            "en": ["Saudi Arabia", "Saudi", "Riyadh", "Jeddah"],
            "ar": ["السعودية", "سعودي"],
        },
    },
    {
        "name": "阿联酋",
        "name_en": "UAE",
        "flag": "🇦🇪",
        "code": "ae",
        "region": "中东",
        "search_keywords": {
            "en": ["UAE", "United Arab Emirates", "Dubai", "Abu Dhabi", "Emirati"],
            "ar": ["الإمارات", "دبي", "أبوظبي"],
        },
    },
    {
        "name": "阿曼",
        "name_en": "Oman",
        "flag": "🇴🇲",
        "code": "om",
        "region": "中东",
        "search_keywords": {
            "en": ["Oman", "Omani", "Muscat"],
            "ar": ["عمان", "مسقط"],
        },
    },
    {
        "name": "卡塔尔",
        "name_en": "Qatar",
        "flag": "🇶🇦",
        "code": "qa",
        "region": "中东",
        "search_keywords": {
            "en": ["Qatar", "Qatari", "Doha"],
            "ar": ["قطر", "الدوحة"],
        },
    },
    {
        "name": "科威特",
        "name_en": "Kuwait",
        "flag": "🇰🇼",
        "code": "kw",
        "region": "中东",
        "search_keywords": {
            "en": ["Kuwait", "Kuwaiti", "Kuwait City"],
            "ar": ["الكويت", "كويتي"],
        },
    },
    {
        "name": "巴林",
        "name_en": "Bahrain",
        "flag": "🇧🇭",
        "code": "bh",
        "region": "中东",
        "search_keywords": {
            "en": ["Bahrain", "Bahraini", "Manama"],
            "ar": ["البحرين", "المنامة"],
        },
    },
    {
        "name": "巴基斯坦",
        "name_en": "Pakistan",
        "flag": "🇵🇰",
        "code": "pk",
        "region": "中东",
        "search_keywords": {
            "en": ["Pakistan", "Pakistani", "Islamabad", "Lahore", "Karachi"],
            "ur": ["پاکستان", "اسلام آباد"],
        },
    },
    {
        "name": "伊拉克",
        "name_en": "Iraq",
        "flag": "🇮🇶",
        "code": "iq",
        "region": "中东",
        "search_keywords": {
            "en": ["Iraq", "Iraqi", "Baghdad"],
            "ar": ["العراق", "بغداد"],
        },
    },
    {
        "name": "阿富汗",
        "name_en": "Afghanistan",
        "flag": "🇦🇫",
        "code": "af",
        "region": "中东",
        "search_keywords": {
            "en": ["Afghanistan", "Afghan", "Kabul"],
            "ar": ["أفغانستان", "كابل"],
        },
    },
    {
        "name": "也门",
        "name_en": "Yemen",
        "flag": "🇾🇪",
        "code": "ye",
        "region": "中东",
        "search_keywords": {
            "en": ["Yemen", "Yemeni", "Sanaa", "Houthi"],
            "ar": ["اليمن", "صنعاء"],
        },
    },
    {
        "name": "约旦",
        "name_en": "Jordan",
        "flag": "🇯🇴",
        "code": "jo",
        "region": "中东",
        "search_keywords": {
            "en": ["Jordan", "Jordanian", "Amman"],
            "ar": ["الأردن", "عمان"],
        },
    },
    {
        "name": "黎巴嫩",
        "name_en": "Lebanon",
        "flag": "🇱🇧",
        "code": "lb",
        "region": "中东",
        "search_keywords": {
            "en": ["Lebanon", "Lebanese", "Beirut"],
            "ar": ["لبنان", "بيروت"],
        },
    },

    # ========================
    # 中亚及高加索地区 (9国)
    # ========================
    {
        "name": "哈萨克斯坦",
        "name_en": "Kazakhstan",
        "flag": "🇰🇿",
        "code": "kz",
        "region": "中亚",
        "search_keywords": {
            "en": ["Kazakhstan", "Kazakh", "Astana", "Almaty"],
            "ru": ["Казахстан", "казахстанский"],
            "local": ["Қазақстан"],
        },
    },
    {
        "name": "乌兹别克斯坦",
        "name_en": "Uzbekistan",
        "flag": "🇺🇿",
        "code": "uz",
        "region": "中亚",
        "search_keywords": {
            "en": ["Uzbekistan", "Uzbek", "Tashkent", "Samarkand"],
            "ru": ["Узбекистан", "узбекский"],
            "local": ["O'zbekiston"],
        },
    },
    {
        "name": "吉尔吉斯斯坦",
        "name_en": "Kyrgyzstan",
        "flag": "🇰🇬",
        "code": "kg",
        "region": "中亚",
        "search_keywords": {
            "en": ["Kyrgyzstan", "Kyrgyz", "Bishkek"],
            "ru": ["Кыргызстан", "кыргызский"],
            "local": ["Кыргызстан"],
        },
    },
    {
        "name": "塔吉克斯坦",
        "name_en": "Tajikistan",
        "flag": "🇹🇯",
        "code": "tj",
        "region": "中亚",
        "search_keywords": {
            "en": ["Tajikistan", "Tajik", "Dushanbe"],
            "ru": ["Таджикистан", "таджикский"],
            "local": ["Тоҷикистон"],
        },
    },
    {
        "name": "土库曼斯坦",
        "name_en": "Turkmenistan",
        "flag": "🇹🇲",
        "code": "tm",
        "region": "中亚",
        "search_keywords": {
            "en": ["Turkmenistan", "Turkmen", "Ashgabat"],
            "ru": ["Туркменистан", "туркменский"],
            "local": ["Türkmenistan"],
        },
    },
    {
        "name": "蒙古",
        "name_en": "Mongolia",
        "flag": "🇲🇳",
        "code": "mn",
        "region": "中亚",
        "search_keywords": {
            "en": ["Mongolia", "Mongolian", "Ulaanbaatar"],
            "ru": ["Монголия", "монгольский"],
            "local": ["Монгол"],
        },
    },
    {
        "name": "阿塞拜疆",
        "name_en": "Azerbaijan",
        "flag": "🇦🇿",
        "code": "az",
        "region": "中亚",
        "search_keywords": {
            "en": ["Azerbaijan", "Azerbaijani", "Baku"],
            "ru": ["Азербайджан", "азербайджанский", "Баку"],
            "local": ["Azərbaycan", "Bakı"],
        },
    },
    {
        "name": "亚美尼亚",
        "name_en": "Armenia",
        "flag": "🇦🇲",
        "code": "am",
        "region": "中亚",
        "search_keywords": {
            "en": ["Armenia", "Armenian", "Yerevan"],
            "ru": ["Армения", "армянский"],
            "local": ["Հայաստան"],
        },
    },
    {
        "name": "格鲁吉亚",
        "name_en": "Georgia",
        "flag": "🇬🇪",
        "code": "ge",
        "region": "中亚",
        "search_keywords": {
            "en": ["Georgia", "Georgian", "Sakartvelo", "საქართველო"],
            "ru": ["Грузия", "грузинский", "Тбилиси"],
            "local": ["საქართველო", "თბილისი"],
        },
    },
]

# ============================================================
# 新闻领域定义（5 大领域 + 搜索关键词）
# ============================================================
DOMAINS = [
    {
        "name_zh": "政治",
        "name_en": "Politics",
        "icon": "🏛️",
        "keywords_en": [
            "politics", "government", "president", "parliament",
            "election", "diplomatic", "foreign policy", "minister",
            "political", "opposition", "reform", "constitution",
            "conflict", "war", "military", "security", "peace",
        ],
        "keywords_zh": [
            "政治", "政府", "总统", "议会", "选举", "外交",
            "部长", "改革", "宪法", "反对派", "冲突", "军事", "安全",
        ],
    },
    {
        "name_zh": "经济",
        "name_en": "Economy",
        "icon": "💰",
        "keywords_en": [
            "economy", "trade", "GDP", "investment", "economic",
            "industry", "infrastructure", "agriculture", "energy",
            "export", "import", "sanction", "development",
            "finance", "banking", "stock market", "currency",
            "central bank", "exchange rate", "bond", "loan",
            "financial", "monetary", "inflation", "debt",
            "fiscal", "budget", "tax", "public spending",
            "treasury", "subsidy", "revenue", "expenditure",
            "deficit", "sovereign fund", "pension", "oil",
        ],
        "keywords_zh": [
            "经济", "贸易", "投资", "GDP", "产业",
            "基础设施", "农业", "能源", "出口", "进口",
            "金融", "银行", "股市", "货币", "央行",
            "汇率", "债券", "贷款", "通胀",
            "财政", "预算", "税收", "公共支出", "补贴",
            "养老金", "赤字", "财政收入", "石油",
        ],
    },
    {
        "name_zh": "科技",
        "name_en": "Technology",
        "icon": "🔬",
        "keywords_en": [
            "technology", "digital", "innovation", "startup",
            "telecom", "internet", "AI", "cyber",
            "space", "science", "tech", "5G", "data center",
        ],
        "keywords_zh": [
            "科技", "数字", "创新", "创业", "电信",
            "互联网", "人工智能", "航天", "5G",
        ],
    },
]
# ============================================================
# 新闻源配置
# ============================================================




# 新闻源选择性启用（可在 GUI 或命令行中覆盖）
ENABLE_GOOGLE_RSS = True

# 每个国家-领域组合获取的文章数量
ARTICLES_PER_QUERY = 6  # 多取1条用于去重后的余量
TARGET_ARTICLES = 99     # v2.4: 不设硬性上限（实际由时间窗口和去重控制）

# 请求超时和重试设置
REQUEST_TIMEOUT = 15     # 单次请求超时（秒）
MAX_RETRIES = 2          # 失败重试次数
REQUEST_DELAY = 1.2      # 请求间隔（秒）,避免触发频率限制

# ============================================================
# 时间窗口配置（v2.0 新增）
# ============================================================
# 新闻时间筛选基准：从「北京时间昨日 00:00:00」开始计算
# 即：每次运行时,只收录发布时间 ≥ 北京时间昨日 00:00 的新闻
# 例如：5月1日 16:44 运行 → 收录 4月30日 00:00 至今的所有新闻
# 这样可以避免同一天多次运行时产生大量重复内容
TIME_WINDOW_START_HOUR = 0    # 起始小时（北京时间）
TIME_WINDOW_START_MINUTE = 0  # 起始分钟（北京时间）
TIME_WINDOW_START_SECOND = 0  # 起始秒（北京时间）
TIME_WINDOW_OFFSET_DAYS = -1  # 偏移天数（-1 = 昨天,0 = 今天）

# ============================================================
# 文章正文抓取配置
# ============================================================

# 是否抓取文章全文内容（True=开启,False=仅获取摘要）
ENABLE_CONTENT_FETCH = False

# 并行抓取的工作线程数（1-10,推荐 3-5）
CONTENT_FETCH_WORKERS = 4

# 单篇文章抓取超时（秒）
CONTENT_FETCH_TIMEOUT = 12

# 文章摘要最大长度（字符）,超出则截断（Markdown 显示用,原文完整保留）
SUMMARY_MAX_LENGTH = 600

# 文章正文最大长度（字符）,超出则截断
CONTENT_MAX_LENGTH = 1500

# 文章正文最小长度（字符）,短于此长度的结果将被丢弃
CONTENT_MIN_LENGTH = 60

# ============================================================
# 进度显示配置（v2.1 新增）
# ============================================================
# 是否在运行时显示详细的抓取进度
# True=显示每个国家-领域的抓取详情（来源、条数等）
# False=仅显示简要摘要
ENABLE_PROGRESS_DETAIL = True

# ============================================================
# RSS 新闻源配置（v2.1 新增）
# ============================================================
# 综合新闻 RSS（覆盖多个国家或全球新闻,用于 Google News 查询式搜索之外补充）
GENERAL_RSS_FEEDS = []

# 各国专属 RSS 新闻源
# 结构: { "国家中文名": [ {"name": "源名称", "url": "RSS地址", "enabled": True/False}, ... ] }
# enabled 默认 True,可在 GUI 中单独勾选

# ============================================================
# 已知不可用/已移除的 RSS 源 (记录备用,避免重复尝试)
# ============================================================
# 阿联酋: Gulf News, Khaleej Times - HTTP 连接失败 (2026-05-02 实测)
# 科威特: Kuwait Times - HTTP 连接失败 (2026-05-02 实测)
# 巴林: Gulf Daily News - HTTP 连接失败 (2026-05-02 实测)
# 伊拉克: Rudaw English - HTTP 连接失败 (2026-05-02 实测)
# 阿富汗: TOLOnews - HTTP 连接失败 (2026-05-02 实测)
# 也门: SABA News (saba.ye) - 站点不可访问
# 黎巴嫩: LBCI Lebanon (lbcgroup.tv) - 无有效 RSS
# 约旦: Petra News (petra.gov.jo) - RSS 格式不兼容
# 蒙古: UB Post (ubpost.mongolnews.mn) - 站点已关闭
# 乌兹别克斯坦: Kun.uz - 无英文 RSS
# 吉尔吉斯斯坦: 24.kg, AKIpress - 无英文 RSS
# 塔吉克斯坦: Asia-Plus - 无有效英文 RSS
# 土库曼斯坦: Turkmenportal - 无有效英文 RSS
# 蒙古: Montsame - 无有效英文 RSS
# 阿塞拜疆: AzerNews, Trend - RSS 需VPN且不稳定
# 亚美尼亚: Armenpress, ARKA News - RSS 需VPN且不稳定
# 格鲁吉亚: Civil.ge, Agenda.ge - RSS 需VPN且不稳定

# 各国专属 RSS 新闻源 (v2.6 新增领域分组)
# 结构: { "国家中文名": { "综合": [...], "政治": [...], "经济": [...], "科技": [...] } }
# - "综合": 未分类RSS, 抓取后需本地关键词分类
# - "政治/经济/科技": 领域专属RSS, 抓取后直接归入该领域(无需本地分类)
# enabled 默认 True, 可在 GUI 中单独勾选
# 空列表表示该国家该领域暂无可用源

COUNTRY_RSS_FEEDS = {
    # ========================
    # 中东地区
    # ========================
    "沙特阿拉伯": {
        "综合": [],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "阿联酋": {
        "综合": [
            {"name": "Emirates247 (UAE)", "url": "https://www.emirates247.com/rss/mobile/v2/uae.rss", "enabled": True},
        ],
        "政治": [],
        "经济": [
            {"name": "Emirates247 (Economy)", "url": "https://www.emirates247.com/rss/mobile/v2/business.rss", "enabled": True},            

        ],
        "科技": [
            {"name": "Emirates247 (Technology)", "url": "https://www.emirates247.com/rss/mobile/v2/technology.rss", "enabled": True},            

        ],
    },
    "阿曼": {
        "综合": [
            {"name": "Times of Oman", "url": "https://timesofoman.com/feed", "enabled": True},
        ],
        "政治": [
        ],
        "经济": [
            {"name": "Oman Observer (Economy)", "url": "https://qna.org.qa/en/Pages/RSS-Feeds/Qatar", "enabled": True},
        ],
        "科技": [],
    },
    "卡塔尔": {
        "综合": [
            {"name": "Qatar News Agency (Qatar)", "url": "https://qna.org.qa/en/Pages/RSS-Feeds/Economy-Local", "enabled": True},

        ],
        "政治": [],
        "经济": [
            {"name": "Qatar News Agency (Economy Local)", "url": "https://qna.org.qa/en/Pages/RSS-Feeds/Economy-Local", "enabled": True},
        ],
        "科技": [],
    },
    "科威特": {
        "综合": [
            {"name": "Arab Times Online (Kuwait)", "url": "https://www.arabtimesonline.com/rssfeed/73/", "enabled": True},
        ],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "巴林": {
        "综合": [],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "巴基斯坦": {
        "综合": [
            {"name": "Dawn", "url": "https://www.dawn.com/feeds/home", "enabled": True},
            {"name": "The News International", "url": "https://www.thenews.com.pk/rss/1/1", "enabled": True},
        ],
        "政治": [
            {"name": "Tribune (Politics)", "url": "https://tribune.com.pk/feed/politics", "enabled": True},

        ],
        "经济": [
            {"name": "Tribune (Business)", "url": "https://tribune.com.pk/feed/business", "enabled": True},
        ],
        "科技": [
            {"name": "Tribune (Technology)", "url": "https://tribune.com.pk/feed/technology", "enabled": True},

        ],
    },
    "伊拉克": {
        "综合": [],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "阿富汗": {
        "综合": [
            {"name": "Khaama Press", "url": "https://www.khaama.com/feed", "enabled": True},
            {"name": "Afghanistan News", "url": "https://feeds.afghanistannews.net/rss/6e1d5c8e1f98f17c", "enabled": True},
        ],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "也门": {
        "综合": [],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "约旦": {
        "综合": [],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "黎巴嫩": {
        "综合": [
            {"name": "lbcgroup.tv (Lebanon News)", "url": "https://www.lbcgroup.tv/Rss/News/en/8/lebanon-news", "enabled": True},
        ],
        "政治": [],
        "经济": [
            {"name": "lbcgroup.tv (Lebanon Economy)", "url": "https://www.lbcgroup.tv/Rss/News/en/104/lebanon-economy", "enabled": True},

        ],
        "科技": [],
    },

    # ========================
    # 中亚及高加索地区
    # ========================
    "哈萨克斯坦": {
        "综合": [
            {"name": "Astana Times", "url": "https://astanatimes.com/feed/", "enabled": True},
        ],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "乌兹别克斯坦": {
        "综合": [
            {"name": "UzDaily", "url": "https://www.uzdaily.com/en/rss", "enabled": True},
        ],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "吉尔吉斯斯坦": {
        "综合": [],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "塔吉克斯坦": {
        "综合": [],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "土库曼斯坦": {
        "综合": [],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "蒙古": {
        "综合": [],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "阿塞拜疆": {
        "综合": [],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "亚美尼亚": {
        "综合": [],
        "政治": [],
        "经济": [],
        "科技": [],
    },
    "格鲁吉亚": {
        "综合": [
            {"name": "Civil Georgia", "url": "https://civil.ge/feed", "enabled": True},
            {"name": "Jam News", "url": "https://jam-news.net/feed/", "enabled": True},
        ],
        "政治": [],
        "经济": [],
        "科技": [],
    },
}

# ============================================================
# 摘要/正文长度配置
# ============================================================

# ============================================================
# 邮件配置（QQ 邮箱 SMTP）
# ============================================================
EMAIL_CONFIG = {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "sender_email": "",
    "sender_name": "每日中东中亚新闻聚合",
    "auth_code": "",
    "receiver_email": "",
    "receiver_email2": "",
}

# ============================================================
# 输出文件配置
# ============================================================
OUTPUT_DIR = "新闻聚合输出"
OUTPUT_FILE = "每日中东中亚新闻信息聚合.md"
LOG_DIR = "运行日志"    # 日志保存目录（项目根目录下）

# ============================================================
# 翻译配置
# ============================================================
ENABLE_TRANSLATION = True


# ============================================================
# 翻译引擎选择 (v2.1 新增)
# ============================================================
# 可选值: "baidu" (百度翻译, 国内首选), "google" (Google翻译, 需VPN), "microsoft" (微软翻译)
TRANSLATION_ENGINE = "google"



# ============================================================
# 时间窗口模式 (v2.1 新增)
# ============================================================
# "yesterday_only": 只抓取
# 日志级别
LOG_LEVEL = "INFO"

# 时间窗
# TIME_WINDOW_MODE = "yesterday_only" #设置为仅抓取昨天的新闻（默认模式）
TIME_WINDOW_MODE = "up_to_now" #设置为抓取最新的

# ============================================================
# Google RSS 消歧配置 (v2.5 新增)
# ============================================================
# 仅需为存在歧义的国家配置。无配置的国家只做 Tier 1 + Tier 3,跳过 Tier 2 和后处理。
#
# 字段:
#   broad_exclude    — 宽泛查询负向排除词 (仅高信号体育/大学词, 其余由后处理 noise_signals 覆盖)
#   tier2_terms      — 正向锁定关键词 (可唯一标识该国, 如首都/城市)
#   country_signals  — 后处理: 命中任一即确认是该国新闻
#   noise_signals    — 后处理: 当 country_signals=0 时, 命中任一即丢弃
COUNTRY_RSS_DISAMBIGUATION = {
    "格鲁吉亚": {
        # ── 宽泛查询负向排除词 ──
        # Tier 1 已有领域关键词做主题过滤, 美国体育/地方新闻不易混入.
        # 仅覆盖美国佐治亚州政界人物和机构, 防止 "Georgia politics" 命中州政治新闻.
        "broad_exclude": [
            # 仅保留最高信号词 (体育队/大学名霸占Google排名)
            "Bulldogs", "Falcons", "Braves", "Hawks",
            "Georgia Tech", "UGA",
        ],

        # ── Tier 2 正向锁定关键词 ──
        # 当某领域 Tier 1 结果 < RSS_DOMAIN_THRESHOLD 时启用.
        # 这些词可唯一标识格鲁吉亚国家, 不需要和 "Georgia" 做 OR.
        "tier2_terms": [
            "Tbilisi",      # 首都
            "Kutaisi",      # 第二大城市, 议会所在地之一
            "Batumi",       # 黑海港口, 旅游经济中心
        ],

        # ── 后处理: 国家信号词 ──
        # 命中任一即保留 (即使同时有 noise_signals 也不丢弃).
        "country_signals": [
            "Tbilisi", "Kutaisi", "Batumi", "Rustavi", "Zugdidi",
            "Gori", "Poti", "Telavi", "Mtskheta",
            "Kakheti", "Imereti", "Adjara", "Svaneti", "Samegrelo",
            "Kvemo Kartli", "Shida Kartli",
            "Abkhazia", "South Ossetia", "Tskhinvali", "Sukhumi",
            "Georgian Dream", "Saakashvili", "Kobakhidze",
            "Zourabichvili", "Kavelashvili", "Ivanishvili",
            "Garibashvili", "Gakharia",
            "Sakartvelo",
        ],

        # ── 后处理: 美国噪音信号词 ──
        # 仅当 country_signals=0 时才生效.
        "noise_signals": [
            # ── 美国50州 (单数词涵盖所有组合) ──
            "Alabama", "Alaska", "Arizona", "Arkansas", "California",
            "Colorado", "Connecticut", "Delaware", "Florida",
            "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
            "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
            "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
            "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
            "New Mexico", "New York", "North Carolina", "North Dakota",
            "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
            "Rhode Island", "South Carolina", "South Dakota",
            "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
            "Washington", "West Virginia", "Wisconsin", "Wyoming",
            # —— 美国著名城市 ——
            "NY"
            # ── 佐治亚城市 ──
            "Atlanta", "Savannah", "Augusta", "Macon",
            "Alpharetta", "Roswell", "Dunwoody", "Marietta",
            "Sandy Springs", "Athens", "Columbus",
            # —— 佐治亚城市名（全）
            "Abbeville", "Acworth", "Adairsville", "Adel", "Adrian", "Ailey", "Alamo", "Alapaha", "Albany", "Aldora", "Allenhurst", "Allentown", "Alma", "Alpharetta", "Alston", "Alto", "Americus", "Aragon", "Arcade", "Ashburn", "Athens-Clarke County", "Atlanta", "Auburn", "Augusta-Richmond County", "Austell", "Avondale Estates", "Bainbridge", "Baldwin", "Ball Ground", "Barnesville", "Baxley", "Belvedere Park", "Berkeley Lake", "Blackshear", "Blairsville", "Blakely", "Blue Ridge", "Blythe", "Bogart", "Boston", "Bowdon", "Bowersville", "Braselton", "Bremen", "Brinson", "Brookhaven", "Brunswick", "Buford", "Cairo", "Calhoun", "Camilla", "Canton", "Carrollton", "Cartersville", "Cave Spring", "Cedartown", "Centerville", "Chamblee", "Chatsworth", "Chattahoochee Hills", "Chickamauga", "Clarkesville", "Clarkston", "Clayton", "Cleveland", "Cochran", "College Park", "Colbert", "Collins", "Colquitt", "Columbus", "Comer", "Commerce", "Concord", "Conyers", "Coolidge", "Cordele", "Cornelia", "Covington", "Crawford", "Crawfordville", "Culloden", "Cumming", "Cusseta", "Cuthbert", "Dacula", "Dahlonega", "Dallas", "Dalton", "Damascus", "Danielsville", "Danville", "Darien", "Dasher", "Davisboro", "Dawson", "Dawsonville", "Dearing", "Decatur", "Deepstep", "Demorest", "Denton", "De Soto", "Dexter", "Dillard", "Doerun", "Donalsonville", "Dooling", "Doraville", "Douglas", "Douglasville", "Dublin", "Dudley", "Duluth", "Dunwoody", "Du Pont", "East Dublin", "East Ellijay", "Eastman", "East Point", "Eatonton", "Edge Hill", "Edison", "Elberton", "Ellaville", "Ellenton", "Ellijay", "Emerson", "Enigma", "Ephesus", "Eton", "Euharlee", "Fairburn", "Fairmount", "Fargo", "Fayetteville", "Fitzgerald", "Flemington", "Flovilla", "Flowery Branch", "Folkston", "Forest Park", "Forsyth", "Fort Gaines", "Fort Oglethorpe", "Fort Valley", "Franklin", "Franklin Springs", "Funston", "Gainesville", "Garden City", "Georgetown", "Gibson", "Gillsville", "Glenwood", "Goldsboro", "Good Hope", "Gordon", "Gray", "Greensboro", "Greenville", "Griffin", "Grovetown", "Hahira", "Hampton", "Hapeville", "Haralson", "Harrisburg", "Hartwell", "Hawkinsville", "Hazelhurst", "Helen", "Hephzibah", "Herndon", "Hickory Flat", "Hinesville", "Hiram", "Hoboken", "Hogansville", "Holly Springs", "Homerville", "Hoschton", "Ivey", "Irondale", "Isle of Hope", "Jackson", "Jacksonville", "Jakin", "Jasper", "Jefferson", "Jeffersonville", "Jenkinsburg", "Jersey", "Jesup", "Johns Creek", "Jonesboro", "Kennesaw", "Keysville", "Kingsland", "Kingston", "Kite", "Knoxville", "LaFayette", "LaGrange", "Lakeland", "Lake Park", "Lavonia", "Lawrenceville", "Leary", "Leesburg", "Lenox", "Leslie", "Lexington", "Lilburn", "Lilly", "Lincolnton", "Lindale", "Lithia Springs", "Lithonia", "Locust Grove", "Loganville", "Lookout Mountain", "Louisville", "Lovejoy", "Ludowici", "Lula", "Lumpkin", "Macon-Bibb County", "Madison", "Manassas", "Marietta", "Marshallville", "Martinez", "Marysville", "Maysville", "McCaysville", "McDonough", "McRae-Helena", "Meansville", "Meldrim", "Menlo", "Metter", "Midland", "Midway", "Milner", "Milledgeville", "Millen", "Milton", "Mitchell", "Monroe", "Monticello", "Montrose", "Moody AFB", "Moreland", "Morgan", "Morganton", "Morrow", "Morven", "Moultrie", "Mountain Park", "Mount Airy", "Mount Vernon", "Mount Zion", "Nahunta", "Nashville", "Nelson", "Newborn", "Newington", "Newnan", "Newton", "Nicholls", "Nicholson", "Norcross", "Norman Park", "North Decatur", "North Druid Hills", "North High Shoals", "Norwood", "Nunez", "Oak Park", "Oakwood", "Ochlocknee", "Ocilla", "Oconee", "Odum", "Offerman", "Oglethorpe", "Oliver", "Omega", "Orchard Hill", "Oxford", "Palmetto", "Panthersville", "Parrott", "Patterson", "Pavo", "Peachtree City", "Peachtree Corners", "Pearson", "Pelham", "Pembroke", "Pendergrass", "Perry", "Phillipsburg", "Pinehurst", "Pine Lake", "Pine Mountain", "Pineview", "Pitts", "Plains", "Plainville", "Pooler", "Portal", "Porterdale", "Port Wentworth", "Poulan", "Powder Springs", "Preston", "Pridgen", "Pulaski", "Putney", "Quitman", "Ranger", "Raoul", "Rayle", "Ray City", "Rebecca", "Redan", "Red Oak", "Reidsville", "Remerton", "Resaca", "Rex", "Riceboro", "Richland", "Richmond Hill", "Ridgeville", "Rincon", "Ringgold", "Rising Fawn", "Riverdale", "Roberta", "Rochelle", "Rockingham", "Rockmart", "Rock Spring", "Rocky Face", "Rome", "Roopville", "Roosterville", "Rossville", "Roswell", "Royston", "Rutledge", "Saint George", "Saint Marys", "Saint Simons Island", "Sandersville", "Sandy Springs", "Savannah", "Scotland", "Sconyers", "Screven", "Sea Island", "Senoia", "Shady Dale", "Sharon", "Sharpsburg", "Shellman", "Shiloh", "Silver Creek", "Smithville", "Smyrna", "Snellville", "Social Circle", "Soperton", "South Fulton", "Sparta", "Springfield", "Statham", "Statesboro", "Statenville", "Stephens", "Sterling", "Stilesboro", "Stockbridge", "Stone Mountain", "Stonecrest", "Sugar Hill", "Suwanee", "Swainsboro", "Sylvania", "Sylvester", "Talbotton", "Talking Rock", "Tallapoosa", "Tallulah Falls", "Tifton", "Tignall", "Tillman", "Thomaston", "Thomasville", "Thomson", "Toomsboro", "Toccoa", "Trenton", "Trion", "Tucker", "Tunnel Hill", "Turbotville", "Turner", "Tybee Island", "Tyrone", "Ty Ty", "Unadilla", "Union City", "Union Point", "Uvalda", "Valdosta", "Varnell", "Vernonburg", "Vidalia", "Vidette", "Vienna", "Villa Rica", "Waco", "Wadley", "Waleska", "Walker", "Walnut Grove", "Walthourville", "Warrenton", "Warner Robins", "Washington", "Waterville", "Waverly", "Waycross", "Waynesboro", "West Point", "Whigham", "White", "White Plains", "Whitfield", "Willacoochee", "Winder", "Winston", "Woodbine", "Woodbury", "Woodland", "Woodstock", "Woolsey", "Wrens", "Wrightsville", "Yatesville", "Young Harris", "Zebulon",
            # ── 佐治亚郡县 (单词即可匹配 "X County" 组合) ──
            "Fulton", "Gwinnett", "Cobb", "DeKalb", "Clayton",
            "Chatham", "Cherokee", "Forsyth", "Hall", "Henry",
            "Paulding", "Douglas", "Coweta", "Carroll", "Fayette",
            "Newton", "Rockdale", "Walton", "Barrow", "Jackson",
            "Bartow", "Whitfield", "Floyd", "Troup", "Spalding",
            "Walker", "Houston", "Bibb", "Richmond", "Muscogee",
            "Clarke", "Lowndes", "Bulloch", "Liberty", "Gordon",
            "Habersham", "Polk", "Murray", "Gilmer", "White",
            "Lumpkin", "Dawson", "Pickens", "Union", "Towns",
            "Rabun", "Stephens", "Franklin", "Hart", "Elbert",
            "Madison", "Oconee", "Morgan", "Greene", "Putnam",
            "Baldwin", "Jones", "Monroe", "Lamar", "Butts",
            "Jasper", "Upson", "Harris", "Meriwether", "Pike",
            "Talbot", "Taylor", "Crawford", "Peach", "Dooly",
            "Sumter", "Lee", "Dougherty", "Mitchell",
            "Thomas", "Grady", "Decatur", "Colquitt", "Cook",
            "Tift", "Berrien", "Brooks", "Ware",
            "Camden", "Glynn", "Wayne", "Brantley", "Pierce",
            "Bacon", "Coffee", "Jeff Davis", "Appling", "Toombs",
            "Emanuel", "Burke", "Jefferson", "Washington", "Laurens",
            "Johnson", "Treutlen", "Montgomery", "Wheeler", "Tattnall",
            "Evans", "Long", "Bryan", "Effingham", "Screven",
            "Jenkins", "Candler",
            # ── 佐治亚政治人物 (姓氏即可匹配全名) ──
            "Kemp", "Abrams", "Ossoff", "Warnock",
            "Marjorie Taylor Greene",
            # ── 佐治亚机构/特征 ──
            "Georgia State",
            "Georgia Bulldogs", "Georgia Tech",
            "Falcons", "Braves", "Hawks", "Atlanta United",
            "UGA", "SEC championship", "Sanford Stadium",
            "Peach State", "Georgia National Guard", "Georgia Facility",
            "Georgia Forestry",
            "Georgia Nicols", "Georgia-Pacific",
            # 美国政治相关
            "GOP", "Democrat", "Biden", "Georgia Capitol", "Georgia plant",
            "Wall Street", "Republican"
            # 美国大学
            "Georgia Institute of Technology", "University of North Georgia",
            # 美国体育
            "Georgia TD", "NHRA", "Georgia Motorsports", "Georgia Southern",
            "On3", "NCAA", "tennis", 
            # 美国媒体
            "boltsmag", "WJCL", ".gov", "WCTV", "AG INFORMATION", "ESPN", "Georgia Recorder",
            "Georgia Public Broadcasting", "E&E", "The Guardian", "AJC.com", "American Journal", "Georgia Ports",
            "GA Dept", "WDUN", "WRDW", "WTVC", "CNBC", "Gulfstream", "Georgia Asian Times",
            "Sports Illustrated", "JazzTimes", "army.mil", "WSB", "Grice Connect", "NewsNation",
            "American Banker", "georgiastatesports", "mcduffieprogess", "The Fabricator",
            "MSN", "11Alive.com", "Georgia Outdoor", "WBAL", "Wall Street", "People.com",
            "ABC", "Newsweek", "WRGB", "WTVM", "AAA", "ICE", "dailydispatch", "NBC",
            "Forbes", "Georgia Bulletin"
        ]
    },

    "阿塞拜疆": {
        # ── 宽泛查询负向排除词 ──
        # 伊朗有东阿塞拜疆省(首府 Tabriz)和西阿塞拜疆省(首府 Urmia).
        # Tier 1 有领域关键词做主题过滤, 精简版仅覆盖伊朗省份地名.
        "broad_exclude": [
            # 仅保留最高信号词 (伊朗省份首府)
            "Tabriz", "Urmia",
        ],

        # ── Tier 2 正向锁定关键词 ──
        # 当某领域 Tier 1 结果 < RSS_DOMAIN_THRESHOLD 时启用.
        "tier2_terms": [
            "Baku",         # 首都
            "Nakhchivan",   # 飞地, 唯一标识阿塞拜疆国家
            "Ganja",        # 第二大城市
            "Sumgait",      # 第三大城市
        ],

        # ── 后处理: 国家信号词 ──
        "country_signals": [
            "Baku", "Nakhchivan", "Ganja", "Sumgait",
            "Aliyev", "Ilham Aliyev",
            "SOCAR", "Shah Deniz",
            "Nagorno-Karabakh", "Karabakh",
            "Azərbaycan",
        ],

        # ── 后处理: 伊朗阿塞拜疆省噪音信号词 ──
        "noise_signals": [
            "Tabriz", "Urmia", "Ardabil", "Lake Urmia",
            "East Azerbaijan", "West Azerbaijan",
            "Iranian Azerbaijan", "Iran's Azerbaijan",
            "Sahand", "Tabriz University",
        ],
    },
}

# ============================================================


# ============================================================
# Google RSS 域查询达标阈值 (v2.5 新增)
# ============================================================
# 某领域 Tier 1 结果数 < 此值 → 触发 Tier 2 补充查询
# 默认 3, 可在 GUI 中修改

# ============================================================
# 查询流水线顺序 (v2.6 新增)
# ============================================================
PIPELINE_ORDER = [
    {"id": "broad_google_rss",    "enabled": True},
    {"id": "country_rss",          "enabled": True},
    {"id": "targeted_google_rss", "enabled": True},
]

# ============================================================
# 以伊专题 (v2.6 新增)
# ============================================================
WAR_TOPIC_ENABLED = True
WAR_TOPIC_ARTICLES = 20
WAR_TOPIC_KEYWORDS = [
    "Israel Iran war", "Iran Israel war",
    "Israel Iran conflict", "Israel Iran military",
    "Israel strike Iran", "Iran strike Israel",
    "Israel attack Iran", "Iran attack Israel",
    "Israel Iran tensions", "Israel Iran escalation",
    "Israel airstrike Iran", "Iran missile Israel",
    "Iranian drone Israel", "Iran nuclear Israel",
    "Israel war", "Iran war",
    "Israel military strike", "Iran military strike",
    "Israel airstrike", "Iran airstrike",
    "Israel missile attack", "Iran missile attack",
    "IDF strike", "IRGC attack",
    "Israel defense forces Iran",
    "Middle East war", "Middle East conflict",
    "Gaza war Israel", "Israel Gaza conflict",
    "Hezbollah Israel", "Israel Hezbollah",
    "Houthi Israel", "Israel Houthi",
    "Houthi Red Sea attack",
    "Netanyahu war", "Khamenei war",
    "Netanyahu Iran", "Khamenei Israel",
    "Netanyahu military", "Khamenei military",
    "Israel Iran ceasefire", "Israel ceasefire",
    "Iran ceasefire deal", "Middle East ceasefire",
    "Israel Iran diplomacy", "Israel Iran negotiations",
]

# ============================================================
# Google RSS 域查询达标阈值 (v2.5 新增)
# ============================================================
RSS_DOMAIN_THRESHOLD = 3

# ============================================================
# 域新闻数量上限 (v2.5.1 新增)
# ============================================================
RSS_DOMAIN_MAX = 5

# ============================================================
# 外部 API 密钥加载 (用于编译版 EXE, v2.5.1)
# ============================================================
# 如果存在 api_keys.json (放在程序同级目录), 则覆盖以上默认值。
# 编译 safe 版时 api_keys.json 由 build_exe_safe.bat 生成模板。
import os as _os, json as _json
_keys_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "api_keys.json")
if _os.path.exists(_keys_path):
    try:
        with open(_keys_path, "r", encoding="utf-8") as _f:
            _keys = _json.load(_f)
        if _keys.get("EMAIL_SENDER"):
            EMAIL_CONFIG["sender_email"] = _keys["EMAIL_SENDER"]
        if _keys.get("EMAIL_AUTH_CODE"):
            EMAIL_CONFIG["auth_code"] = _keys["EMAIL_AUTH_CODE"]
        if _keys.get("EMAIL_RECEIVER2"):
            EMAIL_CONFIG["receiver_email2"] = _keys["EMAIL_RECEIVER2"]
        del _keys, _f
    except Exception:
        pass
del _os, _json, _keys_path
