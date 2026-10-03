"""Daily news digest -> email. Config comes from environment variables (never hardcode keys)."""
import os, sys, json, html, smtplib, ssl, urllib.request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CATEGORIES = ["Business", "Technology", "World", "US", "Sports", "Science", "Health", "Entertainment"]
PER_CAT = 5

def fetch_news():
    """OkSurf free Google News API - no API key needed. Returns {category: [articles]}."""
    req = urllib.request.Request("https://ok.surf/api/v1/news-feed",
                                 headers={"accept": "application/json", "User-Agent": "daily-news-digest/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def build_html(data):
    parts = ['<div style="font-family:Arial,sans-serif;max-width:640px;margin:auto">',
             '<h2>Good morning! Aaj ki khabrein</h2>']
    for cat in CATEGORIES:
        items = data.get(cat, [])[:PER_CAT]
        if not items:
            continue
        parts.append(f'<h3 style="border-bottom:2px solid #eee;padding-bottom:4px">{html.escape(cat)}</h3><ul style="padding-left:18px">')
        for it in items:
            t, l, s = html.escape(it.get("title", "")), it.get("link", "#"), html.escape(it.get("source", ""))
            parts.append(f'<li style="margin:8px 0"><a href="{l}" style="text-decoration:none;color:#1a0dab">{t}</a> <span style="color:#777">- {s}</span></li>')
        parts.append("</ul>")
    parts.append("</div>")
    return "\n".join(parts)

def send_email(body_html):
    user, pwd = os.environ["GMAIL_USER"], os.environ["GMAIL_APP_PASSWORD"]
    to = os.environ.get("MAIL_TO", user)
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = "Your Morning News", user, to
    msg.attach(MIMEText(body_html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(user, pwd)
        s.sendmail(user, [to], msg.as_string())

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":   # python news_digest.py --preview sample.json
        data = json.load(open(sys.argv[2]))
        open("preview.html", "w").write(build_html(data)); print("preview.html written")
    else:
        send_email(build_html(fetch_news()))
        print("Sent")
