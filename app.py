import streamlit as st
import pandas as pd
from datetime import date
import os

# 🔐 Secrets
OPENROUTER_API_KEY = st.secrets["openrouter"]["api_key"]
API_KEY = st.secrets["alpha_vantage"]["api_key"]

st.title("🧠 Daily Mood & Focus Tracker")

# Input form
with st.form("entry_form"):
    mood = st.slider("How's your mood today?", 1, 10, 5)
    sleep = st.slider("How many hours did you sleep?", 0, 12, 6)
    focus = st.slider("How focused did you feel?", 1, 10, 5)
    notes = st.text_area("Any notes or reflections?", "")
    submitted = st.form_submit_button("Save Entry")

# Prepare data file
file_path = "mood_log.csv"

# Save data if submitted
if submitted:
    new_data = pd.DataFrame({
        "date": [date.today()],
        "mood": [mood],
        "sleep": [sleep],
        "focus": [focus],
        "notes": [notes]
    })
    if os.path.exists(file_path):
        existing = pd.read_csv(file_path)
        df = pd.concat([existing, new_data], ignore_index=True)
    else:
        df = new_data
    df.to_csv(file_path, index=False)
    st.success("✅ Entry saved!")

# Load and display past data
if os.path.exists(file_path):
    st.subheader("📈 Mood & Focus Over Time")
    data = pd.read_csv(file_path)
    st.line_chart(data[["mood", "sleep", "focus"]])
    with st.expander("📋 Show Past Entries"):
        st.dataframe(data[::-1])  # show most recent first
