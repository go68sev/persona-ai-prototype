import os
import streamlit as st
from openai import OpenAI
import json
import utils
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
EXTRACTED_PREFS_FILE = os.path.join(BASE_DIR, "profiles", "extractedPreferences.json")
INTERVIEW_RESPONSES_FILE = os.path.join(BASE_DIR, "profiles", "interviewResponse.json")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_user_profile():
    """Load extracted preferences with proper error handling."""
    if not os.path.exists(EXTRACTED_PREFS_FILE):
        return None

    try:
        if os.path.getsize(EXTRACTED_PREFS_FILE) == 0:
            return None

        with open(EXTRACTED_PREFS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            return utils.safe_json_loads(content) if content.strip() else None
    except json.JSONDecodeError as e:
        st.error(f"⚠️ AI profile JSON is corrupted: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Error loading extracted preferences: {str(e)}")
        return None

def load_subjects():
    if not os.path.exists(INTERVIEW_RESPONSES_FILE):
        return ["general"]

    try:
        with open(INTERVIEW_RESPONSES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Assuming "SECTION 1 — Personal Background-1" contains topics
        topics = data.get("SECTION 1 — Personal Background-1", "")
        if topics:
            # Split by comma and strip whitespace
            subjects = [t.strip() for t in topics.split(",")]
            return subjects
        else:
            return ["general"]

    except Exception as e:
        st.error(f"❌ Could not load subjects: {e}")
        return ["general"]
    
def save_chat(subject, role, content, date=None, msg_index=None):
    """
    Save a chat message or update feedback in the chat JSON file.
    
    Args:
        subject (str): Subject name.
        role (str): 'user' or 'assistant'.
        content (str): Message content.
        date (str, optional): Date string 'YYYY-MM-DD'. Defaults to today.
        msg_index (int, optional): Index of message to update (for feedback). If None, append new message.
    """
    folder = "profiles/chat_history"
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{subject}.json")

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    # Load existing data
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        data = {}

    # Ensure today's list exists
    if date not in data:
        data[date] = []

    # If msg_index is provided, update that message (feedback)
    if msg_index is not None:
        if 0 <= msg_index < len(data[date]):
            data[date][msg_index] = content
        else:
            # Fallback: append if index is invalid
            data[date].append(content)
    else:
        # Append new message
        data[date].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "feedback": {"thumbs_up": 0, "thumbs_down": 0} if role == "assistant" else {}
        })

    # Save back to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_chat(subject):
    folder = "profiles/chat_history"
    file_path = os.path.join(folder, f"{subject}.json")

    if not os.path.exists(file_path):
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_feedback(subject, date):
    folder = "profiles/chat_history"
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{subject}.json")

    # Load existing data
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        data = {}

    # Ensure date entry exists
    if date not in data:
        data[date] = []

    # Update counts for today
    counts = st.session_state.feedback_summary[subject][date]
    data[date + "_feedback"] = counts

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_content():
    """
    Chatbot page with:
    - right-side subject selector
    - daily chat sessions stored inside the subject JSON
    - ability to view old chats
    - thumbs up/down feedback per AI response
    """
    # ---------------- Layout ----------------
    left, right = st.columns([3, 1])

    with left:
        st.title("💬 Chat with Persona AI")
        st.markdown("Ask anything — I'm here to help! 😇")

    # ---------------- Dropdown Row ----------------
    col1, col2 = st.columns([1, 1])

    with col1:
        subjects = load_subjects()
        subjects.insert(0, "General")
        subject = st.selectbox(
            "Subject",
            subjects,
            key="subject_dropdown"
        )

    # Load chat history after subject loads
    profile = load_user_profile()

    # ---------------- Manage Session State ----------------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}

    # Load subject chat history (from file if first time)
    if subject not in st.session_state.chat_history:
        st.session_state.chat_history[subject] = load_chat(subject)

    chat_by_date = st.session_state.chat_history[subject]
    today = datetime.now().strftime("%Y-%m-%d")

    if today not in chat_by_date:
        chat_by_date[today] = []

    chat_dates = sorted(chat_by_date.keys(), reverse=True)

    with col2:
        active_date = st.selectbox(
            "Chat session",
            chat_dates,
            index=0,
            key="date_dropdown"
        )

    # ---------------- Chat Input ----------------
    user_input = st.text_input(
        "You:",
        placeholder="Type your question here...",
        key="user_input"
    )

    # ---------------- Chat Send Logic ----------------
    if st.button("Send", key="send_button") and user_input.strip():
        # Append user message
        chat_by_date[active_date].append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        save_chat(subject, "user", user_input)

        # Build system prompt
        system_prompt = f"""
        You are Persona AI, a personalized assistant.

        Here is the user's profile data extracted from an interview:
        {json.dumps(profile, indent=2)}

        The topic we are dealing with is "{subject}".

        Always use this information to tailor your responses.
        Respond in a tone that the user prefers.
        Generate the content according to their learning preferences.
        """

        # Generate AI response
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}]
                         + chat_by_date[active_date],
                temperature=0.7,
            )
            ai_message =  response.choices[0].message.content
            print("AI Response:", ai_message)

            chat_by_date[active_date].append({
                "role": "assistant",
                "content": ai_message,
                "timestamp": datetime.now().isoformat(),
                "feedback": {"thumbs_up": 0, "thumbs_down": 0}
            })
            save_chat(subject, "assistant", ai_message)

        except Exception as e:
            ai_message = f"❌ Error generating response: {str(e)}"
            st.error(ai_message)
            chat_by_date[active_date].append({
                "role": "assistant",
                "content": 'Error generating response.',
                "timestamp": datetime.now().isoformat(),
                "feedback": {"thumbs_up": 0, "thumbs_down": 0}
            })
            save_chat(subject, "assistant", chat_by_date[active_date][-1])

    # ---------------- Display Chat ----------------
    messages = chat_by_date.get(active_date, [])
    chat_container = st.container()
    for i, msg in enumerate(messages):
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Persona:** {msg['content']}")

            # -------- Feedback Buttons per AI message --------
            col_up, col_down, _ = st.columns([1, 1, 7])

            thumbs_up_key = f"up_{active_date}_{i}"
            thumbs_down_key = f"down_{active_date}_{i}"

            # Render buttons with markdown and HTML
            thumbs_up_clicked = col_up.button("👍", key=thumbs_up_key, help="Press to like", args=None)
            thumbs_down_clicked = col_down.button("👎", key=thumbs_down_key, help="Press to dislike", args=None)

            # Logic to handle clicks and highlight
            if thumbs_up_clicked:
                msg["feedback"]["thumbs_up"] = 1
                msg["feedback"]["thumbs_down"] = 0
                save_chat(subject, "assistant", msg, date=active_date, msg_index=i)

            if thumbs_down_clicked:
                msg["feedback"]["thumbs_down"] = 1
                msg["feedback"]["thumbs_up"] = 0
                save_chat(subject, "assistant", msg, date=active_date, msg_index=i)
