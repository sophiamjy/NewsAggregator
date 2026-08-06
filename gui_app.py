#!/usr/bin/env python3
"""每日中东中亚新闻聚合 GUI v3.0"""
import json as _json, logging, os, sys, threading, tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk, simpledialog

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _APP_DIR)

from config import (
    OUTPUT_DIR, LOG_DIR, ENABLE_TRANSLATION, ENABLE_CONTENT_FETCH,
    ENABLE_PROGRESS_DETAIL, TIME_WINDOW_MODE, COUNTRY_RSS_FEEDS,
    RSS_DOMAIN_THRESHOLD, RSS_DOMAIN_MAX, PIPELINE_ORDER, WAR_TOPIC_ENABLED,
    WAR_TOPIC_ARTICLES, EMAIL_CONFIG, TRANSLATION_ENGINE,
)
from news_fetcher import (NewsAggregator, get_time_window_start,
                          get_time_window_end, set_window_mode)
from markdown_writer import (generate_markdown, write_markdown_file,
                             generate_markdown_bilingual, write_html_file)
from translator import TranslationEngine, translate_news_items
from email_sender import send_email, send_email_attachment
from profile_manager import (load_profiles, save_profiles, gather_settings,
                             apply_settings, profile_summary)

O_ORIG = "每日中东中亚新闻_{date}_原文.md"
O_TRANS = "每日中东中亚新闻_{date}_翻译.md"
O_BI = "每日中东中亚新闻_{date}_对照.md"


def _fn(ds, is_trans, suffix=""):
    t = O_TRANS if is_trans else O_ORIG
    n = t.replace("{date}", ds)
    if suffix: n = n.replace(".md", f"_{suffix}.md")
    return n


class AppLogger(logging.Handler):
    def __init__(self, w):
        super().__init__(); self.w = w
        self.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))

    def emit(self, r):
        self.w.after(0, lambda: self._a(self.format(r) + "\n"))

    def _a(self, m):
        self.w.insert(tk.END, m); self.w.see(tk.END)


class NewsAggregatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("每日中东中亚新闻聚合 v3.0")
        self.root.geometry("920x860"); self.root.minsize(800, 660)
        self._running = False; self._rss_vars = {}
        self._setup_ui(); self._setup_logger()

    def _setup_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        tf = ttk.Frame(main); tf.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(tf, text="每日中东中亚新闻聚合 v3.0", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.CENTER)
        ws = get_time_window_start(TIME_WINDOW_MODE); we = get_time_window_end(TIME_WINDOW_MODE)
        self._win_label = ttk.Label(tf, text=f"时间窗口: {ws.strftime('%Y-%m-%d %H:%M')} ~ {we.strftime('%Y-%m-%d %H:%M')} (北京)", font=("Microsoft YaHei", 8))
        self._win_label.pack(anchor=tk.CENTER)
        nb = ttk.Notebook(main); nb.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        tab1 = ttk.Frame(nb, padding=10); nb.add(tab1, text="运行设置")
        self._build_run_tab(tab1)
        tab2 = ttk.Frame(nb, padding=10); nb.add(tab2, text="新闻源选择")
        self._build_source_tab(tab2)
        tab3 = ttk.Frame(nb, padding=10); nb.add(tab3, text="关键词管理")
        self._build_keyword_tab(tab3)
        self._refresh_profiles()
        lf = ttk.LabelFrame(main, text="运行日志", padding=5)
        lf.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.log_text = scrolledtext.ScrolledText(lf, font=("Consolas", 9), wrap=tk.WORD,
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="white", height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main, text="v3.0", font=("Microsoft YaHei", 8), foreground="gray").pack(anchor=tk.E, pady=(3, 0))

    def _build_run_tab(self, p):
        pf = ttk.LabelFrame(p, text="配置方案", padding=8)
        pf.pack(fill=tk.X, pady=(0, 8))
        pr = ttk.Frame(pf); pr.pack(fill=tk.X)
        ttk.Label(pr, text="方案:", font=("Microsoft YaHei", 9)).pack(side=tk.LEFT, padx=(0, 6))
        self._profiles = load_profiles()
        self._pv = tk.StringVar(); self._pc = ttk.Combobox(pr, textvariable=self._pv, state="readonly", width=18)
        self._pc.pack(side=tk.LEFT, padx=(0, 6))
        self._pc.bind("<<ComboboxSelected>>", lambda e: self._on_profile_select())
        ttk.Button(pr, text="保存当前", command=self._save_profile).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(pr, text="设默认", command=self._set_default).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(pr, text="删除", command=self._delete_profile).pack(side=tk.LEFT)
        self._pi = ttk.Label(pf, text="", font=("Microsoft YaHei", 8), foreground="gray")
        self._pi.pack(anchor=tk.W, pady=(4, 0))

        sf = ttk.LabelFrame(p, text="运行阶段", padding=10)
        sf.pack(fill=tk.X, pady=(0, 8))
        r0 = ttk.Frame(sf); r0.pack(fill=tk.X)
        self.var_fetch = tk.BooleanVar(value=True)
        ttk.Checkbutton(r0, text="1. 抓取新闻", variable=self.var_fetch).pack(side=tk.LEFT, padx=(0, 15))
        self.var_trans = tk.BooleanVar(value=ENABLE_TRANSLATION)
        ttk.Checkbutton(r0, text="2. 翻译为中文", variable=self.var_trans).pack(side=tk.LEFT)

        ff = ttk.LabelFrame(p, text="抓取选项", padding=10)
        ff.pack(fill=tk.X, pady=(0, 8))
        r1 = ttk.Frame(ff); r1.pack(fill=tk.X)
        self.var_content = tk.BooleanVar(value=ENABLE_CONTENT_FETCH)
        ttk.Checkbutton(r1, text="抓取正文", variable=self.var_content).pack(side=tk.LEFT, padx=(0, 15))
        self.var_progress = tk.BooleanVar(value=ENABLE_PROGRESS_DETAIL)
        ttk.Checkbutton(r1, text="详细进度", variable=self.var_progress).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Label(r1, text="达标阈值:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_rss_threshold = tk.StringVar(value=str(RSS_DOMAIN_THRESHOLD))
        ttk.Spinbox(r1, textvariable=self.var_rss_threshold, from_=1, to=20, width=3).pack(side=tk.LEFT)
        ttk.Label(r1, text=" 域上限:", font=("Microsoft YaHei", 8), foreground="gray").pack(side=tk.LEFT)
        self.var_domain_max = tk.StringVar(value=str(RSS_DOMAIN_MAX))
        ttk.Spinbox(r1, textvariable=self.var_domain_max, from_=1, to=20, width=3).pack(side=tk.LEFT)

        self.var_bilingual = tk.BooleanVar(value=False)
        ttk.Checkbutton(p, text="生成对照版", variable=self.var_bilingual).pack(anchor=tk.W, pady=(5, 0))
        self.var_html = tk.BooleanVar(value=True)
        ttk.Checkbutton(p, text="生成HTML版", variable=self.var_html).pack(anchor=tk.W, pady=(2, 0))
        self.var_war_topic = tk.BooleanVar(value=WAR_TOPIC_ENABLED)
        ttk.Checkbutton(p, text="以伊专题", variable=self.var_war_topic).pack(anchor=tk.W, pady=(2, 0))

        tf3 = ttk.LabelFrame(p, text="时间窗口", padding=10)
        tf3.pack(fill=tk.X, pady=(0, 8))
        r3 = ttk.Frame(tf3); r3.pack(fill=tk.X)
        dm = TIME_WINDOW_MODE if TIME_WINDOW_MODE in ("up_to_now", "yesterday_only") else "up_to_now"
        self.var_winmode = tk.StringVar(value=dm)
        self.var_winmode.trace_add("write", lambda *a: self._update_win_label())
        ttk.Radiobutton(r3, text="昨日00:00~当前", variable=self.var_winmode, value="up_to_now").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(r3, text="仅前一天", variable=self.var_winmode, value="yesterday_only").pack(side=tk.LEFT)

        ef = ttk.LabelFrame(p, text="邮件设置", padding=10)
        ef.pack(fill=tk.X, pady=(0, 8))
        er = ttk.Frame(ef); er.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(er, text="发送:").pack(side=tk.LEFT, padx=(0, 8))
        self.var_send_orig = tk.BooleanVar(value=False)
        ttk.Checkbutton(er, text="原文", variable=self.var_send_orig).pack(side=tk.LEFT, padx=(0, 8))
        self.var_send_trans = tk.BooleanVar(value=True)
        ttk.Checkbutton(er, text="翻译", variable=self.var_send_trans).pack(side=tk.LEFT, padx=(0, 8))
        self.var_send_bi = tk.BooleanVar(value=False)
        ttk.Checkbutton(er, text="对照", variable=self.var_send_bi).pack(side=tk.LEFT)
        er2 = ttk.Frame(ef); er2.pack(fill=tk.X)
        self.var_attach = tk.BooleanVar(value=True)
        ttk.Checkbutton(er2, text="以附件发送", variable=self.var_attach).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(er2, text="收件:", font=("Microsoft YaHei", 9)).pack(side=tk.LEFT, padx=(0, 8))
        self.var_to_email = tk.StringVar(value=EMAIL_CONFIG.get("receiver_email", ""))
        ttk.Entry(er2, textvariable=self.var_to_email, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)

        bf = ttk.Frame(p); bf.pack(fill=tk.X, pady=(0, 5))
        self.btn_run = ttk.Button(bf, text="开始运行", command=self._start_run)
        self.btn_run.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_stop = ttk.Button(bf, text="停止", command=self._stop_run, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_clear = ttk.Button(bf, text="清空日志", command=self._clear_log)
        self.btn_clear.pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(p, textvariable=self.status_var, font=("Microsoft YaHei", 9), foreground="gray").pack(anchor=tk.W)
        self.progress = ttk.Progressbar(p, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(5, 0))

    # ── 新闻源选择 ──
    def _build_source_tab(self, p):
        af = ttk.LabelFrame(p, text="Google News RSS", padding=10)
        af.pack(fill=tk.X, pady=(0, 8))
        self.var_rss = tk.BooleanVar(value=True)
        ttk.Checkbutton(af, text="启用 Google RSS（免费，需VPN）", variable=self.var_rss).pack(side=tk.LEFT)

        ttk.Label(p, text="各国专属 RSS", font=("Microsoft YaHei", 10, "bold")).pack(anchor=tk.W, pady=(5, 3))
        ro = ttk.Frame(p); ro.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(ro, highlightthickness=0, height=160)
        sb = ttk.Scrollbar(ro, orient=tk.VERTICAL, command=canvas.yview)
        sf = ttk.Frame(canvas)
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor=tk.NW)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self._rss_vars = {}
        RSS_DOMAIN_ORDER = ["政治", "经济", "科技", "综合"]
        RSS_DOMAIN_LABEL = {"综合": "综合", "政治": "政治", "经济": "经济", "科技": "科技"}
        for cn, domains in COUNTRY_RSS_FEEDS.items():
            has_any = any(len(domains.get(d, [])) > 0 for d in RSS_DOMAIN_ORDER)
            if not has_any: continue
            cg = ttk.LabelFrame(sf, text=cn, padding=5)
            cg.pack(fill=tk.X, pady=2, padx=5)
            self._rss_vars[cn] = {}
            for domain in RSS_DOMAIN_ORDER:
                feeds = domains.get(domain, [])
                if not feeds: continue
                df = ttk.Frame(cg); df.pack(fill=tk.X, pady=(1, 0))
                ttk.Label(df, text=f"{RSS_DOMAIN_LABEL[domain]}RSS:", font=("Microsoft YaHei", 8), width=8, anchor=tk.W).pack(side=tk.LEFT)
                vl = []
                for feed in feeds:
                    var = tk.BooleanVar(value=feed.get("enabled", True))
                    ttk.Checkbutton(df, text=feed["name"], variable=var).pack(side=tk.LEFT, padx=(0, 12))
                    vl.append(var)
                self._rss_vars[cn][domain] = vl

        # 流水线
        plf = ttk.LabelFrame(p, text="查询顺序 (↑↓调整)", padding=10)
        plf.pack(fill=tk.X, pady=(10, 0))
        self._pl_rows_frame = ttk.Frame(plf); self._pl_rows_frame.pack(fill=tk.X)
        self._init_pipeline_stages(); self._rebuild_pipeline_rows()
        ttk.Button(plf, text="重置默认", command=self._reset_pipeline_order).pack(pady=(5, 0))

    PIPELINE_STAGE_LABELS = {
        "broad_google_rss": "宽泛查询 - Google RSS",
        "country_rss": "各国专属RSS查询",
        "targeted_google_rss": "定向域搜索 - Google RSS",
    }

    LITE_DEFAULT_PIPELINE = [
        {"id": "country_rss", "enabled": True},
        {"id": "broad_google_rss", "enabled": True},
        {"id": "targeted_google_rss", "enabled": True},
    ]

    def _init_pipeline_stages(self, order=None):
        if order is None: order = self.LITE_DEFAULT_PIPELINE
        self._pipeline_stages = []
        for s in order:
            sid = s.get("id", "")
            if sid in self.PIPELINE_STAGE_LABELS:
                self._pipeline_stages.append({
                    "id": sid, "enabled_var": tk.BooleanVar(value=s.get("enabled", True)),
                    "label": self.PIPELINE_STAGE_LABELS[sid],
                })

    def _rebuild_pipeline_rows(self):
        for row in getattr(self, '_pl_rows', []): row.destroy()
        self._pl_rows = []
        for i, ps in enumerate(self._pipeline_stages):
            row = ttk.Frame(self._pl_rows_frame); row.pack(fill=tk.X, pady=1)
            ttk.Button(row, text="↑", width=2, command=lambda idx=i: self._move_pipeline_stage(idx, -1)).pack(side=tk.LEFT, padx=(0, 2))
            ttk.Button(row, text="↓", width=2, command=lambda idx=i: self._move_pipeline_stage(idx, 1)).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Checkbutton(row, text=f"{i+1}. {ps['label']}", variable=ps["enabled_var"]).pack(side=tk.LEFT)
            self._pl_rows.append(row)

    def _move_pipeline_stage(self, idx, direction):
        new_idx = idx + direction
        if 0 <= new_idx < len(self._pipeline_stages):
            self._pipeline_stages[idx], self._pipeline_stages[new_idx] = self._pipeline_stages[new_idx], self._pipeline_stages[idx]
            self._rebuild_pipeline_rows()

    def _reset_pipeline_order(self):
        self._init_pipeline_stages(); self._rebuild_pipeline_rows()
        self._log("流水线已重置")

    def _get_pipeline_order(self):
        return [{"id": ps["id"], "enabled": ps["enabled_var"].get()} for ps in self._pipeline_stages]

    # ── 关键词管理 ──
    def _build_keyword_tab(self, p):
        from config import DOMAINS as _D
        ttk.Label(p, text="编辑领域关键词（每行一个）", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=(0, 5))
        self._kw_texts = {}
        for d in _D:
            gf = ttk.LabelFrame(p, text=f"{d.get('icon','')} {d['name_zh']}", padding=5)
            gf.pack(fill=tk.BOTH, expand=True, pady=2)
            tw = tk.Text(gf, height=4, font=("Consolas", 9), wrap=tk.WORD)
            tw.insert("1.0", "\n".join(d.get("keywords_en", [])))
            tw.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
            self._kw_texts[d["name_zh"]] = tw
        ttk.Button(p, text="保存关键词", command=self._save_keywords).pack(pady=(5, 0))

    def _save_keywords(self):
        from config import DOMAINS as _D
        for d in _D:
            if d["name_zh"] in self._kw_texts:
                txt = self._kw_texts[d["name_zh"]].get("1.0", tk.END).strip()
                d["keywords_en"] = [k.strip() for k in txt.split("\n") if k.strip()]
        self._log("关键词已更新")

    # ── 配置方案 ──
    def _refresh_profiles(self):
        names = list(self._profiles.get("profiles", {}).keys())
        self._pc["values"] = names
        default = self._profiles.get("default", "")
        if default and default in names: self._pv.set(default); self._apply_profile(default)
        elif names: self._pv.set(names[0]); self._apply_profile(names[0])

    def _apply_profile(self, name):
        p = self._profiles.get("profiles", {}).get(name)
        if p: apply_settings(self, p); self._pi.configure(text=f"[{name}] {profile_summary(p)}")

    def _on_profile_select(self): self._apply_profile(self._pv.get())
    def _save_profile(self):
        name = simpledialog.askstring("保存方案", "方案名称:", parent=self.root)
        if not name: return
        self._profiles.setdefault("profiles", {})[name] = gather_settings(self)
        save_profiles(self._profiles); self._refresh_profiles(); self._log(f"方案 [{name}] 已保存")

    def _set_default(self):
        name = self._pv.get()
        if name: self._profiles["default"] = name; save_profiles(self._profiles); self._log(f"[{name}] 已设为默认")

    def _delete_profile(self):
        name = self._pv.get()
        if name and name in self._profiles.get("profiles", {}):
            del self._profiles["profiles"][name]
            if self._profiles.get("default") == name: self._profiles["default"] = ""
            save_profiles(self._profiles); self._refresh_profiles(); self._log(f"方案 [{name}] 已删除")

    # ── Logger ──
    def _setup_logger(self):
        try:
            gh = AppLogger(self.log_text); gh.setLevel(logging.INFO)
            log_dir = os.path.join(_APP_DIR, LOG_DIR); os.makedirs(log_dir, exist_ok=True)
            lf = os.path.join(log_dir, f"运行日志{datetime.now().strftime('%Y%m%d%H%M%S')}.log")
            fh = logging.FileHandler(lf, encoding="utf-8"); fh.setLevel(logging.INFO)
            fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
            rl = logging.getLogger(); rl.setLevel(logging.INFO)
            for h in rl.handlers[:]: rl.removeHandler(h)
            rl.addHandler(gh); rl.addHandler(fh)
            self._log(f"日志: {lf}")
        except Exception as e:
            try: self._al(f"!!! 日志初始化失败: {e}\n")
            except: pass

    def _update_win_label(self):
        m = self.var_winmode.get(); ws = get_time_window_start(m); we = get_time_window_end(m)
        self._win_label.configure(text=f"时间窗口: {ws.strftime('%Y-%m-%d %H:%M')} ~ {we.strftime('%Y-%m-%d %H:%M')} (北京)")

    def _log(self, msg): self._al(f"{datetime.now().strftime('%H:%M:%S')} [INFO] {msg}\n")
    def _al(self, msg):
        try: self.log_text.insert(tk.END, msg); self.log_text.see(tk.END)
        except: pass

    def _set_ui_state(self, running):
        if running: self.btn_run.configure(state=tk.DISABLED); self.btn_stop.configure(state=tk.NORMAL); self.progress.start(10)
        else: self.btn_run.configure(state=tk.NORMAL); self.btn_stop.configure(state=tk.DISABLED); self.progress.stop()

    def _get_rss_config(self):
        r = {}
        for cn, domains in COUNTRY_RSS_FEEDS.items():
            dn_vars = self._rss_vars.get(cn, {}); r[cn] = {}
            for domain, feeds in domains.items():
                vl = dn_vars.get(domain, [])
                r[cn][domain] = [{**f, "enabled": vl[i].get() if i < len(vl) else f.get("enabled", True)} for i, f in enumerate(feeds)]
        return r

    def _start_run(self):
        if self._running: return
        if self.var_fetch.get() and not any([self.var_rss.get(), *[v.get() for dn_vars in self._rss_vars.values() for vl in dn_vars.values() for v in vl]]):
            messagebox.showwarning("警告", "请至少选择一个新闻数据源！"); return
        self._running = True; self._set_ui_state(True); self.status_var.set("运行中..."); self._clear_log()
        threading.Thread(target=self._run_pipeline, daemon=True).start()

    def _stop_run(self):
        self._running = False; self._set_ui_state(False); self.status_var.set("已停止"); self._log("用户停止了运行")
    def _clear_log(self): self.log_text.delete(1.0, tk.END)
    def _ds(self):
        m = self.var_winmode.get(); ws = get_time_window_start(m)
        return ws.strftime("%Y-%m-%d") if m == "yesterday_only" else ws.strftime("%Y-%m-%d") + "起"

    def _run_pipeline(self):
        try:
            bd = _APP_DIR; mode = self.var_winmode.get(); set_window_mode(mode)
            sp = self.var_progress.get(); ds = self._ds()
            orig_file, trans_file, bi_file = None, None, None
            orig_html, trans_html, bi_html = None, None, None

            if self.var_fetch.get():
                self._log("=" * 50); self._log("新闻抓取")
                ws = get_time_window_start(mode); we = get_time_window_end(mode)
                self._log(f"时间窗口: {ws.strftime('%Y-%m-%d %H:%M')} ~ {we.strftime('%Y-%m-%d %H:%M')} (北京)")
                if not self._running: return
                import config as _cfg
                try: _cfg.RSS_DOMAIN_THRESHOLD = int(self.var_rss_threshold.get())
                except ValueError: _cfg.RSS_DOMAIN_THRESHOLD = 3
                try: _cfg.RSS_DOMAIN_MAX = int(self.var_domain_max.get())
                except ValueError: _cfg.RSS_DOMAIN_MAX = 5
                try: _cfg.WAR_TOPIC_ENABLED = self.var_war_topic.get()
                except: pass
                agg = NewsAggregator(enable_google_rss=self.var_rss.get(),
                    country_rss_config=self._get_rss_config(), window_mode=mode,
                    stop_check=lambda: not self._running)
                pipeline_order = self._get_pipeline_order()
                if not self._running: return
                def pc(m):
                    if sp: self._al(f"  {m}\n")
                data = agg.fetch_all(fetch_content=self.var_content.get(), progress_callback=pc, pipeline_order=pipeline_order)
                stats = agg.stats
                self._log(f"抓取完成: {stats['total_fetched']} 条 (R={stats['google_rss']} RSS={stats['country_rss']})")
                orig_md = generate_markdown(data, generation_time=datetime.now(), is_translated=False, window_mode=mode, stats=stats, has_content=self.var_content.get())
                orig_file = write_markdown_file(orig_md, bd, output_dir=OUTPUT_DIR, output_file=_fn(ds, False), prepend=True)
                self._log(f"原文: {orig_file}")
                if self.var_html.get():
                    orig_html = write_html_file(orig_md, bd, output_dir=OUTPUT_DIR, output_file=_fn(ds, False), data=data)
                if not self._running: return

                if self.var_trans.get():
                    self._log("-" * 40); self._log("翻译")
                    engine = TranslationEngine(preferred="google")
                    if engine.available:
                        data_t = translate_news_items(data, engine)
                        trans_md = generate_markdown(data_t, generation_time=datetime.now(), is_translated=True, window_mode=mode, stats=stats, has_content=self.var_content.get())
                        trans_file = write_markdown_file(trans_md, bd, output_dir=OUTPUT_DIR, output_file=_fn(ds, True), prepend=True)
                        self._log(f"翻译: {trans_file}")
                        if self.var_html.get():
                            trans_html = write_html_file(trans_md, bd, output_dir=OUTPUT_DIR, output_file=_fn(ds, True), data=data_t)
                        if self.var_bilingual.get():
                            bi_md = generate_markdown_bilingual(data_t, generation_time=datetime.now(), window_mode=mode, stats=stats, has_content=self.var_content.get())
                            bi_file = write_markdown_file(bi_md, bd, output_dir=OUTPUT_DIR, output_file=O_BI.replace("{date}", ds), prepend=True)
                            self._log(f"对照: {bi_file}")
                            if self.var_html.get():
                                bi_html = write_html_file(bi_md, bd, output_dir=OUTPUT_DIR, output_file=O_BI.replace("{date}", ds), data=data_t)
                    else: self._log("Google翻译不可用（需VPN）")
                else: self._log("跳过翻译")

            # 邮件
            if self.var_send_trans.get() or self.var_send_orig.get() or self.var_send_bi.get():
                self._log("-" * 40); self._log("发送邮件")
                rec = self.var_to_email.get().strip()
                if orig_file is None: orig_file = os.path.join(bd, OUTPUT_DIR, _fn(ds, False))
                if trans_file is None: trans_file = os.path.join(bd, OUTPUT_DIR, _fn(ds, True))
                if bi_file is None: bi_file = os.path.join(bd, OUTPUT_DIR, O_BI.replace("{date}", ds))
                use_attach = self.var_attach.get()
                def _send(label, md_path, html_path):
                    if use_attach and html_path and os.path.exists(html_path):
                        return send_email_attachment(html_path, to_email=rec, subject=f"每日中东中亚新闻-{ds}({label})")
                    elif os.path.exists(md_path):
                        with open(md_path, "r", encoding="utf-8") as f:
                            return send_email(f.read(), to_email=rec, subject=f"每日中东中亚新闻-{ds}({label})")
                    return False
                if self.var_send_orig.get(): _send("原文", orig_file, orig_html); self._log("原文已发送")
                if self.var_send_trans.get(): _send("翻译", trans_file, trans_html); self._log("翻译已发送")
                if self.var_send_bi.get(): _send("对照", bi_file, bi_html); self._log("对照已发送")

            self._log("=" * 50); self._log("全部完成！"); self.root.after(0, lambda: self.status_var.set("运行完成"))
        except Exception as e:
            logging.getLogger().error(f"异常: {e}", exc_info=True); self.root.after(0, lambda: self.status_var.set("运行出错"))
        finally:
            self._running = False; self.root.after(0, lambda: self._set_ui_state(False))


def main():
    root = tk.Tk(); NewsAggregatorGUI(root); root.mainloop()

if __name__ == "__main__": main()
