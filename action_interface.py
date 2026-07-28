import streamlit as st
import time
import datetime
import hashlib
import random
import base64

# --- 1. SETUP & CONFIG ---
st.set_page_config(page_title="Guardian Eye: Command Center", layout="wide")

# --- 2. ENTERPRISE USER DATABASE (RBAC) ---
USER_DB = {
    "SEC_ADMIN_01": {"password": "Admin_Grd_2026!", "role": "Admin"},
    "OPS_FLOOR_04": {"password": "Safe_Ops_!99", "role": "Operator"}
}

# --- 3. SESSION STATE (The System's Memory) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'time_left' not in st.session_state:
    st.session_state.time_left = 60
if 'timer_mode' not in st.session_state:
    st.session_state.timer_mode = "STANDBY" # Modes: STANDBY, VERIFYING, ACTIVE, LOCKED, ABORTED
if 'alarm_triggered' not in st.session_state:
    st.session_state.alarm_triggered = False
if 'stream_authentic' not in st.session_state:
    st.session_state.stream_authentic = True
if 'alerts' not in st.session_state:
    st.session_state.alerts = [] 
if 'frame_data' not in st.session_state:
    st.session_state.frame_data = "SECURE_FRAME_DATA_001"
if 'auto_mode' not in st.session_state:
    st.session_state.auto_mode = False
if 'last_auto_trigger' not in st.session_state:
    st.session_state.last_auto_trigger = time.time()
if 'sound_played' not in st.session_state:
    st.session_state.sound_played = False

# --- 4. ACCESSIBILITY: AUDIO SIREN ---
def play_siren():
    """Triggers audio alert for visually impaired workers."""
    st.audio("https://www.soundjay.com/buttons/beep-01a.mp3", format="audio/mp3", autoplay=True)

