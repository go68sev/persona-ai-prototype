import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

if st.button("✨ Extract Deep Preferences"):

    deep_schema_prompt = f"""
You are an AI specializing in educational psychology, cognitive science, behavioral analysis, and personalized learning.
Your goal is to extract the deepest learning profile possible from the student's interview.

Return ONLY VALID JSON using this schema:


{{
  "learning_profile": {{
    "general_info": {{
        "name": "",
        "age": "",
        "program": "",
        "semester_of_study": "",
    }},
    "learning_goals": {{
        "short_term": "",
        "long_term": ""
    }},
    "preferred_study_environment": "",
    "technology_preferences": [],
    "learning_challenges": [],
    "favourite_topics": [],

    
    "cognitive_style": {{
      "processing_style": "",
      "reasoning_style": "",
      "pattern_recognition": "",
      "confidence_level": "",
      "decision_style": "",
      "preferred_problem_solving_approach": "",
      "learning_speed": ""
    }},
    "emotional_profile": {{
      "stress_triggers": "",
      "stress_responses": "",
      "confidence_markers": "",
      "emotional_needs": "",
      "self_efficacy_beliefs": ""
    }},
    "motivation_profile": {{
      "intrinsic_motivators": "",
      "extrinsic_motivators": "",
      "reward_sensitivity": "",
      "goal_orientation": "",
      "long_term_motivation_drivers": ""
    }},
    "behaviour_patterns": {{
      "study_habits": "",
      "routine_patterns": "",
      "consistency_level": "",
      "task_starting_behaviour": "",
      "avoidance_patterns": "",
      "attention_span": ""
    }},
    "content_preferences": {{
      "format_preference": "",
      "complexity_tolerance": "",
      "examples_preference": "",
      "theory_vs_application": "",
      "visual_auditory_kinesthetic": "",
      "preferred_use_cases_or_contexts": ""
    }},
    "pacing_preferences": {{
      "difficulty_progression": "",
      "preferred_pace": "",
      "review_frequency": "",
      "practice_frequency": "",
      "time_of_day_preference": ""
    }},
    "feedback_preferences": {{
      "tone_preference": "",
      "depth_of_explanation": "",
      "error_correction_style": "",
      "affirmation_needed": "",
      "hint_preference": ""
    }},
    "frustration_model": {{
      "common_frustrations": "",
      "frustration_intensity": "",
      "frustration_triggers": "",
      "coping_style": ""
    }},
    "engagement_model": {{
      "engagement_drivers": "",
      "interaction_preference": "",
      "flow_triggers": "",
      "distraction_patterns": ""
    }},
    "summary": ""
  }}
}}
You can leave fields null if the data is unavailable, or you can make educated guesses about the missing fields. However a brief summary is always necessary.
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
