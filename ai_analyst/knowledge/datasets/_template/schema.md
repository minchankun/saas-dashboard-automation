# Schema Documentation — subscription_saas

## Dataset Overview
Customer-level snapshot of a monthly SaaS subscription product.
Each row represents one customer. No per-period transaction rows.

## Table: subscription_saas

| Column | Type | Description | Values / Unit | Notes |
|--------|------|-------------|---------------|-------|
| customer_id | string | Mã khách hàng | CUS-1001, ... | Primary key |
| plan | string | Gói thuê bao | Basic, Pro, Enterprise | Ordered: Basic < Pro < Enterprise |
| signup_date | date | Ngày đăng ký | YYYY-MM-DD | Dùng cho cohort & signup trend |
| region | string | Khu vực địa lý | APAC, EMEA, Americas | Segmentation dimension |
| tenure_months | int | Số tháng đã dùng | Tháng | Continuous; tương quan với churn risk |
| monthly_revenue | float | MRR của khách hàng | USD/tháng | Một số giá trị âm → cần kiểm tra |
| status | string | Trạng thái tài khoản | Active, Churned | Redundant với cột churn |
| churn | string/int | Nhãn churn | Yes/No hoặc 1/0 | Classification target; mixed encoding |
