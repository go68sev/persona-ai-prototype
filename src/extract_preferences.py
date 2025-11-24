import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("Interview Preference Extractor")

interview_text = st.text_area("Enter interview transcript:")

if st.button("Analyze"):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Echo what the user says"},
            {"role": "user", "content": interview_text}
        ]
    )
    st.write(response.choices[0].message.content)