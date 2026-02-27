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

# --- 2. EXACT MOCK DATA FROM INVOICE (OD336636889712015100) ---
ORDER_DATA = {
    "Item": "BIODERMA Node G Purifying shampoo",
    "Status": "Shipped",
    [cite_start]"Order_ID": "OD336636889712015100", # [cite: 5]
    [cite_start]"Invoice_Date": "27-01-2026", # [cite: 7]
    [cite_start]"Seller": "NAOS SKIN CARE INDIA PRIVATE LIMITED", # [cite: 2]
    [cite_start]"GSTIN": "29AAECN7906P1ZP", # [cite: 4]
    [cite_start]"Taxable_Value": "₹1,385.60", # [cite: 22]
    [cite_start]"SGST": "₹124.70", # [cite: 22]
    [cite_start]"CGST": "₹124.70", # [cite: 22]
    [cite_start]"GT_Charges": "₹238.00", # Goods Transport Charges [cite: 81]
    [cite_start]"Platform_Fee": "₹7.00", # [cite: 46]
    "Grand_Total": "₹1,880.00" 
}

# --- 3. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey Rohit 👋, I'm your Flipkart Support Assistant"},
        {"role": "product_card", "content": ""},
        {"role": "assistant", "content": f"I see that your order for {ORDER_DATA['Item']} is {ORDER_DATA['Status'].lower()}. How can I help you?"}
    ]

# --- 4. GEMINI API CONFIGURATION (DYNAMIC RESOLUTION) ---
@st.cache_resource
def get_chatbot_model():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # WHAT WORKED: Use list_models() to bypass 404 errors
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if '1.5-flash' in m), 'gemini-1.5-flash')

        return genai.GenerativeModel(
            model_name=target_model, 
            system_instruction=(
                "You are a cost-conscious Flipkart Support Assistant. User: Rohit. "
                f"Data Context: {ORDER_DATA}. "
                "LOGIC & ESCALATION RULES: "
                "1. If status is 'Shipped', clarify that the PDF invoice is finalized upon delivery."
                "2. COST OPTIMIZATION: Sending a WhatsApp reminder is a high-cost action. DO NOT offer it if the customer is calm or in the first response."
                "3. WHATSAPP TRIGGER: Only offer the WhatsApp reminder if: "
                "   a) Customer explicitly asks for it. "
                "   b) Customer repeats the PDF request after being denied once. "
                "   c) Customer displays high anxiety/frustration (e.g., 'need it now', 'office deadline')."
                "4. MINIMALIST RESOLUTION: Provide text-based tax values (GST, GT Charges) as a zero-cost first resolution for office claims."
                "5. TERMINOLOGY: GT Charges = 'Goods Transport Charges'. [cite_start]Platform Fee = ₹7.00. [cite: 81, 46]"
                "6. Hallucination Guard: NEVER use placeholders. Reject technician claims for shampoo politely."
            )
        )
    except:
        return None

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

# --- 6. CHAT INPUT & HISTORY-AWARE GENERATION ---
if prompt := st.chat_input("Write a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    if model:
        try:
            # Passing history ensures the AI detects 'anxiety' or 'repetition' over time
            chat = model.start_chat(history=[
                {"role": m["role"] if m["role"] != "assistant" else "model", "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1] if m["role"] != "product_card"
            ])
            with st.spinner("Thinking..."):
                response = chat.send_message(prompt)
                ai_response = response.text
        except Exception as e:
            ai_response = f"⚠️ **Technical Error:** {str(e)}"
    else:
        ai_response = "Bot configuration failed."

    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    st.rerun()