# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai

# --- 1. PAGE CONFIG & UI STYLING ---
st.set_page_config(page_title="Flipkart Support Assistant", page_icon="🔵")

st.markdown("""
    <style>
    .stApp { background-color: #F1F3F6; }
    .main-header {
        background-color: white; padding: 10px; display: flex; align-items: center;
        font-family: 'Roboto', sans-serif; font-weight: 500; font-size: 18px;
        border-bottom: 1px solid #E0E0E0; position: fixed; top: 0; width: 100%; z-index: 999;
    }
    .bot-bubble {
        background-color: #FFFFFF; border-radius: 12px; padding: 12px; color: #212121;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1); margin-bottom: 10px; max-width: 85%;
        font-family: 'Roboto', sans-serif; font-size: 14px; line-height: 1.4;
    }
    .user-bubble {
        background-color: #E3F2FD; border-radius: 12px; padding: 12px; color: #212121;
        margin-left: auto; margin-bottom: 10px; max-width: 85%;
        font-family: 'Roboto', sans-serif; font-size: 14px; text-align: right;
    }
    .product-card {
        background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
        padding: 10px; display: flex; align-items: center; margin: 10px 0; max-width: 85%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOCK DATA ---
ORDER_DATA = {
    "Item": "BIODERMA Node G Purifying shampoo",
    "Status": "Shipped",
    "Is_Installable": False,
    "Total": "1,642.00",
    "Taxable": "1,385.60",
    "GST": "249.40"
}

# --- 3. SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey Rohit 👋, I'm your Flipkart Support Assistant"},
        {"role": "product_card", "content": ""},
        {"role": "assistant", "content": f"I see that your product is {ORDER_DATA['Status'].lower()} to you. How may I help you?"}
    ]

# --- 4. GEMINI API CONFIGURATION (AUTO-RESOLVE 404) ---
@st.cache_resource
def get_chatbot_model():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Auto-detect the correct model name to avoid 404 errors
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Priority: 1.5-flash (fastest) -> 1.5-pro -> gemini-pro (legacy)
    target_model = 'models/gemini-1.5-flash' # Default
    for m_name in available_models:
        if 'gemini-1.5-flash' in m_name:
            target_model = m_name
            break
        elif 'gemini-pro' in m_name:
            target_model = m_name

    return genai.GenerativeModel(
        model_name=target_model, 
        system_instruction=(
            f"You are a Flipkart Support Assistant. Order: {ORDER_DATA['Item']}. "
            "Policy: No PDF if Shipped. Provide tax details textually for claims. "
            "Reject technician claims for non-installable goods politely."
        )
    )

# Create the 'model' variable
try:
    model = get_chatbot_model()
except Exception as e:
    st.error(f"Configuration Error: {str(e)}")
    model = None

# --- 5. UI DISPLAY ---
st.markdown('<div class="main-header">✕ &nbsp; Flipkart Support</div>', unsafe_allow_html=True)
st.write("##") 

for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.markdown(f'<div class="bot-bubble">{message["content"]}</div>', unsafe_allow_html=True)
    elif message["role"] == "user":
        st.markdown(f'<div class="user-bubble">{message["content"]}</div>', unsafe_allow_html=True)
    elif message["role"] == "product_card":
        st.markdown(f'''<div class="product-card"><img src="https://rukminim2.flixcart.com/image/128/128/xif0q/shampoo/g/p/p/-original-imagp6y68hgfhzgt.jpeg" width="50" style="margin-right:15px; border-radius:4px;"><div style="font-size:14px; color:#212121;">{ORDER_DATA["Item"]}</div></div>''', unsafe_allow_html=True)

# --- 6. CHAT INPUT & GENERATIVE LOGIC ---
if prompt := st.chat_input("Write a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    if model:
        try:
            chat = model.start_chat(history=[])
            with st.spinner("Thinking..."):
                response = chat.send_message(prompt)
                ai_response = response.text
        except Exception as e:
            ai_response = f"⚠️ **Actual Technical Error:** {str(e)}"
    else:
        ai_response = "Bot is not configured properly. Please check your API key."

    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    st.rerun()