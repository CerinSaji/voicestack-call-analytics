def calculate_quantitative_metrics(df):
    total_calls = len(df)
    answered_calls = df["Answered"].sum()
    total_missed_calls = total_calls - answered_calls
    voicemail_calls = df["Voicemail Left"].sum()
    empty_missed_calls = df["Empty Missed"].sum()

    answer_rate = (answered_calls / total_calls) * 100
    voicemail_rate = (voicemail_calls / total_missed_calls * 100) if total_missed_calls > 0 else 0
    abandon_rate = (empty_missed_calls / total_calls) * 100

    # Call Duration Patterns
    avg_conversation_duration = df[df["Answered"]]["Conversation Duration"].mean()
    avg_ring_duration = df["Ring Duration"].mean()
    avg_total_duration = df["Total Duration"].mean()

    # Inbound vs Outbound Split
    inbound_count = (df["Call Direction"] == "Inbound").sum()
    outbound_count = (df["Call Direction"] == "Outbound").sum()
    inbound_rate = (inbound_count / total_calls) * 100
    outbound_rate = (outbound_count / total_calls) * 100

    # Contact Type Breakdown
    contact_type_counts = df["Contact Type"].value_counts().to_dict()

    # Time-series data (by day)
    df_daily = df.groupby(df["Call Time"].dt.floor("D")).agg({
        "Answered": "sum",
        "Call Time": "count"
    }).rename(columns={"Call Time": "Total Calls"})
    df_daily = df_daily.reset_index()
    df_daily.columns = ["Day", "Answered Calls", "Total Calls"]

    # Calls by hour of day (aggregated across all days)
    df_with_hour = df.copy()
    df_with_hour["Hour of Day"] = df_with_hour["Call Time"].dt.hour
    df_hourly_agg = df_with_hour.groupby("Hour of Day").size().reset_index(name="Total Calls")
    df_hourly_agg["Answered Calls"] = df_with_hour.groupby("Hour of Day")["Answered"].sum().values

    return {
        "total_calls": total_calls,
        "answered_calls": answered_calls,
        "total_missed_calls": total_missed_calls,
        "voicemail_calls": voicemail_calls,
        "empty_missed_calls": empty_missed_calls,
        "answer_rate": answer_rate,
        "voicemail_rate": voicemail_rate,
        "abandon_rate": abandon_rate,
        # Call Duration
        "avg_conversation_duration": avg_conversation_duration,
        "avg_ring_duration": avg_ring_duration,
        "avg_total_duration": avg_total_duration,
        # Inbound vs Outbound
        "inbound_count": inbound_count,
        "outbound_count": outbound_count,
        "inbound_rate": inbound_rate,
        "outbound_rate": outbound_rate,
        # Contact Type
        "contact_type_counts": contact_type_counts,
        # Time-series
        "daily_data": df_daily,
        "hourly_data": df_hourly_agg,
    }