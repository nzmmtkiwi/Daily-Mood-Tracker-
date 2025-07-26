import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os
import requests

st.set_page_config(page_title="Country Economy Sentiment", layout="centered")
st.title("🌏 Country Economy Sentiment (Last 30 Days)")

countries = ["New Zealand", "Australia", "USA", "UK", "Singapore", "Other"]
selected_country = st.selectbox("Select a country to compare with Singapore", countries)

def get_economy_sentiment(country):
    # Replace this with a real API call if available
    # For now, return a placeholder
    return f"Sentiment summary for {country} (last 30 days):\n\n- Economy is stable.\n- Consumer confidence is moderate.\n- Inflation is under control."

if selected_country:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"{selected_country}")
        sentiment = get_economy_sentiment(selected_country)
        st.info(sentiment)
    with col2:
        st.subheader("Singapore")
        sg_sentiment = get_economy_sentiment("Singapore")
        st.info(sg_sentiment)

# Daily Mood Tracker Section
st.title("🧠 Daily Mood & Focus Tracker")

# Input form
with st.form("entry_form"):
    country = st.selectbox("Country", countries)
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

def get_country_sentiment(country, data):
    last_30 = data[
        (data['country'] == country) &
        (pd.to_datetime(data['date']) >= pd.Timestamp.today() - timedelta(days=30))
    ]
    if last_30.empty:
        return "No entries for this country in the last 30 days."
    notes_concat = "\n".join(last_30['notes'].dropna())
    prompt = (
        f"Here are daily notes from people in {country} over the last 30 days:\n{notes_concat}\n\n"
        "Summarize the overall sentiment and provide a short reflection for this country."
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
        return f"⚠️ AI sentiment summary failed: {e}"

if submitted:
    new_data = pd.DataFrame({
        "date": [date.today()],
        "country": [country],
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
    st.subheader("🌏 Country Sentiment Summary (Last 30 Days)")
    selected_country = st.selectbox("Select country for sentiment summary", countries)
    if "country" in data.columns:
        with st.spinner("🤖 Analyzing country sentiment..."):
            sentiment = get_country_sentiment(selected_country, data)
        st.info(f"**{selected_country} Sentiment:**\n\n{sentiment}")
    else:
        st.warning("No country data available in your log. New entries will include country information.")

    if not data.empty and all(col in data.columns for col in ["mood", "sleep", "focus"]):
        st.subheader("📈 Mood, Sleep & Focus Over Time")
        st.line_chart(data[["mood", "sleep", "focus"]])
    with st.expander("📋 Show Past Entries"):
        st.dataframe(data[::-1])  # Most recent on top
