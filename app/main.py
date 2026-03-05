import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from theme import init_theme, get_theme_vars, apply_theme_css, render_sidebar, render_toggle

st.set_page_config(
    page_title="Energy Forecaster",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_theme()
t = get_theme_vars()
apply_theme_css(t)
render_toggle("theme_btn_main")
render_sidebar(t)

# ── Hero ────────────────────────────────────────────────────────────────────────
st.markdown("# ⚡ ENERGY FORECASTER")
st.markdown("##### Household power consumption analysis & multi-model forecasting")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Records",       "34,589",  "Hourly")
with col2:
    st.metric("Date Range",          "4 Years", "2006–2010")
with col3:
    st.metric("Best Model R²",       "0.9981",  "XGBoost")
with col4:
    st.metric("Features Engineered", "15",      "Lag + Time")

st.markdown("---")

col_left, col_right = st.columns([2, 1])
with col_left:
    st.markdown("### About This Project")
    st.markdown("""
    This application analyses **4 years of minute-level household electricity
    consumption** from the UCI Machine Learning Repository, resampled to hourly
    granularity for meaningful forecasting.

    Three fundamentally different forecasting models are implemented and compared:
    - **XGBoost** — gradient boosted trees with rich lag and time features
    - **Prophet** — Facebook's decomposition-based trend forecasting model
    - **ARIMA** — classical autoregressive statistical model

    The goal is not just prediction accuracy but understanding *why* different
    models behave differently on the same data — a question that matters deeply
    in real-world energy management systems.
    """)
with col_right:
    st.markdown("### Quick Stats")
    st.info("**Peak consumption** typically occurs between 18:00–21:00 on weekday evenings.")
    st.info("**Winter months** show ~40% higher average consumption than summer months.")
    st.info("**HVAC systems** account for the largest share of sub-metered energy usage.")

st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:{t['SUBTEXT']};font-size:0.75rem;"
    f"font-family:Share Tech Mono,monospace;'>"
    f"UCI HOUSEHOLD POWER CONSUMPTION DATASET · "
    f"BUILT WITH STREAMLIT · XGBOOST · PROPHET · ARIMA</p>",
    unsafe_allow_html=True,
)