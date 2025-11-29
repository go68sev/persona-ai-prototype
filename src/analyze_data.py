import pandas as pd
import streamlit as st
import json
import os

# ----------------- Paths -----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_FILE = os.path.join(BASE_DIR, "profiles", "extractedPreferences.json")

st.set_page_config(page_title="Persona Analyzer", layout="wide")
st.title("📊 Your Persona Analyzer")

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
    st.subheader(title)
    
    # If it's not a dict, just show it as a single row
    if not isinstance(data_dict, dict):
        st.table(pd.DataFrame({"Value": [data_dict]}, index=[title]))
        return
    
    # Convert keys nicely
    clean_dict = {k.replace("_", " ").title(): v for k, v in data_dict.items()}
    
    # Convert non-scalars to strings
    for k, v in clean_dict.items():
        if isinstance(v, (list, dict)):
            clean_dict[k] = str(v)
    
    # Create DataFrame with row headers
    df = pd.DataFrame.from_dict(clean_dict, orient='index', columns=['Value'])
    
    st.table(df)

col1, col2 = st.columns(2)

with col1:
    # General / Meta info
    show_category("📝 Personal Background", lp.get("personal_background", {}))
    show_category("🎯 Learning Goals", lp.get("learning_goals", {}))
    show_category("📚 Learning Prefernces", lp.get("learning_preferences", {}))
    show_category("🧩 Cognitive Style", lp.get("cognitive_style", {}))
    show_category("💬 Content Preferences", lp.get("content_preferences", {}))
    show_category("⏱ Pacing Preferences", lp.get("pacing_preferences", {}))
    show_category("🎧 Feedback Preferences", lp.get("feedback_preferences", {}))

with col2:
    show_category("❤️ Emotional Profile", lp.get("academic_emotions_and_behavior", {}))
    show_category("🔥 Motivation Profile", lp.get("motivation_profile", {}))
    show_category("🗣️ Communication style", lp.get("communication_style", {}))
    show_category("📚 Behaviour Patterns", lp.get("behaviour_patterns", {}))
    show_category("🥺 Frustration Model", lp.get("frustration_model", {}))
    show_category("⚡ Engagement Model", lp.get("engagement_model", {}))
    # show_category("🛠 Learning Challenges", lp.get("learning_challenges", []))   # not needed right now

# Summary at the end
if "summary" in lp:
    st.subheader("📝 Persona Summary")
    st.write(lp["summary"])