# --- 5. LOGIN LOGIC ---
def login():
    st.title("🔐 SYSTEM ACCESS REQUIRED")
    st.write("Please enter your corporate credentials to access the Command Center.")
    with st.form("login_form"):
        username = st.text_input("Employee ID (Username)")
        password = st.text_input("Access Key (Password)", type="password")
        submit = st.form_submit_button("Authorize Access")
        if submit:
            if username in USER_DB and USER_DB[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user_role = USER_DB[username]["role"]
                st.rerun()
            else:
                st.error("Unauthorized: Invalid Credentials.")

# --- 6. MAIN DASHBOARD ---
def main_dashboard():
    # --- STROBE CSS (Accessibility for Deaf Workers) ---
    st.markdown("""
        <style>
        .alarm-box {
            background-color: #ff4b4b; color: white; padding: 30px;
            border-radius: 15px; text-align: center; font-weight: bold;
            font-size: 35px; animation: blinker 0.5s linear infinite;
            border: 5px solid white;
        }
        .abort-box {
            background-color: #ff8c00; color: black; padding: 30px;
            border-radius: 15px; text-align: center; font-weight: bold;
            font-size: 40px; animation: blinker 0.3s linear infinite;
            border: 8px solid black;
        }
        @keyframes blinker { 50% { opacity: 0; } }
        </style>
        """, unsafe_allow_html=True)

    # SIDEBAR (Access Control & Simulation)
    with st.sidebar:
        st.title("👤 ACCESS CONTROL")
        st.write(f"**User:** `{st.session_state.user_role}`")
        st.divider()
        st.subheader("🤖 SYSTEM SIMULATION")
        st.session_state.auto_mode = st.toggle("Enable Auto-Monitoring", value=False)
        st.caption("Simulates real-time AI detections (Compliance vs Critical).")
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- AUTOMATION ENGINE (The Intelligence Loop) ---
    if st.session_state.auto_mode and not st.session_state.alarm_triggered:
        if time.time() - st.session_state.last_auto_trigger > 15:
            is_critical = random.choice([True, False])
            
            # THE NOISE REDUCTION LOGIC (Context-Aware Filtering)
            if st.session_state.timer_mode == "ACTIVE":
                if is_critical:
                    # SCENARIO: Person enters during blast $\rightarrow$ ABORT
                    st.session_state.alarm_triggered = True
                    st.session_state.timer_mode = "ABORTED"
                    new_alert = {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "priority": "CRITICAL", "msg": "🚨 BLAST ABORTED",
                        "reason": "INTRUSION DURING COUNTDOWN", "identity": "EMP_99",
                        "photo": "https://randomuser.me/api/portraits/men/32.jpg", "is_abort": True
                    }
                    st.session_state.alerts.insert(0, new_alert)
                    st.session_state.last_auto_trigger = time.time()
                    st.rerun()
                else:
                    # Ignore Compliance noise during Active Blast to prevent distraction
                    pass 

            elif st.session_state.timer_mode == "VERIFYING":
                if is_critical:
                    # SCENARIO: Person found before blast $\rightarrow$ LOCK
                    st.session_state.timer_mode = "LOCKED"
                    st.session_state.alarm_triggered = True
                    new_alert = {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "priority": "CRITICAL", "msg": "PRE-BLAST FAILURE",
                        "reason": "AREA NOT CLEAR: PERSON DETECTED", "identity": "EMP_44",
                        "photo": "https://randomuser.me/api/portraits/women/44.jpg", "is_abort": False
                    }
                    st.session_state.alerts.insert(0, new_alert)
                    st.session_state.last_auto_trigger = time.time()
                    st.rerun()
                else:
                    # Normal Compliance during Verification
                    new_alert = {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "priority": "COMPLIANCE", "msg": "⚠️ COMPLIANCE ISSUE",
                        "reason": "Missing Helmet", "identity": "EMP_12",
                        "photo": "https://randomuser.me/api/portraits/men/12.jpg", "is_abort": False
                    }
                    st.session_state.alerts.insert(0, new_alert)
                    st.session_state.last_auto_trigger = time.time()
                    st.rerun()

            elif st.session_state.timer_mode == "STANDBY":
                if not is_critical:
                    new_alert = {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "priority": "COMPLIANCE", "msg": "⚠️ COMPLIANCE ISSUE",
                        "reason": "No High-Vis Vest", "identity": "EMP_07",
                        "photo": "https://randomuser.me/api/portraits/men/7.jpg", "is_abort": False
                    }
                    st.session_state.alerts.insert(0, new_alert)
                    st.session_state.last_auto_trigger = time.time()
                    st.rerun()

    # MAIN UI LAYOUT
    st.title("🛡️ THE GUARDIAN EYE: COMMAND CENTER")
    st.markdown("---")
    left_column, right_column = st.columns([2, 1])

    with left_column:
        st.subheader("📹 LIVE CCTV MONITOR")
        if not st.session_state.stream_authentic:
            st.error("🚫 SECURITY ALERT: UNAUTHENTICATED FEED!")
            st.image("https://via.placeholder.com/800x450.png?text=SIGNAL+LOST", use_container_width=True)
        else:
            st.image("https://via.placeholder.com/800x450.png?text=SECURE+LIVE+FEED+ACTIVE", use_container_width=True)

        # ACCESSIBILITY: VISUAL STROBES & ABORT/LOCK MESSAGES
        if st.session_state.alarm_triggered:
            if st.session_state.timer_mode == "ABORTED":
                st.markdown('<div class="abort-box">🚨 BLAST ABORTED: EVACUATE IMMEDIATELY! 🚨</div>', unsafe_allow_html=True)
            elif st.session_state.timer_mode == "LOCKED":
                st.markdown('<div class="alarm-box">🚨 AREA NOT CLEAR: DO NOT START! 🚨</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alarm-box">⚠️ CRITICAL VIOLATION DETECTED! ⚠️</div>', unsafe_allow_html=True)
            
            if not st.session_state.sound_played:
                play_siren()
                st.session_state.sound_played = True

    with right_column:
        st.subheader("⚙️ CONTROL PANEL")
        # SECURITY STATUS
        if st.session_state.stream_authentic:
            st.markdown('<p style="color:green;">✅ STREAM AUTHENTICATED</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:red;">❌ TAMPERED</p>', unsafe_allow_html=True)
        st.divider()

        # TIMER LOGIC
        st.write("### ⏳ BLAST TIMER")
        if st.session_state.timer_mode == "STANDBY":
            st.info("STATUS: READY")
            if st.button("🚀 START BLAST SEQUENCE", use_container_width=True, type="primary"):
                st.session_state.timer_mode = "VERIFYING"
                st.rerun()
        elif st.session_state.timer_mode == "VERIFYING":
            st.warning("🔍 VERIFYING AREA CLEARANCE...")
            time.sleep(3) 
            if random.choice([True, False]):
                st.session_state.timer_mode = "ACTIVE"
                st.success("AREA CLEAR. COUNTDOWN STARTED.")
            else:
                st.session_state.timer_mode = "LOCKED"
                st.session_state.alarm_triggered = True
            st.rerun()
        elif st.session_state.timer_mode == "ACTIVE":
            if st.session_state.time_left > 0:
                st.metric(label="Seconds Remaining", value=f"{st.session_state.time_left}s")
                time.sleep(1)
                st.session_state.time_left -= 1
                st.rerun()
            else:
                st.error("🛑 TIMER EXPIRED")
                st.session_state.timer_mode = "LOCKED"
        elif st.session_state.timer_mode == "ABORTED":
            st.error("🛑 SEQUENCE ABORTED")
        elif st.session_state.timer_mode == "LOCKED":
            st.error("🛑 SEQUENCE BLOCKED")

        st.divider()
        st.write("### 🛠️ TEST CONTROLS")
        if st.button("🚨 MANUAL CRITICAL ALARM", use_container_width=True, type="primary"):
            st.session_state.alarm_triggered = True
            st.session_state.timer_mode = "LOCKED"
            st.session_state.alerts.insert(0, {"time": datetime.datetime.now().strftime("%H:%M:%S"), "priority": "CRITICAL", "msg": "MANUAL TEST", "reason": "Manual Trigger", "identity": "ADMIN_TEST", "photo": "https://randomuser.me/api/portraits/men/1.jpg", "is_abort": False})
            st.rerun()
        if st.button("🔄 RESET SYSTEM", use_container_width=True):
            st.session_state.time_left = 60
            st.session_state.timer_mode = "STANDBY"
            st.session_state.alarm_triggered = False
            st.session_state.stream_authentic = True
            st.session_state.alerts = []
            st.session_state.sound_played = False
            st.rerun()

    st.divider()
    st.subheader("🚨 SAFETY & SECURITY LOG")
    for alert in st.session_state.alerts:
        is_crit = alert['priority'] == "CRITICAL"
        # ROLE-BASED PRIVACY: Admin sees Photo + ID; Operator sees Redacted ID
        if st.session_state.user_role == "Admin":
            full_info = f"{alert['reason']} (ID: {alert['identity']})"
            col1, col2 = st.columns([4, 1])
            with col1:
                if is_crit: st.error(f"**[{alert['time']}] {alert['msg']}** \n\n {full_info}")
                else: st.warning(f"**[{alert['time']}] {alert['msg']}** \n\n {full_info}")
            with col2:
                st.image(alert['photo'], width=80)
        else:
            # Operator View
            display_info = f"{alert['reason']} (ID: [REDACTED])"
            if is_crit: st.error(f"**[{alert['time']}] {alert['msg']}** \n\n {display_info}")
            else: st.warning(f"**[{alert['time']}] {alert['msg']}** \n\n {display_info}")

# --- 6. EXECUTION ---
if not st.session_state.logged_in:
    login()
else:
    main_dashboard()