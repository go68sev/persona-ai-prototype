"""
app.py - Main Application for Persona AI

This is the main entry point for the Persona AI user profile system.
It manages navigation between Interview, Profile, and Chat pages.

FIXES APPLIED:
1. Fixed schema mismatch - now correctly reads from USER_PROFILE_SCHEMA structure
2. Added imports from utils.py for proper error handling
3. Improved error handling throughout
4. Better integration with extract_preferences.py
5. Added save functionality to edit profile
6. Fixed tab navigation to AI Learning Profile after interview completion
7. Fixed list values display (converting ['value'] to 'value')
"""

import streamlit as st
import json
import os
import time
import importlib.util
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --------------------- Configuration ---------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
RESPONSES_FILE = os.path.join(BASE_DIR, "profiles", "interviewResponse.json")
QUESTIONS_FILE = os.path.join(BASE_DIR, "docs", "interviewQuestions.json")
EXTRACTED_PREFS_FILE = os.path.join(BASE_DIR, "profiles", "extractedPreferences.json")
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

# --------------------- Initialize Session State ---------------------
if "page" not in st.session_state:
    st.session_state.page = "interview"
if "interview_completed" not in st.session_state:
    st.session_state.interview_completed = False
if "selected_profile_tab" not in st.session_state:
    st.session_state.selected_profile_tab = 0  # 0 = Your Profile, 1 = AI Learning Profile
if "force_regenerate" not in st.session_state:
    st.session_state.force_regenerate = False

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

# --------------------- Auto Run extract_preferences.py ---------------------
def run_extract_preferences():
    """Run the preference extraction module."""
    try:
        # Import the silent extraction function
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

                    # Safe access to question text
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
                        
                        # Unique keys for widgets
                        if isinstance(value, (int, float)) and 1 <= value <= 10:
                            updated_responses[key] = st.slider(
                                "", 1, 10, int(value), key=f"slider_{key}"
                            )
                        else:
                            updated_responses[key] = st.text_area(
                                "", value=value, height=80, key=f"text_area_{key}"
                            )

                        st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

        # Save button
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("💾 Save Changes", type="primary", use_container_width=True):
                try:
                    # Remove old file if it exists
                    if os.path.exists(RESPONSES_FILE):
                        os.remove(RESPONSES_FILE)

                    # Save new responses                    
                    with open(RESPONSES_FILE, "w", encoding="utf-8") as f:
                        json.dump(updated_responses, f, indent=4)

                    # Also remove extracted preferences so it regenerates with new data                    
                    if os.path.exists(EXTRACTED_PREFS_FILE):
                        os.remove(EXTRACTED_PREFS_FILE)
                    
                    st.success("✅ Your profile has been updated successfully!")
                    st.info("🔄 AI Learning Profile will regenerate with your new responses.")
                    
                    # Wait a moment for user to see the message                    
                    time.sleep(1.5)
                    st.rerun()
                    
                except PermissionError:
                    st.error("❌ Permission denied. Cannot save changes.")
                except Exception as e:
                    st.error(f"❌ Error saving changes: {str(e)}")

    else:
        # ------------------ TAB 2: AI Learning Profile ------------------
        st.subheader("🧠 Personalized AI Learning Profile")
        
        # Check if we should force regeneration (coming from interview)
        should_generate = False
        if st.session_state.force_regenerate:
            if os.path.exists(EXTRACTED_PREFS_FILE):
                os.remove(EXTRACTED_PREFS_FILE)
            st.session_state.force_regenerate = False
            should_generate = True
        
        extracted_prefs = load_extracted_preferences()

        # Auto-generate if coming from interview or if profile doesn't exist
        if (should_generate or extracted_prefs is None):
            st.info("⚙️ Generating your AI learning profile...")
            run_extract_preferences()
            extracted_prefs = load_extracted_preferences()
        
        if extracted_prefs:
             # Get the learning_profile data (handle both nested and flat structures)
            lp = extracted_prefs.get("learning_profile", extracted_prefs)

            st.success("🎉 AI-generated learning profile found!")

            # ===== SUMMARY =====
            summary = clean_value(safe_get(lp, "summary", default="No summary generated."))
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
            st.markdown("<br>", unsafe_allow_html=True)

            # ===== SECTION 1: BACKGROUND =====
            st.markdown("### 📚 Background")
            bg = lp.get("background", {})
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

            st.markdown("<br>", unsafe_allow_html=True)

            # ===== SECTION 2: LEARNING PREFERENCES =====
            st.markdown("### 📖 Learning Preferences")
            lprefs = lp.get("learning_preferences", {})

            # Key preferences as badges
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

            # Detail level progress bar
            detail_level = lprefs.get("detail_level")
            if detail_level and isinstance(detail_level, (int, float)):
                st.markdown("**Detail Level Preference:**")
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.progress(min(detail_level / 10, 1.0))
                with col2:
                    st.markdown(f"**{int(detail_level)}/10**")

            # Additional preferences
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

            st.markdown("<br>", unsafe_allow_html=True)

            # ===== SECTION 3: COMMUNICATION STYLE =====
            st.markdown("### 💬 Communication Style")
            cs = lp.get("communication_style", {})
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

            st.markdown("<br>", unsafe_allow_html=True)

            # ===== SECTION 4: EMOTIONAL PATTERNS =====
            st.markdown("### 🧠 Emotional Patterns")
            ep = lp.get("emotional_patterns", {})
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
            
            # Confidence level progress bar
            confidence = ep.get("confidence_level")
            if confidence and isinstance(confidence, (int, float)):
                st.markdown("**Confidence Level:**")
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.progress(min(confidence / 10, 1.0))
                with col2:
                    st.markdown(f"**{int(confidence)}/10**")

            st.markdown("<br>", unsafe_allow_html=True)

            # ===== SECTION 5: STUDY BEHAVIOR =====
            st.markdown("### 📅 Study Behavior")
            sb = lp.get("study_behavior", {})
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    f"""
                    <div style="background-color:#E3F2FD; padding:15px; border-radius:12px;">
                        <b>Study Rhythm:</b> {clean_value(safe_get(sb, "study_rhythm"))}<br>
                        <b>Focus Duration:</b> {clean_value(safe_get(sb, "focus_duration"))}
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
            
            attention = sb.get("attention_span")
            if attention and isinstance(attention, (int, float)):
                st.markdown("**Attention Span:**")
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.progress(min(attention / 10, 1.0))
                with col2:
                    st.markdown(f"**{int(attention)}/10**")

            st.markdown("<br>", unsafe_allow_html=True)

            # ===== REGENERATE BUTTON =====
            if st.button("🔄 Regenerate Profile"):
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
        
        # Call the chatbot UI function
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
    