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
    
def save_chat(subject, role, content):
    folder = "profiles/chat_history"
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{subject}.json")

    timestamp = datetime.now().isoformat()
    entry = {"role": role, "content": content, "timestamp": timestamp}

    # Load existing messages
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(entry)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_chat(subject):
    folder = "profiles/chat_history"
    file_path = os.path.join(folder, f"{subject}.json")

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def generate_content():
    """
    Chatbot page.
    Users can ask questions and receive AI-generated responses.
    """
    st.title("💬 Chat with Persona AI")
    st.markdown("Ask anything — I'm here to help! 😇")

    profile = load_user_profile()

    # TODO: need to store the chat history 
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}

    # ---------------- Input box ----------------
    user_input = st.text_input(
        "You:", placeholder="Type your question here...", key="user_input"
    )

    # ----------------------------------------
    # Construct system prompt with user profile
    system_prompt = f"""
    You are Persona AI, a personalized assistant.

    Here is the user's profile data extracted from an interview:
    {json.dumps(profile, indent=2)}

    Always use this information to tailor your responses.
    Respond in a tone that the user prefers.
    Generate the content according to their learning preferences.
    """
    # --------------------------------------------

    # Load subjects dynamically
    subjects = load_subjects()
    subjects.insert(0, "General")  # Always have a general option

    subject = st.selectbox(
        "Select the topic/subject:",
        subjects,
        index=0
    )
    # Ensure chat history for the selected subject exists
    if subject not in st.session_state.chat_history:
        # Load from file if exists
        st.session_state.chat_history[subject] = load_chat(subject)

    if st.button("Send") and user_input:
        # Append to session state for this subject
        st.session_state.chat_history[subject].append({"role": "user", "content": user_input})
        save_chat(subject, "user", user_input)

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}]
                        + st.session_state.chat_history[subject],
                temperature=0.7,
            )
            ai_message = response.choices[0].message.content

            st.session_state.chat_history[subject].append({"role": "assistant", "content": ai_message})
            save_chat(subject, "assistant", ai_message)

        except Exception as e:
            ai_message = f"❌ Error generating response: {e}"
            st.error(ai_message)
            st.session_state.chat_history[subject].append({"role": "assistant", "content": ai_message})

    # ---------------- Display chat ----------------
    for msg in st.session_state.chat_history.get(subject, []):
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Persona:** {msg['content']}")
