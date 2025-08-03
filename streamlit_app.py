
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Smart Home Energy Dashboard", layout="wide")

# Theme
st.markdown("<meta name='viewport' content='width=device-width, initial-scale=1.0'>", unsafe_allow_html=True)

st.markdown("""
    <style>
    .mobile-toggle {
        position: fixed;
        top: 12px;
        left: 12px;
        z-index: 9999;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6EE7B7, #3B82F6);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
        animation: pulse 2s infinite;
        cursor: pointer;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .mobile-toggle i {
        color: white;
        font-size: 20px;
    }
    .section-header {
        padding: 12px;
        margin: 30px 0 10px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 22px;
        background: linear-gradient(to right, #2c5364, #203a43, #0f2027);
        color: white;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        letter-spacing: 0.5px;
        animation: fadeInHeader 1s ease-in-out;
    }
    @keyframes fadeInHeader {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stTabs [role="tab"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        transition: all 0.3s ease;
        white-space: nowrap;
        overflow: auto;
        max-width: 200px;
    }
    .stTabs [role="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.15);
        transform: scale(1.03);
    }
    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #6366F1, #EC4899);
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .stTabs [role="tablist"] {
        display: flex;
        overflow-x: auto;
        overflow-y: hidden;
        white-space: nowrap;
        scrollbar-width: thin;
    }
    .collapsible {
        background: linear-gradient(to right, #1d2671, #c33764);
        color: white;
        cursor: pointer;
        padding: 14px;
        width: 100%;
        text-align: left;
        border: none;
        outline: none;
        font-size: 18px;
        margin-top: 15px;
        border-radius: 10px;
    }
    .content {
        padding: 0 18px;
        display: none;
        overflow: hidden;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    </style>
    <div class='mobile-toggle'><i>📱</i></div>
""", unsafe_allow_html=True)

# Custom CSS for the Top Appliance Table
st.markdown("""
<style>
/* Style only the dataframes that come next */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 12px;
    overflow: hidden;
    backdrop-filter: blur(10px);
    background: rgba(255,255,255,0.03);
}
div[data-testid="stDataFrame"] table {
    color: #f0f0f0;
}
div[data-testid="stDataFrame"] thead tr {
    background: linear-gradient(to right, #141E30, #243B55);
    color: white;
}
div[data-testid="stDataFrame"] tbody tr:hover {
    background-color: rgba(255,255,255,0.1);
}
div[data-testid="stDataFrame"] th, div[data-testid="stDataFrame"] td {
    padding: 12px 15px;
    text-align: left;
}
</style>
""", unsafe_allow_html=True)

# Sidebar theme
st.sidebar.markdown("""
    <style>
    .css-1aumxhk, .css-1d391kg {
        background: linear-gradient(to bottom right, #141E30, #243B55);
        color: white;
    }
    .css-1d391kg .stRadio > label {
        color: white;
    }
    </style>
                    
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .stDownloadButton button {
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: bold;
        color: white;
        background: linear-gradient(90deg, #36D1DC, #5B86E5);
        border: none;
        transition: all 0.3s ease;
        margin: 8px 0;
    }
    .stDownloadButton button:hover {
        transform: scale(1.05);
        background-color: #38bdf8 !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Change background and border */
div[data-baseweb="select"] > div {
    background: rgba(20, 30, 48, 0.9);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 12px;
    color: white;
}

/* Change selected option pills */
div[data-baseweb="select"] span {
    background: linear-gradient(135deg, #f43b47, #453a94) !important;
    border-radius: 6px !important;
    padding: 4px 8px !important;
    color: #fff !important;
}

/* Hover effect for the options dropdown */
div[data-baseweb="popover"] div[role="listbox"] {
    background: rgba(20,30,48,0.95);
    border: 1px solid rgba(255,255,255,0.1);
}

/* Text inside the dropdown */
div[data-baseweb="option"] {
    color: white;
}

/* Highlight selected option */
div[data-baseweb="option"]:hover {
    background-color: rgba(255,255,255,0.1);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Sidebar container */
[data-testid="stSidebar"] {
    background: linear-gradient(to bottom right, #141E30, #243B55);
    color: #ffffff;
    padding: 1rem;
    box-shadow: 0 0 20px rgba(0,255,255,0.2);
}

/* Radio buttons label text */
[data-testid="stSidebar"] .stRadio > label {
    color: #ffffff !important;
    font-weight: 500;
}

/* Radio buttons with glow */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > div {
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 8px;
    margin-bottom: 6px;
    background: rgba(255,255,255,0.05);
    box-shadow: 0 0 6px rgba(0,255,255,0.3);
    transition: all 0.2s ease;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > div:hover {
    background: rgba(255,255,255,0.15);
    box-shadow: 0 0 12px rgba(0,255,255,0.5);
}

/* Date input fields with glow */
[data-testid="stSidebar"] input[type="text"] {
    background: rgba(0,0,0,0.6);
    color: #ffffff;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 8px;
    box-shadow: 0 0 6px rgba(0,255,255,0.3);
}

/* Section headers with neon gradient and glow */
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    color: #ffffff;
    background: linear-gradient(to right, #4facfe, #00f2fe);
    padding: 6px 12px;
    border-radius: 8px;
    text-shadow: 0 0 6px rgba(0,255,255,0.7);
}

/* Labels */
[data-testid="stSidebar"] label {
    color: #ffffff;
    text-shadow: 0 0 3px rgba(0,255,255,0.6);
}
</style>
""", unsafe_allow_html=True)

