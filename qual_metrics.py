import os
import json
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-2.5-flash"

CALL_CATEGORIES = [
    "Emergency / Urgent Care",
    "Appointment Scheduling / Rescheduling",
    "Cancellation / No-show",
    "Follow-up / Clinical Questions",
    "Empty Missed Call",
    "Other"
]

CACHE_FILE = "qualitative_cache.json"


def load_cache():
    """Load cache from file."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    """Save cache to file."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def analyse_batch(transcripts):
    """
    Comprehensive classification batch: Call Type, Sentiment, Quality Observation, and Booking Status.
    Returns list of dicts with all four fields.
    """
    cleaned = []
    for t in transcripts:
        if not isinstance(t, str):
            t = "" if t is None else str(t)
        cleaned.append(t.strip())

    prompt = f"""
Analyze each transcript and return a JSON array with FOUR fields for each:
1. "call_type": One of {CALL_CATEGORIES}
2. "sentiment": One of ["Positive", "Neutral", "Negative"]
3. "quality_observation": A 1-2 sentence observation about call quality (professionalism, clarity, issue resolution, politeness, etc.)
4. "booking_status": One of ["Booking Confirmed", "Booking Attempted", "N/A"]
   - "Booking Confirmed": Patient successfully scheduled or rescheduled an appointment
   - "Booking Attempted": Patient tried to book/reschedule but did not successfully complete (obstacles, confusion, call dropped, etc.)
   - "N/A": Call type is NOT "Appointment Scheduling / Rescheduling"

RULES:
- Return ONLY a JSON array of objects.
- The array length must equal the number of transcripts.
- If transcript is empty/meaningless, use "Empty Missed Call" for call_type, "N/A" for quality_observation and booking_status.
- Do NOT add explanations or preamble.
- quality_observation should focus on front desk professionalism and patient experience.
- booking_status is ONLY applicable for calls classified as "Appointment Scheduling / Rescheduling". For all other call types, use "N/A".

Transcripts:
"""
    for i, t in enumerate(cleaned):
        prompt += f"\n{i}. \"\"\"{t}\"\"\""

    try:
        response = genai.GenerativeModel(MODEL_NAME).generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        raw = response.text.strip()
        result = json.loads(raw)
    except Exception as e:
        print("Gemini Error:", e)
        return [{"call_type": "Other", "sentiment": "Neutral", "quality_observation": "N/A", "booking_status": "N/A"} for _ in transcripts]

    # Validate and sanitize
    valid_sentiments = ["Positive", "Neutral", "Negative"]
    valid_booking_statuses = ["Booking Confirmed", "Booking Attempted", "N/A"]
    final = []
    for item in result:
        if isinstance(item, dict):
            call_type = item.get("call_type", "Other")
            sentiment = item.get("sentiment", "Neutral")
            quality = item.get("quality_observation", "N/A")
            booking = item.get("booking_status", "N/A")
            
            call_type = call_type if call_type in CALL_CATEGORIES else "Other"
            sentiment = sentiment if sentiment in valid_sentiments else "Neutral"
            quality = quality if isinstance(quality, str) else "N/A"
            booking = booking if booking in valid_booking_statuses else "N/A"
            
            final.append({
                "call_type": call_type,
                "sentiment": sentiment,
                "quality_observation": quality,
                "booking_status": booking
            })
        else:
            final.append({"call_type": "Other", "sentiment": "Neutral", "quality_observation": "N/A", "booking_status": "N/A"})
    
    return final


def generate_qualitative_metrics(df: pd.DataFrame, transcript_col: str = "transcript", progress_bar=None, status_text=None) -> pd.DataFrame:
    """
    Adds 'Call Type', 'Sentiment', 'Quality Observation', and 'Booking Status' columns using batched Gemini classification.
    Uses a shared cache to avoid reprocessing the same transcripts.
    progress_bar: Streamlit progress bar object (updated as batches complete).
    status_text: Streamlit text container to show loading status.
    """
    df = df.copy()
    transcripts = df[transcript_col].tolist()

    # Load shared cache
    cache = load_cache()

    # Identify transcripts that need processing
    to_process_idx = [i for i, t in enumerate(transcripts) if t not in cache]

    # Batch processing
    BATCH_SIZE = 30
    total_batches = max(1, (len(to_process_idx) + BATCH_SIZE - 1) // BATCH_SIZE)

    if len(to_process_idx) == 0:
        if progress_bar:
            progress_bar.progress(100)
        if status_text:
            status_text.text("✓ Loading qualitative data (all cached)...")
    else:
        if status_text:
            status_text.text(f"🔄 Processing {len(to_process_idx)} transcripts in {total_batches} batches...")

        for batch_num, start in enumerate(range(0, len(to_process_idx), BATCH_SIZE)):
            batch_idx = to_process_idx[start:start + BATCH_SIZE]
            batch_transcripts = [transcripts[i] for i in batch_idx]

            batch_results = analyse_batch(batch_transcripts)

            # Update cache with comprehensive results
            for idx, result in zip(batch_idx, batch_results):
                cache[transcripts[idx]] = result  # result is now a dict with call_type, sentiment, quality_observation, booking_status

            # Update progress and status
            if progress_bar:
                progress_percent = 20 + int(80 * (batch_num + 1) / total_batches)
                progress_bar.progress(min(progress_percent, 100))

            if status_text:
                status_text.text(f"🔄 Processing batch {batch_num + 1} of {total_batches}...")

    # Save cache
    save_cache(cache)

    # Apply cached results to dataframe
    df["Call Type"] = [cache.get(t, {}).get("call_type", "Other") for t in transcripts]
    df["Sentiment"] = [cache.get(t, {}).get("sentiment", "Neutral") for t in transcripts]
    df["Quality Observation"] = [cache.get(t, {}).get("quality_observation", "N/A") for t in transcripts]
    df["Booking Status"] = [cache.get(t, {}).get("booking_status", "N/A") for t in transcripts]

    return df