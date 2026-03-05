import streamlit as st

AMBER = "#f5a623"

def init_theme():
    """Initialise theme state if not already set."""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

def get_theme_vars():
    """Return theme colour variables based on current mode."""
    is_dark = st.session_state.get("dark_mode", True)
    if is_dark:
        return dict(
            is_dark   = True,
            BG        = "#0f0f0f",
            SECONDARY = "#141414",
            TEXT      = "#e0e0e0",
            SUBTEXT   = "#888888",
            BORDER    = "#2a2a2a",
            CARD_BG   = "#1a1a1a",
            GRID      = "#2a2a2a",
            AMBER     = AMBER,
        )
    else:
        return dict(
            is_dark   = False,
            BG        = "#f5f5f5",
            SECONDARY = "#ffffff",
            TEXT      = "#1a1a1a",
            SUBTEXT   = "#666666",
            BORDER    = "#e0e0e0",
            CARD_BG   = "#ffffff",
            GRID      = "#e8e8e8",
            AMBER     = AMBER,
        )

def apply_theme_css(t: dict):
    """Inject full theme CSS."""
    is_dark = t['is_dark']
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@300;400;600;700&display=swap');

/* ── Base ── */
html, body, [class*="css"],
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMainBlockContainer"],
[data-testid="stMain"] {{
    font-family: 'Barlow', sans-serif !important;
    background-color: {t['BG']} !important;
    color: {t['TEXT']} !important;
}}

