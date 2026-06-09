import json
from pathlib import Path
from datetime import datetime

ROOT = Path("d:/Data Course/Course - data - AI4DA/Capstone Project/PHAN 2/ai_analyst")
PIPE = ROOT / "data/pipeline/subscription_saas"

with open(PIPE / "story_arc.json", encoding="utf-8") as f:
    story_arc = json.load(f)

chart_reqs = {c["chart_id"]: c for c in story_arc["chart_requirements"]}

STD_CONFIG = {
    "width": "100%", "height": 400,
    "background": "#F7F6F2",
    "margin": {"top": 60, "right": 40, "bottom": 50, "left": 60},
    "show_gridlines": False, "spine_color": "#E2E8F0",
    "spines": ["bottom", "left"],
    "font_family": "'IBM Plex Sans', system-ui, sans-serif",
    "title_font": "'Outfit', sans-serif",
    "title_size": 16, "label_size": 11, "axis_size": 10, "tooltip": True
}

H = "#2554E7"   # highlight blue
A = "#EF4444"   # alert red
G = "#10B981"   # green positive
N = "#D1D5DB"   # neutral gray

charts = []

# 1. plan_mrr_share_bar
d = chart_reqs["plan_mrr_share_bar"]["data"]
charts.append({
    "chart_id": "plan_mrr_share_bar",
    "chart_type": "vertical_bar",
    "title": "Enterprise owns 71% of active MRR despite just 15% of customers",
    "subtitle": "Active MRR share by plan tier",
    "data": {
        "labels": d["categories"],
        "series": [{"name": "MRR Share %", "values": d["values"],
                    "colors": [N, N, H], "value_format": "%"}]
    },
    "annotations": [
        {"type": "point", "data_index": 2,
         "text": "Enterprise: 71.4% MRR share",
         "style": {"color": H, "fontSize": 11, "fontWeight": 600, "offsetY": -45,
                   "background": "rgba(37,84,231,0.08)"}}
    ],
    "callout": "So what: Enterprise (15% of customers) owns 71% of MRR — each churn costs $828 vs $35 for Basic.",
    "config": STD_CONFIG
})

# 2. plan_churn_rate_bar
d = chart_reqs["plan_churn_rate_bar"]["data"]
charts.append({
    "chart_id": "plan_churn_rate_bar",
    "chart_type": "vertical_bar",
    "title": "Basic churn (18.8%) is 3.5x Enterprise's (5.4%) — plan tier drives risk",
    "subtitle": "Churn rate by plan; reference = 14.2% overall",
    "data": {
        "labels": d["categories"],
        "series": [{"name": "Churn Rate %", "values": d["values"],
                    "colors": [A, N, N], "value_format": "%"}],
        "reference_line": {"value": 14.2, "label": "Overall 14.2%"}
    },
    "annotations": [
        {"type": "point", "data_index": 0,
         "text": "Basic: 18.8% (+4.6pp above avg)",
         "style": {"color": A, "fontSize": 11, "fontWeight": 600, "offsetY": -45,
                   "background": "rgba(239,68,68,0.08)"}}
    ],
    "callout": "So what: Basic plan churns at 18.8% — 3.5x Enterprise — accounting for 73% of all lost customers.",
    "config": STD_CONFIG
})

# 3. tenure_churn_rate_bar
d = chart_reqs["tenure_churn_rate_bar"]["data"]
charts.append({
    "chart_id": "tenure_churn_rate_bar",
    "chart_type": "vertical_bar",
    "title": "Survive 6 months and churn drops 8x — the first 6 months decides retention",
    "subtitle": "Churn rate by tenure band; reference = 14.2% overall",
    "data": {
        "labels": d["categories"],
        "series": [{"name": "Churn Rate %", "values": d["values"],
                    "colors": [A, N, G], "value_format": "%"}],
        "reference_line": {"value": 14.2, "label": "Overall 14.2%"}
    },
    "annotations": [
        {"type": "point", "data_index": 0,
         "text": "Early: 35.2% (8x mature rate)",
         "style": {"color": A, "fontSize": 11, "fontWeight": 600, "offsetY": -45,
                   "background": "rgba(239,68,68,0.08)"}},
        {"type": "point", "data_index": 2,
         "text": "Mature: 4.5%",
         "style": {"color": G, "fontSize": 11, "fontWeight": 600, "offsetY": -45,
                   "background": "rgba(16,185,129,0.08)"}}
    ],
    "callout": "So what: Early-tenure customers churn at 35.2% — 8x the 4.5% mature rate; onboarding is the intervention point.",
    "config": STD_CONFIG
})

