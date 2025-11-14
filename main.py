import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from quant_metrics import calculate_quantitative_metrics
from qual_metrics import generate_qualitative_metrics

st.set_page_config(page_title="Call Analytics Dashboard", layout="wide")

# --------------------------
# Loading Screen with Status Text
loading_container = st.empty()
progress_bar = st.empty()
status_text = st.empty()

with loading_container.container():
    st.markdown("<h1 style='text-align:center; font-size:60px;'>📞 Call Analytics Dashboard</h1>", unsafe_allow_html=True)

progress_bar.progress(0)
status_text.text("📊 Loading quantitative data...")

# --------------------------
# Load Data
df = pd.read_csv("call_logs.csv")

# Derived Metrics
df["Answered"] = df["Conversation Duration"] > 0
df["Voicemail Left"] = df["Voicemail Duration"] > 0
df["Empty Missed"] = (df["Conversation Duration"] == 0) & (df["Voicemail Duration"] == 0)

# Convert Call Time to datetime
df["Call Time"] = pd.to_datetime(df["Call Time"])

# --------------------------
# Quantitative metrics
quant_metrics = calculate_quantitative_metrics(df)
progress_bar.progress(20)
status_text.text("🔄 Loading qualitative data in batches...")

# --------------------------
# Qualitative metrics (progress bar will update inside)
df_qual = generate_qualitative_metrics(df, progress_bar=progress_bar, status_text=status_text)

# --------------------------
# Remove loading screen
loading_container.empty()
progress_bar.empty()
status_text.empty()

# --------------------------
# Dashboard Title
st.title("📞 Call Analytics Dashboard")

st.markdown(
    """
**Quick Definitions:**  
- 📞 **Answer Rate**: % of total calls answered by staff  
- 🎙 **Voicemail Rate**: % of missed calls that left a voicemail  
- ❌ **Abandon Rate**: % of calls missed without leaving a voicemail
"""
)

# --------------------------
# TABS for Organization
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "⏱️ Duration & Direction", "👥 Contact Types", "📈 Trends"])

# ============================================
# TAB 1: OVERVIEW
# ============================================
with tab1:
    st.subheader("Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total Calls", quant_metrics["total_calls"])
    with col2:
        st.metric("📞 Answer Rate", f"{quant_metrics['answer_rate']:.2f}%", f"{quant_metrics['answered_calls']} answered")
    with col3:
        st.metric("🎙 Voicemail Rate", f"{quant_metrics['voicemail_rate']:.2f}%", f"{quant_metrics['voicemail_calls']} voicemails")
    with col4:
        st.metric("❌ Abandon Rate", f"{quant_metrics['abandon_rate']:.2f}%", f"{quant_metrics['empty_missed_calls']} empty missed")

    st.divider()

    st.subheader("Summary Metrics Table")
    summary_df = pd.DataFrame({
        "Total Calls": [quant_metrics["total_calls"]],
        "Answered Calls": [quant_metrics["answered_calls"]],
        "Total Missed Calls": [quant_metrics["total_missed_calls"]],
        "Voicemails Left": [quant_metrics["voicemail_calls"]],
        "Empty Missed Calls": [quant_metrics["empty_missed_calls"]],
        "Answer Rate (%)": [f"{quant_metrics['answer_rate']:.2f}"],
        "Voicemail Rate (% of missed)": [f"{quant_metrics['voicemail_rate']:.2f}"],
        "Abandon Rate (%)": [f"{quant_metrics['abandon_rate']:.2f}"],
    })
    st.dataframe(summary_df, use_container_width=True)

# ============================================
# TAB 2: DURATION & DIRECTION
# ============================================
with tab2:
    st.subheader("Call Duration Patterns")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⏱️ Avg Conversation Duration", f"{quant_metrics['avg_conversation_duration']:.0f}s")
    with col2:
        st.metric("📳 Avg Ring Duration", f"{quant_metrics['avg_ring_duration']:.0f}s")
    with col3:
        st.metric("📞 Avg Total Duration", f"{quant_metrics['avg_total_duration']:.0f}s")

    st.divider()

    st.subheader("🏷️ Call Type Classification")
    call_type_counts = df_qual["Call Type"].value_counts().reset_index()
    call_type_counts.columns = ["Call Type", "Count"]
    
    fig_call_type = px.bar(
        call_type_counts,
        x="Call Type",
        y="Count",
        text="Count",
        labels={"Count": "Number of Calls"},
        color="Call Type",
        color_discrete_sequence=px.colors.qualitative.Set3,
        title="Distribution of Call Types"
    )
    fig_call_type.update_traces(textposition="outside")
    fig_call_type.update_xaxes(tickangle=45)
    fig_call_type.update_layout(height=450)
    st.plotly_chart(fig_call_type, use_container_width=True)

    st.divider()

    st.subheader("Inbound vs Outbound Split")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("📥 Inbound Calls", f"{quant_metrics['inbound_count']} ({quant_metrics['inbound_rate']:.1f}%)")
    with col2:
        st.metric("📤 Outbound Calls", f"{quant_metrics['outbound_count']} ({quant_metrics['outbound_rate']:.1f}%)")

    inbound_outbound_data = pd.DataFrame({
        "Direction": ["Inbound", "Outbound"],
        "Count": [quant_metrics["inbound_count"], quant_metrics["outbound_count"]]
    })
    fig_direction = px.pie(
        inbound_outbound_data,
        values="Count",
        names="Direction",
        color_discrete_map={"Inbound": "#1f77b4", "Outbound": "#ff7f0e"}
    )
    st.plotly_chart(fig_direction, use_container_width=True)

