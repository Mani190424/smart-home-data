import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config("Smart Home Energy Dashboard", layout="wide")

# Load CSV data from GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Mani190424/smart-home-data/main/smart_home_8yr_simulated.csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("🔧 Filters")
room_list = df["Room"].unique().tolist()
selected_room = st.sidebar.selectbox("Select Room", room_list)
timeframe = st.sidebar.radio("Select Timeframe", ["Weekly", "Monthly", "Yearly"])

# Filter and Resample Data
df_room = df[df["Room"] == selected_room]

if timeframe == "Weekly":
    df_grouped = df_room.resample("W-Mon", on="Date").mean(numeric_only=True)
elif timeframe == "Monthly":
    df_grouped = df_room.resample("M", on="Date").mean(numeric_only=True)
else:
    df_grouped = df_room.resample("Y", on="Date").mean(numeric_only=True)

# Header and KPIs
st.title("🏠 Smart Home Energy Dashboard")
col1, col2, col3 = st.columns(3)
col1.metric("⚡ Total Power Used", f"{df_room['Power'].sum():,.2f} kWh")
col2.metric("🌡️ Avg Temperature", f"{df_room['Temperature'].mean():.2f} °C")
col3.metric("💧 Avg Humidity", f"{df_room['Humidity'].mean():.2f} %")

# Power Trend
st.subheader("📈 Power Usage Over Time")
fig_power = px.line(df_grouped, x=df_grouped.index, y="Power", markers=True, title="Power Consumption")
st.plotly_chart(fig_power, use_container_width=True)

# Temperature & Humidity
st.subheader("🌡️ Temperature and 💧 Humidity Trends")
col4, col5 = st.columns(2)

with col4:
    fig_temp = px.area(df_grouped, x=df_grouped.index, y="Temperature", title="Temperature Trend")
    st.plotly_chart(fig_temp, use_container_width=True)

with col5:
    fig_hum = px.bar(df_grouped, x=df_grouped.index, y="Humidity", title="Humidity Trend")
    st.plotly_chart(fig_hum, use_container_width=True)

# Room-wise Power Share
st.subheader("📊 Room-wise Power Contribution")
room_power = df.groupby("Room")["Power"].sum().reset_index()
fig_donut = px.pie(room_power, names="Room", values="Power", hole=0.4)
st.plotly_chart(fig_donut, use_container_width=True)

# Footer
st.markdown("---")
st.caption("📊 Built by Mani | Smart Home Automation | Streamlit + GitHub")
