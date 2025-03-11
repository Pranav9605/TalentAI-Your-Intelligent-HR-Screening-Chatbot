# frontend/streamlit_app.py

import streamlit as st
import requests

st.set_page_config(page_title="HR Chatbot", layout="wide")
st.title("HR Chatbot with JD Upload")

# Sidebar: Upload Job Description
st.sidebar.header("Upload Job Description")
uploaded_file = st.sidebar.file_uploader("Choose a JD file (TXT format)", type=["txt"])
if uploaded_file is not None:
    try:
        response = requests.post("http://localhost:8000/upload_jd", files={"file": uploaded_file})
        if response.status_code == 200:
            st.sidebar.success("Job description uploaded successfully!")
        else:
            st.sidebar.error("Failed to upload JD: " + response.text)
    except Exception as e:
        st.sidebar.error("Error connecting to backend: " + str(e))

# Chat Interface
st.header("Ask Your HR Questions")
user_input = st.text_input("Enter your HR-related question:")
if st.button("Send") and user_input:
    st.session_state.setdefault("chat_history", []).append(("You", user_input))
    payload = {"message": user_input}
    backend_url = "http://localhost:8000/chat"  # Update if necessary
    try:
        response = requests.post(backend_url, json=payload)
        if response.status_code == 200:
            data = response.json()
            st.write("**Response Breakdown:**")
            for seg in data["segments"]:
                st.markdown(f"**Segment:** {seg['segment']}")
                st.markdown(f"**Detected Intents:** {', '.join(seg['intents'])}")
                for intent, resp in seg["responses"].items():
                    st.markdown(f"**{intent.upper()} Response:** {resp}")
                    st.session_state.setdefault("chat_history", []).append((intent.upper(), resp))
                st.markdown("---")
        else:
            st.error("Backend error: " + response.text)
    except Exception as e:
        st.error("Error connecting to backend: " + str(e))

# Display Chat History
st.subheader("Chat History")
for sender, message in reversed(st.session_state.get("chat_history", [])):
    if sender == "You":
        st.markdown(
            f"<div style='background-color: #d4edda; padding: 10px; margin-bottom: 10px; border-radius: 10px;'>"
            f"<strong>{sender}:</strong> {message}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='background-color: #f8d7da; padding: 10px; margin-bottom: 10px; border-radius: 10px;'>"
            f"<strong>{sender}:</strong> {message}</div>",
            unsafe_allow_html=True,
        )
