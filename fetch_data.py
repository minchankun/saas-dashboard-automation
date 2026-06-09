"""
fetch_data.py — GitHub Actions version
----------------------------------------
Validate subscription_saas.csv và log basic stats.
Không gọi API bên ngoài — data là snapshot từ CRM export.

Logic:
- Kiểm tra file tồn tại và đúng schema
- Log stats cơ bản (row count, MRR, churn rate)
- Ghi logs/last_updated.txt với timestamp hôm nay

Output: logs/last_updated.txt, logs/fetch.log
"""

import csv
import logging
import sys
from datetime import date
from pathlib import Path

import yaml

# ─── ĐỌC CONFIG ──────────────────────────────────────────────────────────────

_config = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8"))
DATA_FILE = Path("data/subscription_saas.csv")
LAST_UPDATED_FILE = Path("logs/last_updated.txt")
LOG_FILE = Path("logs/fetch.log")
REQUIRED_COLUMNS = {
    "customer_id", "plan", "signup_date", "region",
    "tenure_months", "monthly_revenue", "status", "churn",
}

# ─── LOGGING ─────────────────────────────────────────────────────────────────

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def validate_and_log():
    if not DATA_FILE.exists():
        log.error(f"Không tìm thấy {DATA_FILE}. Dừng.")
        sys.exit(1)

    rows = []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            log.error(f"Thiếu cột: {missing}. Dừng.")
            sys.exit(1)
        rows = list(reader)

    total = len(rows)
    churned = sum(
        1 for r in rows
        if r.get("churn", "").strip().lower() in ("yes", "1", "true")
    )
    active_rows = [r for r in rows if r.get("status", "").strip().lower() == "active"]

    mrr_total = 0.0
    for r in active_rows:
        try:
            mrr_total += float(r["monthly_revenue"])
        except (ValueError, KeyError):
            pass

    churn_rate = churned / total * 100 if total > 0 else 0.0

    log.info("=== Validation OK ===")
    log.info(f"Total customers : {total}")
    log.info(f"Active          : {len(active_rows)}")
    log.info(f"Churned         : {churned} ({churn_rate:.1f}%)")
    log.info(f"Total MRR       : ${mrr_total:,.2f}")

    LAST_UPDATED_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_UPDATED_FILE.write_text(date.today().strftime("%Y-%m-%d"), encoding="utf-8")
    log.info(f"Đã ghi {LAST_UPDATED_FILE}: {date.today()}")


if __name__ == "__main__":
    validate_and_log()
