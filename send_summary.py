"""
send_summary.py
---------------
Đọc subscription_saas.csv, tính metrics SaaS, gửi email tóm tắt qua Gmail SMTP.
Chạy sau fetch_data.py trong GitHub Actions.
"""

import csv
import os
import smtplib
import sys
from collections import defaultdict
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import yaml

# ─── CONFIG ──────────────────────────────────────────────────────────────────

_config = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8"))
PLANS = _config["segments"]["plans"]
TOP_N = _config["report"].get("top_segments", 3)
CHURN_ALERT = _config["analysis"].get("churn_alert_threshold", 0.20)

DATA_FILE = Path("data/subscription_saas.csv")

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
EMAIL_TO = os.environ.get("EMAIL_TO", GMAIL_USER)

TODAY = date.today().strftime("%Y-%m-%d")
SUBJECT = f"SaaS Health Briefing — {TODAY}"

# ─── ĐỌC DATA ────────────────────────────────────────────────────────────────

def read_csv():
    rows = []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows

# ─── TÍNH METRICS ────────────────────────────────────────────────────────────

def compute_metrics(rows):
    plan_stats = defaultdict(lambda: {
        "total": 0, "churned": 0, "mrr": 0.0, "revenue_at_risk": 0.0,
    })

    total_customers = len(rows)
    total_churned = 0
    total_mrr = 0.0
    total_revenue_at_risk = 0.0

    for r in rows:
        plan = r.get("plan", "Unknown")
        is_churned = r.get("churn", "").strip().lower() == "yes"
        is_active = r.get("status", "").strip().lower() == "active"
        try:
            mrr = float(r.get("monthly_revenue", 0))
        except ValueError:
            mrr = 0.0

        plan_stats[plan]["total"] += 1
        if is_churned:
            plan_stats[plan]["churned"] += 1
            plan_stats[plan]["revenue_at_risk"] += mrr
            total_churned += 1
            total_revenue_at_risk += mrr
        if is_active:
            plan_stats[plan]["mrr"] += mrr
            total_mrr += mrr

    results = []
    for plan in PLANS:
        s = plan_stats.get(plan, {"total": 0, "churned": 0, "mrr": 0.0, "revenue_at_risk": 0.0})
        churn_rate = s["churned"] / s["total"] if s["total"] > 0 else 0.0
        results.append({
            "plan": plan,
            "total": s["total"],
            "churned": s["churned"],
            "churn_rate": churn_rate,
            "mrr": s["mrr"],
            "revenue_at_risk": s["revenue_at_risk"],
        })

    results.sort(key=lambda x: x["churn_rate"], reverse=True)

    overall = {
        "total_customers": total_customers,
        "total_churned": total_churned,
        "churn_rate": total_churned / total_customers if total_customers > 0 else 0.0,
        "total_mrr": total_mrr,
        "total_revenue_at_risk": total_revenue_at_risk,
    }

    return results, overall

# ─── TẠO EMAIL ───────────────────────────────────────────────────────────────

def build_email(plan_metrics, overall):
    top_risk = plan_metrics[:TOP_N]
    alert_color = "#fff3e0" if overall["churn_rate"] >= CHURN_ALERT else "#e8f5e9"

    lines = [
        f"<h2>SaaS Health Briefing — {TODAY}</h2>",
        "<div style='display:flex;gap:16px;margin-bottom:16px;flex-wrap:wrap'>",
        f"  <div style='background:#e8f5e9;padding:12px 20px;border-radius:8px'>"
        f"<b>Total MRR</b><br>${overall['total_mrr']:,.0f}</div>",
        f"  <div style='background:{alert_color};padding:12px 20px;border-radius:8px'>"
        f"<b>Churn Rate</b><br>{overall['churn_rate']*100:.1f}%</div>",
        f"  <div style='background:#e8f5e9;padding:12px 20px;border-radius:8px'>"
        f"<b>Active Customers</b><br>{overall['total_customers'] - overall['total_churned']}</div>",
        f"  <div style='background:#fce4ec;padding:12px 20px;border-radius:8px'>"
        f"<b>Revenue at Risk</b><br>${overall['total_revenue_at_risk']:,.0f}</div>",
        "</div>",
        "<h3>📊 Breakdown theo Plan</h3>",
        "<table border='1' cellpadding='6' cellspacing='0' "
        "style='border-collapse:collapse;font-family:Arial;font-size:13px'>",
        "<tr style='background:#f0f0f0'>"
        "<th>Plan</th><th>Customers</th><th>Churn Rate</th>"
        "<th>Active MRR</th><th>Revenue at Risk</th></tr>",
    ]

    for m in plan_metrics:
        is_alert = m["churn_rate"] >= CHURN_ALERT
        color = "#f8d7da" if is_alert else "#d4edda"
        flag = " 🚨" if is_alert else ""
        lines.append(
            f"<tr style='background:{color}'>"
            f"<td><b>{m['plan']}{flag}</b></td>"
            f"<td>{m['total']} ({m['churned']} churned)</td>"
            f"<td>{m['churn_rate']*100:.1f}%</td>"
            f"<td>${m['mrr']:,.0f}</td>"
            f"<td>${m['revenue_at_risk']:,.0f}</td>"
            f"</tr>"
        )

    lines.append("</table>")
    lines.append(f"<h3>🚨 Top {TOP_N} segments churn cao nhất</h3><ul>")
    for m in top_risk:
        status = "🚨 HIGH RISK" if m["churn_rate"] >= CHURN_ALERT else "⚠️ Watch"
        lines.append(
            f"<li><b>{m['plan']}</b> [{status}] — "
            f"Churn: {m['churn_rate']*100:.1f}%, "
            f"Revenue at Risk: ${m['revenue_at_risk']:,.0f}</li>"
        )
    lines.append("</ul>")
    lines.append(
        "<p style='color:gray;font-size:11px'>Auto-generated by SaaS Subscription Pipeline</p>"
    )
    return "\n".join(lines)

# ─── GỬI EMAIL ───────────────────────────────────────────────────────────────

def send_email(html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = SUBJECT
    msg["From"] = GMAIL_USER
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, EMAIL_TO, msg.as_string())

    print(f"✓ Email gửi thành công đến {EMAIL_TO}")

# ─── MAIN ────────────────────────────────────────────────────────────────────

def get_latest_report() -> Path | None:
    reports_dir = Path("data/reports")
    if not reports_dir.exists():
        return None
    cutoff = date.today() - timedelta(days=3)
    candidates = []
    for f in reports_dir.glob("saas_report_*.html"):
        for part in f.stem.split("_"):
            try:
                file_date = date.fromisoformat(part)
                if file_date >= cutoff:
                    candidates.append((file_date, f))
                break
            except ValueError:
                continue
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


if __name__ == "__main__":
    if not DATA_FILE.exists():
        print("Không tìm thấy subscription_saas.csv. Bỏ qua gửi email.")
        sys.exit(0)

    latest_report = get_latest_report()
    if latest_report is None:
        print("Không tìm thấy saas_report HTML trong 3 ngày gần nhất. Bỏ qua gửi email.")
        sys.exit(0)
    print(f"Dùng report: {latest_report.name}")

    rows = read_csv()
    plan_metrics, overall = compute_metrics(rows)

    if not plan_metrics:
        print("Không đủ data để tính metrics. Bỏ qua.")
        sys.exit(0)

    html = build_email(plan_metrics, overall)
    send_email(html)
