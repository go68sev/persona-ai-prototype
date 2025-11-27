import streamlit as st
import json
import time
import os

# --------------------- Step 0: Define paths ---------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root
QUESTIONS_FILE = os.path.join(BASE_DIR, "docs", "interviewQuestions.json")
RESPONSES_FILE = os.path.join(BASE_DIR, "profiles", "interviewResponse.json")  # Save in profiles/

# Ensure profiles folder exists
os.makedirs(os.path.join(BASE_DIR, "profiles"), exist_ok=True)

# --------------------- Step 1: Load Questions ---------------------
with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
    questions_data = json.load(f)

sections = [key for key in questions_data.keys() if key not in ["OPENING SCRIPT", "Closing SCRIPT"]]

# --------------------- Step 2: Initialize Session State ---------------------
for key, default in {
    "section_idx": -1,
    "question_idx": 0,
    "responses": {},
    "opening_displayed": False,
    "closing_displayed": False,
    "rerun_flag": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --------------------- Step 3: Typing Effect ---------------------
def typing_effect(text, speed=0.03):
    placeholder = st.empty()
    typed_text = ""
    for char in text:
        typed_text += char
        placeholder.markdown(typed_text)
        time.sleep(speed)

# --------------------- Step 4: Handle Opening Script ---------------------
if st.session_state.section_idx == -1:
    if not st.session_state.opening_displayed:
        typing_effect(questions_data["OPENING SCRIPT"]["script"])
        st.session_state.opening_displayed = True
    else:
        st.markdown(questions_data["OPENING SCRIPT"]["script"])

    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #4CAF50;
            color: white;
            padding: 12px 28px;
            font-size: 18px;
            border-radius: 10px;
            transition: transform 0.3s;
        }
        div.stButton > button:first-child:hover {
            background-color: #45a049;
            transform: scale(1.05);
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("Start Interview 🚀", key="start_interview"):
        st.session_state.section_idx = 0
        st.session_state.question_idx = 0
        st.rerun()

    st.stop()

# --------------------- Step 5: Display Questions ---------------------
if st.session_state.section_idx >= len(sections):
    if not st.session_state.closing_displayed:
        st.session_state.closing_displayed = True
        typing_effect(questions_data["Closing SCRIPT"]["script"])
    
    st.success("🎉 Interview Completed!")
    st.json(st.session_state.responses)

    # Save responses to JSON inside profiles folder
    with open(RESPONSES_FILE, "w", encoding="utf-8") as json_file:
        json.dump(st.session_state.responses, json_file, indent=4)
    st.write(f"✅ Responses saved to `{RESPONSES_FILE}`")
    
    st.stop()

current_section = sections[st.session_state.section_idx]
section_questions = questions_data[current_section]
current_q = section_questions[st.session_state.question_idx]

st.title(current_section)
st.write(f"**Question {st.session_state.question_idx + 1} / {len(section_questions)}**")
st.progress((st.session_state.question_idx + 1) / len(section_questions))

st.markdown("""
    <style>
    .big-question {
        font-size: 24px;
        font-weight: bold;
        color: #1f1f1f;
        margin-bottom: 20px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Show question based on type
response_key = f"{current_section}-{st.session_state.question_idx}"
existing_response = st.session_state.responses.get(response_key, None)

response = None
if current_q["type"] == "text":
    st.markdown(f'<p class="big-question">{current_q["question"]}</p>', unsafe_allow_html=True)
    response = st.text_area("", value=existing_response if existing_response else "", placeholder=current_q.get("placeholder", ""), label_visibility="collapsed")
elif current_q["type"] == "mcq":
    st.markdown(f'<p class="big-question">{current_q["question"]}</p>', unsafe_allow_html=True)
    options = current_q.get("options", [])
    default_index = options.index(existing_response) if existing_response in options else 0
    response = st.radio("", options, index=default_index, label_visibility="collapsed")
elif current_q["type"] == "rating":
    st.markdown(f'<p class="big-question">{current_q["question"]}</p>', unsafe_allow_html=True)
    default_value = existing_response if existing_response else 1
    response = st.slider("", 1, current_q["scale"], value=default_value, label_visibility="collapsed")

# Check if question is mandatory
is_mandatory = True
if st.session_state.section_idx == 0 and st.session_state.question_idx == len(section_questions) - 1:
    is_mandatory = False

# --------------------- Step 6: Navigation Buttons ---------------------
st.markdown("<br>", unsafe_allow_html=True)

show_previous = st.session_state.section_idx > 0 or st.session_state.question_idx > 0
error_placeholder = st.empty()

if show_previous:
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️", key="prev_question", use_container_width=True):
            st.session_state.responses[response_key] = response
            
            if st.session_state.question_idx > 0:
                st.session_state.question_idx -= 1
            else:
                st.session_state.section_idx -= 1
                st.session_state.question_idx = len(questions_data[sections[st.session_state.section_idx]]) - 1
            st.rerun()
    
    with col3:
        if st.button("➡️", key="next_question", use_container_width=True):
            if is_mandatory:
                error_msg = None
                if current_q["type"] == "text" and (not response or response.strip() == ""):
                    error_msg = "⚠️ Please answer this question before proceeding."
                elif current_q["type"] == "mcq" and not response:
                    error_msg = "⚠️ Please select an option before proceeding."
                elif current_q["type"] == "rating" and not response:
                    error_msg = "⚠️ Please provide a rating before proceeding."
                
                if error_msg:
                    error_placeholder.error(error_msg)
                    st.stop()
            
            st.session_state.responses[response_key] = response

            if st.session_state.question_idx < len(section_questions) - 1:
                st.session_state.question_idx += 1
            else:
                st.session_state.section_idx += 1
                st.session_state.question_idx = 0
            
            st.rerun()
else:
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button("➡️", key="next_question", use_container_width=True):
            if is_mandatory:
                error_msg = None
                if current_q["type"] == "text" and (not response or response.strip() == ""):
                    error_msg = "⚠️ Please answer this question before proceeding."
                elif current_q["type"] == "mcq" and not response:
                    error_msg = "⚠️ Please select an option before proceeding."
                elif current_q["type"] == "rating" and not response:
                    error_msg = "⚠️ Please provide a rating before proceeding."
                
                if error_msg:
                    error_placeholder.error(error_msg)
                    st.stop()
            
            st.session_state.responses[response_key] = response

            if st.session_state.question_idx < len(section_questions) - 1:
                st.session_state.question_idx += 1
            else:
                st.session_state.section_idx += 1
                st.session_state.question_idx = 0
            
            st.rerun()
