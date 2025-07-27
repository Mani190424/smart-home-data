import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from fpdf import FPDF

# -----------------------
# 1. LOGIN PAGE
# -----------------------
def login():
    st.title("🔐 Smart Home Dashboard Login")
    password = st.text_input("Enter Password", type="password")
    if password == "admin123":
        st.session_state["authenticated"] = True
        st.rerun()
    elif password:
        st.warning("Incorrect password")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()

# -----------------------
# 2. LOAD DATA
# -----------------------
url = "https://raw.githubusercontent.com/Mani190424/smart-home-data/refs/heads/main/Smart_Automation_Home_System(in).csv"
df = pd.read_csv(url)

# Rename columns for ease
df.rename(columns={
    "Temperature (°C)": "Temperature",
    "Humidity (%)": "Humidity",
    "Energy Consumption (kWh)": "Energy"
}, inplace=True)

# Parse dates
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors='coerce')

# Add Date_only
df["Date_only"] = df["Date"].dt.date

# -----------------------
# 3. SIDEBAR CONTROLS
# -----------------------
st.sidebar.title("📊 Dashboard Controls")
selected_room = st.sidebar.selectbox("Select Room", df["Room"].unique())
view_option = st.sidebar.radio("View Mode", ["Daily", "Weekly", "Monthly"])

# Filter by Room
filtered_df = df[df["Room"] == selected_room]

# Resample if needed
if view_option == "Weekly":
    filtered_df = filtered_df.resample("W-MON", on="Date").mean(numeric_only=True).reset_index()
elif view_option == "Monthly":
    filtered_df = filtered_df.resample("M", on="Date").mean(numeric_only=True).reset_index()

# -----------------------
# 4. MAIN DASHBOARD
# -----------------------
st.title("🏠 Smart Home Automation Dashboard")
st.subheader(f"Room: {selected_room} | View: {view_option}")

# KPI Cards
col1, col2, col3 = st.columns(3)
col1.metric("⚡ Total Energy", f"{filtered_df['Energy'].sum():.2f} kWh")
col2.metric("🌡️ Avg Temp", f"{filtered_df['Temperature'].mean():.1f} °C")
col3.metric("💧 Avg Humidity", f"{filtered_df['Humidity'].mean():.1f} %")

# Line Chart with average line
fig = px.line(filtered_df, x="Date", y="Energy", title="Energy Usage Over Time")
fig.add_hline(
    y=filtered_df["Energy"].mean(),
    line_dash="dash", line_color="green",
    annotation_text="Average", annotation_position="top left"
)
st.plotly_chart(fig, use_container_width=True)

# -----------------------
# 5. APPLIANCE TOGGLE
# -----------------------
st.subheader("🛠️ Appliances")
colA, colB, colC = st.columns(3)
ac = colA.toggle("AC", key="ac")
fan = colB.toggle("Fan", key="fan")
light = colC.toggle("Light", key="light")

st.info(f"Appliance States — AC: {'On' if ac else 'Off'}, Fan: {'On' if fan else 'Off'}, Light: {'On' if light else 'Off'}")

# -----------------------
# 6. EXPORT OPTIONS
# -----------------------
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df(filtered_df)
st.sidebar.download_button("⬇️ Export CSV", data=csv_data, file_name="filtered_data.csv", mime='text/csv')

# Export PDF
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(200, 10, f"Smart Home Report - {selected_room}", ln=True, align="C")
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")
    def add_table(self, data):
        self.set_font("Arial", size=10)
        self.cell(40, 10, "Date", 1)
        self.cell(30, 10, "Energy", 1)
        self.cell(30, 10, "Temp", 1)
        self.cell(30, 10, "Humidity", 1)
        self.ln()
        for i, row in data.iterrows():
            self.cell(40, 10, str(row["Date"])[:10], 1)
            self.cell(30, 10, f"{row['Energy']:.2f}", 1)
            self.cell(30, 10, f"{row['Temperature']:.1f}", 1)
            self.cell(30, 10, f"{row['Humidity']:.1f}", 1)
            self.ln()

if st.sidebar.button("📄 Export PDF"):
    pdf = PDF()
    pdf.add_page()
    pdf.add_table(filtered_df.head(30))
    pdf.output("smart_home_report.pdf")
    with open("smart_home_report.pdf", "rb") as f:
        st.sidebar.download_button("📥 Download PDF", data=f, file_name="smart_home_report.pdf")
