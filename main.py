import streamlit as st
import pandas as pd
import plotly.express as px
from quant_metrics import calculate_quantitative_metrics
from qual_metrics import generate_qualitative_metrics

st.set_page_config(page_title="Call Analytics Dashboard", layout="wide")

# --------------------------
# Loading placeholder
loading_container = st.empty()
progress_bar = st.progress(0)

with loading_container.container():
    st.markdown("<h1 style='text-align:center; font-size:60px;'>📞 Call Analytics Dashboard</h1>", unsafe_allow_html=True)

# --------------------------
# Load Data
df = pd.read_csv("call_logs.csv")

# Derived Metrics
df["Answered"] = df["Conversation Duration"] > 0
df["Voicemail Left"] = df["Voicemail Duration"] > 0
df["Empty Missed"] = (df["Conversation Duration"] == 0) & (df["Voicemail Duration"] == 0)

# --------------------------
# Quantitative metrics
quant_metrics = calculate_quantitative_metrics(df)
progress_bar.progress(20)  # 20% done after quant metrics

# --------------------------
# Qualitative metrics
st.session_state.progress = progress_bar  # Pass progress bar to qual_metrics if needed

df_qual = generate_qualitative_metrics(df, progress_bar=progress_bar)
# progress will be updated inside generate_qualitative_metrics per batch

# --------------------------
# Remove loading screen
loading_container.empty()
progress_bar.empty()

# --------------------------
# Dashboard Title
st.title("📞 Call Analytics Dashboard")

# KPI Definitions
st.markdown(
    """
**Definitions:**  
- 📞 **Answer Rate**: % of total calls answered by staff  
- 🎙 **Voicemail Rate**: % of missed calls that left a voicemail  
- ❌ **Abandon Rate**: % of calls missed without leaving a voicemail
"""
)

# --------------------------
# KPI Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📊 Total Calls", quant_metrics["total_calls"])
with col2:
    st.metric("📞 Answer Rate", f"{quant_metrics['answer_rate']:.2f}%", f"{quant_metrics['answered_calls']} answered")
with col3:
    st.metric("🎙 Voicemail Rate (Missed Only)", f"{quant_metrics['voicemail_rate']:.2f}%", f"{quant_metrics['voicemail_calls']} voicemails")
with col4:
    st.metric("❌ Abandon Rate", f"{quant_metrics['abandon_rate']:.2f}%", f"{quant_metrics['empty_missed_calls']} empty missed")

# --------------------------
# Summary Table
st.subheader("📄 Summary Metrics Table")
summary_df = pd.DataFrame({
    "Total Calls": [quant_metrics["total_calls"]],
    "Answered Calls": [quant_metrics["answered_calls"]],
    "Total Missed Calls": [quant_metrics["total_missed_calls"]],
    "Voicemails Left": [quant_metrics["voicemail_calls"]],
    "Empty Missed Calls": [quant_metrics["empty_missed_calls"]],
    "Answer Rate (%)": [quant_metrics["answer_rate"]],
    "Voicemail Rate (% of missed)": [quant_metrics["voicemail_rate"]],
    "Abandon Rate (%)": [quant_metrics["abandon_rate"]],
})
st.dataframe(summary_df, use_container_width=True)

# --------------------------
# Call Type Bar Chart
st.subheader("📝 Call Type Distribution")
call_type_counts = df_qual["Call Type"].value_counts()
fig_bar = px.bar(
    x=call_type_counts.index,
    y=call_type_counts.values,
    text=call_type_counts.values,
    labels={"x": "Call Type", "y": "Number of Calls"},
    color=call_type_counts.index,
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig_bar.update_traces(textposition="outside")
st.plotly_chart(fig_bar, use_container_width=True)

# --------------------------
# Collapsible Call Type + Transcript Table
with st.expander("📋 Call Type + Transcript Details"):
    st.dataframe(df_qual[["transcript", "Call Type"]], use_container_width=True)
