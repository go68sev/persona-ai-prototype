import streamlit as st
import json
import os

# ----------------- Paths -----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_FILE = os.path.join(BASE_DIR, "profiles", "extractedPreferences.json")

st.set_page_config(page_title="Persona Analyzer", layout="wide")
st.title("📊 Deep Learning Persona Analyzer")

# ----------------- Check file -----------------
if not os.path.exists(PROFILE_FILE):
    st.error("❌ No extracted preferences found! Please run extraction first.")
    st.stop()

# ----------------- Load JSON -----------------
with open(PROFILE_FILE, "r", encoding="utf-8") as f:
    profile = json.load(f)

# 
# st.sidebar.header("📁 Loaded Preferences JSON")
# st.sidebar.json(profile)

# ============================================================================  
#                      FULL PERSONA OVERVIEW (TABLES ONLY)
# ============================================================================  

st.header("🧠 Your Full Learning Overview")
lp = profile.get("learning_profile", {})


def show_category(title, data_dict):
    if isinstance(data_dict, dict) and data_dict:
        st.subheader(title)
        clean_dict = {k.replace("_", " ").title(): v for k, v in data_dict.items()}
        st.table(clean_dict)
    elif isinstance(data_dict, list) and data_dict:
        st.subheader(title)
        st.table({f"{title} {i+1}": v for i,v in enumerate(data_dict)})
    elif isinstance(data_dict, str) and data_dict:
        st.subheader(title)
        st.write(data_dict)
    # skip empty or None data

col1, col2 = st.columns(2)

with col1:
    # General / Meta info
    show_category("📝 General Info", lp.get("general_info", {}))
    show_category("🎯 Learning Goals", lp.get("learning_goals", {}))
    show_category("🧩 Cognitive Style", lp.get("cognitive_style", {}))
    show_category("💬 Content Preferences", lp.get("content_preferences", {}))
    show_category("⏱ Pacing Preferences", lp.get("pacing_preferences", {}))
    show_category("🎧 Feedback Preferences", lp.get("feedback_preferences", {}))
    show_category("🏫 Preferred Study Environment", lp.get("preferred_study_environment", ""))
    show_category("💻 Technology Preferences", lp.get("technology_preferences", []))

with col2:
    show_category("❤️ Emotional Profile", lp.get("emotional_profile", {}))
    show_category("🔥 Motivation Profile", lp.get("motivation_profile", {}))
    show_category("📚 Behaviour Patterns", lp.get("behaviour_patterns", {}))
    show_category("🥺 Frustration Model", lp.get("frustration_model", {}))
    show_category("⚡ Engagement Model", lp.get("engagement_model", {}))
    show_category("🛠 Learning Challenges", lp.get("learning_challenges", []))
    show_category("📝 Notes", lp.get("notes", ""))

# Summary at the end
if "summary" in lp:
    st.subheader("📝 Persona Summary")
    st.info(lp["summary"])
