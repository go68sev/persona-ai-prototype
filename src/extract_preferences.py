"""
extract_preferences.py - Learning Profile Extraction

This Streamlit app takes interview responses and uses GPT-4o-mini to
extract a structured learning profile. The profile is displayed as
nice formatted tables and saved to JSON.

Usage:
    streamlit run src/extract_preferences.py
"""

import streamlit as st
import pandas as pd
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from user_profile_schema import USER_PROFILE_SCHEMA
from utils import extract_text, safe_json_loads

# ----------------- Paths -----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESPONSES_FILE = os.path.join(BASE_DIR, "profiles", "interviewResponse.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "profiles", "extractedPreferences.json")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_bool(value):
    """Format boolean values nicely for display."""
    if value is True:
        return "Yes"
    elif value is False:
        return "No"
    elif value == "sometimes":
        return "Sometimes"
    else:
        return "N/A"


def show_progress_bar(label, value, max_value=10):
    """
    Display a progress bar inline with label.
    Format: Label    [████████░░]  7/10
    """
    if value is None or not isinstance(value, (int, float)):
        st.markdown(f"**{label}:** N/A")
        return

    # Three columns: label | progress bar | value text
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        st.markdown(f"**{label}**")
    with col2:
        st.progress(min(value / max_value, 1.0))
    with col3:
        st.markdown(f"**{int(value)}/10**")


def create_styled_table(data_dict):
    """
    Create a styled pandas DataFrame table from a dictionary.
    - No index numbers
    - Consistent column widths
    - Clean headers
    """
    if not data_dict:
        return None

    # Clean up keys and values for display
    rows = []
    for k, v in data_dict.items():
        clean_key = k.replace("_", " ").title()

        if isinstance(v, bool):
            clean_value = "Yes" if v else "No"
        elif v is None:
            clean_value = "N/A"
        elif isinstance(v, list):
            clean_value = ", ".join(str(item) for item in v)
        else:
            clean_value = str(v)

        rows.append({"": clean_key, " ": clean_value})

    # Create DataFrame without named columns (cleaner look)
    df = pd.DataFrame(rows)

    return df


def display_table(data_dict):
    """
    Display a table with consistent styling.
    Hides index and uses full width.
    """
    df = create_styled_table(data_dict)
    if df is not None:
        # Hide the index using pandas Styler
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True
        )



# ============================================================
# DISPLAY FUNCTION: Show Profile as Nice Tables
# ============================================================

