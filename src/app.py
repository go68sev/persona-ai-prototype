"""
app.py - Main Application for Persona AI

LATEST FEATURES:
- Editable AI Learning Profile with inline editing
- Rating slider for profile quality
- Review textbox for user feedback
- Auto-save to extractedPreferences.json and profileReview.json
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

# ---- GLOBAL BIGGER SLIDER STYLE ----
st.markdown("""
<style>
/* Make slider track thicker */
div[data-baseweb="slider"] > div:first-child {
    height: 16px !important;
}

/* Make slider thumb bigger */
div[data-baseweb="slider"] > div > div {
    width: 36px !important;
    height: 36px !important;
    top: -12px !important;
}

/* Move numeric value on the right */
div[data-testid="stSlider"] .css-1fv8s86 {  /* container for value */
    margin-left: 12px !important;
    font-size: 18px;
    font-weight: 600;
}

/* Make slider label bigger */
div[data-testid="stSlider"] label {
    font-size: 40px !important;
    font-weight: 600;
}

/* Make text area label bigger */
div[data-testid="stTextArea"] label {
    font-size: 40px !important;
    font-weight: 600;
}

/* Make buttons bigger */
button {
    height: 50px !important;
    font-size: 18px !important;
    font-weight: 600 !important;
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
            st.rerun()
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

    return load_extracted_preferences()

# --------------------- Profile Editing Helpers ---------------------
def render_editable_field(label, value, field_type="text", options=None, key_suffix=""):
    """Render an editable field based on type."""
    if field_type == "slider":
        return st.slider(label, 1, 10, int(value) if value else 5, key=f"edit_{key_suffix}")
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
            st.session_state.edit_mode = False
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
                        
                        if isinstance(value, (int, float)) and 1 <= value <= 10:
                            updated_responses[key] = st.slider(
                                "", 1, 10, int(value), key=f"slider_{key}"
                            )
                        else:
                            updated_responses[key] = st.text_area(
                                "", value=value, height=80, key=f"text_area_{key}"
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
        # ------------------ TAB 2: AI Learning Profile (NOW EDITABLE) ------------------
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

            if False:
                # ============== EDIT MODE ==============
                st.info("✏️ **Edit Mode Active** - Make changes below and click Save")
                
                # Create a copy for editing
                edited_lp = json.loads(json.dumps(lp))  # Deep copy
                
                # ===== SUMMARY =====
                st.markdown("### 📌 Profile Summary")
                edited_lp["summary"] = st.text_area(
                    "Summary",
                    value=lp.get("summary", ""),
                    height=100,
                    key="edit_summary"
                )
                
                st.markdown("---")
                
                # ===== BACKGROUND =====
                st.markdown("### 📚 Background")
                bg = edited_lp.get("background", {})
                col1, col2 = st.columns(2)
                with col1:
                    bg["academic_program"] = st.text_input("Academic Program", value=bg.get("academic_program", ""), key="edit_bg_program")
                    bg["semester"] = st.text_input("Semester", value=bg.get("semester", ""), key="edit_bg_semester")
                    age_val = bg.get("age", 20)
                    try:
                        age_val = int(float(age_val))
                    except (ValueError, TypeError):
                        age_val = 20
                    bg["age"] = st.number_input("Age", value=age_val, min_value=15, max_value=100, key="edit_bg_age")
                with col2:
                    bg["current_focus"] = st.text_input("Current Focus", value=bg.get("current_focus", ""), key="edit_bg_focus")
                    bg["goals"] = st.text_area("Goals", value=bg.get("goals", ""), height=80, key="edit_bg_goals")
                edited_lp["background"] = bg
                
                st.markdown("---")
                
                # ===== LEARNING PREFERENCES =====
                st.markdown("### 📖 Learning Preferences")
                lprefs = edited_lp.get("learning_preferences", {})
                
                col1, col2 = st.columns(2)
                with col1:
                    lprefs["explanation_preference"] = st.selectbox(
                        "Explanation Preference",
                        ["step-by-step", "high-level", "mixed"],
                        index=["step-by-step", "high-level", "mixed"].index(lprefs.get("explanation_preference", "mixed")),
                        key="edit_lp_explanation"
                    )
                    lprefs["examples_preference"] = st.selectbox(
                        "Examples Preference",
                        ["examples-first", "theory-first", "mixed"],
                        index=["examples-first", "theory-first", "mixed"].index(lprefs.get("examples_preference", "mixed")),
                        key="edit_lp_examples"
                    )
                    lprefs["presentation_style"] = st.selectbox(
                        "Presentation Style",
                        ["visual", "verbal", "mixed"],
                        index=["visual", "verbal", "mixed"].index(lprefs.get("presentation_style", "mixed")),
                        key="edit_lp_style"
                    )
                with col2:
                    lprefs["guidance_preference"] = st.selectbox(
                        "Guidance Preference",
                        ["structured", "independent", "balanced"],
                        index=["structured", "independent", "balanced"].index(lprefs.get("guidance_preference", "balanced")),
                        key="edit_lp_guidance"
                    )
                    lprefs["code_examples"] = st.selectbox(
                        "Code Examples",
                        ["yes", "if-necessary", "no"],
                        index=["yes", "if-necessary", "no"].index(lprefs.get("code_examples", "if-necessary")),
                        key="edit_lp_code"
                    )
                    detail_val = lprefs.get("detail_level", 5)
                    try:
                        detail_val = int(float(detail_val))
                    except (ValueError, TypeError):
                        detail_val = 5
                    lprefs["detail_level"] = st.slider("Detail Level", 1, 10, detail_val, key="edit_lp_detail")
                
                col1, col2 = st.columns(2)
                with col1:
                    lprefs["uses_analogies"] = st.checkbox("Uses Analogies", value=lprefs.get("uses_analogies", True), key="edit_lp_analogies")
                with col2:
                    lprefs["practice_problems"] = st.checkbox("Practice Problems", value=lprefs.get("practice_problems", True), key="edit_lp_practice")
                
                edited_lp["learning_preferences"] = lprefs
                
                st.markdown("---")
                
                # ===== COMMUNICATION STYLE =====
                st.markdown("### 💬 Communication Style")
                cs = edited_lp.get("communication_style", {})
                col1, col2 = st.columns(2)
                with col1:
                    cs["tone"] = st.selectbox("Tone", ["formal", "conversational"], 
                                             index=["formal", "conversational"].index(cs.get("tone", "conversational")),
                                             key="edit_cs_tone")
                    cs["feedback_style"] = st.selectbox("Feedback Style", ["supportive", "direct"],
                                                       index=["supportive", "direct"].index(cs.get("feedback_style", "supportive")),
                                                       key="edit_cs_feedback")
                with col2:
                    cs["response_depth"] = st.selectbox("Response Depth", ["quick", "detailed"],
                                                       index=["quick", "detailed"].index(cs.get("response_depth", "detailed")),
                                                       key="edit_cs_depth")
                    cs["question_engagement"] = st.checkbox("Question Engagement", value=cs.get("question_engagement", True), key="edit_cs_engagement")
                edited_lp["communication_style"] = cs
                
                st.markdown("---")
                
                # ===== EMOTIONAL PATTERNS =====
                st.markdown("### 🧠 Emotional Patterns")
                ep = edited_lp.get("emotional_patterns", {})
                col1, col2 = st.columns(2)
                with col1:
                    ep["stress_response"] = st.selectbox("Stress Response", 
                                                        ["push-through", "pause", "avoid", "depends"],
                                                        index=["push-through", "pause", "avoid", "depends"].index(ep.get("stress_response", "depends")),
                                                        key="edit_ep_stress")
                    ep["overwhelm_support"] = st.selectbox("Overwhelm Support",
                                                          ["encouragement", "step-by-step", "break"],
                                                          index=["encouragement", "step-by-step", "break"].index(ep.get("overwhelm_support", "step-by-step")),
                                                          key="edit_ep_overwhelm")
                    confidence_val = ep.get("confidence_level", 5)
                    try:
                        confidence_val = int(float(confidence_val))
                    except (ValueError, TypeError):
                        confidence_val = 5
                    ep["confidence_level"] = st.slider("Confidence Level", 1, 10, confidence_val, key="edit_ep_confidence")
                with col2:
                    ep["motivation_drivers"] = st.text_area("Motivation Drivers", value=ep.get("motivation_drivers", ""), height=80, key="edit_ep_motivation")
                    ep["common_blockers"] = st.text_area("Common Blockers", value=ep.get("common_blockers", ""), height=80, key="edit_ep_blockers")
                edited_lp["emotional_patterns"] = ep
                
                st.markdown("---")
                
                # ===== STUDY BEHAVIOR =====
                st.markdown("### 📅 Study Behavior")
                sb = edited_lp.get("study_behavior", {})
                col1, col2 = st.columns(2)
                with col1:
                    sb["study_rhythm"] = st.selectbox("Study Rhythm",
                                                     ["regular", "cramming", "mixed"],
                                                     index=["regular", "cramming", "mixed"].index(sb.get("study_rhythm", "mixed")),
                                                     key="edit_sb_rhythm")
                    sb["focus_duration"] = st.text_input("Focus Duration", value=sb.get("focus_duration", ""), key="edit_sb_duration")
                    attention_val = sb.get("attention_span", 5)
                    try:
                        attention_val = int(float(attention_val))
                    except (ValueError, TypeError):
                        attention_val = 5
                    sb["attention_span"] = st.slider("Attention Span", 1, 10, attention_val, key="edit_sb_attention")
                with col2:
                    sb["recovery_strategy"] = st.selectbox("Recovery Strategy",
                                                          ["short-break", "task-switch", "goal-review", "external-reminder"],
                                                          index=["short-break", "task-switch", "goal-review", "external-reminder"].index(sb.get("recovery_strategy", "short-break")),
                                                          key="edit_sb_recovery")
                    sb["mistake_handling"] = st.selectbox("Mistake Handling",
                                                         ["immediate-fix", "deferred"],
                                                         index=["immediate-fix", "deferred"].index(sb.get("mistake_handling", "immediate-fix")),
                                                         key="edit_sb_mistakes")
                edited_lp["study_behavior"] = sb
                
                st.markdown("---")
                
                # Save button for edited profile
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    if st.button("💾 Save Profile", type="primary", use_container_width=True):
                        # Update the full structure
                        if "learning_profile" in extracted_prefs:
                            extracted_prefs["learning_profile"] = edited_lp
                        else:
                            extracted_prefs = edited_lp
                        
                        if save_edited_profile(extracted_prefs):
                            st.success("✅ Profile updated successfully!")
                            st.session_state.edit_mode = False
                            time.sleep(1)
                            st.rerun()
                
            else:
                # ============== VIEW MODE (Original Display) ==============
                st.success("🎉 AI-generated learning profile found!")

                # ===== SUMMARY =====
                summary = clean_value(safe_get(lp, "summary", default="No summary generated."))
                st.markdown("### 📌 Profile Summary")
                if st.session_state.edit_summary:
                    edited_summary = st.text_area("Summary", value=summary, height=300, key="edit_summary_input")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Save", key="save_summary"):
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
                            <h4>📌 Profile Summary</h4>
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

                # ===== SECTION 1: BACKGROUND =====
                st.markdown("### 📚 Background")
                bg = lp.get("background", {})
                if st.session_state.edit_background:
                    col1, col2 = st.columns(2)
                    with col1:
                        academic_program = st.text_input("Academic Program", value=bg.get("academic_program", ""), key="edit_bg_program")
                        semester = st.text_input("Semester", value=bg.get("semester", ""), key="edit_bg_semester")
                        age_val = bg.get("age", 20)
                        try:
                            age_val = int(float(age_val))
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

                # ===== SECTION 2: LEARNING PREFERENCES =====
                st.markdown("### 📖 Learning Preferences")
                lprefs = lp.get("learning_preferences", {})
                if st.session_state.edit_learning_preferences:
                    col1, col2 = st.columns(2)
                    with col1:
                        exp_pref = lprefs.get("explanation_preference", "mixed")
                        if isinstance(exp_pref, list) and exp_pref:
                            exp_pref = exp_pref[0]
                        explanation_preference = st.selectbox(
                            "Explanation Preference",
                            ["step-by-step", "high-level", "mixed"],
                            index=["step-by-step", "high-level", "mixed"].index(exp_pref) if exp_pref in ["step-by-step", "high-level", "mixed"] else 2,
                            key="edit_lp_explanation"
                        )
                        ex_pref = lprefs.get("examples_preference", "mixed")
                        if isinstance(ex_pref, list) and ex_pref:
                            ex_pref = ex_pref[0]
                        examples_preference = st.selectbox(
                            "Examples Preference",
                            ["examples-first", "theory-first", "mixed"],
                            index=["examples-first", "theory-first", "mixed"].index(ex_pref) if ex_pref in ["examples-first", "theory-first", "mixed"] else 2,
                            key="edit_lp_examples"
                        )
                        pres_style = lprefs.get("presentation_style", "mixed")
                        if isinstance(pres_style, list) and pres_style:
                            pres_style = pres_style[0]
                        presentation_style = st.selectbox(
                            "Presentation Style",
                            ["visual", "verbal", "mixed"],
                            index=["visual", "verbal", "mixed"].index(pres_style) if pres_style in ["visual", "verbal", "mixed"] else 2,
                            key="edit_lp_style"
                        )
                    with col2:
                        guid_pref = lprefs.get("guidance_preference", "balanced")
                        if isinstance(guid_pref, list) and guid_pref:
                            guid_pref = guid_pref[0]
                        guidance_preference = st.selectbox(
                            "Guidance Preference",
                            ["structured", "independent", "balanced"],
                            index=["structured", "independent", "balanced"].index(guid_pref) if guid_pref in ["structured", "independent", "balanced"] else 2,
                            key="edit_lp_guidance"
                        )
                        code_ex = lprefs.get("code_examples", "if-necessary")
                        if isinstance(code_ex, list) and code_ex:
                            code_ex = code_ex[0]
                        code_examples = st.selectbox(
                            "Code Examples",
                            ["yes", "if-necessary", "no"],
                            index=["yes", "if-necessary", "no"].index(code_ex) if code_ex in ["yes", "if-necessary", "no"] else 1,
                            key="edit_lp_code"
                        )
                        detail_val = lprefs.get("detail_level", 5)
                        try:
                            detail_val = int(float(detail_val))
                        except (ValueError, TypeError):
                            detail_val = 5
                        detail_level = st.slider("Detail Level", 1, 10, detail_val, key="edit_lp_detail")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        uses_analogies = st.checkbox("Uses Analogies", value=lprefs.get("uses_analogies", True), key="edit_lp_analogies")
                    with col2:
                        practice_problems = st.checkbox("Practice Problems", value=lprefs.get("practice_problems", True), key="edit_lp_practice")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Save Learning Preferences", key="save_lp"):
                            extracted_prefs["learning_profile"]["learning_preferences"] = {
                                "explanation_preference": explanation_preference,
                                "examples_preference": examples_preference,
                                "presentation_style": presentation_style,
                                "guidance_preference": guidance_preference,
                                "code_examples": code_examples,
                                "detail_level": detail_level,
                                "uses_analogies": uses_analogies,
                                "practice_problems": practice_problems
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
                    prefs_list = [
                        f"Explanation: {clean_value(safe_get(lprefs, 'explanation_preference'))}",
                        f"Examples: {clean_value(safe_get(lprefs, 'examples_preference'))}",
                        f"Guidance: {clean_value(safe_get(lprefs, 'guidance_preference'))}",
                        f"Style: {clean_value(safe_get(lprefs, 'presentation_style'))}",
                    ]
                    prefs_html = "".join(
                        f"<span style='background-color:#E8F4FD; padding:5px 12px; margin:4px; border-radius:15px; display:inline-block;'>{p}</span>"
                        for p in prefs_list
                    )
                    st.markdown(
                        f"""
                        <div style="background-color:#F5F5F5; padding:15px; border-radius:12px;">
                            {prefs_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    detail_level = lprefs.get("detail_level")
                    if detail_level and isinstance(detail_level, (int, float)):
                        st.markdown("**Detail Level Preference:**")
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

                # ===== SECTION 3: COMMUNICATION STYLE =====
                st.markdown("### 💬 Communication Style")
                cs = lp.get("communication_style", {})
                if st.session_state.edit_communication_style:
                    col1, col2 = st.columns(2)
                    with col1:
                        tone_val = cs.get("tone", "conversational")
                        if isinstance(tone_val, list) and tone_val:
                            tone_val = tone_val[0]
                        tone = st.selectbox("Tone", ["formal", "conversational"], 
                                           index=["formal", "conversational"].index(tone_val) if tone_val in ["formal", "conversational"] else 1,
                                           key="edit_cs_tone")
                        fb_style = cs.get("feedback_style", "supportive")
                        if isinstance(fb_style, list) and fb_style:
                            fb_style = fb_style[0]
                        feedback_style = st.selectbox("Feedback Style", ["supportive", "direct"],
                                                     index=["supportive", "direct"].index(fb_style) if fb_style in ["supportive", "direct"] else 0,
                                                     key="edit_cs_feedback")
                    with col2:
                        resp_depth = cs.get("response_depth", "detailed")
                        if isinstance(resp_depth, list) and resp_depth:
                            resp_depth = resp_depth[0]
                        response_depth = st.selectbox("Response Depth", ["quick", "detailed"],
                                                     index=["quick", "detailed"].index(resp_depth) if resp_depth in ["quick", "detailed"] else 1,
                                                     key="edit_cs_depth")
                        question_engagement = st.checkbox("Question Engagement", value=cs.get("question_engagement", True), key="edit_cs_engagement")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Save Communication Style", key="save_cs"):
                            extracted_prefs["learning_profile"]["communication_style"] = {
                                "tone": tone,
                                "feedback_style": feedback_style,
                                "response_depth": response_depth,
                                "question_engagement": question_engagement
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
                                <b>Feedback Style:</b> {clean_value(safe_get(cs, "feedback_style"))}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with col2:
                        st.markdown(
                            f"""
                            <div style="background-color:#FFF3E0; padding:15px; border-radius:12px;">
                                <b>Response Depth:</b> {clean_value(safe_get(cs, "response_depth"))}<br>
                                <b>Question Engagement:</b> {format_bool(cs.get("question_engagement"))}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                    if st.button("Edit Communication Style", key="edit_cs_btn"):
                        st.session_state.edit_communication_style = True
                        st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

                # ===== SECTION 4: EMOTIONAL PATTERNS =====
                st.markdown("### 🧠 Emotional Patterns")
                ep = lp.get("emotional_patterns", {})
                if st.session_state.edit_emotional_patterns:
                    col1, col2 = st.columns(2)
                    with col1:
                        stress_resp = ep.get("stress_response", "depends")
                        if isinstance(stress_resp, list) and stress_resp:
                            stress_resp = stress_resp[0]
                        stress_response = st.selectbox("Stress Response", 
                                                      ["push-through", "pause", "avoid", "depends"],
                                                      index=["push-through", "pause", "avoid", "depends"].index(stress_resp) if stress_resp in ["push-through", "pause", "avoid", "depends"] else 3,
                                                      key="edit_ep_stress")
                        overwhelm_supp = ep.get("overwhelm_support", "step-by-step")
                        if isinstance(overwhelm_supp, list) and overwhelm_supp:
                            overwhelm_supp = overwhelm_supp[0]
                        overwhelm_support = st.selectbox("Overwhelm Support",
                                                        ["encouragement", "step-by-step", "break"],
                                                        index=["encouragement", "step-by-step", "break"].index(overwhelm_supp) if overwhelm_supp in ["encouragement", "step-by-step", "break"] else 1,
                                                        key="edit_ep_overwhelm")
                        confidence_val = ep.get("confidence_level", 5)
                        try:
                            confidence_val = int(float(confidence_val))
                        except (ValueError, TypeError):
                            confidence_val = 5
                        confidence_level = st.slider("Confidence Level", 1, 10, confidence_val, key="edit_ep_confidence")
                    with col2:
                        motivation_drivers = st.text_area("Motivation Drivers", value=ep.get("motivation_drivers", ""), height=80, key="edit_ep_motivation")
                        common_blockers = st.text_area("Common Blockers", value=ep.get("common_blockers", ""), height=80, key="edit_ep_blockers")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Save Emotional Patterns", key="save_ep"):
                            extracted_prefs["learning_profile"]["emotional_patterns"] = {
                                "stress_response": stress_response,
                                "overwhelm_support": overwhelm_support,
                                "confidence_level": confidence_level,
                                "motivation_drivers": motivation_drivers,
                                "common_blockers": common_blockers
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
                                <b>Overwhelm Support:</b> {clean_value(safe_get(ep, "overwhelm_support"))}
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
                    
                    confidence = ep.get("confidence_level")
                    if confidence and isinstance(confidence, (int, float)):
                        st.markdown("**Confidence Level:**")
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.progress(min(confidence / 10, 1.0))
                        with col2:
                            st.markdown(f"**{int(confidence)}/10**")
                    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                    if st.button("Edit Emotional Patterns", key="edit_ep_btn"):
                        st.session_state.edit_emotional_patterns = True
                        st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

                # ===== SECTION 5: STUDY BEHAVIOR =====
                st.markdown("### 📅 Study Behavior")
                sb = lp.get("study_behavior", {})
                if st.session_state.edit_study_behavior:
                    col1, col2 = st.columns(2)
                    with col1:
                        study_rhythm_val = sb.get("study_rhythm", "flexible")
                        if isinstance(study_rhythm_val, list) and study_rhythm_val:
                            study_rhythm_val = study_rhythm_val[0]
                        study_rhythm = st.selectbox("Study Rhythm", 
                                                   ["morning", "evening", "night", "flexible"],
                                                   index=["morning", "evening", "night", "flexible"].index(study_rhythm_val) if study_rhythm_val in ["morning", "evening", "night", "flexible"] else 3,
                                                   key="edit_sb_rhythm")
                        focus_val = sb.get("focus_duration", 30)
                        try:
                            focus_val = int(float(focus_val))
                        except (ValueError, TypeError):
                            focus_val = 30
                        focus_duration = st.slider("Focus Duration (minutes)", 5, 120, focus_val, key="edit_sb_focus")
                        attention_val = sb.get("attention_span", 45)
                        try:
                            attention_val = int(float(attention_val))
                        except (ValueError, TypeError):
                            attention_val = 45
                        attention_span = st.slider("Attention Span (minutes)", 5, 120, attention_val, key="edit_sb_attention")
                    with col2:
                        recovery_strat = sb.get("recovery_strategy", "")
                        if isinstance(recovery_strat, list) and recovery_strat:
                            recovery_strat = recovery_strat[0]
                        recovery_strategy = st.text_area("Recovery Strategy", value=recovery_strat, height=80, key="edit_sb_recovery")
                        mistake_handl = sb.get("mistake_handling", "")
                        if isinstance(mistake_handl, list) and mistake_handl:
                            mistake_handl = mistake_handl[0]
                        mistake_handling = st.text_area("Mistake Handling", value=mistake_handl, height=80, key="edit_sb_mistake")
                    
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
                                <b>Focus Duration:</b> {clean_value(safe_get(sb, "focus_duration"))} minutes<br>
                                <b>Attention Span:</b> {clean_value(safe_get(sb, "attention_span"))} minutes
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with col2:
                        st.markdown(
                            f"""
                            <div style="background-color:#FFF8E1; padding:15px; border-radius:12px;">
                                <b>Recovery Strategy:</b> {clean_value(safe_get(sb, "recovery_strategy"))}<br>
                                <b>Mistake Handling:</b> {clean_value(safe_get(sb, "mistake_handling"))}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                    if st.button("Edit Study Behavior", key="edit_sb_btn"):
                        st.session_state.edit_study_behavior = True
                        st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

                # ===== RATING & REVIEW SECTION (Always visible) =====
                st.markdown("---")

                st.markdown("### ⭐ Rate This Profile")

                review_data = load_profile_review()

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown('<div class="rating-slider">', unsafe_allow_html=True)

                    st.markdown('<div style="font-size:20px; font-weight:600; margin-bottom:10px;">How accurate is this profile?</div>', unsafe_allow_html=True)

                    rating = st.slider(
                        "",
                        1,
                        10,
                        review_data.get("rating", 5),
                        label_visibility="collapsed",
                        key="profile_rating"
                    )

                    st.markdown('</div>', unsafe_allow_html=True)
                    

                with col2:
                    st.markdown(f"## **{rating}/10**")

                    if rating <= 3:
                        st.markdown("😔 **Needs significant improvement**")
                    elif rating <= 6:
                        st.markdown("😐 **Somewhat accurate**")
                    elif rating <= 8:
                        st.markdown("😊 **Pretty good!**")
                    else:
                        st.markdown("🎉 **Excellent accuracy!**")

                st.markdown('<div style="font-size:20px; font-weight:600; margin-bottom:10px;">Share your feedback (optional)</div>', unsafe_allow_html=True)

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

        spec = importlib.util.spec_from_file_location("chatbot", FEEDBACK_PY_PATH)
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

    if st.session_state.interview_completed and st.session_state.page == "interview":
        st.session_state.page = "chatbot"
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