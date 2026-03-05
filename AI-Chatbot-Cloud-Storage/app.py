
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
from supabase import create_client
from datetime import datetime

# Gemini API Configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

# Supabase Configuration
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
bucket_name = os.getenv("SUPABASE_BUCKET")

supabase = create_client(supabase_url, supabase_key)

# Function to get response
def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

# Save chat history
def save_chat_to_supabase(history):
    content = "\n".join([f"{role}: {text}" for role, text in history])

    filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(filename, "w") as f:
        f.write(content)

    with open(filename, "rb") as f:
        supabase.storage.from_(bucket_name).upload(filename, f)

    os.remove(filename)

# Streamlit UI
st.set_page_config(page_title="AI Chatbot")
st.header("AI Chatbot with Cloud Storage")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

user_input = st.text_input("Ask something")

if st.button("Send") and user_input:

    response = get_gemini_response(user_input)

    st.session_state['chat_history'].append(("User", user_input))

    full_response = ""

    for chunk in response:
        st.write(chunk.text)
        full_response += chunk.text

    st.session_state['chat_history'].append(("Bot", full_response))

    save_chat_to_supabase(st.session_state['chat_history'])

st.subheader("Chat History")

for role, text in st.session_state['chat_history']:
    st.write(f"{role}: {text}")