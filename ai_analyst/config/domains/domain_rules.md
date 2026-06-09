# Domain-Specific KPI Rules & Heuristics

This file defines domain-specific business rules for analysis.
The orchestrator auto-detects the domain from column names and applies
the matching rules for validation, analysis, and reporting.

---

## SaaS / Revenue

**Detection signals:** mrr, arr, churn_rate, ltv, expansion, nrr, subscription,
  churn, tenure, tenure_months, plan, status, monthly_revenue

**Fiscal Year:**
- Default: calendar year (Jan 1 – Dec 31)
- Cohort anchor: `signup_date` month → monthly cohort buckets
- Tenure bands: Early (0–6 mo), Growth (7–24 mo), Mature (25+ mo)

**KPIs:**
- mrr/arr → direction: up_is_good, alert if -15% MoM
- churn_rate → direction: down_is_good, alert if >15% overall; >10% for Enterprise tier
- revenue_at_risk → direction: down_is_good; = MRR of active customers predicted to churn
- expansion_rate → direction: up_is_good, alert if <5%
- NRR → direction: up_is_good, alert if <100%
- LTV → direction: up_is_good, alert if declining 3 consecutive months
- CAC payback → direction: down_is_good, alert if >18 months
- tenure_months → direction: up_is_good; median tenure < 12 mo signals early churn risk

**Data Type Heuristic:**
- If dataset is customer-level snapshot (one row per customer, no period column):
  → MRR time-series forecast NOT applicable
  → Use churn classification as primary predictive task
  → MRR analysis: segment totals only (by plan, region, tenure band)
- If dataset has monthly/period rows per customer:
  → Full MRR waterfall + time-series forecast applicable

**Waterfall:**
Baseline MRR → New Business → Expansion → Contraction → Churned → Net MRR
(snapshot datasets: replace with MRR breakdown by Plan × Region × Status)

**Segments:**
- Plan tier (ordered): Basic < Pro < Enterprise
- Region: APAC, EMEA, Americas
- Tenure band: Early (0–6 mo), Growth (7–24 mo), Mature (25+ mo)
- Cohort: signup_date truncated to month (YYYY-MM)
- Status: Active vs Churned

**Data Quality Rules:**
- Flag `monthly_revenue < 0` as anomaly (possible refund/adjustment — exclude from MRR sum)
- Standardize churn column if mixed encoding detected (Yes/No + 1/0 → binary int 0/1)
- `churn` and `status` are redundant; use `churn` as classification target

**Hypothesis templates:**
- Product feature change → reduced usage → churn
- Pricing change → objection → downgrade/churn
- Macro environment → budget cuts → delayed expansion
- Onboarding failure → low activation → early churn (tenure < 3 mo cohort)
- Support quality → frustration → at-risk accounts
- Plan mismatch → Basic customers outgrowing tier → upgrade or churn

**Ruling-out heuristics:**
- Enterprise stable → not macro (would hit largest first)
- Acquisition on-target → churn not top-of-funnel issue
- Feature usage flat → not product regression
- Churn concentrated in low-tenure cohorts → onboarding issue, not product-market fit

---

## E-commerce

**Detection signals:** orders, revenue, aov, cart, conversion, gmv, items_sold

**KPIs:**
- revenue → direction: up_is_good, alert if -20% MoM
- aov → direction: up_is_good, alert if -10% MoM
- conversion_rate → direction: up_is_good, alert if <1%
- cart_abandonment → direction: down_is_good, alert if >75%
- return_rate → direction: down_is_good, alert if >15%

**Waterfall:**
Sessions → Add-to-Cart → Checkout Started → Payment → Completed Order

**Segments:**
New vs Returning, Device (mobile/desktop), Channel (organic/paid/direct), Category

**Hypothesis templates:**
- Site speed regression → higher bounce → lower conversion
- Promotion ended → reduced traffic → revenue drop
- Inventory stockout → forced substitution → lower AOV
- Payment gateway issue → checkout failure → lost orders
- Seasonal pattern → expected cyclicality

