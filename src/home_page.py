import streamlit as st
import json
import os
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
EXTRACT_PREFS_PY_PATH = os.path.join(CURRENT_DIR, "extract_preferences.py")

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

if os.path.exists(RESPONSES_FILE) and os.path.getsize(RESPONSES_FILE) > 0:
    st.session_state.interview_completed = True

# --------------------- Load Data Helpers ---------------------
def load_responses():
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_questions():
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_extracted_preferences():
    if os.path.exists(EXTRACTED_PREFS_FILE) and os.path.getsize(EXTRACTED_PREFS_FILE) > 0:
        with open(EXTRACTED_PREFS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                st.error("⚠ AI profile JSON is corrupted.")
                return None
    return None

# --------------------- Auto Run extract_preferences.py ---------------------
def run_extract_preferences():
    if not os.path.exists(EXTRACTED_PREFS_FILE):
        with st.spinner("🔍 Generating AI learning profile..."):
            spec = importlib.util.spec_from_file_location("extract_preferences", EXTRACT_PREFS_PY_PATH)
            extract_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(extract_module)
        st.toast("✨ AI Profile generated successfully!", icon="🤖")
        st.rerun()
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

    tab1, tab2 = st.tabs(["📖 Your Profile", "🎯 AI Learning Profile"])

    # ------------------ TAB 1: Editable Profile ------------------
    with tab1:
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
                    question_text = questions_data.get(section, [{}])[question_idx].get("question", "Question not found")

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

    # ------------------ TAB 2: AI Learning Profile ------------------
    with tab2:
        st.subheader("🧠 Personalized AI Learning Profile")
        extracted_prefs = load_extracted_preferences()

        if extracted_prefs:
            lp = extracted_prefs.get("learning_profile", {})

            # Summary
            summary = lp.get("summary", "No summary generated.")

            # Traits
            traits = lp.get("traits", [])
            if not isinstance(traits, list): traits = [traits]

            # Learning style / environment
            learning_style = lp.get("cognitive_style", {}).get("processing_style", "Not specified")
            environment = lp.get("preferred_study_environment", "Not specified")

            # Struggles / motivation factors
            struggles = lp.get("learning_challenges", [])
            if not isinstance(struggles, list): struggles = [struggles]
            motivation_factors = lp.get("motivation_profile", {}).get("intrinsic_motivators", [])
            if not isinstance(motivation_factors, list): motivation_factors = [motivation_factors]

            # Strategies - example: could be added as a list
            strategies = lp.get("content_preferences", {}).get("preferred_use_cases_or_contexts", [])
            if not isinstance(strategies, list): strategies = [strategies]

            st.success("🎉 AI-generated learning profile found!")

            # Overview
            st.markdown(
                f"""
                <div style="background: linear-gradient(to right, #FFF3E0, #FFE0B2);
                            padding: 20px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                    <h4>📌 Overview</h4>
                    <p style="margin-top: 10px;">{summary}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)

            # Traits badges
            traits_html = "".join(
                f"<span style='background-color:#E8F4FD; padding:5px 12px; margin:4px; border-radius:15px; display:inline-block;'>{t}</span>"
                for t in traits
            )
            st.markdown(
                f"""
                <div style="background-color:#E3F2FD; padding:15px; border-radius:12px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                    <h4>🔍 Key Traits</h4>
                    {traits_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # Two columns
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f"""
                    <div style="background-color:#F1F8E9; padding:15px; border-radius:12px;">
                        <h4>🎯 Preferred Learning Style</h4>
                        <p>{learning_style}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                    <div style="background-color:#FFFDE7; padding:15px; border-radius:12px;">
                        <h4>🏡 Best Environment</h4>
                        <p>{environment}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    f"""
                    <div style="background-color:#FFEBEE; padding:15px; border-radius:12px;">
                        <h4>⚠ Learning Challenges</h4>
                        <p>{', '.join(struggles)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                    <div style="background-color:#E8F5E9; padding:15px; border-radius:12px;">
                        <h4>💪 Motivation Factors</h4>
                        <p>{', '.join(motivation_factors)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # Strategies
            strategies_html = "".join([f"<li>{s}</li>" for s in strategies])
            st.markdown(
                f"""
                <div style="background-color:#EDE7F6; padding:15px; border-radius:12px;">
                    <h4>📚 Recommended Strategies / Use Cases</h4>
                    <ul>{strategies_html}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("🔄 Regenerate Profile"):
                if os.path.exists(EXTRACTED_PREFS_FILE):
                    os.remove(EXTRACTED_PREFS_FILE)
                st.rerun()
        else:
            st.info("⚙ No AI profile found. Generating now...")
            run_extract_preferences()

# --------------------- Interview Page ---------------------
def interview_page():
    spec = importlib.util.spec_from_file_location("interview", INTERVIEW_PY_PATH)
    interview_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(interview_module)

    if os.path.exists(RESPONSES_FILE) and os.path.getsize(RESPONSES_FILE) > 0:
        st.session_state.interview_completed = True

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
                st.rerun()
            if st.button("💬 Chat with Persona"):
                st.session_state.page = "chatbot"
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

if __name__ == "__main__":
    main()
