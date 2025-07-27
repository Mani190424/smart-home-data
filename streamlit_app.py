
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load your dataset
import requests
from io import StringIO

csv_url = "https://raw.githubusercontent.com/Mani190424/smart-home-data/main/smart_home_8yr_simulated.csv"
response = requests.get(csv_url)

if response.status_code == 200:
    df = pd.read_csv(StringIO(response.text))
else:
    st.error("❌ Failed to load data from GitHub.")



# --- Clean and preprocess ---
df['Date'] = pd.to_datetime(df['Date'])
df['Week'] = df['Date'].dt.isocalendar().week
df['Month'] = df['Date'].dt.to_period('M').astype(str)
df['Year'] = df['Date'].dt.year
df['Weekday'] = df['Date'].dt.day_name()

# --- Sidebar Controls ---
st.sidebar.title("Smart Home Filters")

# Room Selector
rooms = df['Room'].unique()
selected_room = st.sidebar.selectbox("Select Room", options=rooms)

# Time Range Toggle
time_view = st.sidebar.radio("View By", ["Weekly", "Monthly", "Yearly"])

# Appliance Switch
appliance_state = st.sidebar.toggle(f"{selected_room} Appliance", value=True)
if appliance_state:
    st.sidebar.success(f"{selected_room} Appliance is ON")
else:
    st.sidebar.warning(f"{selected_room} Appliance is OFF")

# Filtered Data
filtered_df = df[df['Room'] == selected_room]

# Time View Grouping
if time_view == "Weekly":
    time_group = filtered_df.groupby(['Year', 'Week']).agg({'Power': 'sum'}).reset_index()
    time_group['Label'] = time_group['Year'].astype(str) + "-W" + time_group['Week'].astype(str)
elif time_view == "Monthly":
    time_group = filtered_df.groupby('Month').agg({'Power': 'sum'}).reset_index()
    time_group['Label'] = time_group['Month']
else:
    time_group = filtered_df.groupby('Year').agg({'Power': 'sum'}).reset_index()
    time_group['Label'] = time_group['Year'].astype(str)

# --- Main App ---
st.title("🏠 Smart Home Energy Dashboard")

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Power", f"{filtered_df['Power'].sum():.2f} kWh")
with col2:
    st.metric("Avg Temperature", f"{filtered_df['Temperature'].mean():.1f} °C")
with col3:
    st.metric("Avg Humidity", f"{filtered_df['Humidity'].mean():.1f} %")

# Time Series Chart
fig = px.line(time_group, x='Label', y='Power', title=f"Energy Usage - {time_view} View")
st.plotly_chart(fig, use_container_width=True)

# Appliance Status
st.subheader("Room Appliance Switch")
st.write(f"Appliance in **{selected_room}** is currently **{'ON' if appliance_state else 'OFF'}**")

# Query param example (replacing deprecated one)
st.query_params(room=selected_room, view=time_view)

# Footer
st.markdown("---")
st.caption("Smart Home Dashboard | Powered by Streamlit & Firebase")