**Ruling-out heuristics:**
- Traffic stable → not awareness issue
- Conversion stable → not UX/checkout issue
- AOV stable → not pricing/mix issue

---

## Marketing

**Detection signals:** cac, cpl, roas, impressions, spend, clicks, ctr, cpm

**KPIs:**
- ROAS → direction: up_is_good, alert if <2.0
- CAC → direction: down_is_good, alert if >$150
- CPL → direction: down_is_good, alert if +25% MoM
- CTR → direction: up_is_good, alert if <0.5%
- Conversion rate → direction: up_is_good, alert if <2%

**Waterfall:**
Impressions → Clicks → Leads → MQLs → SQLs → Closed Won

**Segments:**
Channel (search/social/display/email), Campaign, Audience, Geo

**Hypothesis templates:**
- Creative fatigue → declining CTR → higher CPC
- Audience saturation → frequency too high → diminishing returns
- Competitor bid increase → higher CPM → lower ROAS
- Landing page change → conversion drop → higher CAC
- Attribution model change → apparent metric shift

---

## Finance

**Detection signals:** net_profit, margin, opex, capex, ebitda, cash_flow

**KPIs:**
- net_profit → direction: up_is_good, alert if negative
- gross_margin → direction: up_is_good, alert if <30%
- operating_margin → direction: up_is_good, alert if declining 3 consecutive quarters
- opex_ratio → direction: down_is_good, alert if >70%
- cash_flow → direction: up_is_good, alert if negative 2 consecutive months

**Waterfall:**
Revenue → COGS → Gross Profit → OpEx → EBITDA → Tax → Net Profit

**Segments:**
Business Unit, Cost Center, Region, Product Line

---

## Operations / Logistics

**Detection signals:** fulfillment, shipping, delivery_time, on_time, warehouse

**KPIs:**
- on_time_rate → direction: up_is_good, alert if <95%
- delivery_days → direction: down_is_good, alert if >5
- fulfillment_cost → direction: down_is_good, alert if +15% MoM
- return_rate → direction: down_is_good, alert if >10%
- inventory_turnover → direction: up_is_good, alert if <4x/year

**Segments:**
Warehouse, Carrier, Region, Product Category, Priority Level

---

## Product / Usage

**Detection signals:** dau, mau, retention, feature_usage, session, activation

**KPIs:**
- DAU/MAU ratio → direction: up_is_good, alert if <20%
- retention_d7 → direction: up_is_good, alert if <30%
- retention_d30 → direction: up_is_good, alert if <15%
- activation_rate → direction: up_is_good, alert if <40%
- session_duration → direction: up_is_good (with cap), alert if <2min or >60min

**Waterfall:**
Sign-ups → Activated → Day 1 Active → Day 7 Active → Day 30 Active → Power Users

**Segments:**
Platform (iOS/Android/Web), Cohort, Plan tier, User persona

**Hypothesis templates:**
- New release bug → crash rate → session drop
- Feature removed → power user frustration → churn
- Onboarding change → activation rate shift
- Competitor launch → organic decline

---

## HR / People

**Detection signals:** headcount, attrition, tenure, salary, engagement, hire

**KPIs:**
- attrition_rate → direction: down_is_good, alert if >20% annual
- engagement_score → direction: up_is_good, alert if <3.5/5
- time_to_fill → direction: down_is_good, alert if >45 days
- offer_acceptance → direction: up_is_good, alert if <80%
- diversity_ratio → direction: up_is_good (context-dependent)

**Segments:**
Department, Level, Tenure band, Location, Gender

---

## Generic (Fallback)

**Detection signals:** (none — used when no specific domain matches)

**KPIs:**
- First numeric column → primary metric, direction inferred from name
- Second numeric column → secondary metric

**Segments:**
First categorical column with <20 unique values

**Behavior:**
- Skip domain-specific hypothesis templates
- Use generic trend/change detection
- Apply standard statistical tests without domain priors
