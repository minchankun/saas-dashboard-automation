# SaaS Subscription Pipeline — Hướng dẫn Setup

## Tổng quan pipeline

```
18:00  GitHub Actions (daily_fetch.yml)
       → fetch_data.py validate data → commit logs/last_updated.txt
       → Check: subscription_saas.csv có hợp lệ không?

19:00  Claude Routine
       → Check: data có mới không? (so với last_analyzed.txt)
       → Chạy phân tích MRR + churn → tạo report HTML
       → Push report lên repo

20:00  GitHub Actions (daily_email.yml)
       → Check: có report HTML hôm nay không?
       → Nếu có → gửi email tóm tắt SaaS health
       → Nếu không → bỏ qua (agent chưa chạy xong hoặc lỗi)
```

> Mỗi bước tự validate đầu vào trước khi chạy. Bước sau không chạy nếu bước trước chưa có output.

---

## Cấu trúc repo

```
saas-dashboard-automation/           ← GitHub repo root
├── .github/
│   └── workflows/
│       ├── daily_fetch.yml          ← 18:00: validate data
│       └── daily_email.yml          ← 20:00: gửi email
├── ai_analyst/                      ← agent phân tích
├── data/
│   ├── subscription_saas.csv        ← CRM export (commit thủ công khi có data mới)
│   ├── pipeline/
│   │   └── saas_metrics.json        ← tự động tạo khi Routine chạy
│   └── reports/
│       └── saas_report_YYYY-MM-DD.html  ← report hàng ngày
├── logs/
│   ├── fetch.log                    ← log mỗi lần validate
│   ├── last_updated.txt             ← ngày data được validate lần cuối
│   └── last_analyzed.txt            ← ngày agent chạy lần cuối
├── CLAUDE.md                        ← instructions cho Claude Routine
├── config.yaml                      ← cấu hình segments, ngưỡng churn
├── fetch_data.py                    ← script validate data
├── send_summary.py                  ← script gửi email
└── requirements.txt
```

> Muốn thay đổi ngưỡng cảnh báo hoặc segments → **chỉ sửa `config.yaml`**.

---

## Bước 1 — Tạo repo trên GitHub

1. Vào https://github.com → click **"New"**
2. Điền **Repository name**: `saas-dashboard-automation`, **Visibility**: `Private`
3. Click **"Create repository"**

---

## Bước 2 — Upload files lên repo

**Dùng Git (nhanh nhất):**

```bash
cd "path/to/PHAN 3"
git init
git remote add origin https://github.com/your-username/saas-dashboard-automation.git
git add .
git commit -m "initial setup"
git push -u origin main
```

**Upload thủ công:** Tạo `.github/workflows/daily_fetch.yml` bằng cách vào **"Add file"** → **"Create new file"**, gõ tên file có dấu `/` để tạo thư mục. Các file còn lại upload qua **"Upload files"**.

---

## Bước 3 — Cấp quyền write cho GitHub Actions

Vào repo → **Settings** → **Actions** → **General** → **Workflow permissions** → chọn **"Read and write permissions"** → **Save**.

---

## Bước 4 — Test validate data lần đầu

1. Upload `data/subscription_saas.csv` vào repo trước
2. Vào tab **Actions** → click **"SaaS Daily Fetch"** → **"Run workflow"**
3. Chờ ~1 phút → kiểm tra tab **Code** có `logs/last_updated.txt` chưa

Log sẽ hiện tổng số khách hàng, churn rate tổng, và total MRR.

---

## Bước 5 — Cấp quyền push cho Claude Routine (PAT)

Claude Routine cần PAT để tự push report lên repo.

### 5a — Tạo PAT

1. Vào https://github.com/settings/tokens?type=beta → **"Generate new token"**
2. Điền:
   - **Token name**: `saas-routine`
   - **Expiration**: 90 ngày
   - **Repository access**: Only select repositories → `saas-dashboard-automation`
   - **Permissions** → **Contents**: `Read and write`
3. **Generate token** → copy ngay (chỉ hiện 1 lần)

### 5b — Nhúng PAT vào Routine Instructions

Thêm vào đầu Instructions của Claude Routine:

```
Trước khi push, chạy lệnh:
git remote set-url origin https://<YOUR_PAT>@github.com/your-username/saas-dashboard-automation.git
```

> ⚠️ Không share routine này với ai. Khi PAT hết hạn → tạo token mới → update Instructions.

---

## Bước 6 — Setup Claude Routine (phân tích)

Tạo Claude Routine với:

| Setting | Giá trị |
|---|---|
| **Trigger** | Weekdays, 19:00 |
| **Connector** | repo `saas-dashboard-automation` |
| **Model** | Haiku (tiết kiệm token) |

