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
        font-size: 14px; line-height: 1.4; margin-bottom: 15px;
    }
    .user-bubble {
        background-color: #E3F2FD; border-radius: 12px; padding: 12px; color: #212121;
        margin-left: auto; margin-bottom: 15px; max-width: 85%;
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

# --- 4. GEMINI API CONFIGURATION (STRICT DISCOVERY) ---
@st.cache_resource
def get_chatbot_model():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # LEARNING: Explicitly list and find the exact name authorized for this key
        available_models = list(genai.list_models())
        
        target_model_name = None
        for m in available_models:
            if "generateContent" in m.supported_generation_methods:
                if "flash" in m.name.lower():
                    target_model_name = m.name
                    break
        
        if not target_model_name:
            target_model_name = next(m.name for m in available_models if "generateContent" in m.supported_generation_methods)

        return genai.GenerativeModel(
            model_name=target_model_name, 
            system_instruction=(
                f"""You are an intelligent, cost-optimized Flipkart Support Assistant. User: Rohit. 
                Context Data: {ORDER_DATA}. 
                "TERMINOLOGY RULE: "
                "- 'GT Charges' stands for 'Goods Transport Charges'. If asked for the full form or meaning, explicitly state 'Goods Transport Charges'."
                
                STRATEGIC ESCALATION & LANGUAGE RULES:
                1. If status is 'Shipped', explain that the invoice is not ready yet. 
                Use variations like: 'The system is not designed to generate the invoice at this stage' 
                or 'The official invoice will be available once the order reaches you.'
                2. NO EARLY NUDGE: Do NOT offer the WhatsApp reminder in the 1st or 2nd response. 
                3. PROBE FOR URGENCY: On the 3rd iteration, or if the customer shows desperation, 
                ask an open-ended question to understand their urgency. 
                4. WHATSAPP TRIGGER: Only use the WhatsApp nudge if the user's response to your probe 
                indicates persistent, non-negotiable need. 
                5. ZERO-COST RESOLUTION: Always prefer providing text-based tax values (GST, GT Charges) for claims first. 
                6. NEVER use placeholders. Reject technician claims for shampoo politely.
                7. CALL ME BACK REQUESTS: Politely decline to handover the chat to customer support agents.
                8. NEVER suggest whatsapp reminder for call me back requests."""
            )
        )
    except Exception as e:
        st.error(f"Failed to initialize model: {e}")
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
        st.markdown(f'''<div class="product-card"><img src="https://bioderma.naosindia.in/cdn/shop/files/1_3690e0e6-b59e-48ea-932f-5f4689734042.jpg" width="50" style="margin-right:15px; border-radius:4px;"><div style="font-size:14px; color:#212121;">{ORDER_DATA["Item"]}</div></div>''', unsafe_allow_html=True)

# --- 6. CHAT INPUT & INSTANT UI LOGIC ---
if prompt := st.chat_input("Write a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if st.session_state.messages[-1]["role"] == "user":
    if model:
        try:
            chat_history = []
            for m in st.session_state.messages[:-1]:
                if m["role"] == "assistant":
                    chat_history.append({"role": "model", "parts": [m["content"]]})
                elif m["role"] == "user":
                    chat_history.append({"role": "user", "parts": [m["content"]]})
            
            chat = model.start_chat(history=chat_history)
            
            with st.spinner("Typing..."):
                response = chat.send_message(st.session_state.messages[-1]["content"])
                ai_response = response.text
                
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun()
        except Exception as e:
            st.error(f"⚠️ Technical Error: {str(e)}")
    else:
        st.warning("Model not available. Please check configuration.")
