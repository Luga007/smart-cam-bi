import streamlit as st
import requests
import pandas as pd
import time
import cv2
from PIL import Image
import numpy as np

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="ASSBI Smart Surveillance",
    layout="wide",
    page_icon="🧠"
)

# ------------------------------------------------
# STYLE
# ------------------------------------------------
st.markdown("""
<style>
.main-title {
    font-size:32px;
    font-weight:700;
    color:#00E5FF;
}

.card {
    background-color:#111827;
    padding:15px;
    border-radius:12px;
    margin-bottom:10px;
}

.small-text {
    color:gray;
    font-size:13px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    "<div class='main-title'>🧠 ASSBI Smart Surveillance & BI Platform</div>",
    unsafe_allow_html=True
)

# ------------------------------------------------
# API HELPER
# ------------------------------------------------
@st.cache_data(ttl=5)
def fetch(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}")
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []

# ------------------------------------------------
# SIDEBAR
# ------------------------------------------------
menu = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📷 Camera Management",
        "🎥 Live Cameras",
        "📡 Telemetry",
        "🚨 Alerts",
        "🔍 Detections",
        "🤖 AI Chat"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("ASSBI AI Surveillance System")

# ------------------------------------------------
# DASHBOARD
# ------------------------------------------------
if menu == "📊 Dashboard":

    cameras = fetch("cameras")
    alerts = fetch("alerts")
    telemetry = fetch("crowd-telemetry")

    col1, col2, col3 = st.columns(3)

    col1.metric("📷 Cameras", len(cameras))
    col2.metric("🚨 Alerts", len(alerts))
    col3.metric("📡 Telemetry", len(telemetry))

    st.subheader("📈 Crowd Analytics")

    telemetry_df = pd.DataFrame(telemetry)

    if not telemetry_df.empty:

        if "person_count" in telemetry_df.columns:
            st.line_chart(telemetry_df["person_count"])

        if "crowd_density_score" in telemetry_df.columns:
            st.line_chart(telemetry_df["crowd_density_score"])

    st.subheader("🚨 Recent Alerts")

    alerts_df = pd.DataFrame(alerts)

    if not alerts_df.empty:
        st.dataframe(alerts_df, width="stretch")

# ------------------------------------------------
# CAMERA MANAGEMENT
# ------------------------------------------------
elif menu == "📷 Camera Management":

    st.subheader("📷 Add New Camera")

    # ----------------------------------------
    # LOAD STREETS
    # ----------------------------------------
    streets = fetch("streets")

    street_options = {}

    for street in streets:
        street_options[
            f"{street['name']} (ID: {street['street_id']})"
        ] = street["street_id"]

    # ----------------------------------------
    # LOAD LOCATIONS
    # ----------------------------------------
    locations = fetch("locations")

    location_options = {}

    for loc in locations:
        location_options[
            f"{loc['name']} (ID: {loc['location_id']})"
        ] = loc["location_id"]

    # ----------------------------------------
    # FORM
    # ----------------------------------------
    with st.form("camera_form"):

        camera_name = st.text_input("Camera Name")

        selected_street = st.selectbox(
            "Street",
            list(street_options.keys())
        )

        selected_location = st.selectbox(
            "Location",
            list(location_options.keys())
        )

        status = st.selectbox(
    "Camera Status",
    ["active", "offline", "maintenance"]
)

        video_url = st.text_input(
            "Live Stream URL (optional)"
        )

        uploaded_video = st.file_uploader(
            "Upload MP4 Video",
            type=["mp4"]
        )

        submit = st.form_submit_button("Add Camera")

    # ----------------------------------------
    # CREATE CAMERA
    # ----------------------------------------
    if submit:

        street_id = street_options[selected_street]
        location_id = location_options[selected_location]

        data = {
            "camera_name": camera_name,
            "street_id": street_id,
            "location_id": location_id,
            "status": status,
            "video_url": video_url
        }

        files = {}

        if uploaded_video:
            files["video_file"] = (
                uploaded_video.name,
                uploaded_video,
                "video/mp4"
            )

        try:

            response = requests.post(
                f"{API_URL}/cameras/",
                data=data,
                files=files
            )

            if response.status_code == 200:
                st.success("✅ Camera added successfully")
            else:
                st.error(f"Error: {response.text}")

        except Exception as e:
            st.error(str(e))

    # ----------------------------------------
    # SHOW CAMERAS
    # ----------------------------------------
    st.subheader("📷 Existing Cameras")

    cameras = fetch("cameras")

    if cameras:

        for cam in cameras:

            with st.container():

                st.markdown("<div class='card'>", unsafe_allow_html=True)

                st.markdown(f"### 📷 {cam['camera_name']}")

                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Camera ID:** {cam['camera_id']}")
                    st.write(f"**Street ID:** {cam['street_id']}")
                    st.write(f"**Location ID:** {cam['location_id']}")

                with col2:
                    st.write(f"**Status:** {cam['status']}")

                    if cam.get("video_url"):
                        st.write("✅ Stream URL")

                    if cam.get("video_file"):
                        st.write("✅ Uploaded Video")

                st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------
# LIVE CAMERAS
# ------------------------------------------------
elif menu == "🎥 Live Cameras":

    st.subheader("📡 Live Camera Monitoring")

    cameras = fetch("cameras")

    if not cameras:
        st.warning("No cameras available")

    else:

        cols = st.columns(2)

        for index, cam in enumerate(cameras):

            with cols[index % 2]:

                st.markdown(f"### 📷 {cam['camera_name']}")

                # ------------------------------------
                # MP4 VIDEO
                # ------------------------------------
                if cam.get("video_file"):

                    video_path = cam["video_file"]

                    try:
                        with open(video_path, "rb") as video:
                            st.video(video.read())
                    except:
                        st.error("Cannot open uploaded video")

                # ------------------------------------
                # STREAM URL
                # ------------------------------------
                elif cam.get("video_url"):

                    st.video(cam["video_url"])

                else:
                    st.warning("No video source")

# ------------------------------------------------
# TELEMETRY
# ------------------------------------------------
elif menu == "📡 Telemetry":

    st.subheader("📡 Crowd Telemetry")

    telemetry = fetch("crowd-telemetry")

    df = pd.DataFrame(telemetry)

    if not df.empty:

        st.dataframe(df, width="stretch")

        if "person_count" in df.columns:
            st.line_chart(df["person_count"])

        if "crowd_density_score" in df.columns:
            st.line_chart(df["crowd_density_score"])

# ------------------------------------------------
# ALERTS
# ------------------------------------------------
elif menu == "🚨 Alerts":

    st.subheader("🚨 Security Alerts")

    alerts = fetch("alerts")

    df = pd.DataFrame(alerts)

    if not df.empty:
        st.dataframe(df, width="stretch")

# ------------------------------------------------
# DETECTIONS
# ------------------------------------------------
elif menu == "🔍 Detections":

    st.subheader("🔍 Object Detections")

    detections = fetch("detected-objects")

    df = pd.DataFrame(detections)

    if not df.empty:
        st.dataframe(df, width="stretch")

# ------------------------------------------------
# AI CHAT
# ------------------------------------------------
elif menu == "🤖 AI Chat":

    st.subheader("🤖 AI Surveillance Assistant")

    if "history" not in st.session_state:
        st.session_state.history = []

    for chat in st.session_state.history:

        st.markdown(f"""
        <div class='card'>
        <b>👤 You:</b> {chat['user']}<br><br>
        <b>🤖 AI:</b> {chat['bot']}
        </div>
        """, unsafe_allow_html=True)

    msg = st.text_input("Message")

    if st.button("Send") and msg:

        try:

            response = requests.post(
                f"{API_URL}/chatbot/",
                json={"message": msg}
            )

            reply = response.json().get(
                "response",
                "No response"
            )

        except:
            reply = "Backend connection error"

        st.session_state.history.append({
            "user": msg,
            "bot": reply
        })

        st.rerun()

# ------------------------------------------------
# FOOTER
# ------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.caption("ASSBI • AI Surveillance + Business Intelligence")   