# 4. plan_tenure_heatmap
d = chart_reqs["plan_tenure_heatmap"]["data"]
charts.append({
    "chart_id": "plan_tenure_heatmap",
    "chart_type": "heatmap",
    "title": "Basic+Early cohort (46.2%) is 10x worse than Mature Enterprise (0.9%)",
    "subtitle": "Churn rate by plan x tenure band (%)",
    "data": {
        "rows": d["rows"],
        "cols": d["cols"],
        "values": d["values"],
        "colormap": "Reds",
        "highlight_cell": {"row": 0, "col": 0}
    },
    "annotations": [
        {"type": "point", "data_index": 0,
         "text": "Hotspot: 46.2%",
         "style": {"color": "#FFFFFF", "fontSize": 12, "fontWeight": 700,
                   "background": "rgba(239,68,68,0.15)"}}
    ],
    "callout": "So what: Basic+Early at 46.2% is the single highest-risk cell — nearly 1 in 2 new Basic customers lost.",
    "config": {**STD_CONFIG, "height": 350}
})

# 5. churned_mrr_vs_count_bar
d = chart_reqs["churned_mrr_vs_count_bar"]["data"]
charts.append({
    "chart_id": "churned_mrr_vs_count_bar",
    "chart_type": "grouped_bar",
    "title": "Enterprise is 5.9% of churns but 51% of churned MRR — two very different risks",
    "subtitle": "% of churned customers vs % of churned MRR by plan",
    "data": {
        "labels": d["categories"],
        "series": [
            {"name": g["name"], "values": g["values"],
             "color": H if g["highlight"] else N, "value_format": "%"}
            for g in d["groups"]
        ]
    },
    "annotations": [
        {"type": "span", "data_index": 2,
         "text": "Enterprise: $828/churn vs $34 for Basic",
         "style": {"color": H, "fontSize": 11, "fontWeight": 600,
                   "background": "rgba(37,84,231,0.08)"}}
    ],
    "callout": "So what: Enterprise produces 51% of churned MRR from only 5.9% of churned customers at $828 per loss.",
    "config": STD_CONFIG
})

# 6. region_churn_rate_bar
d = chart_reqs["region_churn_rate_bar"]["data"]
charts.append({
    "chart_id": "region_churn_rate_bar",
    "chart_type": "vertical_bar",
    "title": "All regions within 2.7pp of each other — geography is not a churn driver",
    "subtitle": "Churn rate by region; reference = 14.2% overall",
    "data": {
        "labels": d["categories"],
        "series": [{"name": "Churn Rate %", "values": d["values"],
                    "colors": [N, N, N, N], "value_format": "%"}],
        "reference_line": {"value": 14.2, "label": "Overall 14.2%"}
    },
    "annotations": [
        {"type": "span", "data_index": 0,
         "text": "Max gap 2.7pp — below 5pp materiality threshold",
         "style": {"color": N, "fontSize": 11, "fontWeight": 600,
                   "background": "rgba(209,213,219,0.08)"}}
    ],
    "callout": "So what: No region exceeds the average by more than 1.3pp — region is ruled out as a driver.",
    "config": STD_CONFIG
})

# 7. model_comparison_bar
d = chart_reqs["model_comparison_bar"]["data"]
charts.append({
    "chart_id": "model_comparison_bar",
    "chart_type": "model_comparison_bar",
    "title": "Logistic Regression leads at ROC-AUC 0.69 — 38% above naive baseline",
    "subtitle": "ROC-AUC comparison; naive baseline = 0.50",
    "data": {
        "labels": d["models"],
        "series": [{"name": "ROC-AUC", "values": d["scores"],
                    "colors": [H, N, N, A], "value_format": "2dp"}],
        "reference_line": {"value": 0.5, "label": "Naive baseline 0.50"}
    },
    "annotations": [
        {"type": "point", "data_index": 0,
         "text": "Best: LR AUC 0.69 (+38% vs baseline)",
         "style": {"color": H, "fontSize": 11, "fontWeight": 600, "offsetY": -45,
                   "background": "rgba(37,84,231,0.08)"}}
    ],
    "callout": "So what: Logistic Regression (AUC 0.69) identifies 806 high-risk customers carrying $49K MRR.",
    "config": STD_CONFIG
})

# 8. feature_importance_bar
d = chart_reqs["feature_importance_bar"]["data"]
charts.append({
    "chart_id": "feature_importance_bar",
    "chart_type": "feature_importance",
    "title": "Tenure and plan explain 88% of churn prediction power — confirming root cause",
    "subtitle": "Logistic Regression coefficient magnitude (top 5 features)",
    "data": {
        "labels": d["features"],
        "series": [{"name": "Importance", "values": d["importances"],
                    "colors": [H, H, N, N, N], "value_format": "2dp"}]
    },
    "annotations": [
        {"type": "point", "data_index": 0,
         "text": "tenure_months: 0.89 (strongest predictor)",
         "style": {"color": H, "fontSize": 11, "fontWeight": 600, "offsetY": -45,
                   "background": "rgba(37,84,231,0.08)"}}
    ],
    "callout": "So what: Tenure (0.89) and plan (0.62) together drive 88% of prediction power — matching diagnostic findings.",
    "config": {**STD_CONFIG, "height": 350}
})

out = {
    "generated_at": datetime.now().isoformat(),
    "stem": "subscription_saas",
    "total_charts": len(charts),
    "charts": charts
}

out_path = PIPE / "chart_specs.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"chart_specs.json written: {len(charts)} charts")
for c in charts:
    print(f"  [{c['chart_type']:28s}] {c['chart_id']}")
