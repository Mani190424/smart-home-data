import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar

# --- Page Config ---
st.set_page_config("Smart Home Dashboard", layout="wide")

# --- Logo & Sidebar ---
with st.sidebar:
    st.image("assets/logo.png", width=120)
    st.title("Smart Home Control")
    room = st.selectbox("Select Room", ["All", "Bedroom1", "Bedroom2", "Kitchen", "Living Room", "Store Room"])
    view_mode = st.radio("View Mode", ["Weekly", "Monthly", "Yearly"])
    st.markdown("---")
    st.caption("Powered by Firebase 🔥")

# --- Load Data ---
url = "https://raw.githubusercontent.com/Mani190424/smart-home-data/main/smart_home_8yr_simulated.csv"
df = pd.read_csv(url)

# --- Fix Date Format ---
df['Date'] = pd.to_datetime(df['Date'])

# --- Set Query Params ---
st.query_params["room"] = room
st.query_params["view"] = view_mode

# --- Filter by Room ---
if room != "All":
    df = df[df["Room"] == room]

# --- Resample Based on View Mode ---
if view_mode == "Weekly":
    df_grouped = df.resample("W", on="Date").mean(numeric_only=True)
elif view_mode == "Monthly":
    df_grouped = df.resample("M", on="Date").mean(numeric_only=True)
else:
    df_grouped = df.resample("Y", on="Date").mean(numeric_only=True)

# --- Welcome Card ---
today = datetime.now()
weather_status = "☀️ Sunny"
temp_now = round(df['Temperature'].mean(), 1)
st.markdown(f"""
    <div style='padding:20px; background: linear-gradient(90deg, #1e3c72, #2a5298); border-radius: 12px; color:white'>
        <h2>Welcome Home 🌟</h2>
        <p style='font-size:16px;'>Today is <b>{today.strftime('%A, %d %B %Y')}</b></p>
        <p style='font-size:20px;'>Weather: {weather_status} | Temp: {temp_now}°C</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("### 🔍 Room Overview")

# --- KPI Cards ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("⚡ Total Energy", f"{df['Power'].sum():,.2f} kWh")
with col2:
    st.metric("🌡️ Avg Temp", f"{df['Temperature'].mean():.1f}°C")
with col3:
    st.metric("💧 Avg Humidity", f"{df['Humidity'].mean():.1f}%")
with col4:
    motion_detected = df["Motion"].sum()
    st.metric("🚶 Motion Count", f"{int(motion_detected)}")

# --- Trend Chart ---
st.markdown(f"### 📈 {view_mode} Energy Usage Trend")
fig = px.line(df_grouped, x=df_grouped.index, y="Power", title=f"{room} Energy Usage ({view_mode})")
st.plotly_chart(fig, use_container_width=True)

# --- Room Appliance Switch ---
st.markdown("### 🛋 Room Appliance Switches")
room_states = {}
room_cols = st.columns(5)
rooms = ["Bedroom1", "Bedroom2", "Kitchen", "Living Room", "Store Room"]
for idx, r in enumerate(rooms):
    with room_cols[idx]:
        room_states[r] = st.toggle(f"{r}", value=True, key=f"{r}_toggle")

# --- Room Filter Table ---
if room != "All":
    st.markdown("### 🗂 Room Data Preview")
    st.dataframe(df.tail(50), use_container_width=True)

# --- Footer ---
st.markdown("---")
st.caption("© 2025 Smart Home Automation | Built with ❤️ by Makka")
