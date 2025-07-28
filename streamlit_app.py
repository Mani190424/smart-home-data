
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------- USER PROFILE HANDLING ----------------
st.sidebar.header("👤 User Profile")

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": "",
        "email": "",
        "mobile": "",
        "image": None,
        "submitted": False
    }

profile = st.session_state.user_profile

if not profile["submitted"]:
    name = st.sidebar.text_input("Name", value=profile["name"])
    email = st.sidebar.text_input("Email", value=profile["email"])
    mobile = st.sidebar.text_input("Mobile", value=profile["mobile"])
    image = st.sidebar.file_uploader("Upload Profile Pic", type=["png", "jpg"])

    if st.sidebar.button("✅ Save Profile"):
        if name and email and mobile and image:
            profile["name"] = name
            profile["email"] = email
            profile["mobile"] = mobile
            profile["image"] = image
            profile["submitted"] = True
            st.session_state.user_profile = profile
            st.rerun()
        else:
            st.sidebar.warning("Please fill all fields and upload a profile picture.")
else:
    with st.sidebar.expander("📄 Profile Summary", expanded=True):
        st.image(profile["image"], width=100)
        st.markdown(f"**Name:** {profile['name']}")
        st.markdown(f"**Email:** {profile['email']}")
        st.markdown(f"**Mobile:** {profile['mobile']}")

    if st.sidebar.button("✏️ Edit Profile"):
        profile["submitted"] = False
        st.session_state.user_profile = profile
        st.rerun()

# -------------- Theme Toggle --------------
theme = st.sidebar.radio("🎨 Theme", ["🌞 Light", "🌙 Dark"])
primary_color = "#000000" if theme == "🌞 Light" else "#fca6bc"
bg_color = "#dda0dd" if theme == "🌞 Light" else "#0E1117"
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

# Room Tab
rooms = df["Room"].dropna().unique().tolist()

if not rooms:
    st.warning("No room data available for selected date range.")
    st.stop()

room_tabs = st.tabs(rooms)

for i, room in enumerate(rooms):
    with room_tabs[i]:
        st.markdown(f"## 🚪 {room}")

        filtered_df = df[df['Room'] == room]
        room_appliances = sorted(filtered_df['Appliance'].dropna().unique())
        selected_appliances = st.multiselect("🔌 Select Appliances", options=room_appliances, default=room_appliances, key=f"appliance_{room}")
        filtered_df = filtered_df[filtered_df['Appliance'].isin(selected_appliances)]

        if view_by == "Weekly":
            group_col = "Week"
        elif view_by == "Monthly":
            group_col = "Month"
        elif view_by == "Yearly":
            group_col = "Year"
        else:
            group_col = "Date"

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
        chart_type = st.selectbox("📊 Select Chart Type", ["Line", "Bar", "Pie", "Donut"], key=f"chart_{room}")

        st.subheader("⚡ Energy Usage (kWh)")
        if chart_type == "Line":
            fig = px.line(grouped, x=group_col, y="Energy Consumption (kWh)")
        elif chart_type == "Bar":
            fig = px.bar(grouped, x=group_col, y="Energy Consumption (kWh)")
        elif chart_type == "Pie":
            fig = px.pie(grouped, names=group_col, values="Energy Consumption (kWh)")
        elif chart_type == "Donut":
            fig = px.pie(grouped, names=group_col, values="Energy Consumption (kWh)", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🌡 Temperature (°C)")
        if chart_type == "Line":
            fig2 = px.line(grouped, x=group_col, y="Temperature (°C)")
        elif chart_type == "Bar":
            fig2 = px.bar(grouped, x=group_col, y="Temperature (°C)")
        elif chart_type == "Pie":
            fig2 = px.pie(grouped, names=group_col, values="Temperature (°C)")
        elif chart_type == "Donut":
            fig2 = px.pie(grouped, names=group_col, values="Temperature (°C)", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("💧 Humidity (%)")
        if chart_type == "Line":
            fig3 = px.line(grouped, x=group_col, y="Humidity (%)")
        elif chart_type == "Bar":
            fig3 = px.bar(grouped, x=group_col, y="Humidity (%)")
        elif chart_type == "Pie":
            fig3 = px.pie(grouped, names=group_col, values="Humidity (%)")
        elif chart_type == "Donut":
            fig3 = px.pie(grouped, names=group_col, values="Humidity (%)", hole=0.4)
        st.plotly_chart(fig3, use_container_width=True)

# Export Data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

st.sidebar.download_button(
    label="📁 Export Filtered Data",
    data=convert_df(df),
    file_name='filtered_smart_home_data.csv',
    mime='text/csv'
)
