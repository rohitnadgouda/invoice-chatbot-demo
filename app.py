# -*- coding: utf-8 -*-
import streamlit as st


import streamlit as st


# --- PAGE CONFIG ---
st.set_page_config(page_title="Flipkart Support Assistant", page_icon="🔵")


# --- CUSTOM FLIPKART UI STYLING (CSS) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #F1F3F6; }
    
    /* Header Styling */
    .main-header {
        background-color: white;
        padding: 10px;
        display: flex;
        align-items: center;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        font-size: 18px;
        border-bottom: 1px solid #E0E0E0;
        position: fixed;
        top: 0;
        width: 100%;
        z-index: 999;
    }


    /* Chat Bubbles */
    .stChatMessage { background-color: transparent !important; border: none !important; }
    
    .bot-bubble {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 12px;
        color: #212121;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        max-width: 85%;
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        line-height: 1.4;
    }


    /* Product Card */
    .product-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 10px;
        display: flex;
        align-items: center;
        margin: 10px 0;
        max-width: 85%;
    }


    /* Quick Action Buttons */
    .stButton>button {
        background-color: white !important;
        border: 1px solid #E0E0E0 !important;
        color: #2874F0 !important;
        border-radius: 8px !important;
        text-align: left !important;
        font-weight: 500 !important;
        padding: 10px !important;
        transition: 0.3s;
        display: flex;
        justify-content: space-between;
    }
    
    .stButton>button:hover {
        border-color: #2874F0 !important;
        background-color: #F0F5FF !important;
    }
    </style>
    """, unsafe_allow_html=True)


# --- MOCK DATA (PRD CASE) ---
ORDER_DATA = {
    "User": "Rohit",
    "Item": "BIODERMA Node G Purifying shampoo",
    "Status": "Shipped",
    "Is_Installable": False, # Logic: Shampoo does not need a tech
    "Total": "₹1,642.00",
    "Taxable": "₹1,385.60",
    "GST": "₹249.40"
}


# --- APP UI ---
st.markdown('<div class="main-header">✕ &nbsp; Flipkart Support</div>', unsafe_allow_html=True)
st.write("##") # Spacer for fixed header


# 1. Bot Greeting
st.markdown(f'<div class="bot-bubble">Hey {ORDER_DATA["User"]} 👋, I\'m your Flipkart Support Assistant</div>', unsafe_allow_html=True)


# 2. Product Card
st.markdown(f'''
    <div class="product-card">
        <img src="https://rukminim2.flixcart.com/image/128/128/xif0q/shampoo/g/p/p/-original-imagp6y68hgfhzgt.jpeg" width="50" style="margin-right:15px; border-radius:4px;">
        <div style="font-size:14px; color:#212121;">{ORDER_DATA["Item"]}</div>
    </div>
''', unsafe_allow_html=True)


# 3. Contextual Message
st.markdown(f'<div class="bot-bubble">I see that your product is {ORDER_DATA["Status"].lower()} to you.</div>', unsafe_allow_html=True)
st.markdown('<div class="bot-bubble">How may I help you?</div>', unsafe_allow_html=True)


# --- INTERACTIVE CHAT LOGIC ---
if "flow_step" not in st.session_state:
    st.session_state.flow_step = "initial"


# Quick Actions
if st.session_state.flow_step == "initial":
    if st.button("Get my bill or invoice"):
        st.session_state.flow_step = "ask_reason"
        st.rerun()
    st.button("I need to return the item")
    st.button("Know more about SuperCoins")


# Scrutiny Logic Flow
if st.session_state.flow_step == "ask_reason":
    st.markdown('<div class="bot-bubble">Since your order is <b>Shipped</b>, the invoice is finalized upon delivery. For your records, the total is <b>' + ORDER_DATA["Total"] + '</b>. <br><br>Could you share why you need it before the delivery is completed?</div>', unsafe_allow_html=True)
    
    user_input = st.chat_input("Explain your requirement...")
    
    if user_input:
        # DATA SCIENCE LOGIC SIMULATION
        input_lower = user_input.lower()
        
        # Exception Bucket: Installation
        if any(word in input_lower for word in ["tech", "install", "engineer", "service"]):
            if ORDER_DATA["Is_Installable"]:
                st.success("Exception Approved. Download Invoice: [Invoice_PDF_Link]")
            else:
                st.error(f"I notice this order is for {ORDER_DATA['Item']}, which doesn't typically require a technician. The invoice will be available once delivered.")
        
        # Admin Bucket: Office Claims
        elif any(word in input_lower for word in ["office", "claim", "reimbursement", "company"]):
            st.info(f"I understand this is for an office claim. To ensure tax compliance, the final PDF is released upon delivery. <br><br><b>Draft Details:</b><br>Taxable Value: {ORDER_DATA['Taxable']}<br>GST: {ORDER_DATA['GST']}", icon="ℹ️")
        
        else:
            st.warning("The invoice will be ready in your 'My Orders' section the moment the package reaches you.")


# Reset Button for Walkthrough
if st.sidebar.button("Reset Demo"):
    st.session_state.flow_step = "initial"
    st.rerun()