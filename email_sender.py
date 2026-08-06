"""邮件发送模块 v3.0 — QQ SMTP + HTML附件"""
import logging, os, re as _re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from email.utils import formataddr
from datetime import datetime

import markdown as md_lib
from config import EMAIL_CONFIG
from markdown_writer import generate_html

logger = logging.getLogger(__name__)


def markdown_to_html(md_text):
    md_text = _re.sub(r'<[^>]+>', '', md_text)
    html_body = md_lib.markdown(md_text, extensions=["extra", "sane_lists"])
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"></head>
<body style="font-family:'Microsoft YaHei',sans-serif;line-height:1.8;color:#333;max-width:800px;margin:0 auto;padding:20px;background:#fafafa">
<div style="background:#fff;padding:30px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.1);">
{html_body}</div>
<div style="text-align:center;margin-top:20px;color:#999;font-size:12px;">本邮件由每日中东中亚新闻聚合自动生成</div>
</body></html>"""


def send_email(md_content, subject=None, to_email=None, to_email2=None,
               sender_email=None, auth_code=None, is_html=False):
    cfg = EMAIL_CONFIG.copy()
    if sender_email: cfg["sender_email"] = sender_email
    if auth_code: cfg["auth_code"] = auth_code
    recipient = to_email or cfg.get("receiver_email", cfg["sender_email"])
    recipient2 = to_email2 or cfg.get("receiver_email2")

    if not cfg.get("auth_code"):
        logger.error("未配置 SMTP 授权码")
        return False
    if subject is None:
        subject = f"每日中东中亚新闻聚合 - {datetime.now().strftime('%Y-%m-%d')}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = formataddr((cfg["sender_name"], cfg["sender_email"]))
    msg["To"] = recipient
    if recipient2:
        msg["Cc"] = recipient2

    if is_html:
        msg.attach(MIMEText(md_content, "html", "utf-8"))
    else:
        msg.attach(MIMEText(md_content, "plain", "utf-8"))
        try:
            msg.attach(MIMEText(generate_html(md_content), "html", "utf-8"))
        except Exception:
            pass

    try:
        with smtplib.SMTP_SSL(cfg["smtp_server"], cfg["smtp_port"], timeout=30) as s:
            s.login(cfg["sender_email"], cfg["auth_code"])
            recipients = [recipient]
            if recipient2: recipients.append(recipient2)
            s.sendmail(cfg["sender_email"], recipients, msg.as_string())
        logger.info("邮件发送成功")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP 认证失败")
        return False
    except Exception as e:
        logger.error(f"邮件发送失败: {e}")
        return False


def send_email_attachment(html_path, subject=None, to_email=None, to_email2=None,
                          sender_email=None, auth_code=None):
    cfg = EMAIL_CONFIG.copy()
    if sender_email: cfg["sender_email"] = sender_email
    if auth_code: cfg["auth_code"] = auth_code
    recipient = to_email or cfg.get("receiver_email", cfg["sender_email"])
    recipient2 = to_email2 or cfg.get("receiver_email2")

    if not cfg.get("auth_code"):
        logger.error("未配置 SMTP 授权码")
        return False
    if not os.path.exists(html_path):
        logger.error(f"附件不存在: {html_path}")
        return False
    if subject is None:
        subject = f"每日中东中亚新闻聚合 - {datetime.now().strftime('%Y-%m-%d')}"

    msg = MIMEMultipart()
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = formataddr((cfg["sender_name"], cfg["sender_email"]))
    msg["To"] = recipient
    if recipient2: msg["Cc"] = recipient2

    msg.attach(MIMEText(f"新闻聚合报告，请查看附件。\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "plain", "utf-8"))

    with open(html_path, "rb") as f:
        att = MIMEBase("application", "octet-stream")
        att.set_payload(f.read())
    encoders.encode_base64(att)
    att.add_header("Content-Disposition", "attachment", filename=("utf-8", "", os.path.basename(html_path)))
    msg.attach(att)

    try:
        with smtplib.SMTP_SSL(cfg["smtp_server"], cfg["smtp_port"], timeout=30) as s:
            s.login(cfg["sender_email"], cfg["auth_code"])
            recipients = [recipient]
            if recipient2: recipients.append(recipient2)
            s.sendmail(cfg["sender_email"], recipients, msg.as_string())
        logger.info("邮件(附件)发送成功")
        return True
    except Exception as e:
        logger.error(f"邮件发送失败: {e}")
        return False
