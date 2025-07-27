import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

# ---------- Load Data ----------
df = pd.read_csv("Smart_Automation_Home_System.csv")
df['DateTime'] = pd.to_datetime(df['DateTime'], format="%d-%m-%Y %H:%M")

# ---------- Sidebar ----------
import os
logo_path = os.path.join("assets", "logo.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=120)
else:
    st.sidebar.warning("Logo not found")

st.sidebar.title("Smart Home Menu")
room_list = df['Room'].unique().tolist()
selected_room = st.sidebar.selectbox("Select Room", options=room_list)

# Filter data
room_data = df[df['Room'] == selected_room]

# ---------- Welcome Card ----------
today = pd.to_datetime(datetime.now().date())
today_data = room_data[room_data['DateTime'].dt.date == today.date()]
avg_temp = round(today_data['Temperature (°C)'].mean(), 1) if not today_data.empty else "N/A"

st.markdown(
    f"""
    <div style="background-color:#b299ff; padding: 25px; border-radius: 20px; color: white; text-align: left; margin-bottom: 20px;">
        <h2 style="margin-bottom: 0;">👋 MANI</h2>
        <p style="margin-top: 5px; font-size: 18px;">Welcome home</p>
        <h3 style="margin: 10px 0;">🌡️ Weather {avg_temp}°C &nbsp; | &nbsp; ☀️ Sunny Day</h3>
    </div>
    """, unsafe_allow_html=True
)

# ---------- KPIs ----------
col1, col2 = st.columns(2)

with col1:
    temp_now = round(room_data['Temperature (°C)'].iloc[-1], 1)
    st.metric(label="🌡️ Current Temperature", value=f"{temp_now} °C")

with col2:
    humidity_now = round(room_data['Humidity (%)'].iloc[-1], 1)
    st.metric(label="💧 Current Humidity", value=f"{humidity_now} %")

# ---------- Charts Section ----------
st.markdown("### 📊 Weekly Energy Consumption")

df['Week'] = df['Week'].astype(str)
weekly_energy = df.groupby(['Week', 'Room'])['Energy Consumption (kWh)'].sum().reset_index()
room_energy = weekly_energy[weekly_energy['Room'] == selected_room]

bar_fig = px.bar(
    room_energy,
    x='Week',
    y='Energy Consumption (kWh)',
    color='Week',
    title='Weekly Energy Usage (kWh)',
    template='plotly_white',
    color_discrete_sequence=px.colors.sequential.Purples
)
st.plotly_chart(bar_fig, use_container_width=True)

# ---------- Footer Toggles ----------
st.markdown("### 🏠 Room Controls")

room_toggle = st.columns(len(room_list))
for i, room in enumerate(room_list):
    with room_toggle[i]:
        if st.button(room):
            st.experimental_set_query_params(room=room)

# ---------- Raw Data Table ----------
with st.expander("📄 View Raw Data"):
    st.dataframe(room_data.tail(100), use_container_width=True)
