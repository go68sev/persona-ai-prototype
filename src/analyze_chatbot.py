import os
import streamlit as st
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_FOLDER = "profiles/chat_history"
PROGRESS_FOLDER = "profiles/progress_tracker"

def load_chat(subject):
    file_path = os.path.join(CHAT_FOLDER, f"{subject}.json")
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def load_progress(subject):
    path = os.path.join(PROGRESS_FOLDER, f"{subject}.json")

    # If file does not exist, create an empty one
    if not os.path.exists(path):
        os.makedirs(PROGRESS_FOLDER, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
        return {}

    # Load existing file
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If file is corrupted, reset safely
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
        return {}

    

def save_progress(subject, date, entry):
    os.makedirs(PROGRESS_FOLDER, exist_ok=True)
    path = os.path.join(PROGRESS_FOLDER, f"{subject}.json")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        data = {}

    # Save ONE object per date (overwrite allowed)
    data[date] = entry

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


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

def build_chat_text(chat_data, date):
    """
    Convert chat history of a given date into a readable text
    for LLM analysis.
    """
    messages = chat_data.get(date, [])
    lines = []

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")

        if role == "user":
            lines.append(f"[{timestamp}] User: {content}")
        elif role == "assistant":
            lines.append(f"[{timestamp}] Assistant: {content}")

    return "\n".join(lines)


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


# ---------------- Study Behavior Analysis ----------------
st.divider()
st.subheader("📘 Study Behavior Analysis")

chat_data = load_chat(subject)

# Available dates (only real chat days)
available_dates = [
    d for d, msgs in chat_data.items()
    if isinstance(msgs, list) and len(msgs) > 0
]

if not available_dates:
    st.info("No chat history available for study behavior analysis.")
else:
    selected_date = st.selectbox(
        "Select Date",
        sorted(available_dates, reverse=True),
        width=300
    )

    if st.button("Analyze Study Behavior"):
        chat_text = build_chat_text(chat_data, selected_date)

        if not chat_text.strip():
            st.warning("No chat content found for this date.")
        else:
            with st.spinner("Analyzing study behavior..."):
                
                prompt = f"""
You are an educational analyst AI.

Below is a full chat conversation between a student and a tutor
for ONE study session on {selected_date}.

Each message includes a timestamp in ISO format.

Your tasks:
1. Analyze the student's study behavior in 2-4 concise sentences. You are talking to the student directly, so use "you" and "your".
2. Estimate the approximate total time the student actively spent studying this subject.

Return ONLY valid JSON.
Do NOT include markdown.
Do NOT include explanations.
Do NOT include extra text.

The JSON must follow EXACTLY this schema:

{{
  "date": "<YYYY-MM-DD>",
  "summary": "<concise summary>",
  "topics_covered": "<comma-separated topics>",
  "estimated_study_time": "<time in minutes or hours>",
  "confidence_level": "<number out of 10>",
  "satisfaction_level": "<number out of 10>",
  "mood": "<short description>",
  "improvements": "<specific suggestions>"
}}

Conversation:
{chat_text}
"""

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You analyze study behavior."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.4,
                    )

                    analysis_text = response.choices[0].message.content.strip()
                    try:
                        analysis_json = json.loads(analysis_text)
                    except json.JSONDecodeError:
                        st.error("LLM did not return valid JSON")
                        st.text(analysis_text)
                        st.stop()

                    st.markdown("### 🧠 Study Behavior Summary")

                    st.markdown(
                        f"""
                        <div style="padding:14px; border-radius:8px; background-color:#f5f5f5;">
                        <b>Summary:</b> {analysis_json["summary"]}<br><br>
                        <b>Main topics covered:</b> {analysis_json["topics_covered"]}<br>
                        <b>Estimated study time:</b> {analysis_json["estimated_study_time"]}<br>
                        <b>Confidence level:</b> {analysis_json["confidence_level"]}<br>
                        <b>Satisfaction level:</b> {analysis_json["satisfaction_level"]}<br>
                        <b>Mood:</b> {analysis_json["mood"]}<br><br>
                        <b>What can be improved:</b> {analysis_json["improvements"]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    # Save analysis to progress tracker
                    save_progress(
                        subject,
                        analysis_json["date"],
                        {
                            "Topics covered": analysis_json["topics_covered"],
                            "Time spent on the subject": analysis_json["estimated_study_time"],
                            "Mood": analysis_json["mood"],
                            "Satisfaction level": analysis_json["satisfaction_level"]
                        }
                    )

                except Exception as e:
                    st.error(f"Failed to analyze study behavior: {e}")


