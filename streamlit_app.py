
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Mani190424/smart-home-data/main/smart_home_8yr_simulated.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Week'] = df['Date'].dt.isocalendar().week
    df['Month'] = df['Date'].dt.month_name()
    df['Year'] = df['Date'].dt.year
    return df

df = load_data()

# Sidebar Filters
st.sidebar.title("🔧 Filters")
room_filter = st.sidebar.multiselect("Select Room", options=df['Room'].unique(), default=df['Room'].unique())
view_mode = st.sidebar.radio("Select View", ["Weekly", "Monthly", "Yearly"])

df_filtered = df[df['Room'].isin(room_filter)]

# View Aggregation
if view_mode == "Weekly":
    group_cols = ['Year', 'Week', 'Room']
elif view_mode == "Monthly":
    group_cols = ['Year', 'Month', 'Room']
else:
    group_cols = ['Year', 'Room']

df_agg = df_filtered.groupby(group_cols).agg({
    'Power (kW)': 'sum',
    'Temperature (°C)': 'mean',
    'Humidity (%)': 'mean'
}).reset_index()

# KPIs
st.title("📊 Smart Home Automation Dashboard")
col1, col2, col3 = st.columns(3)
col1.metric("Total Energy (kW)", f"{df_filtered['Power (kW)'].sum():,.2f}")
col2.metric("Avg Temp (°C)", f"{df_filtered['Temperature (°C)'].mean():.1f}")
col3.metric("Avg Humidity (%)", f"{df_filtered['Humidity (%)'].mean():.1f}")

st.markdown("---")

# Charts
st.subheader("⚡ Energy Usage Over Time")
fig_energy = px.line(df_agg, 
    x="Week" if view_mode == "Weekly" else "Month" if view_mode == "Monthly" else "Year", 
    y="Power (kW)", 
    color="Room",
    markers=True, 
    title="Energy Consumption Trend"
)
st.plotly_chart(fig_energy, use_container_width=True)

st.subheader("🌡️ Temperature and Humidity")
col4, col5 = st.columns(2)

with col4:
    fig_temp = px.bar(df_agg, x="Room", y="Temperature (°C)", color="Room", title="Avg Temperature")
    st.plotly_chart(fig_temp, use_container_width=True)

with col5:
    fig_hum = px.pie(df_agg, values="Humidity (%)", names="Room", title="Humidity Share by Room")
    st.plotly_chart(fig_hum, use_container_width=True)

st.markdown("Made with ❤️ by [YourName] | Data from 8-Year Smart Home Simulation")
