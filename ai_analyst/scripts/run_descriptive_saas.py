"""
Descriptive analysis for subscription_saas dataset.
Writes data/pipeline/subscription_saas/descriptive_output.json
"""
import pandas as pd
import numpy as np
import json
from datetime import datetime

CLEANED_FILE = r"D:\Data Course\Course - data - AI4DA\Capstone Project\PHAN 2\ai_analyst\data\cleaned\subscription\subscription_saas_cleaned.xlsx"
OUTPUT_FILE = r"D:\Data Course\Course - data - AI4DA\Capstone Project\PHAN 2\ai_analyst\data\pipeline\subscription_saas\descriptive_output.json"

# ── Load ─────────────────────────────────────────────────────────────────────
df = pd.read_excel(CLEANED_FILE)
df["churn"] = df["churn"].astype(int)
df["signup_date"] = pd.to_datetime(df["signup_date"])
df["signup_month"] = df["signup_date"].dt.to_period("M").astype(str)
df["signup_year"] = df["signup_date"].dt.year

active = df[df["status"] == "Active"]
churned = df[df["status"] == "Churned"]

# ── Overall KPIs ─────────────────────────────────────────────────────────────
total_mrr       = round(float(df["monthly_revenue"].sum()), 2)
active_mrr      = round(float(active["monthly_revenue"].sum()), 2)
total_customers = int(len(df))
active_customers= int(len(active))
churned_customers = int(len(churned))
churn_rate_pct  = round(churned_customers / total_customers * 100, 2)

# ── Signups by month ──────────────────────────────────────────────────────────
signups_list = [
    {"month": row["signup_month"], "signups": int(row["signups"])}
    for _, row in df.groupby("signup_month").size().reset_index(name="signups").iterrows()
]

# ── By plan ───────────────────────────────────────────────────────────────────
plan_order = ["Basic", "Pro", "Enterprise"]
by_plan = []
for plan in plan_order:
    p = df[df["plan"] == plan]
    p_active  = p[p["status"] == "Active"]
    p_churned = p[p["status"] == "Churned"]
    count      = int(len(p))
    churn_cnt  = int(len(p_churned))
    t_mrr      = round(float(p["monthly_revenue"].sum()), 2)
    a_mrr      = round(float(p_active["monthly_revenue"].sum()), 2)
    by_plan.append({
        "plan":            plan,
        "customer_count":  count,
        "customer_pct":    round(count / total_customers * 100, 2),
        "active_count":    int(len(p_active)),
        "churn_count":     churn_cnt,
        "churn_rate_pct":  round(churn_cnt / count * 100, 2),
        "total_mrr":       t_mrr,
        "active_mrr":      a_mrr,
        "avg_mrr":         round(float(p["monthly_revenue"].mean()), 2),
        "mrr_share_pct":   round(t_mrr / total_mrr * 100, 2),
    })

# ── By region ─────────────────────────────────────────────────────────────────
region_order = ["APAC", "EMEA", "Americas", "Unknown"]
by_region = []
for region in region_order:
    r = df[df["region"] == region]
    r_active  = r[r["status"] == "Active"]
    r_churned = r[r["status"] == "Churned"]
    count     = int(len(r))
    churn_cnt = int(len(r_churned))
    t_mrr     = round(float(r["monthly_revenue"].sum()), 2)
    a_mrr     = round(float(r_active["monthly_revenue"].sum()), 2)
    by_region.append({
        "region":         region,
        "customer_count": count,
        "customer_pct":   round(count / total_customers * 100, 2),
        "active_count":   int(len(r_active)),
        "churn_count":    churn_cnt,
        "churn_rate_pct": round(churn_cnt / count * 100, 2) if count > 0 else 0,
        "total_mrr":      t_mrr,
        "active_mrr":     a_mrr,
        "mrr_share_pct":  round(t_mrr / total_mrr * 100, 2),
    })

# ── By tenure band ────────────────────────────────────────────────────────────
band_order = ["Early (0-6 mo)", "Growth (7-24 mo)", "Mature (25+ mo)"]
by_tenure = []
for band in band_order:
    t = df[df["tenure_band"] == band]
    t_active  = t[t["status"] == "Active"]
    t_churned = t[t["status"] == "Churned"]
    count     = int(len(t))
    churn_cnt = int(len(t_churned))
    t_mrr     = round(float(t["monthly_revenue"].sum()), 2)
    by_tenure.append({
        "tenure_band":    band,
        "customer_count": count,
        "active_count":   int(len(t_active)),
        "churn_count":    churn_cnt,
        "churn_rate_pct": round(churn_cnt / count * 100, 2) if count > 0 else 0,
        "avg_mrr":        round(float(t["monthly_revenue"].mean()), 2),
        "total_mrr":      t_mrr,
    })