# ============================================
# TAB 3: CONTACT TYPES
# ============================================
with tab3:
    st.subheader("Contact Type Breakdown")

    contact_type_df = pd.DataFrame(
        list(quant_metrics["contact_type_counts"].items()),
        columns=["Contact Type", "Count"]
    ).sort_values("Count", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig_contact = px.bar(
            contact_type_df,
            x="Contact Type",
            y="Count",
            text="Count",
            labels={"Count": "Number of Calls"},
            color="Contact Type",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_contact.update_traces(textposition="outside")
        st.plotly_chart(fig_contact, use_container_width=True)

    with col2:
        st.dataframe(contact_type_df, use_container_width=True, hide_index=True)



# ============================================
# TAB 4: TIME-SERIES TRENDS
# ============================================
with tab4:
    st.subheader("Total Calls & Answered Calls Over Time")

    # Daily trend - Total vs Answered
    daily_df = quant_metrics["daily_data"].copy()
    fig_daily = px.line(
        daily_df,
        x="Day",
        y=["Total Calls", "Answered Calls"],
        markers=True,
        title="Daily Call Volume & Answered Calls",
        labels={"value": "Number of Calls", "variable": "Call Type"},
        color_discrete_map={"Total Calls": "#1f77b4", "Answered Calls": "#2ca02c"}
    )
    fig_daily.update_layout(height=400, hovermode="x unified")
    st.plotly_chart(fig_daily, use_container_width=True)

    st.divider()

    st.subheader("Calls by Hour of Day")

    # Hourly distribution - shows which hours are busiest
    hourly_df = quant_metrics["hourly_data"].copy()
    fig_hourly = px.bar(
        hourly_df,
        x="Hour of Day",
        y="Total Calls",
        color="Total Calls",
        color_continuous_scale="Blues",
        title="Call Volume by Hour (Peak Hours Indicator)",
        labels={"Total Calls": "Number of Calls"}
    )
    fig_hourly.update_layout(height=400)
    st.plotly_chart(fig_hourly, use_container_width=True)

    # Optional: Show answered calls by hour
    st.write("**Answered Calls by Hour**")
    fig_hourly_answered = px.bar(
        hourly_df,
        x="Hour of Day",
        y="Answered Calls",
        color="Answered Calls",
        color_continuous_scale="Greens",
        labels={"Answered Calls": "Number of Answered Calls"}
    )
    fig_hourly_answered.update_layout(height=350)
    st.plotly_chart(fig_hourly_answered, use_container_width=True)

# ============================================
# QUALITATIVE ANALYSIS SECTION (Below all tabs)
# ============================================
st.divider()
st.title("🤖 Qualitative Analysis")

st.subheader("AI-Generated Call Type Classifications")
call_type_counts = df_qual["Call Type"].value_counts().reset_index()
call_type_counts.columns = ["Call Type", "Count"]

fig_call_type = px.bar(
    call_type_counts,
    x="Call Type",
    y="Count",
    text="Count",
    labels={"Count": "Number of Calls"},
    color="Call Type",
    color_discrete_sequence=px.colors.qualitative.Set3,
    title="Distribution of Call Types (AI Classification)"
)
fig_call_type.update_traces(textposition="outside")
fig_call_type.update_xaxes(tickangle=45)
fig_call_type.update_layout(height=450)
st.plotly_chart(fig_call_type, use_container_width=True)

# --------------------------
# Call Details Table
st.subheader("Call Details with Classifications")

with st.expander("View all call transcripts with AI classifications"):
    st.dataframe(df_qual[["Call Time", "Call Direction", "Contact Type", "Call Type", "transcript"]], use_container_width=True)