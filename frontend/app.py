import streamlit as st

st.set_page_config(
    page_title="HR Chatbot",
    page_icon="🤖",
    layout="wide"
)

import requests
import time
import sys
import os

# Start backend
@st.cache_resource
def init_backend():
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from main import start_api_server
        start_api_server()
        return True
    except Exception as e:
        st.error(f"Backend failed: {e}")
        return False

backend_ready = init_backend()
API_URL = "http://127.0.0.1:8000"

# Simple CSS
st.markdown("""
<style>
.user-msg { background: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right; }
.bot-msg { background: #f5f5f5; padding: 10px; border-radius: 10px; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

def check_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200, response.json()
    except:
        return False, {"error": "Backend not ready"}

def upload_file(content, filename):
    try:
        response = requests.post(f"{API_URL}/upload_jd_direct", 
                               json={"filename": filename, "content": content}, 
                               timeout=30)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, f"Error: {str(e)}"

def send_message(message):
    try:
        response = requests.post(f"{API_URL}/chat", 
                               json={"message": message}, 
                               timeout=30)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"response": f"Error: {str(e)}", "intent": "error"}

# Main app
st.title("🤖 HR Chatbot Assistant")

# Check backend
if not backend_ready:
    st.error("❌ Backend failed to start")
    st.stop()

healthy, info = check_health()
if not healthy:
    st.error("❌ Backend not ready")
    st.json(info)
    st.stop()

st.success("✅ Backend Online")
if info.get("api_configured"):
    st.success("🔑 API Key OK")
else:
    st.warning("⚠️ API Key Missing")

# Two columns
col1, col2 = st.columns([1, 2])

# File upload
# In src/streamlit_app.py, replace the entire file‐upload sidebar with:

with col1:
    st.header("📄 Job Description Upload")
    
    uploaded_file = st.file_uploader("Choose a .txt or .md file", type=['txt', 'md'])
    
    if uploaded_file:
        # Use session state to track upload status
        file_key = f"{uploaded_file.name}_{len(uploaded_file.getvalue())}"
        
        if f"uploaded_{file_key}" not in st.session_state:
            # Show selection
            st.success(f"✅ File selected: {uploaded_file.name} ({len(uploaded_file.getvalue())} bytes)")
            
            # Auto-upload ONCE
            try:
                content = uploaded_file.read().decode('utf-8', errors='ignore')
                success, result = upload_file(content, uploaded_file.name)
                
                if success:
                    st.success("🚀 Job description uploaded successfully!")
                    st.text_area("Preview:", result["preview"], height=150, disabled=True)
                    # Mark as uploaded to prevent re-uploading
                    st.session_state[f"uploaded_{file_key}"] = True
                    
                else:
                    st.error(f"❌ Upload failed: {result}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            # Already uploaded - just show status
            st.success(f"✅ File: {uploaded_file.name} - Already uploaded!")
            st.info("💬 You can now ask questions about the job in the chat!")
    else:
        st.info("👆 Select your JD file to upload automatically")


# Chat
with col2:
    st.header("💬 Chat")
    
    # Initialize messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg"><b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg"><b>Bot:</b> {msg["content"]}</div>', unsafe_allow_html=True)
    
    # Input using callback method (NO LOOPS!)
    def handle_input():
        user_input = st.session_state.user_input
        if user_input.strip():
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get bot response
            success, response = send_message(user_input)
            if success:
                st.session_state.messages.append({"role": "bot", "content": response["response"]})
            else:
                st.session_state.messages.append({"role": "bot", "content": response["response"]})
            
            # Clear input
            st.session_state.user_input = ""
    
    # Text input with callback
    st.text_input("Type message:", 
                  key="user_input", 
                  on_change=handle_input,
                  placeholder="Ask about the job or just chat...")
    
    # Clear button
    if st.button("🗑️ Clear"):
        st.session_state.messages = []
        st.rerun()

st.markdown("---")
st.markdown("🤖 **HR Chatbot** | Powered by Google Gemini AI")
