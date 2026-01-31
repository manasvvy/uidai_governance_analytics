import streamlit as st
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIG (MUST BE FIRST STREAMLIT COMMAND)
# --------------------------------------------------
st.set_page_config(
    page_title="UIDAI Governance-First Dashboard",
    layout="wide"
)

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.title("UIDAI Aadhaar Enrolment — Governance-First Dashboard")
st.caption("Designed to discourage blind trust in aggregate numbers")

# --------------------------------------------------
# PATHS
# --------------------------------------------------
BASE_DIR = Path(__file__).parent
PLOTS_DIR = BASE_DIR / "plots"
DATA_FILE = PLOTS_DIR / "state_confidence_table.csv"

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_state_data():
    return pd.read_csv(DATA_FILE)

try:
    state_df = load_state_data()
except Exception as e:
    st.error("Failed to load state confidence data.")
    st.exception(e)
    st.stop()

# --------------------------------------------------
# CUSTOM CSS TO REMOVE BLUE LINKS
# --------------------------------------------------
st.markdown("""
    <style>
    [data-testid="stSidebar"] a {
        color: white !important;
        text-decoration: none !important;
    }
    [data-testid="stSidebar"] a:hover {
        color: #FF4B4B !important;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR NAV
# --------------------------------------------------
st.sidebar.title("Navigate")
st.sidebar.markdown("📊 [National Overview](#national-overview)")
st.sidebar.markdown("⚠️ [Behind the Numbers](#behind-the-numbers)")
st.sidebar.markdown("📍 [Regional Confidence Ranking](#regional-confidence-ranking)")
st.sidebar.markdown("✅ [Decision Summary](#decision-summary)")

# --------------------------------------------------
# SECTION 1 — NATIONAL OVERVIEW
# --------------------------------------------------
st.header("National Overview", anchor="national-overview")
st.caption("Quick snapshot of overall enrollment trends and confidence levels")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Aggregate Enrolment Trend")
    
    age_group_plot = PLOTS_DIR / "age_group_trend.png"
    if age_group_plot.exists():
        st.image(str(age_group_plot), use_container_width=True)
    else:
        st.warning("⚠️ Visualization not available")

with col2:
    avg_conf = state_df["confidence_score"].mean()

    if avg_conf < 0.40:
        label = "🔴 High Bias Risk"
    elif avg_conf < 0.60:
        label = "🟡 Moderate Confidence"
    else:
        label = "🟢 High Confidence"

    st.metric("Confidence Indicator", label)
    st.caption("Confidence reflects demographic balance behind this trend.")

st.divider()

# --------------------------------------------------
# SECTION 2 — BEHIND THE NUMBERS
# --------------------------------------------------
st.header("Behind the Numbers", anchor="behind-the-numbers")
st.caption("Understand the demographic breakdown driving these aggregate numbers")

st.subheader("What's Really Driving These Totals?")

# Display plot in a smaller container
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    aggregate_plot = PLOTS_DIR / "aggregate_enrolments.png"
    if aggregate_plot.exists():
        st.image(str(aggregate_plot), use_container_width=True)
    else:
        st.warning("⚠️ Visualization not available")

st.markdown(
    "⚠️ **Warning:** This trend is dominated by a single demographic segment. "
    "High total numbers don't mean balanced participation across all groups."
)

st.divider()

# --------------------------------------------------
# SECTION 3 — REGIONAL RANKING
# --------------------------------------------------
st.header("Regional Confidence Ranking", anchor="regional-confidence-ranking")
st.markdown("""
This section compares states by total Aadhaar enrolments alongside a confidence score that reflects demographic balance.

Higher confidence scores indicate more evenly distributed participation across age groups, while lower scores signal dominance by a single demographic segment.

**High enrolment volume alone should not be interpreted as a reliable indicator of broad participation or policy success.**
""")

# Display table in a centered container
col1, col2, col3 = st.columns([0.5, 3, 0.5])
with col2:
    # Add colored indicators to bias_flag
    display_df = state_df[["state", "total_enrolments", "confidence_score", "bias_flag"]].copy()
    display_df = display_df.sort_values("total_enrolments", ascending=False)

    # Add color indicators based on bias level
    display_df["bias_flag"] = display_df["bias_flag"].apply(
        lambda x: f"🔴 {x}" if x == "High bias risk" 
        else f"🟡 {x}" if x == "Moderate bias risk"
        else f"🟢 {x}"
    )

    st.dataframe(display_df, use_container_width=True)

st.subheader("Enrolments vs Confidence (State-wise)")

# Display scatter plot in a centered container
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    state_plot = PLOTS_DIR / "state_enrolments_vs_confidence.png"
    if state_plot.exists():
        st.image(str(state_plot), use_container_width=True)
    else:
        alt_plot = PLOTS_DIR / "enrolments_vs_confidence.png"
        if alt_plot.exists():
            st.image(str(alt_plot), use_container_width=True)
        else:
            st.warning("⚠️ Visualization not available")

st.divider()

# --------------------------------------------------
# SECTION 4 — DECISION SUMMARY
# --------------------------------------------------
st.header("Decision Support Summary", anchor="decision-summary")
st.caption("Key insights for policy decisions. Regions with high bias require targeted intervention, not just celebration of total numbers")

st.subheader("Confidence-Gated Decision Framework")
st.markdown("""
Before allocating resources or declaring program success, decision-makers should review the demographic composition driving enrolment growth.

**Recommended Actions by Confidence Level:**

- 🟢 **High Confidence (≥0.60)**: Aggregate numbers are reliable for policy decisions and resource allocation.

- 🟡 **Moderate Confidence (0.40-0.60)**: Use aggregate numbers alongside demographic breakdown. Check which age groups are underrepresented before scaling programs.

- 🔴 **High Bias Risk (<0.40)**: Aggregate numbers are misleading. Targeted analysis required before action. High enrolment does not mean broad participation.

**Key Point**: Regions with high enrolment but low confidence need targeted outreach to underrepresented age groups, not broad expansion.
""")

st.divider()

# Key metrics
high_bias = (state_df["bias_flag"] == "High bias risk").sum()
moderate_bias = (state_df["bias_flag"] == "Moderate bias risk").sum()

col1, col2 = st.columns(2)
col1.metric("High Bias Regions", high_bias)
col2.metric("Moderate Bias Regions", moderate_bias)

st.markdown(
    "**Regions flagged with high bias risk should not be evaluated "
    "using aggregate enrolment numbers alone.**"
)