import os
import streamlit as st
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

CHAT_FOLDER = "profiles/chat_history"

def load_chat(subject):
    file_path = os.path.join(CHAT_FOLDER, f"{subject}.json")
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def analyze_feedback(subject):
    data = load_chat(subject)
    daily_feedback = []

    for date, messages in data.items():
        # Skip non-list entries (like feedback summaries)
        if not isinstance(messages, list):
            continue

        thumbs_up = sum(m.get("feedback", {}).get("thumbs_up", 0) for m in messages)
        thumbs_down = sum(m.get("feedback", {}).get("thumbs_down", 0) for m in messages)
        daily_feedback.append({
            "Date": date,
            "Thumbs Up": thumbs_up,
            "Thumbs Down": thumbs_down
        })

    return pd.DataFrame(daily_feedback).sort_values("Date", ascending=False)

# ---------------- Streamlit UI ----------------
st.title("📊 Chatbot Feedback Analysis")

# List subjects
subjects = [f.replace(".json", "") for f in os.listdir(CHAT_FOLDER) if f.endswith(".json")]
subject = st.selectbox("Select Subject", subjects, width=300)

df = analyze_feedback(subject)

if df.empty:
    st.info("No feedback data found for this subject yet.")
else:
# ---------------- Plot ----------------
    st.subheader("Daily Feedback Chart")
    fig, ax = plt.subplots(figsize=(4, 2))

    bar_width = 0.4

    ax.bar(df["Date"], df["Thumbs Up"], color="#4CAF50", label="👍 Thumbs Up", width=bar_width)
    ax.bar(df["Date"], df["Thumbs Down"], bottom=df["Thumbs Up"], color="#F44336", label="👎 Thumbs Down", width=bar_width)

    ax.set_ylabel("Count", fontsize=5)
    ax.set_xlabel("Date", fontsize=5)
    ax.set_title(f"Daily Feedback for Subject: '{subject}'", fontsize=7)
    ax.legend(fontsize=9)
    ax.tick_params(axis='x', labelrotation=45, labelsize=9)
    ax.tick_params(axis='y', labelsize=9)

    st.pyplot(fig)