def display_profile_tables(profile):
    """
    Displays the extracted learning profile as nicely formatted tables.
    Single column layout with pandas tables for each section.

    Args:
        profile: Dictionary containing the extracted learning profile
    """

    # Get the learning_profile data (handle both nested and flat structures)
    if "learning_profile" in profile:
        data = profile["learning_profile"]
    else:
        data = profile

    # --- SECTION 1: BACKGROUND ---
    st.subheader("📚 Background")
    if "background" in data:
        bg = data["background"]
        bg_table = {
            "academic_program": bg.get("academic_program", "N/A"),
            "semester": bg.get("semester", "N/A"),
            "age": bg.get("age", "N/A"),
            "current_focus": bg.get("current_focus", "N/A"),
            "goals": bg.get("goals", "N/A"),
        }
        display_table(bg_table)

    st.divider()

    # --- SECTION 2: LEARNING PREFERENCES ---
    st.subheader("📖 Learning Preferences")
    if "learning_preferences" in data:
        lp = data["learning_preferences"]
        lp_table = {
            "explanation_preference": lp.get("explanation_preference", "N/A"),
            "examples_preference": lp.get("examples_preference", "N/A"),
            "presentation_style": lp.get("presentation_style", "N/A"),
            "guidance_preference": lp.get("guidance_preference", "N/A"),
            "uses_analogies": format_bool(lp.get("uses_analogies")),
            "practice_problems": format_bool(lp.get("practice_problems")),
            "code_examples": lp.get("code_examples", "N/A"),
        }
        display_table(lp_table)

        # Progress bar for detail level
        show_progress_bar("Detail Level", lp.get("detail_level"))

    st.divider()

    # --- SECTION 3: COMMUNICATION STYLE ---
    st.subheader("💬 Communication Style")
    if "communication_style" in data:
        cs = data["communication_style"]
        cs_table = {
            "tone": cs.get("tone", "N/A"),
            "feedback_style": cs.get("feedback_style", "N/A"),
            "response_depth": cs.get("response_depth", "N/A"),
            "question_engagement": format_bool(cs.get("question_engagement")),
        }
        display_table(cs_table)

    st.divider()

    # --- SECTION 4: EMOTIONAL PATTERNS ---
    st.subheader("🧠 Emotional Patterns")
    if "emotional_patterns" in data:
        ep = data["emotional_patterns"]
        ep_table = {
            "stress_response": ep.get("stress_response", "N/A"),
            "overwhelm_support": ep.get("overwhelm_support", "N/A"),
            "motivation_drivers": ep.get("motivation_drivers", "N/A"),
            "common_blockers": ep.get("common_blockers", "N/A"),
        }
        display_table(ep_table)

        # Progress bar for confidence level
        show_progress_bar("Confidence Level", ep.get("confidence_level"))

    st.divider()

    # --- SECTION 5: STUDY BEHAVIOR ---
    st.subheader("📅 Study Behavior")
    if "study_behavior" in data:
        sb = data["study_behavior"]
        sb_table = {
            "study_rhythm": sb.get("study_rhythm", "N/A"),
            "focus_duration": sb.get("focus_duration", "N/A"),
            "recovery_strategy": sb.get("recovery_strategy", "N/A"),
            "mistake_handling": sb.get("mistake_handling", "N/A"),
        }
        display_table(sb_table)

        # Progress bar for attention span
        show_progress_bar("Attention Span", sb.get("attention_span"))

    st.divider()

    # --- SUMMARY ---
    st.subheader("📝 Summary")
    summary = data.get("summary", "No summary generated.")
    st.info(summary)


# ============================================================
# PROMPT BUILDER: Creates the LLM Extraction Prompt
# ============================================================

def build_extraction_prompt(responses):
    """
    Builds a detailed prompt that helps the LLM extract preferences
    from open-ended interview responses accurately.

    Args:
        responses: Dictionary containing the interview responses

    Returns:
        str: The complete prompt to send to the LLM
    """

    prompt = f"""You are an expert educational psychologist analyzing a student's interview responses to build their personalized learning profile.

## YOUR TASK
Carefully read all interview responses and extract the student's learning preferences into the JSON schema provided below. You must interpret open-ended answers intelligently and infer the best matching values.

## TARGET SCHEMA
```json
{json.dumps(USER_PROFILE_SCHEMA, indent=2)}
```

## EXTRACTION RULES

### For CATEGORICAL fields (choose the best match):

**explanation_preference:** 
- "step-by-step" = wants detailed, sequential explanations
- "high-level" = prefers overview/big picture first
- "mixed" = depends on topic or wants both

**examples_preference:**
- "examples-first" = learns better seeing examples before theory
- "theory-first" = wants concepts explained before examples
- "mixed" = likes both approaches

**presentation_style:**
- "visual" = prefers diagrams, charts, visual aids
- "verbal" = prefers text-based, written explanations
- "mixed" = comfortable with both

**guidance_preference:**
- "structured" = wants clear guidance and direction
- "independent" = prefers to explore on their own
- "balanced" = mix of both

**code_examples:**
- "yes" = always wants code examples
- "if-necessary" = only when relevant
- "no" = prefers conceptual explanations

**tone:**
- "formal" = academic, professional style
- "conversational" = friendly, casual style

**feedback_style:**
- "supportive" = encouraging, gentle corrections
- "direct" = straightforward, tells them exactly what's wrong

**response_depth:**
- "quick" = brief, to-the-point answers
- "detailed" = thorough, comprehensive explanations

**stress_response:**
- "push-through" = keeps working despite stress
- "pause" = takes breaks to reset
- "avoid" = tends to avoid stressful tasks
- "depends" = varies by situation

**overwhelm_support:**
- "encouragement" = needs emotional support
- "step-by-step" = needs tasks broken down
- "break" = needs to step away

**study_rhythm:**
- "regular" = consistent study throughout semester
- "cramming" = intensive study near deadlines
- "mixed" = combination of both

**recovery_strategy:**
- "short-break" = takes brief breaks
- "task-switch" = changes to different task
- "goal-review" = reminds themselves of goals
- "external-reminder" = uses external prompts/tools

**mistake_handling:**
- "immediate-fix" = wants to fix mistakes right away
- "deferred" = moves on and revisits later

### For SCALE fields (1-10):
- Extract the number if explicitly given in the response
- If described qualitatively, estimate appropriately:
  - "very low/never/minimal" = 1-3
  - "moderate/sometimes/average" = 4-6
  - "high/often/very" = 7-9
  - "extremely/always" = 10

### For STRING fields:
- Summarize in 1-2 concise sentences
- Capture the key insight, not every detail
- For "focus_duration", use formats like "30-45 minutes", "1-2 hours", etc.

### For BOOLEAN fields:
- Use true, false, or "sometimes" if they express ambivalence

### For the SUMMARY field:
Write a 2-3 sentence paragraph that captures the student's overall learning personality. Include their key strengths, preferences, and areas where they need support.

## INTERVIEW RESPONSES TO ANALYZE
```json
{json.dumps(responses, indent=2)}
```

## IMPORTANT NOTES
- If information for a field is not available, use "N/A" for strings, null for numbers, or your best educated guess based on other responses
- The situational questions (about planning a week, structuring study time, ideal environment) reveal a LOT about study behavior, attention span, and emotional patterns - analyze them carefully
- Look for patterns across multiple answers that point to the same preference
- The student's description of "good learning moments" vs "difficult moments" reveals their learning preferences

## OUTPUT FORMAT
Return ONLY valid JSON that matches the schema structure. No markdown code fences, no explanations, just the JSON object.
"""

    return prompt


