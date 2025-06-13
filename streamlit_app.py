import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from streamlit import secrets as _secrets_module

st.title("Reddit Sentiment Trend Analyzer")
st.markdown("Enter a subreddit or keyword, choose number of posts, and see sentiment over time.")

# Safely get BACKEND_URL from secrets, fallback if missing
try:
    BACKEND_URL = st.secrets["BACKEND_URL"]
except Exception:
    BACKEND_URL = "http://127.0.0.1:8000/api/sentiment/"

mode = st.radio("Mode", ["Subreddit", "Keyword"])
if mode == "Subreddit":
    user_input = st.text_input("Subreddit name (without r/)", value="python")
    params = {"subreddit": user_input}
else:
    user_input = st.text_input("Keyword to search", value="openAI")
    params = {"keyword": user_input}

limit = st.slider("Number of posts to fetch", min_value=10, max_value=200, value=50, step=10)
params["limit"] = limit

if st.button("Fetch & Analyze"):
    with st.spinner("Fetching and analyzing..."):
        try:
            resp = requests.get(BACKEND_URL, params=params, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            if 'error' in result:
                st.error(f"Error from backend: {result['error']}")
            else:
                data = result.get("data", [])
                if not data:
                    st.warning("No data returned.")
                else:
                    df = pd.DataFrame(data)
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df.set_index('timestamp', inplace=True)
                    df_hour = df.resample('1H').mean().dropna()
                    fig, ax = plt.subplots()
                    ax.plot(df_hour.index, df_hour['sentiment'], marker='o')
                    ax.set_title(f"Average Sentiment over Time ({mode}: {user_input})")
                    ax.set_xlabel("Time")
                    ax.set_ylabel("Sentiment (VADER compound)")
                    ax.axhline(0, linestyle='--', linewidth=0.5)
                    st.pyplot(fig)
                    if st.checkbox("Show raw data"):
                        st.dataframe(df.reset_index().sort_values('timestamp'))
        except Exception as e:
            st.error(f"Request failed: {e}")
