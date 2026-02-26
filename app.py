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

# --- 2. COMPREHENSIVE MOCK DATA (EXACT INVOICE TERMS) ---
ORDER_DATA = {
    "Item": "BIODERMA Node G Purifying shampoo",
    "Status": "Shipped",
    "Order_ID": "OD336636889712015100",  # [cite: 5, 40, 61]
    "Invoice_Date": "27-01-2026",  # [cite: 7, 42, 60]
    "Seller": "NAOS SKIN CARE INDIA PRIVATE LIMITED",  # [cite: 2, 32]
    "GSTIN": "29AAECN7906P1ZP",  # [cite: 4]
    "Taxable_Value": "₹1,385.60", # [cite: 22]
    "SGST": "₹124.70", # [cite: 22]
    "CGST": "₹124.70", # [cite: 22]
    "GT_Charges": "₹238.00",  # Goods Transport Charges 
    "Platform_Fee": "₹7.00",   # 
    "Grand_Total": "₹1,880.00" 
}

# --- 3. SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey Rohit 👋, I'm your Flipkart Support Assistant"},
        {"role": "product_card", "content": ""},
        {"role": "assistant", "content": f"I see that your product is {ORDER_DATA['Status'].lower()} to you. How may I help you?"}
    ]

# --- 4. GEMINI API CONFIGURATION (AUTO-RESOLVE 404 & MINIMALIST LOGIC) ---
@st.cache_resource
def get_chatbot_model():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Auto-detect correct model name
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
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
                "You are a Flipkart Support Assistant. User: Rohit. "
                f"Context: {ORDER_DATA}. "
                "STRICT RULES: "
                "1. If status is 'Shipped', do not provide a PDF link. "
                "2. NEVER use placeholders like [Current Date] or [Order ID]. Use ONLY provided data. "
                "3. MINIMALIST FIRST: If asked for an invoice/bill, explain the 'Shipped' policy first. "
                "Ask if they specifically need tax details for a claim. Do NOT provide the table yet. "
                "4. Provide specific values ONLY when they confirm they need it for a claim/reimbursement. "
                "5. GT Charges means 'Goods Transport Charges'. "
                "6. Reject technician installation requests for shampoo politely."
            )
        )
    except Exception as e:
        return None

# Call the function to create 'model'
model = get_chatbot_model()

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