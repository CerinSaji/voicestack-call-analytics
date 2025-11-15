# ============================================
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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "⏱️ Duration & Direction", "👥 Contact Types", "📈 Trends", "📞 Call Status"])

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

st.title("📅 Booking Conversion Metrics")

# Filter for scheduling calls only
scheduling_calls = df_qual[df_qual["Call Type"] == "Appointment Scheduling / Rescheduling"].copy()

if len(scheduling_calls) == 0:
    st.warning("No scheduling calls found in the dataset.")
else:
    total_scheduling = len(scheduling_calls)
    confirmed = len(scheduling_calls[scheduling_calls["Booking Status"] == "Booking Confirmed"])
    attempted = len(scheduling_calls[scheduling_calls["Booking Status"] == "Booking Attempted"])
    
    # Calculate rates
    confirmation_rate = (confirmed / total_scheduling) * 100
    attempt_rate = (attempted / total_scheduling) * 100
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Total Scheduling Calls", total_scheduling)
    with col2:
        st.metric("✅ Bookings Confirmed", confirmed, f"{confirmation_rate:.1f}%")
    with col3:
        st.metric("⏳ Bookings Attempted", attempted, f"{attempt_rate:.1f}%")
    with col4:
        st.metric("📊 Confirmation Rate", f"{confirmation_rate:.1f}%")
    
    st.divider()
    
    # Booking Status Distribution
    st.subheader("Booking Status Distribution (Scheduling Calls Only)")
    booking_status_counts = scheduling_calls["Booking Status"].value_counts().reset_index()
    booking_status_counts.columns = ["Booking Status", "Count"]
    booking_status_counts["Percentage"] = (booking_status_counts["Count"] / total_scheduling * 100).round(1)
    
    fig_booking = px.pie(
        booking_status_counts,
        values="Count",
        names="Booking Status",
        color_discrete_map={"Booking Confirmed": "#2ca02c", "Booking Attempted": "#ff7f0e", "N/A": "#d62728"},
        title="Booking Status Breakdown"
    )
    st.plotly_chart(fig_booking, use_container_width=True)
    
    st.divider()
    
    st.subheader("Booking Status by Hour of Day")
    
    scheduling_calls["Hour of Day"] = scheduling_calls["Call Time"].dt.hour
    booking_by_hour = pd.crosstab(scheduling_calls["Hour of Day"], scheduling_calls["Booking Status"])
    booking_by_hour = booking_by_hour.reset_index()
    
    fig_booking_hour = px.bar(
        booking_by_hour,
        x="Hour of Day",
        y=booking_by_hour.columns[1:],
        barmode="stack",
        title="Booking Status Distribution by Hour",
        labels={"value": "Number of Calls", "variable": "Booking Status"},
        color_discrete_map={"Booking Confirmed": "#2ca02c", "Booking Attempted": "#ff7f0e", "N/A": "#d62728"}
    )
    fig_booking_hour.update_layout(height=450, hovermode="x unified")
    st.plotly_chart(fig_booking_hour, use_container_width=True)
    
    st.divider()
    
    st.subheader("Booking Status Summary Table (Scheduling Calls Only)")
    st.dataframe(booking_status_counts, use_container_width=True, hide_index=True)

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
# TAB 5: CALL STATUS
# ============================================
with tab5:
    st.subheader("Call Status Distribution by Hour of Day")

    # Create dataframe with hour and call status
    df_status_by_hour = df.copy()
    df_status_by_hour["Hour of Day"] = df_status_by_hour["Call Time"].dt.hour

    # Create pivot table: Hour x Call Status
    status_by_hour = pd.crosstab(df_status_by_hour["Hour of Day"], df_status_by_hour["Call Status"])
    status_by_hour = status_by_hour.reset_index()

    # Stacked bar chart
    fig_status_hour = px.bar(
        status_by_hour,
        x="Hour of Day",
        y=status_by_hour.columns[1:],
        barmode="stack",
        title="Call Status Distribution Throughout the Day",
        labels={"value": "Number of Calls", "variable": "Call Status"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_status_hour.update_layout(height=450, hovermode="x unified")
    st.plotly_chart(fig_status_hour, use_container_width=True)

    st.divider()

    st.subheader("Overall Call Status Summary")
    call_status_counts = df["Call Status"].value_counts().reset_index()
    call_status_counts.columns = ["Call Status", "Count"]
    call_status_counts["Percentage"] = (call_status_counts["Count"] / call_status_counts["Count"].sum() * 100).round(1)
    st.dataframe(call_status_counts, use_container_width=True, hide_index=True)

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

st.divider()

st.subheader("😊 Sentiment Analysis")

sentiment_counts = df_qual["Sentiment"].value_counts().reset_index()
sentiment_counts.columns = ["Sentiment", "Count"]

# Calculate percentages
total_calls_qual = sentiment_counts["Count"].sum()
sentiment_counts["Percentage"] = (sentiment_counts["Count"] / total_calls_qual * 100).round(1)

col1, col2, col3, col4 = st.columns(4)
with col1:
    positive_count = sentiment_counts[sentiment_counts["Sentiment"] == "Positive"]["Count"].values
    positive_count = positive_count[0] if len(positive_count) > 0 else 0
    st.metric("😊 Positive", positive_count, f"{(positive_count/total_calls_qual*100):.1f}%")
with col2:
    neutral_count = sentiment_counts[sentiment_counts["Sentiment"] == "Neutral"]["Count"].values
    neutral_count = neutral_count[0] if len(neutral_count) > 0 else 0
    st.metric("😐 Neutral", neutral_count, f"{(neutral_count/total_calls_qual*100):.1f}%")
with col3:
    negative_count = sentiment_counts[sentiment_counts["Sentiment"] == "Negative"]["Count"].values
    negative_count = negative_count[0] if len(negative_count) > 0 else 0
    st.metric("😞 Negative", negative_count, f"{(negative_count/total_calls_qual*100):.1f}%")
with col4:
    st.metric("📞 Total Calls Analyzed", total_calls_qual)

fig_sentiment = px.pie(
    sentiment_counts,
    values="Count",
    names="Sentiment",
    color_discrete_map={"Positive": "#2ca02c", "Neutral": "#1f77b4", "Negative": "#d62728"},
    title="Sentiment Distribution"
)
st.plotly_chart(fig_sentiment, use_container_width=True)

st.divider()

st.subheader("🎯 Top Quality Themes")

# Extract and count quality observation themes
quality_obs = df_qual["Quality Observation"].value_counts().head(10)
st.write("**Most Common Quality Observations:**")
for i, (obs, count) in enumerate(quality_obs.items(), 1):
    st.write(f"{i}. **{count} calls** - {obs}")

st.divider()

# --------------------------
# Call Details Table
st.subheader("📋 All Call Details with Classifications & Sentiment")

display_columns = ["Call Time", "Call Direction", "Contact Type", "Call Type", "Sentiment", "Booking Status", "Quality Observation", "transcript"]
st.dataframe(df_qual[display_columns], use_container_width=True, hide_index=True)