"""
app.py - Main Application for Persona AI

FEATURES:
- Editable AI Learning Profile with inline editing
- Rating slider for profile quality (1-10)
- Review textbox for user feedback
- Auto-save to extractedPreferences.json and profileReview.json

Last updated: January 2026
"""

import streamlit as st
import json
import os
import time
import importlib.util
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# --------------------- Configuration ---------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
RESPONSES_FILE = os.path.join(BASE_DIR, "profiles", "interviewResponse.json")
QUESTIONS_FILE = os.path.join(BASE_DIR, "docs", "interviewQuestions.json")
EXTRACTED_PREFS_FILE = os.path.join(BASE_DIR, "profiles", "extractedPreferences.json")
PROFILE_REVIEW_FILE = os.path.join(BASE_DIR, "profiles", "profileReview.json")
INTERVIEW_PY_PATH = os.path.join(CURRENT_DIR, "interview.py")
CHATBOT_PY_PATH = os.path.join(CURRENT_DIR, "generate_content.py")
FEEDBACK_PY_PATH = os.path.join(CURRENT_DIR, "analyze_chatbot.py")
EXTRACT_PREFS_PY_PATH = os.path.join(CURRENT_DIR, "extract_preferences.py")

# Import helper functions from utils.py
try:
    from utils import safe_get, safe_json_loads, format_bool
