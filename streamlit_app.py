import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
from fpdf import FPDF

st.set_page_config(page_title="Smart Home Energy Dashboard", layout="wide")

# ---------- Load Data ----------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Mani190424/smart-home-data/main/smart_home_8yr_simulated.csv"
    response = requests.get(url)
    df = pd.read_csv(StringIO(response.text))
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# ---------- Sidebar Filters ----------
st.sidebar.title("Filters")
room = st.sidebar.selectbox("Select Room", options=["All"] + sorted(df["Room"].unique().tolist()))
timeframe = st.sidebar.radio("Select Timeframe", ["Weekly", Monthly", "Yearly"])
export_format = st.sidebar.radio("Export Format", ["CSV", "PDF"])

if room != "All":
    df = df[df["Room"] == room]

# ---------- Time Grouping ----------
if timeframe == "Weekly":
    df['Period'] = df['Date'].dt.to_period('W').dt.start_time
elif timeframe == "Monthly":
    df['Period'] = df['Date'].dt.to_period('M').dt.start_time
else:
    df['Period'] = df['Date'].dt.to_period('Y').dt.start_time

# ---------- KPI Cards ----------
total_power = df["Power"].sum()
avg_temp = df["Temperature"].mean()
avg_humidity = df["Humidity"].mean()

st.markdown("## 🔌 Smart Home Energy Dashboard")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("⚡ Total Power (kWh)", f"{total_power:.2f}")
kpi2.metric("🌡 Avg. Temperature (°C)", f"{avg_temp:.1f}")
kpi3.metric("💧 Avg. Humidity (%)", f"{avg_humidity:.1f}")

# ---------- Charts ----------
st.markdown("### 📈 Energy Usage Over Time")
chart_data = df.groupby("Period")[["Power"]].sum()
st.line_chart(chart_data)

st.markdown("### 🏠 Room-wise Power Usage")
room_power = df.groupby("Room")["Power"].sum().sort_values()
st.bar_chart(room_power)

# ---------- Export ----------
def export_csv(data):
    data.to_csv("exported_data.csv", index=False)
    st.success("✅ CSV Exported")
    st.download_button("📥 Download CSV", data.to_csv(index=False), file_name="smart_home_export.csv", mime="text/csv")

def export_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Smart Home Dashboard Summary", ln=True, align="C")
    pdf.ln(10)

    # Add KPIs
    pdf.cell(200, 10, txt=f"Total Power: {total_power:.2f} kWh", ln=True)
    pdf.cell(200, 10, txt=f"Avg Temp: {avg_temp:.1f} °C", ln=True)
    pdf.cell(200, 10, txt=f"Avg Humidity: {avg_humidity:.1f} %", ln=True)
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", "B", size=10)
    for col in data.columns[:5]:
        pdf.cell(38, 10, col, 1)
    pdf.ln()

    # Table Rows
    pdf.set_font("Arial", size=9)
    for i, row in data.iterrows():
        for item in row[:5]:
            pdf.cell(38, 10, str(item)[:15], 1)
        pdf.ln()
        if i > 25: break  # Limit rows

    pdf.output("dashboard_summary.pdf")
    with open("dashboard_summary.pdf", "rb") as f:
        st.download_button("📥 Download PDF", f, file_name="dashboard_summary.pdf")

st.markdown("### 📤 Export Data")
if export_format == "CSV":
    export_csv(df)
else:
    export_pdf(df)
