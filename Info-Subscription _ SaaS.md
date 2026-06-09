# Dataset 3 \- Subscription / SaaS

## **0\. Dataset**

\[subscription\_saas\.csv\]



## **1\. Giới thiệu**

Dữ liệu khách hàng của một sản phẩm SaaS bán theo gói thuê bao hằng tháng\. Mỗi dòng là một khách hàng: gói đang dùng, ngày đăng ký, khu vực, thời gian gắn bó, doanh thu hằng tháng \(MRR\) và trạng thái còn hoạt động hay đã rời bỏ\. Trọng tâm là **churn** \(tỷ lệ rời bỏ\) và **MRR**\.



## **2\. Bối cảnh kinh doanh**

Mô hình SaaS sống nhờ giữ chân khách hàng: chi phí có được một khách hàng mới cao hơn nhiều giữ một khách hàng cũ\. Đội Growth/Finance cần biết gói nào và khu vực nào churn cao, doanh thu nào đang gặp rủi ro, và khách hàng nào sắp rời bỏ để chăm sóc kịp thời\.



## **3\. Cấu trúc dataset và business flow**

Đây là **snapshot** ở cấp khách hàng \(mỗi khách hàng một dòng\)\.

```Plain Text
signup_date → dùng sản phẩm (tích lũy tenure_months, trả monthly_revenue)
            → status = Active | Churned
```

Chiều thời gian khai thác qua \`signup\_date\` \(số đăng ký mới theo tháng, phân tích cohort\)\. Vì không có dòng theo từng tháng, **forecast MRR theo chuỗi thời gian không trực tiếp làm được** từ bộ này — bài toán dự báo phù hợp là **classification churn**\. MRR chỉ phân tích ở dạng tổng/theo segment\.



## **4\. Data Dictionary**

|Cột|Kiểu|Ý nghĩa|Giá trị / Đơn vị|Ghi chú|
|---|---|---|---|---|
|`customer_id`|string|Mã khách hàng|`CUS-1001`|Khóa định danh|
|`plan`|string|Gói thuê bao|Basic, Pro, Enterprise|Dimension chính \(có thứ tự\)|
|`signup_date`|date|Ngày đăng ký|`2023-02-10`|Dùng cho cohort / signups theo tháng|
|`region`|string|Khu vực|APAC, EMEA, Americas||
|`tenure_months`|int|Số tháng đã dùng|Tháng||
|`monthly_revenue`|float|MRR của khách|USD/tháng||
|`status`|string|Trạng thái|Active, Churned||
|`churn`|string|Đã churn?|Yes / No|Target classification \(đồng nghĩa `status = Churned`\)|



## **5\. Key Analysis Questions**

\- **L1 \(Descriptive\):** Tổng MRR và churn rate hiện tại? Phân bổ khách hàng và doanh thu theo gói thế nào?

\- **L2 \(Diagnostic\):** Gói hoặc khu vực nào churn cao nhất? Thời gian gắn bó \(tenure\) ảnh hưởng đến churn ra sao?

\- **L3 \(Predictive — classification\):** Dự đoán khách hàng nào sắp churn? Doanh thu đang gặp rủi ro \(revenue at risk\) là bao nhiêu?



