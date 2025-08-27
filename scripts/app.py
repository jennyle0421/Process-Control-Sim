import time
import pandas as pd
import streamlit as st
from log_generator import generate_log, generate_logs

# ----------------------
# STREAMLIT PAGE CONFIG
# ----------------------
st.set_page_config(
    page_title="🚜 John Deere Process Control Simulation",
    page_icon="🚜",
    layout="wide"
)

# ----------------------
# CUSTOM CSS FOR BADGES & FLASHING ALERTS
# ----------------------
st.markdown(
    """
    <style>
    /* Status badges */
    .status-ok {
        background-color: #2ecc71;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: bold;
    }
    .status-alert {
        background-color: #e74c3c;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: bold;
    }

    /* Severity badges */
    .sev-warning {
        background-color: #f1c40f;
        color: black;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: bold;
    }
    .sev-critical {
        background-color: #e67e22;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: bold;
    }
    .sev-emergency {
        background-color: #e74c3c;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: bold;
        animation: pulse 1.2s infinite;
    }

    /* Flashing animation for emergencies */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7); }
        70% { box-shadow: 0 0 0 12px rgba(231, 76, 60, 0); }
        100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------
# HEADER
# ----------------------
st.title("🚜 John Deere Process Control Simulation")
st.markdown(
    "Simulating a **process control network** with **real-time logs**, "
    "**multi-level alerts**, and **dynamic KPI visualization**."
)

# ----------------------
# INITIALIZE LOGS
# ----------------------
if "logs_df" not in st.session_state:
    st.session_state.logs_df = generate_logs(25)

# ----------------------
# SIMULATION CONTROLS
# ----------------------
col1, col2 = st.columns([1, 3])
if col1.button("▶ Start Simulation", use_container_width=True):
    st.session_state.simulation_running = True
if col2.button("⏹ Stop Simulation", use_container_width=True):
    st.session_state.simulation_running = False

# ----------------------
# KPI SUMMARY (KEEPING THE PREVIOUS LAYOUT)
# ----------------------
latest = st.session_state.logs_df.iloc[0]
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

kpi_col1.metric("Temperature (°F)", latest["Temperature (°F)"])
kpi_col2.metric("Vibration (mm/s)", latest["Vibration (mm/s)"])
kpi_col3.metric("Hydraulic Pressure (psi)", latest["Hydraulic Pressure (psi)"])
kpi_col4.metric("Throughput (units/hr)", latest["Throughput (units/hr)"])

# ----------------------
# CLASSIFY ALERT SEVERITY
# ----------------------
def classify_alert(row):
    if row["Temperature (°F)"] > 125 or row["Vibration (mm/s)"] > 3.2:
        return "EMERGENCY"
    elif row["Temperature (°F)"] > 110 or row["Vibration (mm/s)"] > 2.5:
        return "CRITICAL"
    elif row["Hydraulic Pressure (psi)"] < 1700:
        return "WARNING"
    return "OK"

st.session_state.logs_df["Severity"] = st.session_state.logs_df.apply(classify_alert, axis=1)

# ----------------------
# STYLE STATUS & SEVERITY BADGES
# ----------------------
def style_badges(df):
    df = df.copy()

    def status_badge(val):
        return f"<span class='status-ok'>🟢 OK</span>" if val == "OK" else f"<span class='status-alert'>🔴 ALERT</span>"

    def severity_badge(val):
        if val == "WARNING":
            return f"<span class='sev-warning'>⚠️ WARNING</span>"
        elif val == "CRITICAL":
            return f"<span class='sev-critical'>🔥 CRITICAL</span>"
        elif val == "EMERGENCY":
            return f"<span class='sev-emergency'>🚨 EMERGENCY</span>"
        return "<span class='status-ok'>✅ OK</span>"

    df["Status"] = df["Status"].apply(status_badge)
    df["Severity"] = df["Severity"].apply(severity_badge)
    return df.to_html(escape=False, index=False)

# ----------------------
# LIVE LOG STREAMING
# ----------------------
placeholder = st.empty()

while st.session_state.get("simulation_running", False):
    new_log = generate_log()
    st.session_state.logs_df = pd.concat(
        [pd.DataFrame([new_log]), st.session_state.logs_df]
    ).reset_index(drop=True)
    st.session_state.logs_df["Severity"] = st.session_state.logs_df.apply(classify_alert, axis=1)
    styled_logs = style_badges(st.session_state.logs_df.head(30))
    placeholder.markdown(styled_logs, unsafe_allow_html=True)
    time.sleep(2)

# ----------------------
# ALERTS PANEL (KEEPING CLEAN LAYOUT BUT COLORFUL)
# ----------------------
alerts = st.session_state.logs_df[st.session_state.logs_df["Severity"] != "OK"]
st.subheader("⚠️ System Alerts")
if alerts.empty:
    st.success("✅ All systems are operating normally!")
else:
    st.error(f"🚨 {len(alerts)} ACTIVE ALERTS DETECTED")
    styled_alerts = style_badges(alerts)
    st.markdown(styled_alerts, unsafe_allow_html=True)

# ----------------------
# DOWNLOAD SIMULATION LOGS
# ----------------------
st.download_button(
    label="📥 Download Simulation Logs (CSV)",
    data=st.session_state.logs_df.to_csv(index=False),
    file_name="simulation_logs.csv",
    mime="text/csv"
)
