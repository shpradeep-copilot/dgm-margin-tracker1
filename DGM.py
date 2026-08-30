import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from groq import Groq
import os
import json
from pathlib import Path
from typing import List

# 1. Page Configuration
st.set_page_config(
    page_title="Tenarai DGM Margin & AI Insight Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Executive Light System Theme Styling
st.markdown("""
<style>
    /* Google Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main App Light Background */
    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }

    /* Ensure Dark Text Color for High Readability */
    p, span, label, h1, h2, h3, h4, h5, h6, li {
        color: #0F172A !important;
    }

    .stMarkdown, .stMarkdown p {
        color: #1E293B !important;
    }

    /* Sidebar Light Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] p {
        color: #0F172A !important;
    }
    
    /* Hero Banner Header (Light Crisp Gradient with Deep Contrast Accent) */
    .hero-header {
        background: linear-gradient(135deg, #EFF6FF 0%, #EEF2FF 50%, #F0F9FF 100%) !important;
        border: 1px solid #C7D2FE !important;
        padding: 26px 32px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px -2px rgba(99, 102, 241, 0.1);
    }
    
    .hero-title {
        font-size: 28px;
        font-weight: 800;
        color: #1E1B4B !important;
        margin-bottom: 6px;
        display: block;
    }
    
    .hero-subtitle {
        color: #475569 !important;
        font-size: 15px;
        font-weight: 500;
        line-height: 1.5;
    }

    /* Custom Metric Cards (Light Clean Surface) */
    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px;
        padding: 16px 20px;
        min-height: 116px;
        height: 116px;
        box-sizing: border-box;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        border-color: #6366F1 !important;
        transform: translateY(-2px);
    }

    div[data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #4F46E5 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* AI Executive Box */
    .ai-box {
        background-color: #FFFFFF !important;
        border: 1px solid #0284C7 !important;
        border-left: 6px solid #0284C7 !important;
        padding: 24px;
        border-radius: 12px;
        margin-top: 20px;
        color: #0F172A !important;
        box-shadow: 0 4px 16px rgba(2, 132, 199, 0.08);
        line-height: 1.6;
    }
    
    .ai-box p, .ai-box li, .ai-box h1, .ai-box h2, .ai-box h3, .ai-box h4 {
        color: #0F172A !important;
    }

    /* Keep the copilot transcript visually contained like a standard chat panel. */
    .copilot-window {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px 6px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
        margin-bottom: 16px;
    }

    .copilot-window [data-testid="stChatMessage"] {
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 12px;
    }

    /* Expander Container */
    .stExpander {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
    }

    /* Dataframe Styling Accent */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
    }

    /* Keep table headers legible across dataframe and editable table views. */
    div[data-testid="stDataFrame"] [role="columnheader"],
    div[data-testid="stDataFrame"] th,
    div[data-testid="stDataEditor"] [role="columnheader"],
    div[data-testid="stDataEditor"] th {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 12px 24px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%) !important;
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.35);
    }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar Configuration
st.sidebar.markdown("<h2 style='color:#0F172A; font-weight:800;'>⚡ DGM Control Center</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

api_key = None
if "groq_api_key" in st.secrets:
    api_key = st.secrets["groq_api_key"]
else:
    api_key = st.sidebar.text_input("🔑 Groq API Key", type="password", help="Get free key from https://console.groq.com/keys")

uploaded_file = st.sidebar.file_uploader("📂 Upload Excel / CSV Data Sheet", type=["xlsx", "csv"])

st.sidebar.markdown("---")
st.sidebar.markdown("<h4 style='color:#475569;'>⚙️ Target & What-If Controls</h4>", unsafe_allow_html=True)

TARGET_MARGIN_DEFAULT = 58
TARGET_MARGIN_MIN = 30
TARGET_MARGIN_MAX = 80
INDIA_LOAD_FACTOR_DEFAULT = 1.11
ONSITE_LOAD_FACTOR_DEFAULT = 1.25
INR_PER_USD_DEFAULT = 92.0
PROPOSED_RATE_INCREASE_DEFAULT = 0
TARGET_MARGIN_CACHE = Path(__file__).parent / ".streamlit" / "target_dgm_cache.json"


def load_target_margin():
    try:
        cached_value = json.loads(TARGET_MARGIN_CACHE.read_text(encoding="utf-8")).get("target_margin")
        if TARGET_MARGIN_MIN <= int(cached_value) <= TARGET_MARGIN_MAX:
            return int(cached_value)
    except (FileNotFoundError, OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        pass
    return TARGET_MARGIN_DEFAULT


def save_target_margin():
    try:
        TARGET_MARGIN_CACHE.parent.mkdir(parents=True, exist_ok=True)
        TARGET_MARGIN_CACHE.write_text(
            json.dumps({"target_margin": st.session_state.target_margin_threshold}),
            encoding="utf-8"
        )
    except OSError:
        pass


def reset_parameters():
    st.session_state.target_margin_threshold = TARGET_MARGIN_DEFAULT
    st.session_state.proposed_rate_increase = PROPOSED_RATE_INCREASE_DEFAULT
    st.session_state.india_load_factor = INDIA_LOAD_FACTOR_DEFAULT
    st.session_state.onsite_load_factor = ONSITE_LOAD_FACTOR_DEFAULT
    st.session_state.inr_per_usd = INR_PER_USD_DEFAULT
    save_target_margin()


if "target_margin_threshold" not in st.session_state:
    st.session_state.target_margin_threshold = load_target_margin()

st.sidebar.button("Reset Parameters", on_click=reset_parameters, use_container_width=True)

st.sidebar.slider(
    "Target DGM %",
    min_value=TARGET_MARGIN_MIN,
    max_value=TARGET_MARGIN_MAX,
    key="target_margin_threshold",
    on_change=save_target_margin
)
target_margin_threshold = st.session_state.target_margin_threshold
proposed_rate_increase = st.sidebar.slider(
    "Simulate Account Rate Increase %",
    min_value=0,
    max_value=30,
    value=PROPOSED_RATE_INCREASE_DEFAULT,
    key="proposed_rate_increase"
)
inr_per_usd = st.sidebar.number_input(
    "INR per USD Exchange Rate",
    min_value=1.0,
    value=INR_PER_USD_DEFAULT,
    step=0.5,
    key="inr_per_usd"
)
india_load_factor = st.sidebar.number_input(
    "India CTC Load Factor",
    min_value=1.0,
    max_value=3.0,
    value=INDIA_LOAD_FACTOR_DEFAULT,
    step=0.01,
    key="india_load_factor",
    help="Multiplier applied to India-based CTC to account for employment overheads."
)
onsite_load_factor = st.sidebar.number_input(
    "Onsite CTC Load Factor",
    min_value=1.0,
    max_value=3.0,
    value=ONSITE_LOAD_FACTOR_DEFAULT,
    step=0.01,
    key="onsite_load_factor",
    help="Multiplier applied to onsite CTC to account for employment overheads."
)

# Hero Header Banner
st.markdown("""
<div class="hero-header">
    <span class="hero-title">📊 DGM Margin & AI Insight Engine</span>
    <div class="hero-subtitle">Track account/project profitability, simulate rate increases, and generate AI-driven root cause analyses.</div>
</div>
""", unsafe_allow_html=True)

def validate_numeric_column(series, col_name: str, allow_negative: bool = False) -> pd.Series:
    numeric_series = pd.to_numeric(series, errors='coerce')
    if not allow_negative:
        numeric_series = numeric_series.clip(lower=0)
    return numeric_series


def format_currency_columns(df_style, currency_cols: List[str], pct_cols: List[str] = None):
    format_dict = {col: '${:,.2f}' for col in currency_cols if col in df_style.data.columns}
    if pct_cols:
        format_dict.update({col: '{:.2f}%' for col in pct_cols if col in df_style.data.columns})
    return df_style.format(format_dict)


def style_table_headers(df_style):
    return df_style.set_table_styles([
        {
            'selector': 'th',
            'props': [('color', '#000000'), ('font-weight', '800')]
        }
    ])


def show_quantified_gap(scope_label, revenue, cost, average_rate, target_margin):
    target_ratio = target_margin / 100
    current_margin = ((revenue - cost) / revenue * 100) if revenue > 0 else 0
    revenue_target = cost / (1 - target_ratio) if target_ratio < 1 else 0
    revenue_shortfall = max(revenue_target - revenue, 0)
    required_hours = revenue_shortfall / average_rate if average_rate > 0 else 0

    if revenue_shortfall <= 0:
        st.success(f"✨ **{scope_label}** is operating at **{current_margin:.2f}%**, above the **{target_margin:.0f}%** target floor.")
        return

    st.markdown(f"""
    <div style="background: #FEF2F2; border: 1px solid #FCA5A5; border-radius: 12px; padding: 20px; margin-top: 15px; color: #991B1B;">
        <h4 style="color: #991B1B; margin-top:0;">📐 Quantified Margin Deficit Gap</h4>
        <p style="color: #1E293B; margin-bottom: 8px;"><b>Target Revenue for {target_margin:.0f}% Margin:</b> ${revenue_target:,.2f} / month</p>
        <p style="color: #1E293B; margin-bottom: 8px;"><b>Monthly Revenue Shortfall:</b> <span style="color:#DC2626; font-weight:700;">${revenue_shortfall:,.2f}</span> / month</p>
        <p style="color: #1E293B; margin-bottom: 8px;"><b>Equivalent Billable Hours Needed:</b> {required_hours:,.1f} hrs @ current avg rate</p>
        <p style="color: #64748B; font-size:13px; margin-top:10px; margin-bottom:0;"><i>Bottom line: {scope_label} is {abs(current_margin - target_margin):,.2f}% below the floor, requiring a ${revenue_shortfall:,.2f}/mo gap recovery.</i></p>
    </div>
    """, unsafe_allow_html=True)

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
            selected_sheet = "Sheet1"
        else:
            xl = pd.ExcelFile(uploaded_file)
            sheet_names = xl.sheet_names
            selected_sheet = st.sidebar.selectbox("Select Sheet Tab:", sheet_names) if len(sheet_names) > 1 else sheet_names[0]
            df_raw = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        
        if df_raw.empty:
            st.error("❌ Uploaded file is empty. Please verify your spreadsheet.")
            st.stop()
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.stop()

    df = df_raw.copy()
    df.columns = df.columns.astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()

    def find_col(candidates, columns):
        for cand in candidates:
            for c in columns:
                if cand.lower() in c.lower():
                    return c
        return None

    cols = df.columns.tolist()
    sow_col = find_col(['sow'], cols)
    name_col = find_col(['name', 'candidate', 'resource'], cols)
    role_col = find_col(['resource role', 'role', 'designation'], cols)
    rate_col = find_col(['bill rate (usd/hr)', 'rate $/hr', 'bill rate', 'client rate'], cols)
    hrs_col = find_col(['billable hrs/month', 'billable hours/month', 'hrs/month'], cols)
    ctc_col = find_col(['current ctc'], cols)
    location_col = find_col(['location'], [c for c in cols if 'allocation' not in c.lower()])
    ctc_currency_col = find_col(['ctc currency'], cols)

    if not sow_col or not rate_col or not hrs_col or not ctc_col:
        st.error("❌ Required columns not found. Ensure sheet includes **'SOW'**, **'Bill Rate'**, **'Billable Hrs'**, and **'Current CTC'**.")
        st.stop()
    else:
        df = df.dropna(subset=[sow_col]).reset_index(drop=True).copy()
        
        df[rate_col] = validate_numeric_column(df[rate_col], rate_col, allow_negative=False)
        df[ctc_col] = validate_numeric_column(df[ctc_col], ctc_col, allow_negative=False)

        is_india_loc = df[location_col].astype(str).str.strip().str.upper().str.contains('INDIA', na=False) if (location_col and location_col in df.columns) else pd.Series(False, index=df.index)
        is_india_curr = df[ctc_currency_col].astype(str).str.strip().str.upper().str.contains('INR', na=False) if (ctc_currency_col and ctc_currency_col in df.columns) else pd.Series(False, index=df.index)
        is_india = is_india_loc | is_india_curr
        
        df['CTC_Load_Factor'] = is_india.map({True: india_load_factor, False: onsite_load_factor})
        df['Exchange_Denominator'] = is_india.map({True: inr_per_usd, False: 1.0})
        
        df[hrs_col] = validate_numeric_column(df[hrs_col], hrs_col, allow_negative=False).fillna(164.3)
        if (df[hrs_col] <= 0).any():
            st.error("❌ Billable Hrs/Month must be greater than zero.")
            st.stop()
        
        df['Hourly_Cost'] = (
            df[ctc_col] * df['CTC_Load_Factor'] /
            (df[hrs_col] * 12 * df['Exchange_Denominator'])
        )
        df['Monthly_Cost'] = df['Hourly_Cost'] * df[hrs_col]

        df['Current_Monthly_Revenue'] = df[rate_col] * df[hrs_col]
        df['Simulated_Rate'] = df[rate_col] * (1 + proposed_rate_increase / 100)
        df['Simulated_Monthly_Revenue'] = df['Simulated_Rate'] * df[hrs_col]
        
        df['Current_DGM%'] = ((df[rate_col] - df['Hourly_Cost']) / df[rate_col].replace(0, pd.NA) * 100).fillna(0)
        df['Simulated_DGM%'] = ((df['Simulated_Rate'] - df['Hourly_Cost']) / df['Simulated_Rate'].replace(0, pd.NA) * 100).fillna(0)
        
        # Global Portfolio Aggregations (Available across both Overall and Single SOW views)
        tot_revenue = df['Current_Monthly_Revenue'].sum()
        sim_revenue = df['Simulated_Monthly_Revenue'].sum()
        tot_cost = df['Monthly_Cost'].sum()
        curr_account_dgm = ((tot_revenue - tot_cost) / tot_revenue * 100) if tot_revenue > 0 else 0
        sim_account_dgm = ((sim_revenue - tot_cost) / sim_revenue * 100) if sim_revenue > 0 else 0
        
        st.sidebar.success(f"✅ Ingested {len(df)} billable roles ({selected_sheet})")

        sow_list = sorted(df[sow_col].astype(str).unique().tolist())
        view_mode = st.radio("🔍 Select Analysis Scope:", ["Overall Account View", "Single Project (SOW) View"], horizontal=True)
        selected_sow = None
        if view_mode == "Single Project (SOW) View":
            selected_sow = st.selectbox("Select SOW / Project:", sow_list)

        active_scope = df if view_mode == "Overall Account View" else df[df[sow_col].astype(str) == selected_sow]
        scope_label = "Overall Account" if view_mode == "Overall Account View" else f"Project {selected_sow}"
        scope_revenue = active_scope['Current_Monthly_Revenue'].sum()
        scope_cost = active_scope['Monthly_Cost'].sum()
        scope_dgm = ((scope_revenue - scope_cost) / scope_revenue * 100) if scope_revenue > 0 else 0
        copilot_scope_key = f"{view_mode}:{selected_sow or 'all'}"

        salary_sow_default = sow_list if view_mode == "Overall Account View" else [selected_sow]
        salary_filter_key = f"salary_adjustment_sow_filter_{view_mode}_{selected_sow or 'account'}"
        salary_sows = st.sidebar.multiselect(
            "Salary Adjustment SOW Filter",
            sow_list,
            default=salary_sow_default,
            key=salary_filter_key
        )
        salary_scope_df = df[df[sow_col].astype(str).isin(salary_sows)]

        def get_salary_adjustments():
            with st.expander("💰 Edit Resource Salary Adjustments"):
                st.caption("Enter annual CTC increases in the resource's source currency. USD is used for margin calculations.")
                salary_editor_df = salary_scope_df[[sow_col] + [c for c in [name_col, role_col, location_col] if c]].copy()
                if ctc_currency_col and ctc_currency_col in salary_scope_df.columns:
                    salary_editor_df['CTC Currency'] = salary_scope_df[ctc_currency_col]
                salary_editor_df['Current Annual CTC'] = salary_scope_df[ctc_col]
                salary_editor_df['Annual CTC Increase'] = 0.0
                salary_editor_df = st.data_editor(
                    salary_editor_df,
                    use_container_width=True,
                    hide_index=True,
                    disabled=[c for c in salary_editor_df.columns if c not in ['Annual CTC Increase']],
                    column_config={
                        'Current Annual CTC': st.column_config.NumberColumn(
                            'Current Annual CTC', format='%,.2f'
                        ),
                        'Annual CTC Increase': st.column_config.NumberColumn(
                            'Annual CTC Increase', min_value=0.0, max_value=1000000.0, step=100.0, format='%,.2f'
                        ),
                    },
                    key="salary_adjustment_editor_location_currency_v2"
                )
            annual_increases = pd.Series(0.0, index=df.index)
            annual_increases.loc[salary_editor_df.index] = pd.to_numeric(
                salary_editor_df['Annual CTC Increase'], errors='coerce'
            ).fillna(0).clip(lower=0, upper=1000000)
            return annual_increases, annual_increases[annual_increases > 0].index

        def show_salary_adjustment_table(annual_increases):
            adjustment_df = salary_scope_df[
                [sow_col] + [c for c in [name_col, role_col, location_col, ctc_currency_col] if c]
            ].copy()
            adjustment_df['Current Annual CTC'] = df.loc[adjustment_df.index, ctc_col]
            adjustment_df['Annual CTC Increase'] = annual_increases.loc[adjustment_df.index]
            adjustment_df['Adjusted Annual CTC'] = (
                adjustment_df['Current Annual CTC'] + adjustment_df['Annual CTC Increase']
            )
            adjustment_df['Adjusted Cost (USD/hr)'] = df.loc[
                adjustment_df.index, 'Salary_Adjusted_Cost'
            ]
            adjustment_df['Adjusted DGM%'] = df.loc[
                adjustment_df.index, 'Salary_Adjusted_DGM%'
            ]
            adjustment_df = adjustment_df.reset_index(drop=True)
            currency_format = {
                'Current Annual CTC': '{:,.2f}',
                'Annual CTC Increase': '{:,.2f}',
                'Adjusted Annual CTC': '{:,.2f}',
                'Adjusted Cost (USD/hr)': '${:,.2f}',
                'Adjusted DGM%': '{:.2f}%'
            }
            with st.expander("📋 View Post-Adjustment Resource CTC and Margin"):
                st.dataframe(
                    style_table_headers(adjustment_df.style.format(currency_format)),
                    use_container_width=True,
                    hide_index=True
                )

        if view_mode == "Overall Account View":
            st.markdown("<h3 style='color:#0F172A;'>🌐 Consolidated Account Metrics</h3>", unsafe_allow_html=True)

            with st.expander("🔎 View Granular Resource Formula Breakdown"):
                calculation_details = df[
                    [c for c in [name_col, location_col, ctc_currency_col, ctc_col, hrs_col, rate_col,
                                 'CTC_Load_Factor', 'Exchange_Denominator',
                                 'Hourly_Cost', 'Current_DGM%'] if c]
                ].copy()
                calculation_details = calculation_details.rename(columns={
                    'CTC_Load_Factor': 'Location Load Factor',
                    'Exchange_Denominator': 'Exchange Denominator',
                    ctc_col: 'Current CTC (Source Currency)',
                    'Hourly_Cost': 'Calculated Cost (USD/hr)',
                    'Current_DGM%': 'Calculated DGM %'
                })
                st.dataframe(
                    style_table_headers(calculation_details.style),
                    use_container_width=True,
                    hide_index=True
                )
            
            six_month_revenue = tot_revenue * 6
            yearly_revenue = tot_revenue * 12
            billable_headcount = len(df)

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("6-Month Revenue", f"${six_month_revenue:,.2f}", delta=f"+${(sim_revenue - tot_revenue) * 6:,.2f} Hike" if proposed_rate_increase > 0 else None)
            c2.metric("Yearly Revenue", f"${yearly_revenue:,.2f}")
            c3.metric("Monthly Cost", f"${tot_cost:,.2f}")
            c4.metric("Current Account DGM %", f"{curr_account_dgm:.2f}%", delta=f"{sim_account_dgm - curr_account_dgm:+.2f}% Hike" if proposed_rate_increase > 0 else f"{curr_account_dgm - target_margin_threshold:.1f}% vs Floor")
            c5.metric("Billable Headcount", f"{billable_headcount} Roles")

            salary_ctc_increases, salary_adjustment_indices = get_salary_adjustments()
            salary_hourly_increase = (
                salary_ctc_increases * df['CTC_Load_Factor'] /
                (df[hrs_col] * 12 * df['Exchange_Denominator'])
            )
            df['Salary_Adjusted_Monthly_Cost'] = df['Monthly_Cost'] + salary_hourly_increase * df[hrs_col]
            df['Salary_Cost_Increase'] = salary_hourly_increase * df[hrs_col]
            df['Salary_Adjusted_Cost'] = df['Hourly_Cost'] + salary_hourly_increase
            df['Salary_Adjusted_DGM%'] = (
                (df[rate_col] - df['Salary_Adjusted_Cost']) /
                df[rate_col].replace(0, pd.NA) * 100
            ).fillna(0)
            adjusted_tot_cost = df['Salary_Adjusted_Monthly_Cost'].sum()
            salary_account_cost_increase = adjusted_tot_cost - tot_cost

            if len(salary_adjustment_indices) > 0:
                st.subheader("💰 Salary Adjustment Impact Summary")
                salary_c1, salary_c2, salary_c3 = st.columns(3)
                salary_c1.metric("Adjusted Monthly Cost", f"${adjusted_tot_cost:,.2f}", delta=f"+${salary_account_cost_increase:,.2f}")
                salary_c2.metric("Adjusted Monthly Margin $", f"${tot_revenue - adjusted_tot_cost:,.2f}", delta=f"-${salary_account_cost_increase:,.2f}")
                adjusted_account_dgm = ((tot_revenue - adjusted_tot_cost) / tot_revenue * 100) if tot_revenue > 0 else 0
                salary_c3.metric("Adjusted Account DGM %", f"{adjusted_account_dgm:.2f}%", delta=f"{adjusted_account_dgm - curr_account_dgm:+.2f}%")
                show_salary_adjustment_table(salary_ctc_increases)

            show_quantified_gap("The Account Portfolio", tot_revenue, tot_cost, df[rate_col].mean(), target_margin_threshold)

            sow_summary = df.groupby(sow_col).agg(
                Headcount=(rate_col, 'count'),
                Current_Monthly_Revenue=('Current_Monthly_Revenue', 'sum'),
                Simulated_Revenue=('Simulated_Monthly_Revenue', 'sum'),
                Monthly_Cost=('Monthly_Cost', 'sum'),
                Avg_Bill_Rate=(rate_col, 'mean'),
                Avg_Simulated_Rate=('Simulated_Rate', 'mean')
            ).reset_index()

            sow_summary['Current_DGM%'] = ((sow_summary['Current_Monthly_Revenue'] - sow_summary['Monthly_Cost']) / sow_summary['Current_Monthly_Revenue'] * 100).fillna(0)
            sow_summary['Simulated_DGM%'] = ((sow_summary['Simulated_Revenue'] - sow_summary['Monthly_Cost']) / sow_summary['Simulated_Revenue'] * 100).fillna(0) if proposed_rate_increase > 0 else sow_summary['Current_DGM%']

            col_chart, col_impact = st.columns([2, 1])
            
            with col_chart:
                st.subheader("📈 SOW Profitability Visualizer")
                if proposed_rate_increase > 0:
                    fig = px.bar(
                        sow_summary, x=sow_col, y=['Current_DGM%', 'Simulated_DGM%'],
                        barmode='group',
                        title=f"Baseline vs {proposed_rate_increase}% Rate Hike",
                        template="plotly_white",
                        color_discrete_sequence=['#6366F1', '#38BDF8']
                    )
                else:
                    fig = px.bar(
                        sow_summary, x=sow_col, y='Current_DGM%', color='Current_DGM%',
                        color_continuous_scale='RdYlGn', range_color=[30, 80],
                        title="DGM Margin % by Project",
                        template="plotly_white"
                    )
                fig.add_hline(y=target_margin_threshold, line_dash="dash", line_color="#EF4444", annotation_text="Target Floor")
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True, height=450)

            with col_impact:
                if proposed_rate_increase > 0:
                    st.subheader("💡 Simulated Hike Impact")
                    sim_revenue = df['Simulated_Monthly_Revenue'].sum()
                    sim_yearly_revenue = sim_revenue * 12
                    sim_account_dgm = ((sim_revenue - tot_cost) / sim_revenue * 100) if sim_revenue > 0 else 0
                    revenue_increase = sim_revenue - tot_revenue
                    yearly_increase = revenue_increase * 12
                    dgm_improvement = sim_account_dgm - curr_account_dgm

                    st.metric("Simulated Monthly Revenue", f"${sim_revenue:,.2f}", delta=f"+${revenue_increase:,.2f}")
                    st.metric("Simulated Yearly Revenue", f"${sim_yearly_revenue:,.2f}", delta=f"+${yearly_increase:,.2f}")
                    st.metric("Simulated DGM %", f"{sim_account_dgm:.2f}%", delta=f"{dgm_improvement:+.2f}%")

            st.markdown("---")

            st.subheader("📋 SOW Performance Ledger")
            sow_summary.index = range(1, len(sow_summary) + 1)
            
            if proposed_rate_increase > 0:
                display_cols = [sow_col, 'Headcount', 'Current_Monthly_Revenue', 'Simulated_Revenue', 'Monthly_Cost', 'Avg_Bill_Rate', 'Avg_Simulated_Rate', 'Current_DGM%', 'Simulated_DGM%']
                display_df = sow_summary[display_cols].copy()
                styled_summary = style_table_headers(display_df.style.format({
                    'Current_Monthly_Revenue': '${:,.2f}',
                    'Simulated_Revenue': '${:,.2f}',
                    'Monthly_Cost': '${:,.2f}',
                    'Avg_Bill_Rate': '${:,.2f}',
                    'Avg_Simulated_Rate': '${:,.2f}',
                    'Current_DGM%': '{:.2f}%',
                    'Simulated_DGM%': '{:.2f}%'
                }))
            else:
                display_cols = [sow_col, 'Headcount', 'Current_Monthly_Revenue', 'Monthly_Cost', 'Avg_Bill_Rate', 'Current_DGM%']
                display_df = sow_summary[display_cols].copy()
                styled_summary = style_table_headers(format_currency_columns(
                    display_df.style,
                    currency_cols=['Current_Monthly_Revenue', 'Monthly_Cost', 'Avg_Bill_Rate'],
                    pct_cols=['Current_DGM%']
                ))
            
            st.dataframe(styled_summary, use_container_width=True)

        else:
            st.markdown(f"<h3 style='color:#0F172A;'>📂 Single Project Analysis: {selected_sow}</h3>", unsafe_allow_html=True)

            proj_df = df[df[sow_col].astype(str) == selected_sow].copy()
            p_rev = proj_df['Current_Monthly_Revenue'].sum()
            p_sim_rev = proj_df['Simulated_Monthly_Revenue'].sum()
            p_cost = proj_df['Monthly_Cost'].sum()
            p_yearly_rev = p_rev * 12
            p_dgm = ((p_rev - p_cost) / p_rev * 100) if p_rev > 0 else 0
            p_sim_dgm = ((p_sim_rev - p_cost) / p_sim_rev * 100) if p_sim_rev > 0 else 0
            p_headcount = len(proj_df)

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Project 6-Mo Revenue", f"${p_rev * 6:,.2f}", delta=f"+${(p_sim_rev - p_rev) * 6:,.2f} Hike" if proposed_rate_increase > 0 else None)
            c2.metric("Yearly Revenue", f"${p_yearly_rev:,.2f}")
            c3.metric("Project Cost", f"${p_cost:,.2f}")
            c4.metric("Project DGM %", f"{p_dgm:.2f}%", delta=f"{p_sim_dgm - p_dgm:+.2f}% Hike" if proposed_rate_increase > 0 else f"{p_dgm - target_margin_threshold:.1f}% vs Floor")
            c5.metric("Headcount", f"{p_headcount} Roles")

            salary_ctc_increases, salary_adjustment_indices = get_salary_adjustments()
            salary_hourly_increase = (
                salary_ctc_increases * df['CTC_Load_Factor'] /
                (df[hrs_col] * 12 * df['Exchange_Denominator'])
            )
            df['Salary_Adjusted_Monthly_Cost'] = df['Monthly_Cost'] + salary_hourly_increase * df[hrs_col]
            df['Salary_Cost_Increase'] = salary_hourly_increase * df[hrs_col]
            df['Salary_Adjusted_Cost'] = df['Hourly_Cost'] + salary_hourly_increase
            df['Salary_Adjusted_DGM%'] = (
                (df[rate_col] - df['Salary_Adjusted_Cost']) /
                df[rate_col].replace(0, pd.NA) * 100
            ).fillna(0)
            proj_df = df[df[sow_col].astype(str) == selected_sow].copy()
            p_adjusted_cost = proj_df['Salary_Adjusted_Monthly_Cost'].sum()
            p_salary_cost_increase = p_adjusted_cost - p_cost

            if len(salary_adjustment_indices) > 0:
                p_adjusted_dgm = ((p_rev - p_adjusted_cost) / p_rev * 100) if p_rev > 0 else 0
                st.subheader("💰 Salary Adjustment Impact")
                salary_c1, salary_c2, salary_c3 = st.columns(3)
                salary_c1.metric("Project Monthly Cost", f"${p_adjusted_cost:,.2f}", delta=f"+${p_salary_cost_increase:,.2f}")
                salary_c2.metric("Project Monthly Margin $", f"${p_rev - p_adjusted_cost:,.2f}", delta=f"-${p_salary_cost_increase:,.2f}")
                salary_c3.metric("Project DGM %", f"{p_adjusted_dgm:.2f}%", delta=f"{p_adjusted_dgm - p_dgm:+.2f}%")
                show_salary_adjustment_table(salary_ctc_increases)

            show_quantified_gap(f"Project {selected_sow}", p_rev, p_cost, proj_df[rate_col].mean(), target_margin_threshold)

            st.markdown("---")

            col_chart, col_impact = st.columns([2, 1])
            
            with col_chart:
                st.subheader("📈 Resource Rate vs Margin Scatter")
                fig = px.scatter(
                    proj_df[proj_df['Current_Monthly_Revenue'] > 0],
                    x=rate_col, y='Current_DGM%', size='Current_Monthly_Revenue',
                    hover_name=name_col if name_col else role_col,
                    color='Current_DGM%', color_continuous_scale='RdYlGn',
                    title=f"Resource Efficiency ({selected_sow})",
                    template="plotly_white"
                )
                fig.add_hline(y=target_margin_threshold, line_dash="dash", line_color="#EF4444", annotation_text="Target Floor")
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True, height=450)

            with col_impact:
                if proposed_rate_increase > 0:
                    st.subheader("💡 Impact Analysis")
                    revenue_increase = p_sim_rev - p_rev
                    yearly_increase = revenue_increase * 12
                    dgm_improvement = p_sim_dgm - p_dgm

                    st.metric("Simulated Monthly Revenue", f"${p_sim_rev:,.2f}", delta=f"+${revenue_increase:,.2f}")
                    st.metric("Simulated Yearly Revenue", f"${p_sim_rev * 12:,.2f}", delta=f"+${yearly_increase:,.2f}")
                    st.metric("Simulated DGM %", f"{p_sim_dgm:.2f}%", delta=f"{dgm_improvement:+.2f}%")

            st.markdown("---")

            st.subheader(f"📋 Resources assigned to {selected_sow}")
            disp_cols = [c for c in [role_col, name_col, rate_col, 'Hourly_Cost', 'Current_DGM%', 'Current_Monthly_Revenue'] if c]
            proj_df_display = proj_df[disp_cols].copy()
            proj_df_display.index = range(1, len(proj_df_display) + 1)
            styled_proj = style_table_headers(format_currency_columns(
                proj_df_display.style,
                currency_cols=[rate_col, 'Hourly_Cost', 'Current_Monthly_Revenue'],
                pct_cols=['Current_DGM%']
            ))
            st.dataframe(styled_proj, use_container_width=True)

        st.markdown("---")

        ai_chat_tab, ai_diagnostic_tab = st.tabs([
            "💬 Financial Copilot",
            "🤖 Executive Diagnostic"
        ])

        with ai_chat_tab:
            # ---------------------------------------------------------
            # PHASE 1: NATURAL LANGUAGE FINANCIAL COPILOT
            # ---------------------------------------------------------
            st.subheader("💬 Ask Financial Expert Copilot")
            st.caption("Ask natural language questions about your portfolio, low-margin resources, rates, and exchange rate sensitivities.")
    
            # Initialize chat history in session state
            if st.session_state.get("copilot_scope_key") != copilot_scope_key:
                st.session_state.copilot_scope_key = copilot_scope_key
                st.session_state.copilot_messages = [
                    {"role": "assistant", "content": f"👋 Hello! I am your **DGM Financial Copilot** for **{scope_label}**. You can ask me questions like:\n"
                                                     "- *Which resources have a DGM below 50%?*\n"
                                                     "- *What is the highest revenue SOW in this portfolio?*\n"
                                                     "- *How does the exchange rate affect offshore resource costs?*\n"
                                                     "- *Summarize the margin impact if we increase rates by 10%.*"}
                ]
    
            with st.container(border=True):
                # Display Chat Messages
                for msg in st.session_state.copilot_messages:
                    st.chat_message(msg["role"]).write(msg["content"])
        
                # Quick Suggested Prompts
                st.markdown("<p style='font-size:12px; color:#475569; margin-bottom:4px;'>Quick Insights Prompts:</p>", unsafe_allow_html=True)
                col_p1, col_p2, col_p3 = st.columns(3)
                prompt_input = None
        
                if col_p1.button("📉 List roles with DGM < 50%", key="btn_p1"):
                    prompt_input = "List all roles and resources with a current DGM margin percentage below 50%, including their bill rate and monthly revenue impact."
                if col_p2.button("🏆 Top 3 Revenue Generating SOWs", key="btn_p2"):
                    prompt_input = "What are the top 3 revenue-generating SOWs in the portfolio and what is their average DGM%?"
                if col_p3.button("💵 Offshore vs Onsite Delivery Cost Summary", key="btn_p3"):
                    prompt_input = "Provide a summary comparing Onsite vs Offshore headcount, total cost, and average bill rates."
        
                # Chat Input Box
                chat_user_input = st.chat_input("Ask any financial question about your portfolio...")
                if chat_user_input:
                    prompt_input = chat_user_input
        
                if prompt_input:
                    # Append User Message
                    st.session_state.copilot_messages.append({"role": "user", "content": prompt_input})
                    st.chat_message("user").write(prompt_input)
        
                    if not api_key:
                        st.error("❌ Please provide a Groq API Key in the sidebar to chat with the Financial Copilot.")
                    else:
                        try:
                            client = Groq(api_key=api_key)
                            
                            # Prepare Dataset Context for Copilot System Prompt
                            summary_cols = [c for c in [sow_col, role_col, name_col, location_col, rate_col, 'Hourly_Cost', 'Current_DGM%', 'Current_Monthly_Revenue'] if c]
                            top_df_context = active_scope[summary_cols].to_string(index=False)
                            
                            system_prompt = f"""
                            You are an expert Executive Financial Copilot for a Delivered Gross Margin (DGM).
                            You have access to the real-time financial dataset below:
                            
                            Target DGM Floor: {target_margin_threshold}%
                            INR/USD Exchange Rate: {inr_per_usd}
                            Proposed Rate Hike: {proposed_rate_increase}%
                            {scope_label} Monthly Revenue: ${scope_revenue:,.2f}
                            {scope_label} Monthly Cost: ${scope_cost:,.2f}
                            {scope_label} DGM: {scope_dgm:.2f}%
                            
                            Dataset (Billable Resources):
                            {top_df_context}
                            
                            Instructions:
                            - Answer questions precisely using exact numbers from the dataset.
                            - Be executive, concise, and structured in Markdown.
                            - If asked about low margin roles, highlight those below {target_margin_threshold}%.
                            - Maintain a professional financial advisory tone.
                            """
        
                            messages_for_api = [{"role": "system", "content": system_prompt}]
                            for m in st.session_state.copilot_messages[-6:]:  # Keep last 6 context turns
                                messages_for_api.append({"role": m["role"], "content": m["content"]})
        
                            models_to_try = ['openai/gpt-oss-120b', 'qwen/qwen3.6-27b', 'openai/gpt-oss-20b']
                            copilot_response = None
        
                            with st.spinner("🤖 Financial Copilot analyzing portfolio..."):
                                last_api_error = None
                                for m in models_to_try:
                                    try:
                                        chat_res = client.chat.completions.create(
                                            model=m,
                                            messages=messages_for_api,
                                            temperature=0.7,
                                            max_tokens=2048
                                        )
                                        response_content = (
                                            chat_res.choices[0].message.content
                                            if chat_res.choices else None
                                        )
                                        if response_content and response_content.strip():
                                            copilot_response = response_content.strip()
                                            break
                                        last_api_error = RuntimeError(
                                            f"Model {m} returned an empty response."
                                        )
                                    except Exception as e:
                                        last_api_error = e
                                        continue
        
                                if copilot_response:
                                    st.session_state.copilot_messages.append({"role": "assistant", "content": copilot_response})
                                    st.chat_message("assistant").write(copilot_response)
                                else:
                                    error_details = str(last_api_error) if last_api_error else "No model returned usable content."
                                    st.error(f"❌ Copilot service temporarily unavailable. Details: {error_details}")
                        except Exception as e:
                            st.error(f"❌ Error connecting to Copilot API: {str(e)}")
        
        with ai_diagnostic_tab:
            st.subheader("🤖 AI Executive Diagnostic & Strategic Recovery Engine")
            diagnostic_requested = st.button("🚀 Run AI Agentic Margin Diagnostic", type="primary")

        if diagnostic_requested:
            if not api_key:
                st.error("❌ Please provide a valid Groq API Key in the sidebar or secrets configuration.")
            else:
                try:
                    client = Groq(api_key=api_key)
                    
                    low_margin_df = active_scope[active_scope['Current_DGM%'] < target_margin_threshold]
                    
                    if low_margin_df.empty:
                        st.info("✨ No resources found performing below the target margin floor. Portfolio health is optimal!")
                    else:
                        ctx_cols = [c for c in [sow_col, role_col, name_col, location_col, ctc_currency_col, ctc_col, 'Hourly_Cost', 'Current_DGM%', 'Current_Monthly_Revenue'] if c]
                        summary_data = low_margin_df[ctx_cols].to_string()
                        
                        prompt = f"""
                        You are an Executive Financial AI Advisor evaluating a portfolio for Delivered Gross Margin (DGM).
                        
                        Scope: {view_mode}
                        Target Margin Floor: {target_margin_threshold}%
                        Simulated Rate Hike Applied: {proposed_rate_increase}%
                        
                        Low-Performing Resources Below Target Floor:
                        {summary_data}
                        
                        Deliver an executive-level strategic report covering:
                        1. **Primary Margin Drag Factors**: Highlight specific roles/resources pulling down the margin and quantify their monthly cost drag.
                        2. **Operational Root Causes**: Explain why these specific roles have lower margins (e.g., CTC burden, onshore vs offshore mix, billing caps).
                        3. **Actionable Recovery Plan**: Provide 3 concrete, high-ROI recommendations for the DGM (rate re-negotiation, offshore rebalancing, resource pyramid adjustment).
                        """
                        
                        models = ['openai/gpt-oss-120b', 'qwen/qwen3.6-27b', 'openai/gpt-oss-20b']
                        out = None
                        last_error = None
                        
                        with st.spinner("⚡ Running agentic analysis on resource delivery models..."):
                            for m in models:
                                try:
                                    message = client.chat.completions.create(
                                        model=m,
                                        messages=[{"role": "user", "content": prompt}],
                                        temperature=0.7,
                                        max_tokens=2048
                                    )
                                    out = message.choices[0].message.content
                                    break
                                except Exception as e:
                                    last_error = e
                                    continue
                            
                            if out:
                                st.markdown(f'<div class="ai-box">{out}</div>', unsafe_allow_html=True)
                                st.download_button(
                                    label="📥 Download Executive AI Report (.md)",
                                    data=out,
                                    file_name="DGM_Margin_AI_Diagnostic_Report.md",
                                    mime="text/markdown"
                                )
                            else:
                                st.error(f"❌ AI diagnostic service unavailable: {str(last_error)}")
                except Exception as e:
                    st.error(f"❌ Error initializing AI client: {str(e)}")
else:
    st.info("👈 Upload your Excel or CSV file in the sidebar to launch the Executive Portal.")
