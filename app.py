import streamlit as st
import pandas as pd
from datetime import date
import os
import requests

st.set_page_config(page_title="Daily Mood Tracker", layout="centered")
st.title("🧠 Daily Mood & Focus Tracker")

# Input form
with st.form("entry_form"):
    mood = st.slider("How's your mood today?", 1, 10, 5)
    sleep = st.slider("How many hours did you sleep?", 0, 12, 6)
    focus = st.slider("How focused did you feel?", 1, 10, 5)
    notes = st.text_area("Any notes or reflections?", "")
    submitted = st.form_submit_button("Save Entry")

file_path = "mood_log.csv"

deepseek_api_key = st.secrets["deepseek"]["api_key"]

def get_ai_feedback(mood, sleep, focus, notes):
    prompt = (
        f"Today, my mood was {mood}/10, I slept {sleep} hours, "
        f"and my focus level was {focus}/10. My notes: {notes}\n\n"
        "Please provide a short, kind reflection and one actionable tip for tomorrow."
    )
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }
        headers = {
            "Authorization": f"Bearer {deepseek_api_key}"
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ AI feedback failed: {e}"

if submitted:
    new_data = pd.DataFrame({
        "date": [date.today()],
        "mood": [mood],
        "sleep": [sleep],
        "focus": [focus],
        "notes": [notes]
    })
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data
    df.to_csv(file_path, index=False)
    st.success("✅ Entry saved!")

    with st.spinner("🤖 Generating AI reflection..."):
        ai_response = get_ai_feedback(mood, sleep, focus, notes)
    st.info(f"**AI Reflection:**\n\n{ai_response}")

if os.path.exists(file_path):
    data = pd.read_csv(file_path)
    if not data.empty and all(col in data.columns for col in ["mood", "sleep", "focus"]):
        st.subheader("📈 Mood, Sleep & Focus Over Time")
        st.line_chart(data[["mood", "sleep", "focus"]])
    with st.expander("📋 Show Past Entries"):
        st.dataframe(data[::-1])  # Most recent on top
