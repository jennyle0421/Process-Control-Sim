import random
from datetime import datetime
import pandas as pd

# Simulated John Deere equipment IDs
EQUIPMENT_IDS = ["JD-LATHE-001", "JD-MILL-003", "JD-PAINT-002", "JD-ASSEMBLY-005"]

def generate_log():
    """Generate a single mock log entry."""
    equipment = random.choice(EQUIPMENT_IDS)
    temperature = round(random.uniform(60, 130), 2)
    vibration = round(random.uniform(0.1, 3.5), 2)
    hydraulic_pressure = round(random.uniform(1500, 3000), 2)
    throughput = random.randint(80, 250)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status = "OK"
    if temperature > 110 or vibration > 2.5 or hydraulic_pressure < 1700:
        status = "ALERT"

    return {
        "Timestamp": timestamp,
        "Equipment": equipment,
        "Temperature (°F)": temperature,
        "Vibration (mm/s)": vibration,
        "Hydraulic Pressure (psi)": hydraulic_pressure,
        "Throughput (units/hr)": throughput,
        "Status": status,
    }

def generate_logs(num=50):
    """Generate multiple logs for initial display."""
    logs = [generate_log() for _ in range(num)]
    df = pd.DataFrame(logs)
    df.to_csv("data/simulation_logs.csv", index=False)
    return df
