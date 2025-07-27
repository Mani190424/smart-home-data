import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

st.set_page_config(layout="wide", page_title="Smart Home Energy Dashboard")

# Load and cache data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Mani190424/smart-home-data/main/smart_home_8yr_simulated.csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()  # clean whitespace
    if 'Date' not in df.columns:
        st.error("❌ 'Date' column not found in the dataset.")
        st.stop()
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔧 Filters")
rooms = df['Room'].unique().tolist()
selected_room = st.sidebar.selectbox("Select Room", rooms)

timeframe = st.sidebar.radio("Select Timeframe", ["Weekly", "Monthly", "Yearly"])
query_params = st.query_params
query_params.update({"room": selected_room, "timeframe": timeframe})

# Filter data
filtered_df = df[df['Room'] == selected_room]

# Timeframe aggregation
if timeframe == "Weekly":
    filtered_df['Period'] = filtered_df['Date'].dt.to_period('W').dt.start_time
elif timeframe == "Monthly":
    filtered_df['Period'] = filtered_df['Date'].dt.to_period('M').dt.start_time
else:
    filtered_df['Period'] = filtered_df['Date'].dt.to_period('Y').dt.start_time

grouped = filtered_df.groupby('Period').agg({
    'Power (kW)': 'sum',
    'Temperature (°C)': 'mean',
    'Humidity (%)': 'mean'
}).reset_index()

# KPI cards
st.title("🏠 Smart Home Energy Dashboard")
col1, col2, col3 = st.columns(3)
col1.metric("⚡ Total Energy Used", f"{filtered_df['Power (kW)'].sum():.2f} kW")
col2.metric("🌡 Avg Temp", f"{filtered_df['Temperature (°C)'].mean():.1f} °C")
col3.metric("💧 Avg Humidity", f"{filtered_df['Humidity (%)'].mean():.1f} %")

# Room Appliance Switch
st.subheader(f"🔌 Appliance Power Switch – {selected_room}")
switch_col = st.columns(len(rooms))
switch_states = {}
for i, room in enumerate(rooms):
    switch_states[room] = switch_col[i].toggle(f"{room}", value=True)

st.markdown("---")

# Charts
st.subheader(f"📈 {timeframe} Trends for {selected_room}")
chart_type = st.selectbox("Choose Chart Type", ["Line", "Bar"])
if chart_type == "Line":
    st.line_chart(grouped.set_index('Period')[['Power (kW)', 'Temperature (°C)', 'Humidity (%)']])
else:
    st.bar_chart(grouped.set_index('Period')[['Power (kW)', 'Temperature (°C)', 'Humidity (%)']])

# Export options
st.subheader("📤 Export Data")
col_csv, col_pdf = st.columns(2)

with col_csv:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "smart_home_filtered.csv", "text/csv")

with col_pdf:
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, f"{selected_room} - {timeframe} Report", ln=True, align="C")

        def table(self, data):
            self.set_font("Arial", size=10)
            col_widths = [40, 30, 30, 30]
            headers = ['Date', 'Power (kW)', 'Temp (°C)', 'Humidity (%)']
            for i, h in enumerate(headers):
                self.cell(col_widths[i], 10, h, border=1)
            self.ln()
            for _, row in data.iterrows():
                self.cell(col_widths[0], 10, str(row['Date'].date()), border=1)
                self.cell(col_widths[1], 10, f"{row['Power (kW)']:.2f}", border=1)
                self.cell(col_widths[2], 10, f"{row['Temperature (°C)']:.1f}", border=1)
                self.cell(col_widths[3], 10, f"{row['Humidity (%)']:.1f}", border=1)
                self.ln()

    pdf = PDF()
    pdf.add_page()
    pdf.table(filtered_df.head(20))  # First 20 rows
    pdf_output = pdf.output(dest='S').encode('latin1')

    st.download_button("Download PDF", pdf_output, "smart_home_report.pdf", "application/pdf")

# Footer
st.markdown("---")
st.caption("📊 Built with ❤️ using Streamlit · Updated with room switch, timeframe toggle, export options.")
