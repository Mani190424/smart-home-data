import streamlit as st
import pandas as pd
import plotly.express as px
import io

# ===== PAGE CONFIG =====
st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

# ===== LOAD CSS =====
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style.css")

# ===== LOAD DATA =====
@st.cache_data
def load_data_from_github():
    url = "https://raw.githubusercontent.com/Mani190424/smart-home-data/main/Smart_Automation_Home_System_in.csv"
    df = pd.read_csv(url, encoding='ISO-8859-1')
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
    df = df.dropna(subset=["Date"])
    df.columns = df.columns.str.strip()
    return df

df = load_data_from_github()

# ===== SIDEBAR FILTERS =====
# ===== SIDEBAR FILTERS =====
st.sidebar.title("⚙️ Filters")

# Dynamic date range from data
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.slider(
    "Select Date Range 📅",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="DD-MM-YYYY"
)

df = df[(df["Date"].dt.date >= date_range[0]) & (df["Date"].dt.date <= date_range[1])]

# Dynamic group by options
group_options = ["Daily", "Weekly", "Monthly", "Yearly"]
group_by = st.sidebar.selectbox("⏱ Group Data By", group_options)

if group_by == "Daily":
    df["Period"] = df["Date"].dt.date
elif group_by == "Weekly":
    df["Period"] = df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
elif group_by == "Monthly":
    df["Period"] = df["Date"].dt.to_period("M").apply(lambda r: r.start_time)
else:
    df["Period"] = df["Date"].dt.to_period("Y").apply(lambda r: r.start_time)

# ===== HEADER =====
st.markdown('<div class="section-header">🏠 Smart Home Dashboard</div>', unsafe_allow_html=True)

# ===== ROOM SELECTION =====
rooms = df['Room'].dropna().unique()
room_selected = st.selectbox("🏠 Select Room", rooms)
room_df = df[df['Room'] == room_selected]

# ===== KPI CARDS =====
if not room_df.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="kpi-card">🌡 Avg Temp<br><b>{room_df["Temperature (°C)"].mean():.2f} °C</b></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card">💧 Avg Humidity<br><b>{room_df["Humidity (%)"].mean():.2f} %</b></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi-card">⚡ Total Energy<br><b>{room_df["Energy Consumption (kWh)"].sum():.2f} kWh</b></div>', unsafe_allow_html=True)
else:
    st.info("No data available for selected room or date range.")

# ===== TRENDS =====
st.markdown('<div class="section-header">📊 Trends</div>', unsafe_allow_html=True)
fig_temp = px.line(room_df.groupby("Year")["Temperature (°C)"].mean().reset_index(),
                   x="Year", y="Temperature (°C)", title="Temperature Trend", color_discrete_sequence=["red"])
st.plotly_chart(fig_temp, use_container_width=True)

fig_hum = px.line(room_df.groupby("Year")["Humidity (%)"].mean().reset_index(),
                  x="Year", y="Humidity (%)", title="Humidity Trend", color_discrete_sequence=["orange"])
st.plotly_chart(fig_hum, use_container_width=True)

fig_energy = px.line(room_df.groupby("Year")["Energy Consumption (kWh)"].sum().reset_index(),
                     x="Year", y="Energy Consumption (kWh)", title="Energy Consumption Trend", color_discrete_sequence=["green"])
st.plotly_chart(fig_energy, use_container_width=True)

# ===== APPLIANCE TREND =====
st.markdown('<div class="section-header">🔌 Appliance Trend</div>', unsafe_allow_html=True)
appliances = room_df['Appliance'].dropna().unique()
selected_appliances = st.multiselect("Select Appliances", appliances, default=appliances[:3])
appl_df = room_df[room_df['Appliance'].isin(selected_appliances)]
trend_appl = appl_df.groupby(['Period', 'Appliance'])['Energy Consumption (kWh)'].sum().reset_index()
if not trend_appl.empty:
    fig_appl = px.line(trend_appl, x='Period', y='Energy Consumption (kWh)', color='Appliance', title="Appliance Energy Trend")
    st.plotly_chart(fig_appl, use_container_width=True)

# ===== ROOM WISE COMPARISON =====
st.markdown('<div class="section-header">🆚 Room-wise Energy Comparison</div>', unsafe_allow_html=True)
compare_rooms = st.multiselect("Select 2 Rooms for Comparison", df['Room'].dropna().unique(), default=df['Room'].dropna().unique()[:2], max_selections=2)
compare_df = df[df['Room'].isin(compare_rooms)]
room_compare = compare_df.groupby(['Period', 'Room'])['Energy Consumption (kWh)'].sum().reset_index()
if not room_compare.empty:
    fig_comp = px.line(room_compare, x='Period', y='Energy Consumption (kWh)', color='Room', title="Room-wise Energy Comparison")
    st.plotly_chart(fig_comp, use_container_width=True)

# ===== TOP 1 APPLIANCE =====
st.markdown('<div class="section-header">🚀 Top 1 Appliance by Energy</div>', unsafe_allow_html=True)
top_appl = compare_df.groupby(["Room", "Appliance"])["Energy Consumption (kWh)"].sum().reset_index()
top1 = top_appl.sort_values(["Room", "Energy Consumption (kWh)"], ascending=[True, False]).groupby("Room").head(1)
for room in compare_rooms:
    st.markdown(f"**{room}**")
    st.dataframe(top1[top1["Room"] == room][["Appliance", "Energy Consumption (kWh)"]])

# ===== DOWNLOAD ROOM DATA =====
st.markdown('<div class="section-header">⬇️ Download Room Data</div>', unsafe_allow_html=True)
import io
csv_buffer = io.StringIO()
room_df.to_csv(csv_buffer, index=False)
st.download_button("📥 Download CSV", csv_buffer.getvalue(), "smart_home_room.csv", "text/csv")
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    room_df.to_excel(writer, index=False, sheet_name="RoomData")
excel_buffer.seek(0)
st.download_button("📥 Download Excel", excel_buffer, "smart_home_room.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
