import streamlit as st
import time
import datetime
import os
import json
import random

st.set_page_config(page_title="Guardian Eye: Command Center", layout="wide")

# --- USER DATABASE ---
USER_DB = {
    "MGR_01": {"password": "Manager_Pass_123!", "role": "Manager"},
    "EMP_01": {"password": "Employee_Pass_123!", "role": "Employee"}
}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None
if 'time_left' not in st.session_state: st.session_state.time_left = 60
if 'timer_mode' not in st.session_state: st.session_state.timer_mode = "STANDBY"
if 'alarm_triggered' not in st.session_state: st.session_state.alarm_triggered = False
if 'alerts' not in st.session_state: st.session_state.alerts = []
if 'sound_played' not in st.session_state: st.session_state.sound_played = False

def play_siren():
    st.audio("https://www.soundjay.com/buttons/beep-01a.mp3", format="audio/mp3", autoplay=True)

# --- AUTOMATION BRIDGE ---
def sync_with_ai():
    if os.path.exists("ai_signal.json"):
        try:
            with open("ai_signal.json", "r") as f:
                data = json.load(f)
            if data['priority'] == "CRITICAL":
                st.session_state.alarm_triggered = True
                if st.session_state.timer_mode == "ACTIVE":
                    st.session_state.timer_mode = "ABORTED"
                if not st.session_state.alerts or st.session_state.alerts[0]['reason'] != data['reason']:
                    new_alert = {
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "priority": data['priority'], "msg": data['msg'],
                        "reason": data['reason'], "identity": data['identity'],
                        "photo": data.get('photo', 'https://via.placeholder.com/80'),
                    }
                    st.session_state.alerts.insert(0, new_alert)
        except: pass