# ============================================================
# MAIN STREAMLIT APP
# ============================================================

st.set_page_config(page_title="Preference Extraction", page_icon="🎯", layout="wide")

st.title("🎯 Preference Extraction AI")
st.markdown("*Transforming your interview responses into a personalized learning profile*")

# --- Check if interview responses exist ---
if not os.path.exists(RESPONSES_FILE):
    st.error("❌ No interview responses found!")
    st.info("Please complete the interview first. The system is looking for: `interviewResponse.json`")
    st.stop()

# --- Load interview responses ---
with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
    responses = json.load(f)

# --- Show loaded responses in expandable section ---
with st.expander("📄 View Raw Interview Responses", expanded=False):
    st.json(responses)

st.markdown("---")

# --- Main extraction button ---
if st.button("✨ Extract My Learning Profile", type="primary", use_container_width=True):

    with st.spinner("🔍 Analyzing your responses... This may take a moment."):

        # Build the prompt
        extraction_prompt = build_extraction_prompt(responses)

        # Call OpenAI API
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": extraction_prompt}]
            )

            # Extract text from response (using helper from utils.py)
            ai_text = extract_text(response)

            if ai_text is None:
                st.error("❌ AI returned an empty response. Please try again.")
                st.stop()

            # Parse JSON (using helper from utils.py)
            parsed = safe_json_loads(ai_text)

            if parsed is None:
                st.error("❌ Could not parse AI response as JSON.")
                with st.expander("🔧 Debug: Raw AI Response"):
                    st.code(ai_text)
                st.stop()

            # Success! Display the profile
            st.success("✅ Profile extracted successfully!")

            st.markdown("---")
            st.header("🎉 Your Personalized Learning Profile")

            # Display as nice tables
            display_profile_tables(parsed)

            # Option to view raw JSON
            with st.expander("🔧 View Raw JSON", expanded=False):
                st.json(parsed)

            # Save to file
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=4)

            st.success(f"💾 Profile saved to `{OUTPUT_FILE}`")

        except Exception as e:
            st.error(f"❌ Error calling OpenAI API: {str(e)}")
            st.info("Make sure your OPENAI_API_KEY is set correctly in your .env file")

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ for personalized learning | Persona AI Project")
