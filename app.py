import streamlit as st
import pandas as pd
from datetime import date
import os
import openai

# 🔐 Load API Key from Streamlit Secrets
OPENROUTER_API_KEY = st.secrets["openrouter"]["api_key"]
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"  # Important for OpenRouter

st.set_page_config(page_title="Daily Mood Tracker", layout="centered")
st.title("🧠 Daily Mood & Focus Tracker")

# Input form
with st.form("entry_form"):
    mood = st.slider("How's your mood today?", 1, 10, 5)
    sleep = st.slider("How many hours did you sleep?", 0, 12, 6)
    focus = st.slider("How focused did you feel?", 1, 10, 5)
    notes = st.text_area("Any notes or reflections?", "")
    submitted = st.form_submit_button("Save Entry")

# Path to CSV log
file_path = "mood_log.csv"

def get_ai_feedback(mood, sleep, focus, notes):
    prompt = (
        f"Today, my mood was {mood}/10, I slept {sleep} hours, "
        f"and my focus level was {focus}/10. My notes: {notes}\n\n"
        "Please provide a short, kind reflection and one actionable tip for tomorrow."
    )
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"⚠️ AI feedback failed: {e}"

# Save data and display AI reflection
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

# Load & display history
if os.path.exists(file_path):
    data = pd.read_csv(file_path)
    if not data.empty and all(col in data.columns for col in ["mood", "sleep", "focus"]):
        st.subheader("📈 Mood, Sleep & Focus Over Time")
        st.line_chart(data[["mood", "sleep", "focus"]])
    with st.expander("📋 Show Past Entries"):
        st.dataframe(data[::-1])  # Most recent on top
