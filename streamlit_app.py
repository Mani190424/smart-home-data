
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------- Page Config ----------
st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

# ---------- Load Data ----------
df = pd.read_csv("Smart_Automation_Home_System.csv")

# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# ---------- Sidebar ----------
st.sidebar.image("assets/logo.png", width=120)
st.sidebar.title("Smart Home Menu")
room_list = df['Room'].unique().tolist()
selected_room = st.sidebar.selectbox("Select Room", options=room_list)

# Filter room data
room_data = df[df['Room'] == selected_room]

# ---------- Welcome Card ----------
today = pd.to_datetime(datetime.now().date())
today_data = room_data[room_data['Date'].dt.date == today.date()]
avg_temp = round(today_data['Temperature'].mean(), 1) if not today_data.empty else "N/A"

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
    temp_now = round(room_data['Temperature'].iloc[-1], 1)
    st.metric(label="🌡️ Current Temperature", value=f"{temp_now} °C")

with col2:
    light_now = round(room_data['Light'].iloc[-1], 1)
    st.metric(label="💡 Light Intensity", value=f"{light_now} %")

# ---------- Charts Section ----------
st.markdown("### 📊 Monthly Power Usage")

# Monthly Power Bar Chart
df['Month'] = df['Date'].dt.strftime('%b')
monthly_power = df.groupby(['Month', 'Room'])['Power'].sum().reset_index()
room_power = monthly_power[monthly_power['Room'] == selected_room]

bar_fig = px.bar(
    room_power,
    x='Month',
    y='Power',
    color='Month',
    title='Monthly Power Consumption',
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

