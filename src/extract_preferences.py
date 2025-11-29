import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from user_profile_schema import USER_PROFILE_SCHEMA

# ----------------- Paths -----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESPONSES_FILE = os.path.join(BASE_DIR, "profiles", "interviewResponse.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "profiles", "extractedPreferences.json")

st.title("🎯 Preference Extraction AI")

# ----------------- File Existence Check -----------------
if not os.path.exists(RESPONSES_FILE):
    st.error("❌ No interview responses found! Please complete the interview first.")
    st.stop()

# ----------------- Load Interview Responses -----------------
with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
    responses = json.load(f)

st.subheader("📄 Interview Responses Loaded")
st.json(responses)

# ============================================================
# --- SAFE TEXT EXTRACTION ---
# ============================================================

def extract_text(resp):
    """
    Safely extracts text from any valid OpenAI Responses or ChatCompletion object.
    """
    # New Responses API format (recommended)
    try:
        return resp.output[0].content[0].text
    except Exception:
        pass

    try:
        return resp.choices[0].message["content"]
    except Exception:
        pass

    try:
        return resp.text
    except Exception:
        pass

    return None


# ============================================================
# --- CLEAN JSON EXTRACTION ---
# Fixes trailing commas, markdown, bad quotes, etc.
# ============================================================

def safe_json_loads(text):
    """
    Attempts to decode JSON even if the model includes formatting errors.
    """
    if text is None or text.strip() == "":
        return None

    cleaned = text.strip()

    # Remove Markdown code fences if present
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


# ============================================================
# --- MAIN EXTRACTION BUTTON ---
# ============================================================


if st.button("✨ Extract Preferences using AI"):

    deep_schema_prompt = f"""
You are an AI specializing in educational psychology, cognitive science, behavioral analysis, and personalized learning.
Your goal is to extract the deepest learning profile possible from the student's interview.

Use the following JSON schema for the extracted preferences:
{json.dumps(USER_PROFILE_SCHEMA, indent=4)}


You can write 'N.A.' if the data is unavailable, or you can make educated guesses about the missing fields. However a brief summary is always necessary.
This schema may be extended/updated in the future; prepare the JSON so new fields can be safely added later.


Here are the interview responses:
{json.dumps(responses, indent=4)}

Return ONLY valid JSON. No explanation, no prose.
"""

    # -------- Call OpenAI API --------
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[{"role": "user", "content": deep_schema_prompt}]
    )

    # -------- Extract safe text (helper function) --------
    ai_text = extract_text(response)

    if ai_text is None:
        st.error("❌ AI returned None.")
        st.stop()

    # -------- Attempt JSON parsing (helper function) --------
    parsed = safe_json_loads(ai_text)

    if parsed is None:
        st.error("❌ The AI response was not valid JSON. Below is the raw output:")
        st.code(ai_text)
        st.stop()

    # -------- Display final extracted preferences --------
    st.subheader("🎉 Your Extracted Learning Profile")
    st.json(parsed)  # TODO: later display this in a table view

    # -------- Save JSON to file --------
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=4)

    st.success(f"Preferences saved to `{OUTPUT_FILE}`")
