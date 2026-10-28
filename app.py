import streamlit as st
from datetime import datetime, timedelta
from groq import Groq

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="72-Hour Breakup Rescue Protocol",
    page_icon="🛡️",
    layout="wide"
)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are the 72-Hour Breakup Rescue Operator (Triage-72). 
Your mission: Prevent self-sabotage, regulate the user's nervous system, and enforce strict no-contact.
Persona: Calm, firm, direct, compassionate, grounding (like an emergency responder).
Rules:
1. Never encourage contacting the ex. Enforce strict no-contact.
2. Keep responses brief (under 3 short paragraphs). Users in shock have low attention spans.
3. Explain pain chemically (dopamine/oxytocin drop), not as personal failure.
"""

# --- SESSION STATE INITIALIZATION ---
if "breakup_time" not in st.session_state:
    st.session_state.breakup_time = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vault" not in st.session_state:
    st.session_state.vault = []

# --- SIDEBAR: SETUP & API ---
with st.sidebar:
    st.title("🛡️ Rescue Command")
    api_key = st.text_input("Groq API Key (Free)", type="password", help="Key starting with gsk_ from console.groq.com")
    
    selected_model = "llama3-8b-8192"
    if api_key:
        try:
            client_temp = Groq(api_key=api_key)
            models_list = [m.id for m in client_temp.models.list().data if "whisper" not in m.id and "guard" not in m.id]
            selected_model = st.selectbox("Active AI Model", models_list, index=0)
        except Exception:
            selected_model = "llama3-8b-8192"

    st.markdown("---")
    st.subheader("Triage Clock")
    
    hours_ago = st.number_input("How many hours ago did it happen?", min_value=0.0, max_value=72.0, value=2.0, step=0.5)
    
    if st.button("Set Breakup Clock"):
        st.session_state.breakup_time = datetime.now() - timedelta(hours=hours_ago)
        st.success(f"Clock calibrated to Hour {hours_ago:.1f}")

# Calculate current elapsed time
if st.session_state.breakup_time:
    elapsed_seconds = (datetime.now() - st.session_state.breakup_time).total_seconds()
    elapsed_hours = elapsed_seconds / 3600
else:
    elapsed_hours = hours_ago

# Determine Phase
if elapsed_hours < 12:
    current_phase = "Phase 1: Acute Shock & Damage Control"
    phase_color = "#FF4B4B"
elif elapsed_hours < 36:
    current_phase = "Phase 2: Chemical Withdrawal & Friction Shield"
    phase_color = "#FFA500"
else:
    current_phase = "Phase 3: Stabilization & Re-Anchoring"
    phase_color = "#00CC96"

# --- HEADER & STATUS BAR ---
st.markdown(f"### Current Phase: <span style='color:{phase_color}'>{current_phase}</span> (Hour {elapsed_hours:.1f} / 72)", unsafe_allow_html=True)
progress_ratio = min(max(elapsed_hours / 72.0, 0.0), 1.0)
st.progress(progress_ratio)

# --- EMERGENCY PANIC BUTTONS ---
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🚨 PANIC: I'm About to Text Them", use_container_width=True):
        st.error("🛑 STOP. STEP AWAY FROM YOUR PHONE.")
        st.markdown("""
        **10-Minute Friction Lock Activated.**
        1. Place your phone face-down on the table right now.
        2. Inhale 4s... Hold 4s... Exhale 4s... Hold 4s.
        3. If you text them now, you reset chemical withdrawal back to Hour 0.
        """)

with col2:
    if st.button("🧊 Somatic Reset: Panic Attack / Can't Breathe", use_container_width=True):
        st.info("Triggering Mammalian Dive Reflex:")
        st.markdown("""
        1. Go to the sink right now.
        2. Fill a bowl with ice-cold water (or run very cold tap water).
        3. Splash your face or submerge it for 15 seconds.
        *This physically forces your heart rate down within 30 seconds.*
        """)

st.markdown("---")

# --- TABS ---
tab1, tab2 = st.tabs(["💬 Triage Chat", "🔒 The Burner Vault (Intercept Texts)"])

with tab1:
    st.caption("Talk to Triage-72. Keep it raw, keep it honest.")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if user_input := st.chat_input("What is happening right now?"):
        if not api_key:
            st.warning("Please enter your Groq API key in the sidebar.")
        else:
            client = Groq(api_key=api_key)
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
                
            context_prompt = f"{SYSTEM_PROMPT}\nUSER CONTEXT: The user is currently at Hour {elapsed_hours:.1f} of 72. Phase: {current_phase}."
            
            response = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": context_prompt},
                    *st.session_state.messages
                ]
            )
            bot_reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            with st.chat_message("assistant"):
                st.markdown(bot_reply)

with tab2:
    st.subheader("The Interceptor")
    st.markdown("Type what you want to send your ex. **It will be locked here and analyzed instead.**")
    unsent_text = st.text_area("Write the draft here:", height=120)
    
    if st.button("Lock in Vault & Deconstruct"):
        if unsent_text and api_key:
            client = Groq(api_key=api_key)
            deconstruct_prompt = f"""
            The user wants to send this message to their ex:
            "{unsent_text}"

            Deconstruct this in 3 brief bullets:
            1. What emotional validation is the user REALLY craving by sending this?
            2. How will the ex likely react in reality (coldness, silence, irritation)?
            3. Why keeping this unsent protects their dignity.
            """
            analysis = client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "user", "content": deconstruct_prompt}]
            ).choices[0].message.content
            
            st.session_state.vault.append({"text": unsent_text, "analysis": analysis, "time": datetime.now()})
            st.success("Draft intercepted and locked.")
            st.markdown("### Analysis:")
            st.markdown(analysis)
        elif not api_key:
            st.warning("Enter your Groq API key in the sidebar.")