**Instructions — copy nguyên đoạn sau vào ô Instructions:**

```
Trước khi push, chạy lệnh sau để dùng PAT:
git remote set-url origin https://<YOUR_PAT>@github.com/your-username/saas-dashboard-automation.git

---

Đọc CLAUDE.md trong repo để hiểu pipeline, sau đó thực hiện theo thứ tự:

Bước 0 — Kiểm tra trước khi chạy:
- Nếu data/subscription_saas.csv không tồn tại → dừng, báo lỗi
- Nếu logs/last_updated.txt tồn tại và ngày trong đó cách hôm nay quá 3 ngày → dừng, báo "data cũ"
- Nếu logs/last_analyzed.txt tồn tại và ngày trong đó == ngày trong last_updated.txt → dừng, báo "đã phân tích rồi"

Bước 1 — Tính metrics SaaS:
- Total MRR, Overall Churn Rate, Revenue at Risk
- Breakdown theo plan (Basic / Pro / Enterprise): churn rate, MRR, avg tenure
- At-risk customers: active với tenure < 6 tháng, sắp xếp theo MRR giảm dần

Bước 2 — Xếp hạng segment theo churn rate:
- High-risk: churn rate vượt ngưỡng config
- Watch: churn trung bình
- Healthy: churn thấp

Bước 3 — Tạo HTML report 1 trang tại data/reports/saas_report_{YYYY-MM-DD}.html

Bước 4 — Push report lên repo

Bước 5 — Ghi ngày hôm nay vào logs/last_analyzed.txt

Lưu ý token efficiency:
- Không chạy full pipeline ai_analyst, chỉ dùng: descriptive-analyst, story-builder, html-report
- Không giải thích từng bước, chỉ báo khi xong hoặc lỗi
```

> Thay `<YOUR_PAT>` và `your-username` bằng thông tin thực của bạn.

**Validation trong Routine (tự động):**
- Kiểm tra `subscription_saas.csv` tồn tại
- Kiểm tra data không quá 3 ngày kể từ lần validate cuối
- Kiểm tra chưa phân tích data này rồi (so với `last_analyzed.txt`)

---

## Bước 7 — Setup gửi email (tùy chọn)

Email gửi lúc 20:00 sau khi Routine phân tích xong. Script tự check có report hôm nay chưa trước khi gửi — nếu Routine chưa chạy xong thì bỏ qua.

### 7a — Tạo Gmail App Password

Vào https://myaccount.google.com/apppasswords → tạo password tên `saas-github` → copy 16 ký tự.

> Nếu không thấy mục này: account dùng Passkey hoặc Google Workspace — Google chặn tính năng này, không có workaround.

### 7b — Thêm GitHub Secrets

Vào repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Secret name | Value |
|---|---|
| `GMAIL_USER` | your-email@gmail.com |
| `GMAIL_APP_PASSWORD` | 16 ký tự vừa tạo |
| `EMAIL_TO` | email nhận (có thể giống GMAIL_USER) |

Workflow `daily_email.yml` đã cấu hình sẵn, không cần thêm gì.

---

## Tùy chỉnh

| Muốn thay đổi | Sửa ở đâu |
|---|---|
| Thêm/bớt plan hoặc region | `config.yaml` → `segments` |
| Ngưỡng cảnh báo churn | `config.yaml` → `analysis.churn_alert_threshold` |
| Số KH at-risk hiển thị | `config.yaml` → `analysis.top_atrisk` |
| Số segment trong "High Risk" email | `config.yaml` → `report.top_segments` |
| Giờ validate data | `daily_fetch.yml` → `cron` |
| Giờ gửi email | `daily_email.yml` → `cron` |

---

## Troubleshooting

### Lỗi 403 khi Routine push
Toggle "Allow unrestricted git push" không hoạt động ổn định — dùng PAT theo Bước 5.

### PAT hết hạn
Vào https://github.com/settings/tokens?type=beta → tạo token mới → update Instructions của Routine.

### Routine báo "Data cũ" hoặc "Đã phân tích rồi"
Bình thường — cuối tuần, ngày lễ, hoặc data chưa được cập nhật từ CRM.

### Email không gửi dù Routine đã chạy
Kiểm tra: report có trong thư mục `data/reports/` trên GitHub không? Nếu không → Routine bị lỗi lúc push. Xem log trong tab Actions.

### Actions không chạy tự động
Repo private free có 2000 phút/tháng. Pipeline này dùng ~2 phút/ngày → ~40 phút/tháng, trong giới hạn.

### `fetch_data.py` báo thiếu cột
Kiểm tra file CSV export từ CRM có đủ 8 cột: `customer_id, plan, signup_date, region, tenure_months, monthly_revenue, status, churn`.
