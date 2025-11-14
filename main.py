import streamlit as st
import pandas as pd

st.set_page_config(page_title="Call Analytics Dashboard", layout="wide")
st.title("📞 Call Analytics Dashboard")

# --------------------------
# Load Data
df = pd.read_csv("call_logs.csv")
# --------------------------

# --------------------------
# DERIVED METRICS (BASED ON REAL DATA FIELDS)
# --------------------------

# 1. Call was answered if someone picked up
df["Answered"] = df["Conversation Duration"] > 0

# 2. Voicemail was left if Voicemail Duration > 0
df["Voicemail Left"] = df["Voicemail Duration"] > 0

# 3. Empty missed = caller hung up + no voicemail left
df["Empty Missed"] = (df["Conversation Duration"] == 0) & (df["Voicemail Duration"] == 0)

# --------------------------
# METRIC CALCULATIONS
# --------------------------

total_calls = len(df)

answered_calls = df["Answered"].sum()

# ✔ Total Missed = all calls - answered calls
total_missed_calls = total_calls - answered_calls

voicemail_calls = df["Voicemail Left"].sum()

empty_missed_calls = df["Empty Missed"].sum()

# Rates
answer_rate = (answered_calls / total_calls) * 100

# ✔ Voicemail Rate = voicemail calls / missed calls only
voicemail_rate = (
    (voicemail_calls / total_missed_calls) * 100 
    if total_missed_calls > 0 else 0
)

# ✔ Abandon Rate = empty missed / total calls
abandon_rate = (empty_missed_calls / total_calls) * 100

# --------------------------
# KPI CARDS
# --------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total Calls", total_calls)

with col2:
    st.metric("📞 Answer Rate", f"{answer_rate:.2f}%", f"{answered_calls} answered")

with col3:
    st.metric("🎙 Voicemail Rate (Missed Only)", f"{voicemail_rate:.2f}%",
              f"{voicemail_calls} voicemails")

with col4:
    st.metric("❌ Abandon Rate", f"{abandon_rate:.2f}%",
              f"{empty_missed_calls} empty missed")

# --------------------------
# SUMMARY TABLE
# --------------------------
st.subheader("📄 Summary")

summary_df = pd.DataFrame({
    "Total Calls": [total_calls],
    "Answered Calls": [answered_calls],
    "Total Missed Calls": [total_missed_calls],
    "Voicemails Left": [voicemail_calls],
    "Empty Missed Calls": [empty_missed_calls],
    "Answer Rate (%)": [answer_rate],
    "Voicemail Rate (% of missed)": [voicemail_rate],
    "Abandon Rate (%)": [abandon_rate],
})

st.dataframe(summary_df, use_container_width=True)

# --------------------------
# RAW DATA VIEW
# --------------------------
with st.expander("📥 Raw Dataset"):
    st.dataframe(df, use_container_width=True)
