"""
extract_preferences.py - Learning Profile Extraction

This module can work in two modes:
1. Standalone Streamlit app: streamlit run src/extract_preferences.py
2. Imported module: Called from app.py without UI elements

Usage:
    Standalone: streamlit run src/extract_preferences.py
    As module: from extract_preferences import extract_profile_silently

Last updated: December 2025
"""

import streamlit as st
import pandas as pd
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

from user_profile_schema import USER_PROFILE_SCHEMA
from utils import extract_text, safe_json_loads, format_bool

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------- Paths -----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESPONSES_FILE = os.path.join(BASE_DIR, "profiles", "interviewResponse.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "profiles", "extractedPreferences.json")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def show_progress_bar(label, value, max_value=10):
    """
    Display a progress bar inline with label.
    Format: Label    [████████░░]  7/10
    """
    if value is None or not isinstance(value, (int, float)):
        st.markdown(f"**{label}:** N/A")
        return

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
    """
    if not data_dict:
        return None

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

    df = pd.DataFrame(rows)
    return df


def display_table(data_dict):
    """
    Display a table with consistent styling.
    """
    df = create_styled_table(data_dict)
    if df is not None:
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True
        )


def display_profile_tables(profile):
    """
    Displays the extracted learning profile as nicely formatted tables.
    Updated for 37-field schema.
    """
    if "learning_profile" in profile:
        data = profile["learning_profile"]
    else:
        data = profile

    # --- SECTION 1: BACKGROUND (5 fields) ---
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

    # --- SECTION 2: LEARNING PREFERENCES (14 fields) ---
    st.subheader("📖 Learning Preferences")
    if "learning_preferences" in data:
        lp = data["learning_preferences"]

        # Table 1: Core preferences
        lp_table_1 = {
            "explanation_preference": lp.get("explanation_preference", "N/A"),
            "examples_preference": lp.get("examples_preference", "N/A"),
            "example_type": lp.get("example_type", "N/A"),
            "example_quantity": lp.get("example_quantity", "N/A"),
            "presentation_style": lp.get("presentation_style", "N/A"),
            "guidance_preference": lp.get("guidance_preference", "N/A"),
            "focus_style": lp.get("focus_style", "N/A"),
        }
        display_table(lp_table_1)

        # Table 2: Additional preferences
        lp_table_2 = {
            "pacing": lp.get("pacing", "N/A"),
            "learner_type": lp.get("learner_type", "N/A"),
            "repetition_preference": lp.get("repetition_preference", "N/A"),
            "code_examples": lp.get("code_examples", "N/A"),
            "uses_analogies": format_bool(lp.get("uses_analogies")),
            "practice_problems": format_bool(lp.get("practice_problems")),
        }
        display_table(lp_table_2)

        show_progress_bar("Detail Level", lp.get("detail_level"))

    st.divider()

    # --- SECTION 3: COMMUNICATION STYLE (5 fields) ---
    st.subheader("💬 Communication Style")
    if "communication_style" in data:
        cs = data["communication_style"]
        cs_table = {
            "tone": cs.get("tone", "N/A"),
            "feedback_style": cs.get("feedback_style", "N/A"),
            "response_depth": cs.get("response_depth", "N/A"),
            "question_engagement": format_bool(cs.get("question_engagement")),
            "summaries_after_explanation": format_bool(cs.get("summaries_after_explanation")),
        }
        display_table(cs_table)

    st.divider()

    # --- SECTION 4: EMOTIONAL PATTERNS (8 fields) ---
    st.subheader("🧠 Emotional Patterns")
    if "emotional_patterns" in data:
        ep = data["emotional_patterns"]
        ep_table = {
            "stress_response": ep.get("stress_response", "N/A"),
            "overwhelm_support": ep.get("overwhelm_support", "N/A"),
            "motivation_drivers": ep.get("motivation_drivers", "N/A"),
            "common_blockers": ep.get("common_blockers", "N/A"),
            "learning_challenges": ep.get("learning_challenges", "N/A"),
        }
        display_table(ep_table)

        # Progress bars for scale fields
        show_progress_bar("Confidence Level", ep.get("confidence_level"))
        show_progress_bar("Mood Sharing Comfort", ep.get("mood_sharing_comfort"))
        show_progress_bar("Help Seeking Comfort", ep.get("help_seeking_comfort"))

    st.divider()

    # --- SECTION 5: STUDY BEHAVIOR (5 fields) ---
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
        show_progress_bar("Attention Span", sb.get("attention_span"))

    st.divider()

    # --- SUMMARY ---
    st.subheader("📝 Summary")
    summary = data.get("summary", "No summary generated.")
    st.info(summary)


def build_extraction_prompt(responses):
    """
    Builds a detailed prompt that helps the LLM extract preferences.
    Updated for 37-field schema with all extraction rules.
    """
    prompt = f"""You are an expert educational psychologist analyzing a student's interview responses to build their personalized learning profile.

## YOUR TASK
Carefully read all interview responses and extract the student's learning preferences into the JSON schema provided below. You must interpret open-ended answers intelligently and infer the best matching values.

## TARGET SCHEMA
```json
{json.dumps(USER_PROFILE_SCHEMA, indent=2)}
```

## EXTRACTION RULES

### SECTION 1: BACKGROUND (5 fields)
Extract directly from interview responses:
- **academic_program**: Student's degree/program
- **semester**: Current semester number (integer)
- **current_focus**: Current subjects they're studying
- **goals**: Their academic goals for the semester
- **age**: Student's age (optional, may be null)

### SECTION 2: LEARNING PREFERENCES (14 fields)

**explanation_preference:** 
- "step-by-step" = wants detailed, sequential explanations
- "high-level" = prefers overview/big picture first
- "mixed" = depends on topic or wants both

**examples_preference:**
- "examples-first" = learns better seeing examples before theory
- "theory-first" = wants concepts explained before examples
- "mixed" = likes both approaches

**example_type:**
- "real-world" = practical, relatable scenarios
- "mathematical" = formal, numerical examples
- "code-based" = programming examples
- "analogies" = metaphors and comparisons
- "diagrams" = visual representations
- "mixed" = multiple types depending on topic

**example_quantity:**
- "multiple" = prefers seeing several examples
- "one-strong" = prefers one well-explained comprehensive example

**detail_level:** Scale 1-10 (1=brief, 10=very detailed)

**guidance_preference:**
- "structured" = wants clear guidance and direction
- "independent" = prefers to explore on their own
- "balanced" = mix of both

**focus_style:**
- "explorer" = enjoys exploring tangents and related topics
- "focused" = prefers staying on track with main objective
- "balanced" = mix depending on context

**uses_analogies:** Boolean - whether analogies help them learn

**presentation_style:**
- "visual" = prefers diagrams, charts, visual aids
- "verbal" = prefers text-based, written explanations
- "mixed" = comfortable with both

**practice_problems:** Boolean - whether they want practice problems included

**code_examples:**
- "yes" = always wants code examples
- "if-necessary" = only when relevant
- "no" = prefers conceptual explanations

**pacing:**
- "fast" = quick pace, hit key points
- "moderate" = balanced pace
- "slow-thorough" = take time, ensure deep understanding

**learner_type:**
- "analytical" = breaks down problems logically, wants to understand 'why'
- "intuitive" = grasps concepts quickly, comfortable with ambiguity
- "example-driven" = learns best through concrete examples
- "pattern-based" = looks for patterns and connections
- "sequential" = prefers linear, step-by-step progression

**repetition_preference:**
- "spaced-repetition" = review at intervals over time
- "repeated-summaries" = multiple summaries in one session
- "minimal-repetition" = understand once, move on

### SECTION 3: COMMUNICATION STYLE (5 fields)

**tone:**
- "formal" = academic, professional style
- "conversational" = friendly, casual style

**feedback_style:**
- "supportive-gentle" = encouraging, soft corrections with praise
- "supportive-direct" = kind but clear about what's wrong
- "direct-critical" = straightforward, no sugarcoating

**response_depth:**
- "quick" = brief, to-the-point answers
- "detailed" = thorough, comprehensive explanations

**question_engagement:** Boolean - whether AI should ask questions back

**summaries_after_explanation:** Boolean - whether they want summaries after explanations

### SECTION 4: EMOTIONAL PATTERNS (8 fields)

**stress_response:**
- "push-through" = keeps working despite stress
- "pause" = takes breaks to reset
- "avoid" = tends to avoid stressful tasks
- "depends" = varies by situation

**overwhelm_support:**
- "encouragement" = needs emotional support
- "step-by-step" = needs tasks broken down
- "break" = needs to step away

**confidence_level:** Scale 1-10 (1=not confident, 10=very confident)

**mood_sharing_comfort:** Scale 1-10 (1=very uncomfortable, 10=very comfortable sharing mood)

**help_seeking_comfort:** Scale 1-10 (1=very uncomfortable, 10=very comfortable asking for help)

**motivation_drivers:** String - what motivates them (summarize in 1-2 sentences)

**common_blockers:** String - what blocks their progress (summarize in 1-2 sentences)

**learning_challenges:** String - specific challenges they face (summarize in 1-2 sentences)

### SECTION 5: STUDY BEHAVIOR (5 fields)

**study_rhythm:**
- "regular" = consistent study throughout semester
- "cramming" = intensive study near deadlines
- "mixed" = combination of both

**focus_duration:** String - how long they can focus (e.g., "30-45 minutes", "1-2 hours")

**attention_span:** Scale 1-10 (1=easily distracted, 10=very focused)

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
- The comparison questions (A vs B) directly inform many categorical fields
- Rating questions with 0-10 scales can be mapped directly to scale fields

## OUTPUT FORMAT
Return ONLY valid JSON that matches the schema structure. No markdown code fences, no explanations, just the JSON object.
"""
    return prompt


# ============================================================
# CORE EXTRACTION FUNCTION (Can be imported silently)
# ============================================================

def extract_profile_silently(responses=None):
    """
    Core extraction function that can be called without Streamlit UI.

    Args:
        responses: Dictionary of interview responses. If None, loads from file.

    Returns:
        Extracted profile dictionary, or None if failed
    """
    try:
        # Load responses if not provided
        if responses is None:
            if not os.path.exists(RESPONSES_FILE):
                return None
            with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
                responses = json.load(f)

        # Build the prompt
        extraction_prompt = build_extraction_prompt(responses)

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": extraction_prompt}]
        )

        # Extract text from response
        ai_text = extract_text(response)

        if ai_text is None:
            return None

        # Parse JSON
        parsed = safe_json_loads(ai_text)

        if parsed is None:
            return None

        # Save to file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=4)

        return parsed

    except Exception as e:
        print(f"Error in extraction: {str(e)}")
        return None


# ============================================================
# MAIN STREAMLIT APP (Only runs when executed directly)
# ============================================================

def main():
    st.set_page_config(page_title="Preference Extraction", page_icon="🎯", layout="wide")

    st.title("🎯 Preference Extraction AI")
    st.markdown("*Transforming your interview responses into a personalized learning profile (37 fields)*")

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

            # Use the core extraction function
            parsed = extract_profile_silently(responses)

            if parsed is None:
                st.error("❌ Could not parse AI response as JSON.")
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

            st.success(f"💾 Profile saved to `{OUTPUT_FILE}`")

    # --- Footer ---
    st.markdown("---")
    st.caption("Built with ❤️ for personalized learning | Persona AI Project")


if __name__ == "__main__":
    main()