except ImportError:
    st.error("❌ Failed to import utility functions. Please ensure utils.py exists.")
    raise

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(
    page_title="User Profile System",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Sidebar Button Style ----
st.markdown("""
    <style>
    section[data-testid="stSidebar"] button {
        width: 100% !important;
        min-width: 200px !important;
        max-width: 300px !important;
        background-color: #F5F5F5 !important;
        color: black !important;
        border-radius: 10px !important;
        border: 1px solid #DDD !important;
        font-weight: 500 !important;
        padding: 10px !important;
        margin-bottom: 10px;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #E5E5E5 !important;
        color: black !important;
    }
    section[data-testid="stSidebar"] button:focus {
        outline: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---- GLOBAL STYLES ----
st.markdown("""
<style>
/* Make text area label bigger */
div[data-testid="stTextArea"] label {
    font-size: 18px !important;
    font-weight: 600;
}

/* Style select slider */
div[data-testid="stSlider"] label {
    font-size: 18px !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# --------------------- Initialize Session State ---------------------
if "page" not in st.session_state:
    st.session_state.page = "interview"
if "interview_completed" not in st.session_state:
    st.session_state.interview_completed = False
if "selected_profile_tab" not in st.session_state:
    st.session_state.selected_profile_tab = 0
if "force_regenerate" not in st.session_state:
    st.session_state.force_regenerate = False

# Edit mode states for each section
if "edit_summary" not in st.session_state:
    st.session_state.edit_summary = False
if "edit_background" not in st.session_state:
    st.session_state.edit_background = False
if "edit_learning_preferences" not in st.session_state:
    st.session_state.edit_learning_preferences = False
if "edit_communication_style" not in st.session_state:
    st.session_state.edit_communication_style = False
if "edit_emotional_patterns" not in st.session_state:
    st.session_state.edit_emotional_patterns = False
if "edit_study_behavior" not in st.session_state:
    st.session_state.edit_study_behavior = False

if os.path.exists(RESPONSES_FILE) and os.path.getsize(RESPONSES_FILE) > 0:
    st.session_state.interview_completed = True

# --------------------- Helper Function for Clean Display ---------------------
def clean_value(val):
    """Convert list values to clean strings for display"""
    if isinstance(val, list):
        return ", ".join(str(v) for v in val) if val else "N/A"
    return val if val else "N/A"


def get_safe_index(value, options, default=0):
    """Safely get index of value in options list, handling list values"""
    if isinstance(value, list) and value:
        value = value[0]
    if value in options:
        return options.index(value)
    return default

# --------------------- Load Data Helpers ---------------------
def load_responses():
    """Load interview responses with proper error handling."""
    if not os.path.exists(RESPONSES_FILE):
        return {}

    try:
        with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                return {}
            return json.loads(content)
    except json.JSONDecodeError as e:
        st.error(f"❌ Interview responses file is corrupted: {e}")
        return {}
    except PermissionError:
        st.error("❌ Permission denied when reading responses file.")
        return {}
    except Exception as e:
        st.error(f"❌ Error loading responses: {str(e)}")
        return {}


def load_questions():
    """Load interview questions with proper error handling."""
    if not os.path.exists(QUESTIONS_FILE):
        st.warning(f"⚠️ Questions file not found at: {QUESTIONS_FILE}")
        return {}

    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        st.error(f"❌ Questions file is corrupted: {e}")
        return {}
    except Exception as e:
        st.error(f"❌ Error loading questions: {str(e)}")
        return {}


def load_extracted_preferences():
    """Load extracted preferences with proper error handling."""
    if not os.path.exists(EXTRACTED_PREFS_FILE):
        return None

    try:
        if os.path.getsize(EXTRACTED_PREFS_FILE) == 0:
            return None

        with open(EXTRACTED_PREFS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            return safe_json_loads(content) if content.strip() else None
    except json.JSONDecodeError as e:
        st.error(f"⚠️ AI profile JSON is corrupted: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Error loading extracted preferences: {str(e)}")
        return None


def load_profile_review():
    """Load profile review data."""
    if not os.path.exists(PROFILE_REVIEW_FILE):
        return {"rating": 5, "reviews": []}

    try:
        with open(PROFILE_REVIEW_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"rating": 5, "reviews": []}


def save_profile_review(rating, review_text):
    """Save profile review with timestamp."""
    review_data = load_profile_review()

    review_data["rating"] = rating
    review_data["reviews"].append({
        "timestamp": datetime.now().isoformat(),
        "rating": rating,
        "review": review_text
    })

    try:
        with open(PROFILE_REVIEW_FILE, "w", encoding="utf-8") as f:
            json.dump(review_data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"❌ Error saving review: {str(e)}")
        return False

def render_editable_field(label, value, field_type="text", options=None, key_suffix=""):
    """Render an editable field based on type."""
    if field_type == "slider":
        return st.slider(label, 0, 10, int(value) if value else 5, key=f"edit_{key_suffix}")
    elif field_type == "select":
        current_val = value if value else options[0]
        return st.selectbox(label, options, index=options.index(current_val) if current_val in options else 0, key=f"edit_{key_suffix}")
    elif field_type == "boolean":
        bool_val = value if isinstance(value, bool) else (value == "Yes" or value == True)
        return st.checkbox(label, value=bool_val, key=f"edit_{key_suffix}")
    else:
        return st.text_input(label, value=str(value) if value else "", key=f"edit_{key_suffix}")

def save_edited_profile(edited_data):
    """Save edited profile back to extractedPreferences.json."""
    try:
        with open(EXTRACTED_PREFS_FILE, "w", encoding="utf-8") as f:
            json.dump(edited_data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"❌ Error saving profile: {str(e)}")
        return False

# --------------------- Auto Run extract_preferences.py ---------------------
def run_extract_preferences():
    """Run the preference extraction module."""
    try:
        from extract_preferences import extract_profile_silently

        with st.spinner("🔄 Generating AI learning profile..."):
            result = extract_profile_silently()

        if result:
            st.toast("✨ AI Profile generated successfully!", icon="🤖")
            time.sleep(1)
            return result
        else:
            st.error("❌ Failed to generate profile. Please check your responses and try again.")
            return None

    except ImportError as e:
        st.error(f"❌ Failed to import extraction module: {str(e)}")
        st.info("Make sure extract_preferences.py exists in the src folder.")
        return None
    except Exception as e:
        st.error(f"❌ Failed to generate profile: {str(e)}")
        st.info("Please check your OpenAI API key and try again.")
        return None

# --------------------- Profile Page ---------------------
def profile_page():
    st.title("👤 Your Profile")
    st.markdown("---")

    responses = load_responses()
    questions_data = load_questions()

    if not responses:
        st.warning("No interview data found. Please complete the interview first.")
        if st.button("Start Interview 🚀"):
            st.session_state.page = "interview"
            st.rerun()
        st.stop()

    # Custom tab selector using buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📖 Your Profile",
                     type="primary" if st.session_state.selected_profile_tab == 0 else "secondary",
                     use_container_width=True):
            st.session_state.selected_profile_tab = 0
            st.rerun()

    with col2:
        if st.button("🎯 AI Learning Profile",
                     type="primary" if st.session_state.selected_profile_tab == 1 else "secondary",
                     use_container_width=True):
            st.session_state.selected_profile_tab = 1
            st.rerun()

    st.markdown("---")

    # Display content based on selected tab
    if st.session_state.selected_profile_tab == 0:
        # ------------------ TAB 1: Editable Profile ------------------
        st.info("💡 You can edit your answers directly below. Click save when done.")
        updated_responses = {}

        # Group responses by section
        sections_dict = {}
        for key, value in responses.items():
            section_name = key.rsplit("-", 1)[0]
            sections_dict.setdefault(section_name, []).append((key, value))

        for section, items in sections_dict.items():
            st.markdown(f"### 🗂 {section}")
            num_cols = 2
            for i in range(0, len(items), num_cols):
                cols = st.columns(num_cols)
                for j, (key, value) in enumerate(items[i:i+num_cols]):
                    question_idx = int(key.split("-")[-1])

                    section_questions = questions_data.get(section, [])
                    if question_idx < len(section_questions):
                        question_text = section_questions[question_idx].get("question", "Question not found")
                    else:
                        question_text = "Question not found"

                    with cols[j]:
                        st.markdown(
                            f"""
                            <div style='background-color:#E0F7FA; padding:12px; border-radius:12px; margin-bottom:4px;'>
                                <b>{question_text}</b>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # Check if it's a rating question (0-10 scale)
                        if isinstance(value, (int, float)) and 0 <= value <= 10:
                            updated_responses[key] = st.select_slider(
                                "Rating",
                                options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                                value=int(value),
                                key=f"slider_{key}",
                                label_visibility="collapsed"
                            )
                        else:
                            updated_responses[key] = st.text_area(
                                "", value=value if value else "", height=80, key=f"text_area_{key}"
                            )

                        st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("💾 Save Changes", type="primary", use_container_width=True):
                try:
                    if os.path.exists(RESPONSES_FILE):
                        os.remove(RESPONSES_FILE)

                    with open(RESPONSES_FILE, "w", encoding="utf-8") as f:
                        json.dump(updated_responses, f, indent=4)

                    if os.path.exists(EXTRACTED_PREFS_FILE):
                        os.remove(EXTRACTED_PREFS_FILE)

                    st.success("✅ Your profile has been updated successfully!")
                    st.info("🔄 AI Learning Profile will regenerate with your new responses.")
                    time.sleep(1.5)
                    st.rerun()

                except PermissionError:
                    st.error("❌ Permission denied. Cannot save changes.")
                except Exception as e:
                    st.error(f"❌ Error saving changes: {str(e)}")

    else:
        # ------------------ TAB 2: AI Learning Profile (EDITABLE - 37 FIELDS) ------------------
        st.subheader("🧠 Personalized AI Learning Profile")

        # Check if we should force regeneration
        should_generate = False
        if st.session_state.force_regenerate:
            if os.path.exists(EXTRACTED_PREFS_FILE):
                os.remove(EXTRACTED_PREFS_FILE)
            st.session_state.force_regenerate = False
            should_generate = True

        extracted_prefs = load_extracted_preferences()

        if (should_generate or extracted_prefs is None):
            st.info("⚙️ Generating your AI learning profile...")
            run_extract_preferences()
            extracted_prefs = load_extracted_preferences()

        if extracted_prefs:
            lp = extracted_prefs.get("learning_profile", extracted_prefs)

            st.success("🎉 AI-generated learning profile found!")

            # ===== SUMMARY =====
            summary = clean_value(safe_get(lp, "summary", default="No summary generated."))
            st.markdown("### 📌 Profile Summary")
            if st.session_state.edit_summary:
                edited_summary = st.text_area("Summary", value=summary, height=150, key="edit_summary_input")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save Summary", key="save_summary"):
                        extracted_prefs["learning_profile"]["summary"] = edited_summary
                        save_edited_profile(extracted_prefs)
                        st.session_state.edit_summary = False
                        st.success("Summary updated!")
                        st.rerun()
                with col2:
                    if st.button("Cancel", key="cancel_summary"):
                        st.session_state.edit_summary = False
                        st.rerun()
            else:
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(to right, #FFF3E0, #FFE0B2);
                                padding: 20px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                        <p style="margin-top: 10px;">{summary}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                if st.button("Edit Summary", key="edit_summary_btn"):
                    st.session_state.edit_summary = True
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

            # ===== SECTION 1: BACKGROUND (5 fields) =====
            st.markdown("### 📚 Background")
            bg = lp.get("background", {})
            if st.session_state.edit_background:
                col1, col2 = st.columns(2)
                with col1:
                    academic_program = st.text_input("Academic Program", value=bg.get("academic_program", ""), key="edit_bg_program")
                    semester = st.text_input("Semester", value=str(bg.get("semester", "")), key="edit_bg_semester")
                    age_val = bg.get("age", 20)
                    try:
                        age_val = int(float(age_val)) if age_val else 20
                    except (ValueError, TypeError):
                        age_val = 20
                    age = st.number_input("Age", value=age_val, min_value=15, max_value=100, key="edit_bg_age")
                with col2:
                    current_focus = st.text_input("Current Focus", value=bg.get("current_focus", ""), key="edit_bg_focus")
                    goals = st.text_area("Goals", value=bg.get("goals", ""), height=80, key="edit_bg_goals")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save Background", key="save_bg"):
                        extracted_prefs["learning_profile"]["background"] = {
                            "academic_program": academic_program,
                            "semester": semester,
                            "age": age,
                            "current_focus": current_focus,
                            "goals": goals
                        }
                        save_edited_profile(extracted_prefs)
                        st.session_state.edit_background = False
                        st.success("Background updated!")
                        st.rerun()
                with col2:
                    if st.button("Cancel", key="cancel_bg"):
                        st.session_state.edit_background = False
                        st.rerun()
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(
                        f"""
                        <div style="background-color:#E3F2FD; padding:15px; border-radius:12px; margin-bottom:10px;">
                            <b>Academic Program:</b> {clean_value(safe_get(bg, "academic_program"))}<br>
                            <b>Semester:</b> {clean_value(safe_get(bg, "semester"))}<br>
                            <b>Age:</b> {clean_value(safe_get(bg, "age"))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col2:
                    st.markdown(
                        f"""
                        <div style="background-color:#E8F5E9; padding:15px; border-radius:12px; margin-bottom:10px;">
                            <b>Current Focus:</b> {clean_value(safe_get(bg, "current_focus"))}<br>
                            <b>Goals:</b> {clean_value(safe_get(bg, "goals"))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                if st.button("Edit Background", key="edit_bg_btn"):
                    st.session_state.edit_background = True
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

            # ===== SECTION 2: LEARNING PREFERENCES (14 fields) =====
            st.markdown("### 📖 Learning Preferences")
            lprefs = lp.get("learning_preferences", {})
            if st.session_state.edit_learning_preferences:
                # Row 1
                col1, col2 = st.columns(2)
                with col1:
                    explanation_preference = st.selectbox(
                        "Explanation Preference",
                        ["step-by-step", "high-level", "mixed"],
                        index=get_safe_index(lprefs.get("explanation_preference", "mixed"), ["step-by-step", "high-level", "mixed"], 2),
                        key="edit_lp_explanation"
                    )
                    examples_timing = st.selectbox(
                        "Examples Timing",
                        ["examples-first", "theory-first", "mixed"],
                        index=get_safe_index(lprefs.get("examples_timing", "mixed"), ["examples-first", "theory-first", "mixed"], 2),
                        key="edit_lp_examples_timing"
                    )
                    example_type = st.selectbox(
                        "Example Type",
                        ["real-world", "mathematical", "code-based", "analogies", "diagrams", "mixed"],
                        index=get_safe_index(lprefs.get("example_type", "mixed"), ["real-world", "mathematical", "code-based", "analogies", "diagrams", "mixed"], 5),
                        key="edit_lp_example_type"
                    )
                    example_quantity = st.selectbox(
                        "Example Quantity",
                        ["multiple", "one-strong"],
                        index=get_safe_index(lprefs.get("example_quantity", "multiple"), ["multiple", "one-strong"], 0),
                        key="edit_lp_example_quantity"
                    )
                with col2:
                    presentation_style = st.selectbox(
                        "Presentation Style",
                        ["visual", "verbal", "mixed"],
                        index=get_safe_index(lprefs.get("presentation_style", "mixed"), ["visual", "verbal", "mixed"], 2),
                        key="edit_lp_style"
                    )
                    guidance_preference = st.selectbox(
                        "Guidance Preference",
                        ["structured", "independent", "balanced"],
                        index=get_safe_index(lprefs.get("guidance_preference", "balanced"), ["structured", "independent", "balanced"], 2),
                        key="edit_lp_guidance"
                    )
                    focus_style = st.selectbox(
                        "Focus Style",
                        ["explorer", "focused", "balanced"],
                        index=get_safe_index(lprefs.get("focus_style", "balanced"), ["explorer", "focused", "balanced"], 2),
                        key="edit_lp_focus_style"
                    )
                    code_examples = st.selectbox(
                        "Code Examples",
                        ["yes", "if-necessary", "no"],
                        index=get_safe_index(lprefs.get("code_examples", "if-necessary"), ["yes", "if-necessary", "no"], 1),
                        key="edit_lp_code"
                    )

                # Row 2
                col1, col2 = st.columns(2)
                with col1:
                    pacing = st.selectbox(
                        "Pacing",
                        ["fast", "moderate", "slow-thorough"],
                        index=get_safe_index(lprefs.get("pacing", "moderate"), ["fast", "moderate", "slow-thorough"], 1),
                        key="edit_lp_pacing"
                    )
                    learner_type = st.selectbox(
                        "Learner Type",
                        ["analytical", "intuitive", "example-driven", "pattern-based", "sequential"],
                        index=get_safe_index(lprefs.get("learner_type", "example-driven"), ["analytical", "intuitive", "example-driven", "pattern-based", "sequential"], 2),
                        key="edit_lp_learner_type"
                    )
                    repetition_preference = st.selectbox(
                        "Repetition Preference",
                        ["spaced-repetition", "repeated-summaries", "minimal-repetition"],
                        index=get_safe_index(lprefs.get("repetition_preference", "spaced-repetition"), ["spaced-repetition", "repeated-summaries", "minimal-repetition"], 0),
                        key="edit_lp_repetition"
                    )
                with col2:
                    detail_val = lprefs.get("detail_level", 5)
                    try:
                        detail_val = int(float(detail_val)) if detail_val else 5
                    except (ValueError, TypeError):
                        detail_val = 5
                    detail_level = st.slider("Detail Level", 0, 10, detail_val, key="edit_lp_detail")
                    uses_analogies = st.checkbox("Uses Analogies", value=lprefs.get("uses_analogies", True), key="edit_lp_analogies")
                    practice_problems = st.checkbox("Practice Problems", value=lprefs.get("practice_problems", True), key="edit_lp_practice")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save Learning Preferences", key="save_lp"):
                        extracted_prefs["learning_profile"]["learning_preferences"] = {
                            "explanation_preference": explanation_preference,
                            "examples_timing": examples_timing,
                            "example_type": example_type,
                            "example_quantity": example_quantity,
                            "detail_level": detail_level,
                            "guidance_preference": guidance_preference,
                            "focus_style": focus_style,
                            "uses_analogies": uses_analogies,
                            "presentation_style": presentation_style,
                            "practice_problems": practice_problems,
                            "code_examples": code_examples,
                            "pacing": pacing,
                            "learner_type": learner_type,
                            "repetition_preference": repetition_preference
                        }
                        save_edited_profile(extracted_prefs)
                        st.session_state.edit_learning_preferences = False
                        st.success("Learning Preferences updated!")
                        st.rerun()
                with col2:
                    if st.button("Cancel", key="cancel_lp"):
                        st.session_state.edit_learning_preferences = False
                        st.rerun()
            else:
                # Display mode - show all 14 fields
                prefs_list_1 = [
                    f"Explanation: {clean_value(safe_get(lprefs, 'explanation_preference'))}",
                    f"Examples Timing: {clean_value(safe_get(lprefs, 'examples_timing'))}",
                    f"Example Type: {clean_value(safe_get(lprefs, 'example_type'))}",
                    f"Example Quantity: {clean_value(safe_get(lprefs, 'example_quantity'))}",
                    f"Guidance: {clean_value(safe_get(lprefs, 'guidance_preference'))}",
                    f"Focus Style: {clean_value(safe_get(lprefs, 'focus_style'))}",
                    f"Style: {clean_value(safe_get(lprefs, 'presentation_style'))}",
                ]
                prefs_list_2 = [
                    f"Pacing: {clean_value(safe_get(lprefs, 'pacing'))}",
                    f"Learner Type: {clean_value(safe_get(lprefs, 'learner_type'))}",
                    f"Repetition: {clean_value(safe_get(lprefs, 'repetition_preference'))}",
                    f"Code Examples: {clean_value(safe_get(lprefs, 'code_examples'))}",
                ]

                prefs_html_1 = "".join(
                    f"<span style='background-color:#E8F4FD; padding:5px 12px; margin:4px; border-radius:15px; display:inline-block;'>{p}</span>"
                    for p in prefs_list_1
                )
                prefs_html_2 = "".join(
                    f"<span style='background-color:#E8F4FD; padding:5px 12px; margin:4px; border-radius:15px; display:inline-block;'>{p}</span>"
                    for p in prefs_list_2
                )
                st.markdown(
                    f"""
                    <div style="background-color:#F5F5F5; padding:15px; border-radius:12px; margin-bottom:10px;">
                        {prefs_html_1}
                    </div>
                    <div style="background-color:#F5F5F5; padding:15px; border-radius:12px;">
                        {prefs_html_2}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                detail_level = lprefs.get("detail_level")
                if detail_level and isinstance(detail_level, (int, float)):
                    st.markdown("**Detail Level:**")
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.progress(min(detail_level / 10, 1.0))
                    with col2:
                        st.markdown(f"**{int(detail_level)}/10**")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(
                        f"""
                        <div style="background-color:#FFFDE7; padding:12px; border-radius:10px; margin-top:10px;">
                            <b>Uses Analogies:</b> {format_bool(lprefs.get("uses_analogies"))}<br>
                            <b>Practice Problems:</b> {format_bool(lprefs.get("practice_problems"))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col2:
                    st.markdown(
                        f"""
                        <div style="background-color:#F3E5F5; padding:12px; border-radius:10px; margin-top:10px;">
                            <b>Code Examples:</b> {clean_value(safe_get(lprefs, "code_examples"))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                if st.button("Edit Learning Preferences", key="edit_lp_btn"):
                    st.session_state.edit_learning_preferences = True
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

            # ===== SECTION 3: COMMUNICATION STYLE (5 fields) =====
            st.markdown("### 💬 Communication Style")
            cs = lp.get("communication_style", {})
            if st.session_state.edit_communication_style:
                col1, col2 = st.columns(2)
                with col1:
                    tone = st.selectbox("Tone", ["formal", "conversational"],
                                        index=get_safe_index(cs.get("tone", "conversational"), ["formal", "conversational"], 1),
                                        key="edit_cs_tone")
                    feedback_style = st.selectbox("Feedback Style",
                                                  ["supportive-gentle", "supportive-direct", "direct-critical"],
                                                  index=get_safe_index(cs.get("feedback_style", "supportive-direct"),
                                                                       ["supportive-gentle", "supportive-direct", "direct-critical"], 1),
                                                  key="edit_cs_feedback")
                    response_depth = st.selectbox("Response Depth", ["quick", "detailed"],
                                                  index=get_safe_index(cs.get("response_depth", "detailed"), ["quick", "detailed"], 1),
                                                  key="edit_cs_depth")
                with col2:
                    question_engagement = st.checkbox("Question Engagement", value=cs.get("question_engagement", True), key="edit_cs_engagement")
                    summaries_after = st.checkbox("Summaries After Explanation", value=cs.get("summaries_after_explanation", True), key="edit_cs_summaries")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save Communication Style", key="save_cs"):
                        extracted_prefs["learning_profile"]["communication_style"] = {
                            "tone": tone,
                            "feedback_style": feedback_style,
                            "response_depth": response_depth,
                            "question_engagement": question_engagement,
                            "summaries_after_explanation": summaries_after
                        }
                        save_edited_profile(extracted_prefs)
                        st.session_state.edit_communication_style = False
                        st.success("Communication Style updated!")
                        st.rerun()
                with col2:
                    if st.button("Cancel", key="cancel_cs"):
                        st.session_state.edit_communication_style = False
                        st.rerun()
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(
                        f"""
                        <div style="background-color:#E8F5E9; padding:15px; border-radius:12px;">
                            <b>Tone:</b> {clean_value(safe_get(cs, "tone"))}<br>
                            <b>Feedback Style:</b> {clean_value(safe_get(cs, "feedback_style"))}<br>
                            <b>Response Depth:</b> {clean_value(safe_get(cs, "response_depth"))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col2:
                    st.markdown(
                        f"""
                        <div style="background-color:#FFF3E0; padding:15px; border-radius:12px;">
                            <b>Question Engagement:</b> {format_bool(cs.get("question_engagement"))}<br>
                            <b>Summaries After Explanation:</b> {format_bool(cs.get("summaries_after_explanation"))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                if st.button("Edit Communication Style", key="edit_cs_btn"):
                    st.session_state.edit_communication_style = True
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

            # ===== SECTION 4: EMOTIONAL PATTERNS (8 fields) =====
            st.markdown("### 🧠 Emotional Patterns")
            ep = lp.get("emotional_patterns", {})
            if st.session_state.edit_emotional_patterns:
                col1, col2 = st.columns(2)
                with col1:
                    stress_response = st.selectbox("Stress Response",
                                                   ["push-through", "pause", "avoid", "depends"],
                                                   index=get_safe_index(ep.get("stress_response", "depends"),
                                                                        ["push-through", "pause", "avoid", "depends"], 3),
                                                   key="edit_ep_stress")
                    overwhelm_support = st.selectbox("Overwhelm Support",
                                                     ["encouragement", "step-by-step", "break"],
                                                     index=get_safe_index(ep.get("overwhelm_support", "step-by-step"),
                                                                          ["encouragement", "step-by-step", "break"], 1),
                                                     key="edit_ep_overwhelm")
                    confidence_val = ep.get("confidence_level", 5)
                    try:
                        confidence_val = int(float(confidence_val)) if confidence_val else 5
                    except (ValueError, TypeError):
                        confidence_val = 5
                    confidence_level = st.slider("Confidence Level", 0, 10, confidence_val, key="edit_ep_confidence")

                    mood_sharing_val = ep.get("mood_sharing_comfort", 5)
                    try:
                        mood_sharing_val = int(float(mood_sharing_val)) if mood_sharing_val else 5
                    except (ValueError, TypeError):
                        mood_sharing_val = 5
                    mood_sharing_comfort = st.slider("Mood Sharing Comfort", 0, 10, mood_sharing_val, key="edit_ep_mood")

                    help_seeking_val = ep.get("help_seeking_comfort", 5)
                    try:
                        help_seeking_val = int(float(help_seeking_val)) if help_seeking_val else 5
                    except (ValueError, TypeError):
                        help_seeking_val = 5
                    help_seeking_comfort = st.slider("Help Seeking Comfort", 0, 10, help_seeking_val, key="edit_ep_help")

                with col2:
                    motivation_drivers = st.text_area("Motivation Drivers", value=ep.get("motivation_drivers", ""), height=80, key="edit_ep_motivation")
                    common_blockers = st.text_area("Common Blockers", value=ep.get("common_blockers", ""), height=80, key="edit_ep_blockers")
                    learning_challenges = st.text_area("Learning Challenges", value=ep.get("learning_challenges", ""), height=80, key="edit_ep_challenges")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save Emotional Patterns", key="save_ep"):
                        extracted_prefs["learning_profile"]["emotional_patterns"] = {
                            "stress_response": stress_response,
                            "overwhelm_support": overwhelm_support,
                            "confidence_level": confidence_level,
                            "mood_sharing_comfort": mood_sharing_comfort,
                            "help_seeking_comfort": help_seeking_comfort,
                            "motivation_drivers": motivation_drivers,
                            "common_blockers": common_blockers,
                            "learning_challenges": learning_challenges
                        }
                        save_edited_profile(extracted_prefs)
                        st.session_state.edit_emotional_patterns = False
                        st.success("Emotional Patterns updated!")
                        st.rerun()
                with col2:
                    if st.button("Cancel", key="cancel_ep"):
                        st.session_state.edit_emotional_patterns = False
                        st.rerun()
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(
                        f"""
                        <div style="background-color:#FFEBEE; padding:15px; border-radius:12px;">
                            <b>Stress Response:</b> {clean_value(safe_get(ep, "stress_response"))}<br>
                            <b>Overwhelm Support:</b> {clean_value(safe_get(ep, "overwhelm_support"))}<br>
                            <b>Learning Challenges:</b> {clean_value(safe_get(ep, "learning_challenges"))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col2:
                    st.markdown(
                        f"""
                        <div style="background-color:#E8F5E9; padding:15px; border-radius:12px;">
                            <b>Motivation Drivers:</b> {clean_value(safe_get(ep, "motivation_drivers"))}<br>
                            <b>Common Blockers:</b> {clean_value(safe_get(ep, "common_blockers"))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Progress bars for scale fields
                confidence = ep.get("confidence_level")
                if confidence and isinstance(confidence, (int, float)):
                    st.markdown("**Confidence Level:**")
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.progress(min(confidence / 10, 1.0))
                    with col2:
                        st.markdown(f"**{int(confidence)}/10**")

                mood_comfort = ep.get("mood_sharing_comfort")
                if mood_comfort and isinstance(mood_comfort, (int, float)):
                    st.markdown("**Mood Sharing Comfort:**")
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.progress(min(mood_comfort / 10, 1.0))
                    with col2:
                        st.markdown(f"**{int(mood_comfort)}/10**")

                help_comfort = ep.get("help_seeking_comfort")
                if help_comfort and isinstance(help_comfort, (int, float)):
                    st.markdown("**Help Seeking Comfort:**")
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.progress(min(help_comfort / 10, 1.0))
                    with col2:
                        st.markdown(f"**{int(help_comfort)}/10**")

                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                if st.button("Edit Emotional Patterns", key="edit_ep_btn"):
                    st.session_state.edit_emotional_patterns = True
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

            # ===== SECTION 5: STUDY BEHAVIOR (5 fields) =====
            st.markdown("### 📅 Study Behavior")
            sb = lp.get("study_behavior", {})
            if st.session_state.edit_study_behavior:
                col1, col2 = st.columns(2)
                with col1:
                    study_rhythm = st.selectbox("Study Rhythm",
                                                ["regular", "cramming", "mixed"],
                                                index=get_safe_index(sb.get("study_rhythm", "mixed"),
                                                                     ["regular", "cramming", "mixed"], 2),
                                                key="edit_sb_rhythm")
                    focus_duration = st.text_input("Focus Duration", value=sb.get("focus_duration", ""),
                                                   placeholder="e.g., 30-45 minutes", key="edit_sb_focus")
                    attention_val = sb.get("attention_span", 5)
                    try:
                        attention_val = int(float(attention_val)) if attention_val else 5
                    except (ValueError, TypeError):
                        attention_val = 5
                    attention_span = st.slider("Attention Span", 0, 10, attention_val, key="edit_sb_attention")
                with col2:
                    recovery_strategy = st.selectbox("Recovery Strategy",
                                                     ["short-break", "task-switch", "goal-review", "external-reminder"],
                                                     index=get_safe_index(sb.get("recovery_strategy", "short-break"),
                                                                          ["short-break", "task-switch", "goal-review", "external-reminder"], 0),
                                                     key="edit_sb_recovery")
                    mistake_handling = st.selectbox("Mistake Handling",
                                                    ["immediate-fix", "deferred"],
                                                    index=get_safe_index(sb.get("mistake_handling", "immediate-fix"),
                                                                         ["immediate-fix", "deferred"], 0),
                                                    key="edit_sb_mistake")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save Study Behavior", key="save_sb"):
                        extracted_prefs["learning_profile"]["study_behavior"] = {
                            "study_rhythm": study_rhythm,
                            "focus_duration": focus_duration,
                            "attention_span": attention_span,
                            "recovery_strategy": recovery_strategy,
                            "mistake_handling": mistake_handling
                        }
                        save_edited_profile(extracted_prefs)
                        st.session_state.edit_study_behavior = False
                        st.success("Study Behavior updated!")
                        st.rerun()
                with col2:
                    if st.button("Cancel", key="cancel_sb"):
                        st.session_state.edit_study_behavior = False
                        st.rerun()
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(
                        f"""
                        <div style="background-color:#E3F2FD; padding:15px; border-radius:12px;">
                            <b>Study Rhythm:</b> {clean_value(safe_get(sb, "study_rhythm"))}<br>
                            <b>Focus Duration:</b> {clean_value(safe_get(sb, "focus_duration"))}<br>
                            <b>Recovery Strategy:</b> {clean_value(safe_get(sb, "recovery_strategy"))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col2:
                    st.markdown(
                        f"""
                        <div style="background-color:#FFF8E1; padding:15px; border-radius:12px;">
                            <b>Mistake Handling:</b> {clean_value(safe_get(sb, "mistake_handling"))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                attention = sb.get("attention_span")
                if attention and isinstance(attention, (int, float)):
                    st.markdown("**Attention Span:**")
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.progress(min(attention / 10, 1.0))
                    with col2:
                        st.markdown(f"**{int(attention)}/10**")

                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                if st.button("Edit Study Behavior", key="edit_sb_btn"):
                    st.session_state.edit_study_behavior = True
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

            # ===== RATING & REVIEW SECTION =====
            st.markdown("---")
            st.markdown("### ⭐ Rate This Profile")

            review_data = load_profile_review()

            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown('<div style="font-size:18px; font-weight:600; margin-bottom:10px;">How accurate is this profile?</div>', unsafe_allow_html=True)
                rating = st.slider(
                    "",
                    0,
                    10,
                    review_data.get("rating", 5),
                    label_visibility="collapsed",
                    key="profile_rating"
                )

            with col2:
                st.markdown(f"## **{rating}/10**")
                if rating <= 3:
                    st.markdown("😔 **Needs improvement**")
                elif rating <= 6:
                    st.markdown("😐 **Somewhat accurate**")
                elif rating <= 8:
                    st.markdown("😊 **Pretty good!**")
                else:
                    st.markdown("🎉 **Excellent!**")

            st.markdown('<div style="font-size:18px; font-weight:600; margin-bottom:10px;">Share your feedback (optional)</div>', unsafe_allow_html=True)

            review_text = st.text_area(
                "",
                placeholder="What's accurate? What's missing? How could this profile be improved?",
                height=120,
                label_visibility="collapsed",
                key="profile_review"
            )

            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("📝 Submit Review", type="secondary", use_container_width=True):
                    if save_profile_review(rating, review_text):
                        st.success("✅ Thank you for your feedback!")
                        time.sleep(1)
                        st.rerun()

            # ===== REGENERATE BUTTON =====
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Regenerate Profile", use_container_width=True):
                    try:
                        if os.path.exists(EXTRACTED_PREFS_FILE):
                            os.remove(EXTRACTED_PREFS_FILE)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Could not delete profile: {e}")
        else:
            st.warning("⚠️ Could not load the generated profile. Please try regenerating.")
            if st.button("🔄 Try Again"):
                st.rerun()

# --------------------- Interview Page ---------------------
def interview_page():
    """Load and run the interview module."""
    try:
        if not os.path.exists(INTERVIEW_PY_PATH):
            st.error(f"❌ Interview Page not found at: {INTERVIEW_PY_PATH}")
            return

        spec = importlib.util.spec_from_file_location("interview", INTERVIEW_PY_PATH)
        interview_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(interview_module)

        if os.path.exists(RESPONSES_FILE) and os.path.getsize(RESPONSES_FILE) > 0:
            st.session_state.interview_completed = True
    except Exception as e:
        st.error(f"❌ Error loading interview: {str(e)}")


# --------------------- Chatbot Page ---------------------
def chatbot_page():
    """Load and run the Chatbot."""
    try:
        if not os.path.exists(CHATBOT_PY_PATH):
            st.error(f"❌ Chatbot Page not found at: {CHATBOT_PY_PATH}")
            return

        spec = importlib.util.spec_from_file_location("chatbot", CHATBOT_PY_PATH)
        chatbot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(chatbot_module)

        if hasattr(chatbot_module, "generate_content"):
            chatbot_module.generate_content()
        else:
            st.error("❌ generate_content() not found inside generate_content.py")

    except Exception as e:
        st.error(f"❌ Error loading chatbot: {str(e)}")


# --------------------- Feedback Page ---------------------
def feedback_page():
    """Load and run the Feedback."""
    try:
        if not os.path.exists(FEEDBACK_PY_PATH):
            st.error(f"❌ Feedback Page not found at: {FEEDBACK_PY_PATH}")
            return

        spec = importlib.util.spec_from_file_location("feedback", FEEDBACK_PY_PATH)
        feedback_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(feedback_module)

    except Exception as e:
        st.error(f"❌ Error loading Feedback page: {str(e)}")

# --------------------- Main App ---------------------
def main():
    with st.sidebar:
        st.title("Main Menu")

        if st.session_state.interview_completed:
            if st.button("🧠 Know Yourself Better"):
                st.session_state.page = "interview"
                st.rerun()
            if st.button("👤 View Profile"):
                st.session_state.page = "profile"
                st.session_state.selected_profile_tab = 0
                st.rerun()
            if st.button("💬 Chat with Persona"):
                st.session_state.page = "chatbot"
                st.rerun()
            if st.button("📊 Chatbot Feedback"):
                st.session_state.page = "feedback"
                st.rerun()
        else:
            st.markdown("### Welcome to Persona 👋")
            st.info("Please complete the interview first.")
            if st.button("🚀 Start Interview Now"):
                st.session_state.page = "interview"
                st.rerun()

    if st.session_state.page == "interview":
        interview_page()
    elif st.session_state.page == "profile":
        profile_page()
    elif st.session_state.page == "chatbot":
        chatbot_page()
    elif st.session_state.page == "feedback":
        feedback_page()


if __name__ == "__main__":
    main()
