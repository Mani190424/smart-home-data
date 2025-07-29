
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Smart Home Energy Dashboard", layout="wide")

# -------------- Theme Toggle --------------
theme = st.sidebar.radio("🎨 Theme", ["🌞 Light", "🌙 Dark"])
primary_color = "#000000" if theme == "🌞 Light" else "#fca6bc"
bg_color = "#9BFFEC" if theme == "🌞 Light" else "#0E1117"
font_color = "#000000" if theme == "🌞 Light" else "#fca6bc"
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {font_color};
        }}
    </style>
""", unsafe_allow_html=True)

st.title("🏠 Smart Home Energy Dashboard")

# Load data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Mani190424/smart-home-data/refs/heads/main/Smart_Automation_Home_System_in.csv"
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    df['Month'] = df['Date'].dt.to_period("M").astype(str)
    df['Week'] = df['Date'].dt.strftime('%Y-%U')
    df['Year'] = df['Date'].dt.year
    return df

df = load_data()

# Sidebar - Date Filter and View Toggle
st.sidebar.header("📅 Filter Options")
years_range = (2015, 2024)
start_date = st.sidebar.date_input("From", df["Date"].min().date(), min_value=datetime(years_range[0], 1, 1), max_value=datetime(years_range[1], 12, 31))
end_date = st.sidebar.date_input("To", df["Date"].max().date(), min_value=datetime(years_range[0], 1, 1), max_value=datetime(years_range[1], 12, 31))
view_by = st.sidebar.radio("View By", ["Daily", "Weekly", "Monthly", "Yearly"])

# Apply date filter
df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

# Room Icons Map
room_icons = {
    "Living Room": "🛋",
    "Bedroom1": "🧻",
    "Bedroom2": "🛌",
    "Kitchen": "🍽",
    "Store Room": "📦"
}

# Room Tabs with Icons
rooms = df["Room"].dropna().unique().tolist()
if not rooms:
    st.warning("No room data available for selected date range.")
    st.stop()

tab_labels = [f"{room_icons.get(room, '🏠')} {room}" for room in rooms]
room_tabs = st.tabs(tab_labels)

# Export helper
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

for i, room in enumerate(rooms):
    with room_tabs[i]:
        icon = room_icons.get(room, "🏠")
        st.markdown(f"""
            <div style='background-color:#f0f2f6; padding:10px 16px; border-radius:12px; margin-bottom:20px;'>
                <h2 style='margin:0;'>{icon} {room}</h2>
            </div>
        """, unsafe_allow_html=True)

        filtered_df = df[df['Room'] == room]
        room_appliances = sorted(filtered_df['Appliance'].dropna().unique())
        selected_appliances = st.multiselect("🔌 Select Appliances", options=room_appliances, default=room_appliances, key=f"appliance_{room}")
        filtered_df = filtered_df[filtered_df['Appliance'].isin(selected_appliances)]

        group_col = {
            "Weekly": "Week",
            "Monthly": "Month",
            "Yearly": "Year"
        }.get(view_by, "Date")

        grouped = filtered_df.groupby(group_col).agg({
            "Energy Consumption (kWh)": "sum",
            "Temperature (°C)": "mean",
            "Humidity (%)": "mean"
        }).reset_index()

        total_energy = filtered_df["Energy Consumption (kWh)"].sum()
        avg_temp = filtered_df["Temperature (°C)"].mean()
        avg_humidity = filtered_df["Humidity (%)"].mean()

        def kpi_card(title, value, icon="", unit=""):
            return f"""
            <div style="
                background-color: #262730;
                padding: 1.2rem;
                border-radius: 18px;
                box-shadow: 0 4px 14px rgba(0,0,0,0.25);
                text-align: center;
                color: white;
                margin: 0.5rem;
            ">
                <h4 style='margin-bottom: 0.2rem;'>{icon} {title}</h4>
                <h2 style='margin: 0;'>{value}{unit}</h2>
            </div>
            """

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(kpi_card("Total Energy", round(total_energy, 2), "⚡", " kWh"), unsafe_allow_html=True)
        with col2:
            st.markdown(kpi_card("Avg Temp", round(avg_temp, 1), "🌡", " °C"), unsafe_allow_html=True)
        with col3:
            st.markdown(kpi_card("Avg Humidity", round(avg_humidity, 1), "💧", " %"), unsafe_allow_html=True)

        st.markdown("---")
        chart_type = st.selectbox("📊 Select Chart Type", ["Line", "Bar", "Waterfall", "Donut"], key=f"chart_{room}")

        st.subheader("⚡ Energy Usage (kWh)")
        if chart_type == "Line":
            fig = px.line(grouped, x=group_col, y="Energy Consumption (kWh)")
        elif chart_type == "Bar":
            fig = px.bar(grouped, x=group_col, y="Energy Consumption (kWh)")
        elif chart_type == "Waterfall":
            fig = px.pie(grouped, names=group_col, values="Energy Consumption (kWh)")
        elif chart_type == "Donut":
            fig = px.pie(grouped, names=group_col, values="Energy Consumption (kWh)", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🌡 Temperature (°C)")
        if chart_type == "Line":
            fig2 = px.line(grouped, x=group_col, y="Temperature (°C)")
            fig2.update_traces(line=dict(color="red"))
        elif chart_type == "Bar":
            fig2 = px.bar(grouped, x=group_col, y="Temperature (°C)")
            fig2.update_traces(marker_color="crimson")
        elif chart_type == "Waterfall":
            fig2 = px.Waterfall(grouped, names=group_col, values="Temperature (°C)")
        elif chart_type == "Donut":
            fig2 = px.pie(grouped, names=group_col, values="Temperature (°C)", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("💧 Humidity (%)")
        if chart_type == "Line":
            fig3 = px.line(grouped, x=group_col, y="Humidity (%)")
        elif chart_type == "Bar":
            fig3 = px.bar(grouped, x=group_col, y="Humidity (%)")
        elif chart_type == "Waterfall":
            fig3 = px.Waterfall(grouped, names=group_col, values="Humidity (%)")
        elif chart_type == "Donut":
            fig3 = px.pie(grouped, names=group_col, values="Humidity (%)", hole=0.4)
        st.plotly_chart(fig3, use_container_width=True)

        # Room-wise Export
        st.markdown("### 📥 Download This Room's Data")
        st.download_button(
            label="📄 Export Room Data (CSV)",
            data=convert_df(filtered_df),
            file_name=f"{room.lower().replace(' ', '_')}_data.csv",
            mime="text/csv",
            key=f"csv_{room}"
        )
