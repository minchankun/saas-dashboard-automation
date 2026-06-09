# Dataset Quirks — subscription_saas

## Known Issues

1. **churn column — mixed encoding:**
   Cột `churn` chứa cả string "Yes"/"No" lẫn integer "1"/"0".
   Phân bố thực tế: "No"=2,548 · "Yes"=362 · "0"=81 · "1"=9
   → Tổng churned thực: 371 khách hàng (Yes + 1).
   Phải chuẩn hóa về một kiểu duy nhất trước khi phân tích hoặc train model.

2. **monthly_revenue âm:**
   Một số khách hàng có MRR âm (ví dụ: -28.56 USD) dù status = Churned.
   Có thể là refund, điều chỉnh, hoặc lỗi nhập liệu.
   Cần lọc hoặc flag trước khi tính tổng MRR.

3. **churn vs. status — redundant:**
   `churn = "Yes"` ↔ `status = "Churned"` và `churn = "No"` ↔ `status = "Active"`.
   Hai cột biểu diễn cùng thông tin. Dùng `churn` làm classification target,
   `status` có thể drop khi train model.

## Data Quality Notes
- Dataset là **snapshot cấp khách hàng**, không phải chuỗi thời gian theo tháng.
- Chiều thời gian chỉ có qua `signup_date` → phù hợp phân tích cohort & signup trend.
- **Forecast MRR theo time series KHÔNG trực tiếp làm được** từ bộ này.
- Churn rate tổng thể ≈ 12.4% (371 / 3,000).
- Phân bổ plan: Basic 55% · Pro 29% · Enterprise 15%.

## Business Context
- Mô hình SaaS: giữ chân khách hàng là ưu tiên số 1 (CAC >> retention cost).
- Dải thời gian đăng ký: 2023-01-01 → 2025-12-31 (3 năm signups).
- Câu hỏi kinh doanh trọng tâm:
  - Gói / khu vực nào churn cao nhất?
  - Tenure ảnh hưởng churn ra sao?
  - Khách hàng nào sắp churn? Revenue at risk là bao nhiêu?
- Bài toán dự đoán phù hợp: **churn classification** (không phải time-series forecast).
