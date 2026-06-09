# SaaS Subscription Analyst

## Mục tiêu

Khi `subscription_saas.csv` được cập nhật, chạy phân tích và tạo **1 report 1 trang dạng HTML** với tổng quan sức khỏe MRR, churn rate theo từng segment, và danh sách khách hàng có nguy cơ rời bỏ cao nhất.

---

## Data

- **File input**: `data/subscription_saas.csv`
- **Cột**: `customer_id, plan, signup_date, region, tenure_months, monthly_revenue, status, churn`
- **Config**: đọc `config.yaml` để lấy danh sách segments và các tham số — KHÔNG hardcode
- **Dạng**: Snapshot (1 dòng/khách hàng) — không append theo ngày

---

## Nhiệm vụ khi được gọi

### Bước 0 — Kiểm tra data trước khi chạy

**0a — Kiểm tra data có tồn tại không:**
- Nếu `data/subscription_saas.csv` không tồn tại → báo lỗi và dừng.

**0b — Kiểm tra data có fresh không:**
- Đọc `logs/last_updated.txt` (do `fetch_data.py` ghi khi validate data)
- Nếu ngày trong file cách hôm nay quá 3 ngày → báo "Data cũ ({ngày}), có thể update bị lỗi. Dừng." và thoát.
- Nếu file không tồn tại → tiếp tục (lần đầu chạy).

**0c — Kiểm tra đã phân tích chưa:**
- Đọc ngày trong `logs/last_analyzed.txt` (nếu file tồn tại)
- Nếu `last_analyzed` == ngày trong `last_updated.txt` → báo "Đã phân tích data này rồi. Dừng." và thoát.
- Nếu khác hoặc chưa có file → tiếp tục.

### Bước 1 — Đọc và tính toán

Đọc `data/subscription_saas.csv` — dùng **toàn bộ data**.

Tính các chỉ số sau:

**Tổng quan:**
- **Total MRR**: tổng `monthly_revenue` của khách Active
- **Total Customers**: tổng số khách hàng
- **Overall Churn Rate**: % khách hàng Churned / tổng
- **Revenue at Risk**: tổng `monthly_revenue` của khách Churned

**Theo segment (plan và region):**
- **Churn Rate**: % Churned trong segment
- **MRR**: tổng monthly_revenue của Active trong segment
- **Avg Tenure**: trung bình tenure_months
- **Revenue at Risk**: tổng monthly_revenue của Churned trong segment

**At-risk customers (Active nhưng nguy cơ cao):**
- Tenure thấp (< 6 tháng) + plan không phải Enterprise
- Sắp xếp theo monthly_revenue giảm dần
- Lấy top N theo `config.yaml → analysis.top_atrisk`

Lưu kết quả vào `data/pipeline/saas_metrics.json`.

### Bước 2 — Xếp hạng và khuyến nghị

Dựa trên metrics, xếp hạng các segment theo churn rate:

Phân loại thành 3 nhóm:
- 🚨 **High-risk** (churn rate vượt ngưỡng `churn_alert_threshold`) — cần hành động ngay
- ⚠️ **Watch** (churn rate trung bình)
- ✅ **Healthy** (churn rate thấp)

### Bước 3 — Tạo HTML report 1 trang

Dùng **html-report skill** và **story-builder agent** để tạo report tại:
`data/reports/saas_report_{YYYY-MM-DD}.html`

**Report cần có:**
- Tiêu đề: "SaaS Health Briefing — {ngày hôm nay}"
- KPI cards: Total MRR | Churn Rate | Active Customers | Revenue at Risk
- Bảng tóm tắt theo plan: Customers | Churn Rate | Active MRR | Revenue at Risk | Trạng thái
- 1 chart: Churn rate theo plan và region
- Section "High-risk segments hôm nay" — top 3 segment với lý do ngắn gọn (2-3 câu mỗi segment)
- Giữ ngắn gọn: **1 trang, không scroll dài**

---

## Agents liên quan

Hệ thống agent nằm tại: `./ai_analyst`

Sử dụng các agent sau từ folder đó:
- **descriptive-analyst** — tính metrics, phân tích segment
- **story-builder** — viết narrative khuyến nghị
- **visualizer** — tạo chart churn by segment
- **html-report skill** — render HTML output

Đọc `./ai_analyst/CLAUDE.md` để hiểu conventions trước khi dùng.

---

## Output

```
data/
├── subscription_saas.csv          ← input (CRM export, validated bởi fetch_data.py)
├── pipeline/
│   └── saas_metrics.json          ← intermediate
└── reports/
    └── saas_report_YYYY-MM-DD.html  ← output cuối
```

---

## Lưu ý

- Không cần phân tích predictive (forecast). Chỉ cần descriptive + recommendation.
- Report phải đọc được trong 2 phút — ưu tiên KPI cards, bảng và bullet points, không viết dài.
- Nếu một segment không có đủ data (< 5 khách hàng), bỏ qua và note trong report.
- Sau khi tạo report xong, ghi ngày hôm nay vào `logs/last_analyzed.txt`.

## Token efficiency — BẮT BUỘC tuân theo

- **Không chạy full pipeline ai_analyst** — chỉ dùng đúng 3 agent: `descriptive-analyst`, `story-builder`, `html-report`. Bỏ qua tất cả agent khác.
- **Không đọc reference docs** của skill trừ khi thực sự cần — ưu tiên dùng kiến thức sẵn có.
- **Không giải thích từng bước** trong quá trình chạy — chỉ báo khi xong hoặc khi có lỗi.
