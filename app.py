# -*- coding: utf-8 -*-
import streamlit as st


# --- PAGE CONFIG ---
st.set_page_config(page_title="Flipkart Support Assistant", page_icon="🔵")


# --- CUSTOM FLIPKART UI STYLING (CSS) ---
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
        font-family: 'Roboto', sans-serif; font-size: 14px;
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


# --- MOCK DATA ---
ORDER_DATA = {
    "Item": "BIODERMA Node G Purifying shampoo",
    "Status": "Shipped",
    "Is_Installable": False,
    "Total": "1,642.00",
    "Taxable": "1,385.60",
    "GST": "249.40"
}


st.markdown('<div class="main-header">✕ &nbsp; Flipkart Support</div>', unsafe_allow_html=True)
st.write("##") 


# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey Rohit 👋, I'm your Flipkart Support Assistant"},
        {"role": "product_card", "content": ""},
        {"role": "assistant", "content": f"I see that your product is {ORDER_DATA['Status'].lower()} to you. How may I help you?"}
    ]


# --- DISPLAY CONVERSATION HISTORY ---
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.markdown(f'<div class="bot-bubble">{message["content"]}</div>', unsafe_allow_html=True)
    elif message["role"] == "user":
        st.markdown(f'<div class="user-bubble">{message["content"]}</div>', unsafe_allow_html=True)
    elif message["role"] == "product_card":
        st.markdown(f'''
            <div class="product-card">
                <img src="https://rukminim2.flixcart.com/image/128/128/xif0q/shampoo/g/p/p/-original-imagp6y68hgfhzgt.jpeg" width="50" style="margin-right:15px; border-radius:4px;">
                <div style="font-size:14px; color:#212121;">{ORDER_DATA["Item"]}</div>
            </div>
        ''', unsafe_allow_html=True)


# --- CHAT INPUT (Enabled from beginning) ---
if prompt := st.chat_input("Write a message..."):
    # Append user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # LOGIC ENGINE
    query = prompt.lower()
    response = ""
    
    if "invoice" in query or "bill" in query:
        response = f"Since your order is <b>Shipped</b>, the invoice is finalized upon delivery. For your records, the total is <b>₹{ORDER_DATA['Total']}</b>. <br><br>Could you share why you need it before the delivery is completed?"
    
    elif any(word in query for word in ["tech", "install", "engineer", "service"]):
        if ORDER_DATA["Is_Installable"]:
            response = "I see a technician is on-site. **Exception Approved.** [Download Invoice]"
        else:
            response = f"I notice this order is for {ORDER_DATA['Item']}, which doesn't typically require a technician. The invoice will be available once delivered."
            
    elif any(word in query for word in ["office", "claim", "reimbursement"]):
        response = f"I understand this is for an office claim. To ensure tax compliance, the final PDF is released upon delivery. <br><br><b>Draft Details:</b><br>Taxable Value: ₹{ORDER_DATA['Taxable']}<br>GST: ₹{ORDER_DATA['GST']}"
    
    else:
        response = "I'm here to help with your invoice or delivery. Could you please specify your requirement?"


    # Append assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()