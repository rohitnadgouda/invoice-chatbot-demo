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
    .stChatMessage { background-color: transparent !important; border: none !important; }
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

# --- 3. INITIALIZE SESSION STATE (FIXES ATTRIBUTEERROR) ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey Rohit 👋, I'm your Flipkart Support Assistant"},
        {"role": "product_card", "content": ""},
        {"role": "assistant", "content": f"I see that your product is {ORDER_DATA['Status'].lower()} to you. How may I help you?"}
    ]

# --- 4. GEMINI API CONFIGURATION ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # System Instruction grounds the model to your PRD logic
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=(
            f"You are a Flipkart Support Assistant. The user's order for {ORDER_DATA['Item']} is 'Shipped'. "
            f"Business Policy: 1. Do NOT give the invoice PDF while Shipped. "
            f"2. If user mentions 'Office/Claim/Reimbursement', explain that the invoice is ready upon delivery, "
            f"but provide these details textually: Total: {ORDER_DATA['Total']}, Taxable: {ORDER_DATA['Taxable']}, GST: {ORDER_DATA['GST']}. "
            f"3. If user claims a 'Technician' or 'Installation' is there, politely decline because shampoo does not require it. "
            f"4. Maintain empathy but adhere strictly to the policy."
        )
    )
except Exception as e:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")

# --- 5. UI DISPLAY ---
st.markdown('<div class="main-header">✕ &nbsp; Flipkart Support</div>', unsafe_allow_html=True)
st.write("##") # Spacer

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.markdown(f'<div class="bot-bubble">{message["content"]}</div>', unsafe_allow_html=True)
    elif message["role"] == "user":
        st.markdown(f'<div class="user-bubble">{message["content"]}</div>', unsafe_allow_html=True)