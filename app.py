# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai

# --- GEMINI SETUP ---
# Securely fetch your API key from Streamlit Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize the model with System Instructions
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        f"You are a Flipkart Support Assistant. "
        f"Context: Order is for {st.session_state.get('order_item', 'BIODERMA Shampoo')}, "
        f"Status is 'Shipped', Installable: False. "
        "POLICY: 1. Do NOT provide the invoice PDF while status is Shipped. "
        "2. If the user asks for 'Office/Claim', provide tax details (Total: 1,642, Tax: 249.40) textually. "
        "3. If they claim a 'Technician' is there, refuse politely because shampoo doesn't need installation. "
        "4. Be empathetic but firm on policy. Use professional, modern language."
    )
)

# --- CHAT LOGIC ---
if prompt := st.chat_input("Write a message..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate Gemini Response
    try:
        # We pass the history to Gemini for a true conversational experience
        chat = model.start_chat(history=[]) 
        with st.spinner("Gemini is thinking..."):
            response = chat.send_message(prompt)
            ai_response = response.text
    except Exception as e:
        ai_response = "I'm having a bit of trouble connecting to my billing server. Please try again!"

    # Add AI response to state
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    st.rerun()