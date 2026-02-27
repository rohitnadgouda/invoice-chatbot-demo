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
        font-size: 14px; line-height: 1.4;
    }
    .user-bubble {
        background-color: #E3F2FD; border-radius: 12px; padding: 12px; color: #212121;
        margin-left: auto; margin-bottom: 10px; max-width: 85%;
        font-size: 14px; text-align: right;
    }
    .product-card {
        background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
        padding: 10px; display: flex; align-items: center; margin: 10px 0; max-width: 85%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. EXACT MOCK DATA FROM INVOICE ---
ORDER_DATA = {
    "Item": "BIODERMA Node G Purifying shampoo",
    "Status": "Shipped",
    "Order_ID": "OD336636889712015100", 
    "Invoice_Date": "27-01-2026", 
    "Seller": "NAOS SKIN CARE INDIA PRIVATE LIMITED", 
    "GSTIN": "29AAECN7906P1ZP", 
    "Taxable_Value": "₹1,385.60", 
    "SGST": "₹124.70", 
    "CGST": "₹124.70", 
    "GT_Charges": "₹238.00", 
    "Platform_Fee": "₹7.00", 
    "Grand_Total": "₹1,880.00" 
}

# --- 3. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey Rohit 👋, I'm your Flipkart Support Assistant"},
        {"role": "product_card", "content": ""},
        {"role": "assistant", "content": f"I see that your order for {ORDER_DATA['Item']} is {ORDER_DATA['Status'].lower()}. How can I help you?"}
    ]

# --- 4. GEMINI API CONFIGURATION (STABLE DYNAMIC RESOLUTION) ---
@st.cache_resource
def get_chatbot_model():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # WHAT WORKED: List models to identify valid authorized string
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority fallback logic to ensure a valid model is assigned
        target_model = next((m for m in available_models if '1.5-flash' in m), 'gemini-1.5-flash')

        return genai.GenerativeModel(
            model_name=target_model, 
            system_instruction=(
                "You are an intelligent, cost-optimized Flipkart Support Assistant. User: Rohit. "
                f"Context Data: {ORDER_DATA}. "
                "STRATEGIC ESCALATION RULES: "
                "1. If status is 'Shipped', clarify that the PDF invoice is finalized only upon delivery."
                "2. NO EARLY NUDGE: Do NOT offer the WhatsApp reminder in the 1st or 2nd response to optimize costs."
                "3. PROBE FOR URGENCY: From the 3rd iteration onwards, or if the customer shows desperation, "
                "ask an open-ended question to understand their urgency (e.g., 'Could you help me understand if this is for an immediate office claim or a tax filing today?')."
                "4. WHATSAPP TRIGGER: Only use the WhatsApp nudge if the user's response to your probe indicates high persistence or a non-negotiable need."
                "5. ZERO-COST RESOLUTION: Always prefer providing text-based tax values (GST, GT Charges) for claims first."
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
            # Pass history to ensure iteration counting and urgency detection
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