/* ── Header strip ── */
[data-testid="stHeader"] {{
    background-color: {t['BG']} !important;
    border-bottom: 1px solid {t['BORDER']} !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {{
    background-color: {t['SECONDARY']} !important;
    border-right: 1px solid {t['BORDER']} !important;
}}
[data-testid="stSidebar"] * {{ color: {t['TEXT']} !important; }}
[data-testid="stSidebarNavItems"] {{ display: none !important; }}

/* ── Metric cards ── */
[data-testid="stMetric"] {{
    background: {t['CARD_BG']} !important;
    border: 1px solid {t['BORDER']} !important;
    border-left: 3px solid {t['AMBER']} !important;
    padding: 1rem 1.2rem !important;
    border-radius: 4px !important;
}}
[data-testid="stMetricLabel"] {{
    color: {t['SUBTEXT']} !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}}
[data-testid="stMetricValue"] {{
    color: {t['AMBER']} !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 1.6rem !important;
}}

/* ── Headings ── */
h1 {{
    font-family: 'Share Tech Mono', monospace !important;
    color: {t['AMBER']} !important;
    letter-spacing: 0.05em !important;
}}
h2, h3 {{
    font-family: 'Barlow', sans-serif !important;
    color: {t['TEXT']} !important;
    font-weight: 600 !important;
}}
p, li {{ color: {t['TEXT']} !important; }}
hr {{ border-color: {t['BORDER']} !important; }}

/* ── Info boxes ── */
[data-testid="stInfo"] {{
    background: {t['CARD_BG']} !important;
    border-left: 3px solid {t['AMBER']} !important;
    color: {t['TEXT']} !important;
}}

/* ── Dropdowns ── */
[data-baseweb="select"] > div {{
    background-color: {t['CARD_BG']} !important;
    border-color: {t['BORDER']} !important;
    color: {t['TEXT']} !important;
}}
[data-baseweb="popover"] {{
    background-color: {t['CARD_BG']} !important;
}}
[data-baseweb="menu"] {{
    background-color: {t['CARD_BG']} !important;
}}
[role="option"] {{
    background-color: {t['CARD_BG']} !important;
    color: {t['TEXT']} !important;
}}
[role="option"]:hover {{
    background-color: {t['BORDER']} !important;
}}
[aria-selected="true"] {{
    background-color: {t['BORDER']} !important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
    background-color: {t['CARD_BG']} !important;
    border: 1px solid {t['BORDER']} !important;
    border-radius: 4px !important;
}}
[data-testid="stDataFrame"] th {{
    background-color: {t['SECONDARY']} !important;
    color: {t['SUBTEXT']} !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}}
[data-testid="stDataFrame"] td {{
    color: {t['TEXT']} !important;
    background-color: {t['CARD_BG']} !important;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background-color: {t['CARD_BG']} !important;
    border: 1px solid {t['BORDER']} !important;
    border-radius: 4px !important;
}}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {{
    color: {t['TEXT']} !important;
}}

/* ── Spinner ── */
[data-testid="stSpinner"] p {{ color: {t['TEXT']} !important; }}

/* ── Hide branding ── */
footer {{ display: none !important; }}
#MainMenu {{ visibility: hidden; }}

/* ── Theme toggle — scoped to .theme-toggle-container only ── */
.theme-toggle-container {{
    position: fixed;
    top: 0.4rem;
    right: 7rem;
    z-index: 9999;
}}
.theme-toggle-container button {{
    padding: 6px 18px !important;
    border-radius: 10px !important;
    border: 1px solid {'rgba(255,255,255,0.15)' if is_dark else 'rgba(0,0,0,0.1)'} !important;
    background: {'rgba(255,255,255,0.07)' if is_dark else 'rgba(255,255,255,0.6)'} !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    box-shadow: {'0 2px 16px rgba(0,0,0,0.5),inset 0 1px 0 rgba(255,255,255,0.08)'
                 if is_dark else
                 '0 2px 16px rgba(0,0,0,0.08),inset 0 1px 0 rgba(255,255,255,0.9)'} !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    color: {'#e0e0e0' if is_dark else '#1a1a1a'} !important;
    white-space: nowrap !important;
    min-width: 120px !important;
    transition: all 0.25s ease !important;
}}
.theme-toggle-container button:hover {{
    background: {'rgba(255,255,255,0.13)' if is_dark else 'rgba(255,255,255,0.85)'} !important;
    transform: translateY(-1px) !important;
}}
</style>
""", unsafe_allow_html=True)


def render_sidebar(t: dict):
    """Render consistent sidebar with SVG icons across all pages."""

    # SVG icon definitions — minimal line style
    icons = {
        "home": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
        "chart": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
        "forecast": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
        "compare": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>',
        "dataset": '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
        "model": '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M4.93 4.93a10 10 0 0 0 0 14.14"/></svg>',
    }

    with st.sidebar:
        st.markdown(
            f"<p style='font-weight:700;color:{t['AMBER']};letter-spacing:0.08em;"
            f"font-family:Share Tech Mono,monospace;font-size:0.9rem;'>"
            f"⚡ ENERGY FORECASTER</p>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Navigation label
        st.markdown(
            f"<p style='color:{t['SUBTEXT']};font-size:0.68rem;letter-spacing:0.12em;"
            f"text-transform:uppercase;margin-bottom:0.3rem;'>Navigation</p>",
            unsafe_allow_html=True,
        )

        # Custom nav links with SVG icons
        nav_items = [
            ("main.py",             icons["home"],     "Home"),
            ("pages/1_overview.py", icons["chart"],    "Historical Overview"),
            ("pages/2_forecast.py", icons["forecast"], "Forecast"),
            ("pages/3_compare.py",  icons["compare"],  "Model Comparison"),
        ]
        for page, icon, label in nav_items:
            st.page_link(
                page,
                label=f"{label}",
                icon=None,
            )

        # Inject SVG icons via CSS into page links
        st.markdown(f"""
<style>
[data-testid="stSidebarNav"] a span,
[data-testid="stPageLink"] span {{
    font-size: 0.88rem !important;
    letter-spacing: 0.02em !important;
}}
</style>
""", unsafe_allow_html=True)

        st.markdown("---")

        # Dataset section
        st.markdown(
            f"<p style='color:{t['SUBTEXT']};font-size:0.68rem;letter-spacing:0.12em;"
            f"text-transform:uppercase;margin-bottom:0.4rem;'>"
            f"{icons['dataset']} &nbsp;Dataset</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='color:{t['TEXT']};font-size:0.82rem;line-height:1.7;'>"
            f"UCI Household Power<br>"
            f"Dec 2006 — Nov 2010<br>"
            f"34,589 hourly records</p>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Models section
        st.markdown(
            f"<p style='color:{t['SUBTEXT']};font-size:0.68rem;letter-spacing:0.12em;"
            f"text-transform:uppercase;margin-bottom:0.4rem;'>"
            f"{icons['model']} &nbsp;Models</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='color:{t['TEXT']};font-size:0.82rem;line-height:1.8;'>"
            f"XGBoost<br>Prophet<br>ARIMA</p>",
            unsafe_allow_html=True,
        )


def render_toggle(key: str):
    """
    Render the theme toggle button inside a scoped container div.
    The .theme-toggle-container class positions it fixed top-right
    without affecting any other buttons on the page.
    """
    label = "🌙  Dark Mode" if st.session_state.get("dark_mode", True) else "☀️  Light Mode"

    # Open the scoped container
    st.markdown('<div class="theme-toggle-container">', unsafe_allow_html=True)
    st.button(label, on_click=toggle_theme, help="Toggle dark / light mode", key=key)
    st.markdown('</div>', unsafe_allow_html=True)