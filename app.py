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

# --- GET API KEY (Secrets first, then fallback to sidebar) ---
api_key = None
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

# --- SESSION STATE INITIALIZATION ---
if "breakup_time" not in st.session_state:
    st.session_state.breakup_time = datetime.now() - timedelta(hours=2.0)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vault" not in st.session_state:
    st.session_state.vault = []
if "missions_done" not in st.session_state:
    st.session_state.missions_done = {}

# --- SIDEBAR: CONTROLS & API ---
with st.sidebar:
    st.title("🛡️ Rescue Command")
    
    if not api_key:
        api_key = st.text_input("Groq API Key (Free)", type="password", help="Key starting with gsk_ from console.groq.com")
    else:
        st.success("🟢 Rescue Engine: Connected")

    selected_model = "llama-3.3-70b-versatile"
    if api_key:
        try:
            client_temp = Groq(api_key=api_key)
            models_list = [m.id for m in client_temp.models.list().data if "whisper" not in m.id and "guard" not in m.id]
            selected_model = st.selectbox("Active AI Model", models_list, index=0)
        except Exception:
            selected_model = "llama-3.3-70b-versatile"

    st.markdown("---")
    st.subheader("⏱️ Triage Clock")
    
    hours_ago = st.slider("Hours elapsed since breakup:", min_value=0.0, max_value=72.0, value=2.0, step=0.5)
    
    if st.button("Calibrate Clock"):
        st.session_state.breakup_time = datetime.now() - timedelta(hours=hours_ago)
        st.rerun()

# Calculate current elapsed time
if st.session_state.breakup_time:
    elapsed_seconds = (datetime.now() - st.session_state.breakup_time).total_seconds()
    elapsed_hours = max(elapsed_seconds / 3600, hours_ago)
else:
    elapsed_hours = hours_ago

# --- PHASE DETERMINATION ---
if elapsed_hours < 8:
    current_phase = "Phase 1: Acute Shock & Damage Control"
    phase_badge = "🔴 ACUTE ER"
    phase_color = "#FF4B4B"
elif elapsed_hours < 24:
    current_phase = "Phase 2: Chemical Withdrawal & Dopamine Triage"
    phase_badge = "🟠 WITHDRAWAL WARD"
    phase_color = "#FFA500"
else:
    current_phase = "Phase 3: Reality Anchoring & Closure Ritual"
    phase_badge = "🟢 RECOVERY & REBUILD"
    phase_color = "#00CC96"

# --- TOP HEADER & TIMELINE ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown(f"## {phase_badge} — Hour {elapsed_hours:.1f} / 72.0")
    st.markdown(f"**State:** <span style='color:{phase_color}; font-size:1.1rem;'>{current_phase}</span>", unsafe_allow_html=True)
with col_head2:
    st.metric(label="No-Contact Streak", value=f"{int(elapsed_hours)} Hours", delta=f"{int(72 - elapsed_hours)} hrs left in triage")

progress_ratio = min(max(elapsed_hours / 72.0, 0.0), 1.0)
st.progress(progress_ratio)

# --- EMERGENCY PANIC BUTTONS (Always accessible) ---
p1, p2 = st.columns(2)
with p1:
    if st.button("🚨 PANIC: I'm About to Text Them", use_container_width=True):
        st.error("🛑 STOP. STEP AWAY FROM YOUR PHONE RIGHT NOW.")
        st.markdown("""
        **10-Minute Friction Lock Activated:**
        1. Place your phone face-down in another room.
        2. Drink 1 full glass of water slowly.
        3. Texting them now will instantly reset your chemical withdrawal back to Hour 0.
        """)

with p2:
    if st.button("🧊 Somatic Reset: Panic / Hyperventilating", use_container_width=True):
        st.info("Triggering Mammalian Dive Reflex:")
        st.markdown("""
        1. Go to the sink right now.
        2. Splash ice-cold water on your face for 15 seconds.
        3. Exhale twice as long as you inhale (4s in, 8s out).
        """)

st.markdown("---")

# ==============================================================================
# DYNAMIC MODULES BASED ON THE TRIAGE CLOCK
# ==============================================================================

# Create tabs for active modules
tab_names = ["💬 Triage Chat", "🔒 The Burner Vault"]

if elapsed_hours >= 8:
    tab_names.append("⚡ Phase 2: Dopamine Missions")
else:
    tab_names.append("🔒 Phase 2 (Unlocks at Hr 8)")

if elapsed_hours >= 24:
    tab_names.append("🌅 Phase 3: Closure Ritual")
else:
    tab_names.append("🔒 Phase 3 (Unlocks at Hr 24)")

tabs = st.tabs(tab_names)

