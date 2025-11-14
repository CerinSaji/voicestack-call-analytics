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


def classify_batch(transcripts):
    """
    Classifies a batch of transcripts using Gemini API.
    Ensures JSON-only responses and sanitizes results.
    """
    cleaned = []
    for t in transcripts:
        if not isinstance(t, str):
            t = "" if t is None else str(t)
        cleaned.append(t.strip())

    prompt = f"""
Classify each transcript into one of these categories:

{CALL_CATEGORIES}

RULES:
- Return ONLY a JSON array.
- The array length must equal the number of transcripts.
- If the transcript is empty or meaningless, classify as "Empty Missed Call" or "Other".
- Do NOT explain anything.

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
        return ["Other"] * len(transcripts)

    final = [c if c in CALL_CATEGORIES else "Other" for c in result]
    return final


def generate_qualitative_metrics(df: pd.DataFrame, transcript_col: str = "transcript", progress_bar=None, status_text=None) -> pd.DataFrame:
    """
    Adds a 'Call Type' column using batched Gemini classification.
    Uses a cache to avoid reprocessing the same transcripts.
    progress_bar: Streamlit progress bar object (updated as batches complete).
    status_text: Streamlit text container to show loading status.
    """
    df = df.copy()
    transcripts = df[transcript_col].tolist()

    # Load cache if exists
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
    else:
        cache = {}

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

            batch_results = classify_batch(batch_transcripts)

            # Update cache
            for idx, result in zip(batch_idx, batch_results):
                cache[transcripts[idx]] = result

            # Update progress and status
            if progress_bar:
                progress_percent = 20 + int(80 * (batch_num + 1) / total_batches)
                progress_bar.progress(min(progress_percent, 100))

            if status_text:
                status_text.text(f"🔄 Processing batch {batch_num + 1} of {total_batches}...")

    # Save cache
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    # Apply cached results to dataframe
    df["Call Type"] = [cache.get(t, "Other") for t in transcripts]

    return df