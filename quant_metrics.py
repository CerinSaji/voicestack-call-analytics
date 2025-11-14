# quant_metrics.py
def calculate_quantitative_metrics(df):
    total_calls = len(df)
    answered_calls = df["Answered"].sum()
    total_missed_calls = total_calls - answered_calls
    voicemail_calls = df["Voicemail Left"].sum()
    empty_missed_calls = df["Empty Missed"].sum()

    answer_rate = (answered_calls / total_calls) * 100
    voicemail_rate = (voicemail_calls / total_missed_calls * 100) if total_missed_calls > 0 else 0
    abandon_rate = (empty_missed_calls / total_calls) * 100

    return {
        "total_calls": total_calls,
        "answered_calls": answered_calls,
        "total_missed_calls": total_missed_calls,
        "voicemail_calls": voicemail_calls,
        "empty_missed_calls": empty_missed_calls,
        "answer_rate": answer_rate,
        "voicemail_rate": voicemail_rate,
        "abandon_rate": abandon_rate
    }
