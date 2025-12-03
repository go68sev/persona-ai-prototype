import os
import streamlit as st
from openai import OpenAI
import json
import utils

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
EXTRACTED_PREFS_FILE = os.path.join(BASE_DIR, "profiles", "extractedPreferences.json")

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
        st.session_state.chat_history = []

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


    if st.button("Send") and user_input:
        # Save user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        print(system_prompt)

        # Generate AI response
        try:
            # Use your OpenAI client
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}]
                         + st.session_state.chat_history,
                temperature=0.7,
            )
            ai_message = response.choices[0].message.content

            # Save AI message
            st.session_state.chat_history.append({"role": "assistant", "content": ai_message})

        except Exception as e:
            ai_message = f"❌ Error generating response: {e}"
            st.error(ai_message)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_message})

    # ---------------- Display chat ----------------
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**Persona:** {msg['content']}")