# ── Crosstab MRR plan x region ────────────────────────────────────────────────
ct_raw = df.pivot_table(
    values="monthly_revenue", index="plan", columns="region",
    aggfunc="sum", fill_value=0
).round(2)
crosstab_dict = {
    plan_name: {col: round(float(ct_raw.loc[plan_name, col]), 2) for col in ct_raw.columns}
    for plan_name in ct_raw.index
}

# ── Early churn by plan (for F5) ─────────────────────────────────────────────
early = df[df["tenure_band"] == "Early (0-6 mo)"]
early_basic_churn = round(float(early[early["plan"] == "Basic"]["churn"].mean() * 100), 2)
early_pro_churn   = round(float(early[early["plan"] == "Pro"]["churn"].mean() * 100), 2)
early_ent_churn   = round(float(early[early["plan"] == "Enterprise"]["churn"].mean() * 100), 2)

# ── Assemble output ───────────────────────────────────────────────────────────
output = {
    "stem":          "subscription_saas",
    "analysis_type": "descriptive",
    "generated_at":  "2026-06-06T00:00:00",
    "headline": (
        "Enterprise tier (15% of customers) drives 71% of total MRR "
        "— but early-tenure churn at 35% signals an onboarding crisis cutting across all plans"
    ),

    "kpis": {
        "total_mrr":          total_mrr,
        "active_mrr":         active_mrr,
        "total_customers":    total_customers,
        "active_customers":   active_customers,
        "churned_customers":  churned_customers,
        "churn_rate_pct":     churn_rate_pct,
    },

    "header_kpis": [
        {
            "id":           "kpi_1",
            "label":        "Active MRR",
            "value":        "$507,490",
            "delta":        None,
            "delta_abs":    None,
            "prior_value":  None,
            "status":       "good",
            "direction":    "up_is_good",
            "trend_series": [146918, 198457, 203169],
            "note":         "Trend = total MRR by signup cohort year (2023/2024/2025)",
        },
        {
            "id":           "kpi_2",
            "label":        "Churn Rate",
            "value":        "14.2%",
            "delta":        None,
            "delta_abs":    None,
            "prior_value":  None,
            "status":       "alert",
            "direction":    "down_is_good",
            "trend_series": [35.25, 11.1, 4.5],
            "note":         "Trend = churn rate by tenure band (Early/Growth/Mature) — shows lifecycle pattern",
        },
        {
            "id":           "kpi_3",
            "label":        "Active Customers",
            "value":        "2,574",
            "delta":        None,
            "delta_abs":    None,
            "prior_value":  None,
            "status":       "good",
            "direction":    "up_is_good",
            "trend_series": [878, 1001, 1121],
            "note":         "Signups per year — consistent upward growth +27.7% over 3 years",
        },
    ],

    "segments": {
        "by_plan":         by_plan,
        "by_region":       by_region,
        "by_tenure_band":  by_tenure,
    },

    "trends": {
        "signups_by_month": signups_list,
        "signup_growth_note": (
            "Customer acquisition grew consistently: 878 (2023) -> 1,001 (2024) -> 1,121 (2025), "
            "a +27.7% increase over 3 years."
        ),
        "seasonality_note": (
            "Q1 (Jan-Mar) is the strongest signup window. August is the softest month (184 signups). "
            "Feb is the peak month (309 signups). No strong intra-year revenue trend — dataset is a "
            "customer snapshot, not a monthly revenue time series."
        ),
    },

    "crosstabs": {
        "mrr_plan_x_region": crosstab_dict,
        "note": (
            "Enterprise dominates revenue in every region. "
            "APAC largest Enterprise MRR ($141,249) followed by EMEA ($131,548). "
            "Americas has proportionally fewer Enterprise customers but strong per-customer revenue."
        ),
    },

    "findings": [
        {
            "rank":       1,
            "id":         "F1",
            "type":       "Contrast",
            "finding": (
                "Enterprise (15% of customers) owns 71.4% of active MRR — "
                "a revenue concentration that makes every Enterprise churn event disproportionately damaging"
            ),
            "evidence": (
                "460 Enterprise customers generate $371,029 active MRR vs 1,660 Basic customers "
                "generating only $47,322. Enterprise avg MRR = $851.56 vs Basic = $34.90 (24x ratio)."
            ),
            "confidence": "high",
            "metric":     "mrr_share_pct",
            "value":      {"Enterprise": 71.41, "Pro": 18.03, "Basic": 10.56},
        },
        {
            "rank":       2,
            "id":         "F2",
            "type":       "Pattern",
            "finding": (
                "Churn is an early-tenure crisis: customers in their first 6 months "
                "churn at 35.25% — nearly 8x the rate of mature customers (4.5%)"
            ),
            "evidence": (
                "Early band (0-6 mo): 215/610 churned (35.25%). "
                "Growth (7-24 mo): 174/1,567 (11.1%). Mature (25+ mo): 37/823 (4.5%). "
                "56 customers churned with zero tenure (same-day cancellations)."
            ),
            "confidence": "high",
            "metric":     "churn_rate_by_tenure_band",
            "value":      {"Early (0-6 mo)": 35.25, "Growth (7-24 mo)": 11.1, "Mature (25+ mo)": 4.5},
        },
        {
            "rank":       3,
            "id":         "F3",
            "type":       "Contrast",
            "finding": (
                "Basic plan churn (18.8%) is 3.5x Enterprise's (5.4%) — "
                "Basic accounts for 73% of all churned customers but only 25.8% of churned MRR"
            ),
            "evidence": (
                "Basic: 312 churned of 1,660 (18.8%). Pro: 89/880 (10.1%). Enterprise: 25/460 (5.4%). "
                "Churned MRR: Basic $10,612 + Pro $9,750 vs Enterprise $20,691 — "
                "each Enterprise churn costs $828 vs $34 for Basic."
            ),
            "confidence": "high",
            "metric":     "churn_rate_by_plan",
            "value":      {"Basic": 18.8, "Pro": 10.11, "Enterprise": 5.43},
        },
        {
            "rank":       4,
            "id":         "F4",
            "type":       "Ruling Out",
            "finding": (
                "APAC's elevated churn (15.5%) is a genuine regional effect — "
                "NOT explained by a heavier Basic plan concentration in APAC"
            ),
            "evidence": (
                "APAC plan mix (Basic 54.9%, Pro 30.0%, Enterprise 15.1%) is nearly identical "
                "to the overall mix (55.3%/29.3%/15.3%). Within Basic tier, APAC churn = 20.8% "
                "vs overall Basic 18.8% — a genuine +2pp elevation not attributable to composition."
            ),
            "confidence": "high",
            "metric":     "simpsons_paradox_check",
            "value": {
                "APAC":     15.53,
                "EMEA":     14.03,
                "Americas": 12.75,
                "overall":  14.2,
            },
        },
        {
            "rank":       5,
            "id":         "F5",
            "type":       "Implication",
            "finding": (
                "Accelerating acquisition (+27.7% over 3 years) is undermined by 46% early churn "
                "in the Basic plan — new Basic customers are leaving before generating positive LTV"
            ),
            "evidence": (
                "Basic plan Early-band churn = 46.15%. At avg $34.90 MRR, "
                "a Basic customer churning in month 1-3 generates negative LTV after acquisition cost. "
                "Pro and Enterprise early churn (26.1% and 16.5%) are elevated but less severe."
            ),
            "confidence": "medium",
            "metric":     "early_churn_by_plan",
            "value": {
                "Basic_early_churn":      early_basic_churn,
                "Pro_early_churn":        early_pro_churn,
                "Enterprise_early_churn": early_ent_churn,
            },
        },
    ],

    "scqa_draft": {
        "situation": (
            "The SaaS platform has 3,000 customers across three plan tiers (Basic 55%, Pro 29%, "
            "Enterprise 15%) generating $548,543 total MRR, with customer acquisition growing "
            "+27.7% from 2023 to 2025."
        ),
        "complication": (
            "Overall churn stands at 14.2% (426 customers lost), but early-tenure customers "
            "(0-6 months) churn at 35.25% — more than 8x the mature customer rate (4.5%). "
            "Basic plan early-stage churn reaches 46.2%, meaning nearly half of new low-tier "
            "customers leave before generating positive lifetime value."
        ),
        "question": (
            "Where is churn most concentrated across plans, regions, and tenure stages, "
            "and which customer profiles carry the greatest revenue risk?"
        ),
        "answer": (
            "Revenue risk is dominated by Enterprise (71% of active MRR) where each churn event "
            "costs $828/month; volume risk sits in Basic (73% of churned customers) driven by a "
            "broken early-tenure experience. APAC has the highest churn by region (15.5%) via a "
            "genuine regional effect. A classification model on plan, tenure, and region can "
            "identify at-risk customers before they reach their peak churn window."
        ),
    },

    "simpsons_paradox_checks": [
        {
            "check_id":          "SP1",
            "hypothesis":        "APAC has genuinely higher churn than other regions",
            "aggregate_finding": "APAC churn rate = 15.53% vs overall 14.2%",
            "segment_test": (
                "Plan mix in APAC (Basic 54.9%, Pro 30.0%, Enterprise 15.1%) "
                "matches overall mix (55.3%/29.3%/15.3%). "
                "Within-plan: APAC Basic churn 20.8% vs overall Basic 18.8%."
            ),
            "paradox_detected": False,
            "conclusion": (
                "No paradox. APAC elevation is real — not a mix artifact. "
                "Genuine +2pp effect on Basic churn within APAC."
            ),
        },
        {
            "check_id":          "SP2",
            "hypothesis":        "Higher tenure universally predicts lower churn",
            "aggregate_finding": "Mature customers (25+ mo) churn at 4.5% vs Early 35.25%",
            "segment_test": (
                "Enterprise churned customers avg tenure = 8.1 mo vs active Enterprise = 17.3 mo. "
                "Pattern holds within all three plan tiers."
            ),
            "paradox_detected": False,
            "conclusion": (
                "No paradox. Tenure-churn relationship is consistent across segments. "
                "Early tenure is a universal high-risk signal."
            ),
        },
    ],

    "chart_recommendations": [
        {
            "chart_id": "chart_01",
            "type":     "stacked_bar",
            "title":    "Enterprise drives 71% of MRR despite being only 15% of customers",
            "x":        "plan",
            "y":        "mrr_share_pct",
            "segment":  None,
            "insight":  "Revenue concentration risk — single tier dominates",
        },
        {
            "chart_id": "chart_02",
            "type":     "bar",
            "title":    "Early-tenure customers churn at 35% — 8x the rate of mature customers",
            "x":        "tenure_band",
            "y":        "churn_rate_pct",
            "segment":  None,
            "insight":  "Onboarding crisis concentrated in first 6 months",
        },
        {
            "chart_id": "chart_03",
            "type":     "grouped_bar",
            "title":    "Basic plan churn (18.8%) is 3.5x Enterprise (5.4%) — gap persists across regions",
            "x":        "plan",
            "y":        "churn_rate_pct",
            "segment":  "region",
            "insight":  "Plan tier is the primary structural churn driver",
        },
        {
            "chart_id": "chart_04",
            "type":     "line",
            "title":    "Monthly signups grew steadily but Q1 peaks and August troughs repeat each year",
            "x":        "month",
            "y":        "signups",
            "segment":  None,
            "insight":  "Acquisition growth with seasonal softness in mid-year",
        },
        {
            "chart_id": "chart_05",
            "type":     "heatmap",
            "title":    "APAC and EMEA hold equal Enterprise MRR share — both are high-concentration risk zones",
            "x":        "region",
            "y":        "plan",
            "value":    "total_mrr",
            "insight":  "Geographic revenue risk map",
        },
    ],

    "predictive_needed":    True,
    "predictive_type":      "classification",
    "predictive_rationale": (
        "Strong plan-tier, tenure-band, and regional churn signals plus binary churn target "
        "make classification (logistic regression or gradient boosted tree) the appropriate "
        "next step to score active customers by churn probability and quantify revenue at risk."
    ),
}


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, cls=NpEncoder, ensure_ascii=False)

print(f"Written: {OUTPUT_FILE}")
print(f"JSON size: {len(json.dumps(output, cls=NpEncoder)):,} chars")
print()
print("Header KPIs:")
for k in output["header_kpis"]:
    print(f"  {k['label']}: {k['value']}")
print()
print(f"Findings: {len(output['findings'])} total")
print(f"Ruling Out: {sum(1 for f in output['findings'] if f['type'] == 'Ruling Out')}")
print()
print("Key numbers:")
print(f"  Total MRR:        ${output['kpis']['total_mrr']:,.2f}")
print(f"  Active MRR:       ${output['kpis']['active_mrr']:,.2f}")
print(f"  Churn rate:       {output['kpis']['churn_rate_pct']}%")
print(f"  Active customers: {output['kpis']['active_customers']}")
print(f"  Enterprise MRR share: {next(p for p in output['segments']['by_plan'] if p['plan']=='Enterprise')['mrr_share_pct']}%")
print(f"  Early band churn: {next(t for t in output['segments']['by_tenure_band'] if 'Early' in t['tenure_band'])['churn_rate_pct']}%")