# ----------------- TAB 1: TRIAGE CHAT -----------------
with tabs[0]:
    st.caption("24/7 AI Paramedic. Raw, honest, zero-sugarcoating.")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if user_input := st.chat_input("What is happening right now?"):
        if not api_key:
            st.warning("Please configure your Groq API key in sidebar or secrets.")
        else:
            client = Groq(api_key=api_key)
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
                
            context_prompt = f"{SYSTEM_PROMPT}\nUSER CONTEXT: The user is at Hour {elapsed_hours:.1f}/72. Phase: {current_phase}."
            response = client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "system", "content": context_prompt}, *st.session_state.messages]
            )
            bot_reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            with st.chat_message("assistant"):
                st.markdown(bot_reply)

# ----------------- TAB 2: BURNER VAULT -----------------
with tabs[1]:
    st.subheader("The Interceptor (Burner Vault)")
    st.markdown("Type the exact text you want to send your ex. **Do not send it to them. Send it to the vault.**")
    unsent_text = st.text_area("Draft your message:", height=100)
    
    if st.button("Intercept & Deconstruct"):
        if unsent_text and api_key:
            client = Groq(api_key=api_key)
            deconstruct_prompt = f"""
            The user wants to text their ex: "{unsent_text}"
            Deconstruct this in 3 brief bullets:
            1. What emotional validation are they REALLY craving?
            2. The harsh reality of how their ex will respond (coldness/silence).
            3. Why keeping this unsent protects their self-respect.
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
            st.warning("Configure Groq API key first.")

# ----------------- TAB 3: PHASE 2 (HOUR 8-24) -----------------
with tabs[2]:
    if elapsed_hours < 8:
        st.warning(f"🔒 Phase 2 unlocks in {8.0 - elapsed_hours:.1f} hours.")
        st.info("Focus right now on pure survival: Do not text, do not stalk, keep breathing.")
    else:
        st.subheader("⚡ Phase 2: Neurochemical Withdrawal Triage")
        st.markdown("""
        Your brain is currently in dopamine withdrawal. The urge to text is an instinct to get a 'hit' of reassurance. 
        **Replace it with micro-dopamine wins below:**
        """)
        
        missions = [
            ("water", "Drink 500ml of cold water (Nervous system lubrication)"),
            ("food", "Consume 1 solid food item or warm soup (Blood sugar stabilizer)"),
            ("shower", "Take a 5-minute shower and change into clean clothes"),
            ("sunlight", "Step outside or open a window for 10 minutes of natural light"),
            ("archive", "Archive or mute your ex's chat and stories on all apps")
        ]
        
        completed_count = 0
        for key, text in missions:
            checked = st.checkbox(text, key=f"mission_{key}")
            if checked:
                completed_count += 1
                
        st.progress(completed_count / len(missions))
        st.caption(f"Completed {completed_count} of {len(missions)} dopamine recovery tasks.")

# ----------------- TAB 4: PHASE 3 (HOUR 24-72) -----------------
with tabs[3]:
    if elapsed_hours < 24:
        st.warning(f"🔒 Phase 3 unlocks in {24.0 - elapsed_hours:.1f} hours.")
        st.info("Your brain is still too emotionally reactive for closure exercises. Get through Phase 2 first.")
    else:
        st.subheader("🌅 Phase 3: The Closure Ritual & Reality Re-Anchor")
        st.markdown("Stop replaying the highlight reel. Your brain is lying to you by only remembering the good parts.")
        
        with st.expander("📝 The Anti-Fantasy Audit (3 Hard Truths)", expanded=True):
            f1 = st.text_input("1. A moment they made you feel unseen, unsafe, or exhausted:")
            f2 = st.text_input("2. An incompatibility that love alone could never fix:")
            f3 = st.text_input("3. What part of yourself were you shrinking to stay with them?")
            
            if st.button("Generate Re-Anchor Reality Summary"):
                if f1 and f2 and f3 and api_key:
                    client = Groq(api_key=api_key)
                    reanchor_prompt = f"""
                    The user is getting over their ex. Here are 3 hard truths about why the relationship failed:
                    - Truth 1: {f1}
                    - Truth 2: {f2}
                    - Truth 3: {f3}
                    
                    Write a powerful, grounded 2-paragraph reality reminder addressed directly to them. 
                    Remind them that returning to this person means returning to this exact pain.
                    """
                    summary = client.chat.completions.create(
                        model=selected_model,
                        messages=[{"role": "user", "content": reanchor_prompt}]
                    ).choices[0].message.content
                    st.markdown("### Your Grounding Anchor:")
                    st.success(summary)
                elif not api_key:
                    st.warning("Configure Groq API key.")