theme = st.sidebar.radio("🎨 Theme", ["🌞 Light", "🌙 Dark", "🌛 Synthwave"])
primary_color = "#FAF4F4" if theme == "🌞 Light" else ("#960D30" if theme == "🌙 Dark" else "#d47ad7")
bg_color = "#F8FAFC" if theme == "🌞 Light" else ("#F0F2F5" if theme == "🌙 Dark" else "#0f0f1a")
font_color = "#E1E8EC" if theme == "🌞 Light" else ("#a01034" if theme == "🌙 Dark" else "#fc81fc")

st.markdown(f"""
    <style>
        .stApp {{ background: rgba(15,23,42,0.8); color: {font_color}; backdrop-filter: blur(8px); }}
        .kpi-card {{
            background: linear-gradient(to bottom right, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
            padding: 16px;
            border-radius: 18px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            margin: 0.5rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            animation: floatIn 0.7s ease-out;
            transition: transform 0.3s;
        }}
        .kpi-card:hover {{
            transform: scale(1.03);
        }}
        @keyframes floatIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='section-header'>🏠 Smart Home Energy Dashboard</div>", unsafe_allow_html=True)

# JS for toggle chart sections (optional)
st.components.v1.html("""
<script>
document.querySelectorAll(".collapsible").forEach(btn => {
  btn.addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
});
</script>
""", height=0)

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

# Sidebar Filters
st.sidebar.header("🗂️Filter ")
start_date = st.sidebar.date_input("📍From", df["Date"].min().date())
end_date = st.sidebar.date_input("📍To", df["Date"].max().date())

df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
if df.empty:
    st.warning("No data for selected date range.")
    st.stop()

group_by = st.sidebar.radio("📅 Group Data By", ["⌛Daily", "🗓️Weekly", "📅Monthly", "📊Yearly"])
group_col = {
    "⌛Daily": "Date",
    "🗓️Weekly": "Week",
    "📅Monthly": "Month",
    "📊Yearly": "Year"
}[group_by]

# 1. KPIs
st.markdown("<div class='section-header'>📊 Room KPIs</div>", unsafe_allow_html=True)
room_selector = st.selectbox("🏠 Select Room", df["Room"].dropna().unique())
room_df = df[df["Room"] == room_selector]

kpi_grouped = room_df.groupby(group_col).agg({
    "Energy Consumption (kWh)": "sum",
    "Temperature (°C)": "mean",
    "Humidity (%)": "mean"
}).reset_index()

col1, col2, col3 = st.columns(3)
col1.markdown(f"<div class='kpi-card'><h4>⚡ Total Energy</h4><h2>{kpi_grouped['Energy Consumption (kWh)'].sum():.2f} kWh</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='kpi-card'><h4>🌡 Avg Temp</h4><h2>{kpi_grouped['Temperature (°C)'].mean():.1f} °C</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='kpi-card'><h4>💧 Avg Humidity</h4><h2>{kpi_grouped['Humidity (%)'].mean():.1f} %</h2></div>", unsafe_allow_html=True)

# 2. Chart
st.markdown("<div class='section-header'>📈 Energy, 🌡Temperature(°C) &💧Humidity  (%)Trend</div>", unsafe_allow_html=True)
chart_type = st.selectbox("Select Chart Type", ["📈 Line", "📊 Bar", "🌊 Waterfall", "⏲ Solid Gauge"], key="chart-type")

if chart_type != "Solid Gauge":
    animation_args = dict(frame=dict(duration=500, redraw=True), transition=dict(duration=500))
    fig1 = px.line(kpi_grouped, x=group_col, y="Energy Consumption (kWh)") if chart_type == "Line" else px.bar(kpi_grouped, x=group_col, y="Energy Consumption (kWh)")
    fig2 = px.line(kpi_grouped, x=group_col, y="Temperature (°C)") if chart_type == "Line" else px.bar(kpi_grouped, x=group_col, y="Temperature (°C)")
    fig3 = px.line(kpi_grouped, x=group_col, y="Humidity (%)") if chart_type == "Line" else px.bar(kpi_grouped, x=group_col, y="Humidity (%)")
    for fig in [fig1, fig2, fig3]:
        fig.update_layout(transition=animation_args['transition'])
else:
    def solid_gauge(val, title, max_range):
        return go.Figure(go.Indicator(mode="gauge+number", value=val, title={"text": title}, gauge={"axis": {"range": [0, max_range]}}))

    latest_energy = room_df["Energy Consumption (kWh)"].dropna().iloc[-1] if not room_df["Energy Consumption (kWh)"].dropna().empty else 0
    fig1 = solid_gauge(latest_energy, "Current Energy (kWh)", room_df["Energy Consumption (kWh)"].max() or 1)
    latest_temp = room_df["Temperature (°C)"].dropna().iloc[-1] if not room_df["Temperature (°C)"].dropna().empty else 0
    fig2 = solid_gauge(latest_temp, "Current Temp (°C)", 50)
    latest_humidity = room_df["Humidity (%)"].dropna().iloc[-1] if not room_df["Humidity (%)"].dropna().empty else 0
    fig3 = solid_gauge(latest_humidity, "Current Humidity (%)", 100)

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)
st.plotly_chart(fig3, use_container_width=True)

# 3. Appliance Trend
st.markdown("<div class='section-header'>🔌 Appliance-wise Trend</div>", unsafe_allow_html=True)
room_appliances = room_df['Appliance'].dropna().unique().tolist()
selected_appliances = st.multiselect("Select Appliances", room_appliances, default=room_appliances[:3])

appliance_df = room_df[room_df['Appliance'].isin(selected_appliances)]
trend = appliance_df.groupby([group_col, "Appliance"])["Energy Consumption (kWh)"].sum().reset_index()

if not trend.empty:
    fig_app = px.line(trend, x=group_col, y="Energy Consumption (kWh)", color="Appliance", title="Energy Usage Over Time")
    st.plotly_chart(fig_app, use_container_width=True)
else:
    st.info("No appliance data for selection.")

# 4. Download This Room
st.markdown("<div class='section-header'>📥 Download Room Data</div>", unsafe_allow_html=True)
@st.cache_data

def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")

st.download_button("📄 Download Room CSV", convert_df(room_df), f"{room_selector.lower().replace(' ', '_')}_data.csv", "text/csv")

# 5. Compare Energy Between 2 Rooms
st.markdown("<div class='section-header'>🆚 Compare Energy Usage Between Rooms</div>", unsafe_allow_html=True)
compare_rooms = st.multiselect("Select 2 Rooms", df['Room'].dropna().unique().tolist(), default=df['Room'].dropna().unique().tolist()[:2], max_selections=2)
compare_df = df[df['Room'].isin(compare_rooms)]
room_compare = compare_df.groupby([group_col, "Room"])["Energy Consumption (kWh)"].sum().reset_index()
fig_comp = px.line(room_compare, x=group_col, y="Energy Consumption (kWh)", color="Room", title="Room-wise Comparison")
st.plotly_chart(fig_comp, use_container_width=True)

# 6. Appliance Trend Comparison
st.markdown("<div class='section-header'>📊 Appliance Trend </div>", unsafe_allow_html=True)
room_app = compare_df.groupby([group_col, "Room", "Appliance"])["Energy Consumption (kWh)"].sum().reset_index()
fig_room_app = px.line(room_app, x=group_col, y="Energy Consumption (kWh)", color="Appliance", facet_col="Room", title="Appliance Trends by Room")
st.plotly_chart(fig_room_app, use_container_width=True)

# 7. Top Appliance Only
st.markdown(" <div class='section-header'>🚀 Top Appliance by Energy</div>", unsafe_allow_html=True)
top_appl = compare_df.groupby(["Room", "Appliance"])["Energy Consumption (kWh)"].sum().reset_index()
top1 = top_appl.sort_values(["Room", "Energy Consumption (kWh)"], ascending=[True, False]).groupby("Room").head(1)
for room in compare_rooms:
    st.markdown(f"**{room}**")
    st.dataframe(top1[top1["Room"] == room][["Appliance", "Energy Consumption (kWh)"]])

# 8. Export Comparison
st.markdown("<div class='section-header'>📦 Export Comparison Data</div>", unsafe_allow_html=True)
st.download_button("📄 Download Room Comparison", convert_df(room_compare), "room_comparison.csv", "text/csv")
st.download_button("📄 Download Appliance Trends", convert_df(room_app), "appliance_trends.csv", "text/csv")
st.download_button("📄 Download Top 1 Appliance", convert_df(top1), "top1_appliance.csv", "text/csv")