def login():
    st.title("🔐 SYSTEM ACCESS REQUIRED")
    with st.form("login_form"):
        username = st.text_input("Employee/Manager ID")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Authorize Access"):
            if username in USER_DB and USER_DB[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user_role = USER_DB[username]["role"]
                # Reset connection every morning
                with open("config.json", "w") as f:
                    json.dump({"source": 0, "connected": False}, f)
                st.rerun()
            else: st.error("Unauthorized.")

def main_dashboard():
    st.markdown("""
        <style>
        .alarm-box { background-color: #ff4b4b; color: white; padding: 30px; border-radius: 15px; text-align: center; font-weight: bold; font-size: 35px; animation: blinker 0.5s linear infinite; border: 5px solid white; }
        .abort-box { background-color: #ff8c00; color: black; padding: 30px; border-radius: 15px; text-align: center; font-weight: bold; font-size: 40px; animation: blinker 0.3s linear infinite; border: 8px solid black; }
        @keyframes blinker { 50% { opacity: 0; } }
        </style>
        """, unsafe_allow_html=True)

    sync_with_ai()

    with st.sidebar:
        st.title("👤 USER PROFILE")
        st.write(f"**Role:** `{st.session_state.user_role}`")
        st.divider()
        
        st.subheader("📹 CCTV CONNECTION")
        config = {"source": 0, "connected": False}
        if os.path.exists("config.json"):
            with open("config.json", "r") as f: config = json.load(f)
        
        if not config["connected"]:
            if st.button("🔑 CONNECT TO CCTV", use_container_width=True, type="primary"):
                config["connected"] = True
                with open("config.json", "w") as f: json.dump(config, f)
                st.rerun()
        else:
            st.success("✅ CCTV Connected")
            if st.button("🔌 DISCONNECT CCTV", use_container_width=True):
                config["connected"] = False
                with open("config.json", "w") as f: json.dump(config, f)
                st.rerun()
        
        st.divider()
        source_option = st.radio("Select Feed Source", ["Live Webcam", "Upload Video"])
        if source_option == "Upload Video":
            uploaded_file = st.file_uploader("Upload CCTV Clip", type=["mp4", "avi", "mov"])
            if uploaded_file:
                with open("uploaded_video.mp4", "wb") as f: f.write(uploaded_file.read())
                config["source"] = "uploaded_video.mp4"
                with open("config.json", "w") as f: json.dump(config, f)
        else:
            config["source"] = 0
            with open("config.json", "w") as f: json.dump(config, f)

        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.title("🛡️ THE GUARDIAN EYE: COMMAND CENTER")
    st.markdown("---")
    left_column, right_column = st.columns([2, 1])

    with left_column:
        st.subheader("📹 LIVE CCTV MONITOR")
        if config["connected"] and os.path.exists("webcam_feed.jpg"):
            st.image("webcam_feed.jpg", use_container_width=True)
        else:
            st.image("https://via.placeholder.com/800x450.png?text=CCTV+OFFLINE", use_container_width=True)

        if st.session_state.alarm_triggered:
            if st.session_state.timer_mode == "ABORTED":
                st.markdown('<div class="abort-box">🚨 EMERGENCY ABORT: BUZZERS ACTIVE! 🚨</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alarm-box">⚠️ SECURITY ALERT: VIOLATION DETECTED ⚠️</div>', unsafe_allow_html=True)
            if not st.session_state.sound_played:
                play_siren()
                st.session_state.sound_played = True

    with right_column:
        st.subheader("⚙️ CONTROL PANEL")
        
        # --- MANAGER EXCLUSIVE SECTION ---
        if st.session_state.user_role == "Manager":
            st.write("### 🛠️ MANAGEMENT OVERRIDE")
            
            # NEW: RESOLVE PROBLEM BUTTON
            if st.session_state.alarm_triggered:
                if st.button("✅ RESOLVE VIOLATION", use_container_width=True, type="primary"):
                    # CRITICAL: Delete the signal file so the alarm doesn't instantly re-trigger
                    if os.path.exists("ai_signal.json"):
                        os.remove("ai_signal.json")
                    st.session_state.alarm_triggered = False
                    st.success("Violation cleared!")
                    st.rerun()
            
            if st.button("🔊 TRIGGER ARENA BUZZER", use_container_width=True):
                play_siren()
                st.info("Buzzer Activated!")
            st.divider()

        st.write("### ⏳ GOD MODE: BLAST CONTROL")
        if st.session_state.timer_mode == "STANDBY":
            if st.session_state.alarm_triggered:
                st.error("🚫 TIMER BLOCKED: EVACUATE ARENA FIRST!")
                st.button("🚀 START BLAST", disabled=True, use_container_width=True)
            else:
                st.info("STATUS: READY")
                if st.session_state.user_role == "Manager":
                    if st.button("🚀 START BLAST SEQUENCE", use_container_width=True, type="primary"):
                        st.session_state.timer_mode = "ACTIVE"
                        st.rerun()
                else:
                    st.warning("Only Managers can start the sequence.")
        elif st.session_state.timer_mode == "ACTIVE":
            if st.session_state.time_left > 0:
                st.metric(label="Seconds Remaining", value=f"{st.session_state.time_left}s")
                time.sleep(1)
                st.session_state.time_left -= 1
                st.rerun()
        elif st.session_state.timer_mode == "ABORTED":
            st.error("🛑 BLAST CANCELLED: INTRUSION DETECTED")

        st.divider()
        # UPDATED RESET SYSTEM
        if st.button("🔄 RESET SYSTEM", use_container_width=True):
            # CRITICAL: Delete the signal file so it doesn't re-trigger immediately
            if os.path.exists("ai_signal.json"):
                os.remove("ai_signal.json")
            
            st.session_state.time_left = 60
            st.session_state.timer_mode = "STANDBY"
            st.session_state.alarm_triggered = False
            st.session_state.alerts = []
            st.session_state.sound_played = False
            st.rerun()

    st.divider()
    st.subheader("🚨 SAFETY & SECURITY LOG")
    for alert in st.session_state.alerts:
        if st.session_state.user_role == "Manager":
            col1, col2 = st.columns([4, 1])
            with col1:
                st.error(f"**[{alert['time']}] {alert['msg']}** \n\n {alert['reason']} (ID: {alert['identity']})")
            with col2:
                st.image(alert['photo'], width=80)
        else:
            st.warning(f"**[{alert['time']}] SECURITY ALERT** \n\n A violation has been detected. Please follow safety protocols.")

if not st.session_state.logged_in:
    login()
else:
    main_dashboard()