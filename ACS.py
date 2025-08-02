import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Ensure matplotlib backend is compatible with Streamlit
plt.switch_backend('agg')

# ------------------------ Battery Types ------------------------ #
battery_types = {
    "Lithium-Ion": {"voltage": 3.7, "capacity": 2.5, "efficiency": 0.95},
    "Lead-Acid": {"voltage": 2.0, "capacity": 5.0, "efficiency": 0.85},
    "NiMH": {"voltage": 1.2, "capacity": 2.0, "efficiency": 0.75},
    "Solid-State": {"voltage": 3.8, "capacity": 3.0, "efficiency": 0.98},
    "NMC": {"voltage": 3.7, "capacity": 2.8, "efficiency": 0.95},
    "LFP": {"voltage": 3.2, "capacity": 3.0, "efficiency": 0.98},
    "LCO": {"voltage": 3.7, "capacity": 2.5, "efficiency": 0.92},
    "LMO": {"voltage": 3.7, "capacity": 2.2, "efficiency": 0.90},
}

# ------------------------ Simulator ------------------------ #
def simulate_battery(b_config, series_cells, parallel_cells, mode, duration):
    total_voltage = b_config["voltage"] * series_cells
    total_capacity = b_config["capacity"] * parallel_cells
    time = np.arange(0, duration, 1)

    soc, voltage, current = [], [], []
    soc_val = 0 if mode == "Charging" else 100

    for t in time:
        if mode == "Charging":
            soc_val = min(100, soc_val + 100 / duration)
        else:
            soc_val = max(0, soc_val - 100 / duration)

        current_val = (total_capacity / duration) * (1 if mode == "Charging" else -1)
        voltage_val = total_voltage * (soc_val / 100)

        soc.append(soc_val)
        current.append(current_val)
        voltage.append(voltage_val)

    return pd.DataFrame({
        "Time (s)": time,
        "SOC (%)": soc,
        "Current (A)": current,
        "Voltage (V)": voltage
    }), total_voltage, total_capacity

# ------------------------ App UI ------------------------ #
st.set_page_config(layout="wide")
st.title("🔋 Battery Cell Simulator - 8 Individual Dashboards")
st.markdown("Configure, simulate, and monitor 8 different battery cells independently with unique chemistries.")

cell_tabs = st.tabs([f"Cell {i+1}" for i in range(8)])

for i, tab in enumerate(cell_tabs):
    with tab:
        st.header(f"⚙️ Configuration for Cell {i+1}")
        col1, col2 = st.columns(2)
        with col1:
            battery_type = st.selectbox(
                f"🔋 Battery Type (Cell {i+1})", 
                list(battery_types.keys()), 
                key=f"type_{i}"
            )
            series_cells = st.slider(
                f"🔗 Cells in Series (Cell {i+1})", 
                1, 10, 3, 
                key=f"series_{i}"
            )
            parallel_cells = st.slider(
                f"🧩 Cells in Parallel (Cell {i+1})", 
                1, 5, 2, 
                key=f"parallel_{i}"
            )
        with col2:
            sim_mode = st.radio(
                f"⚡ Simulation Mode (Cell {i+1})", 
                ["Charging", "Discharging"], 
                key=f"mode_{i}"
            )
            simulation_time = st.slider(
                f"⏱️ Simulation Duration (s) - Cell {i+1}", 
                10, 100, 60, 
                key=f"duration_{i}"
            )

        b_config = battery_types[battery_type]

        # Run simulation
        df, total_voltage, total_capacity = simulate_battery(
            b_config, series_cells, parallel_cells, sim_mode, simulation_time
        )

        # ------------ Dashboard ------------ #
        st.subheader("📊 Cell Dashboard")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Type", battery_type)
        col2.metric("Voltage", f"{total_voltage:.2f} V")
        col3.metric("Capacity", f"{total_capacity:.2f} Ah")
        col4.metric("Efficiency", f"{b_config['efficiency'] * 100:.0f}%")
        col5.metric("Current", f"{df['Current (A)'].iloc[0]:.2f} A")

        # ------------ Graphs ------------ #
        st.subheader("📈 Battery Graphs")
        fig, ax = plt.subplots(3, 1, figsize=(10, 6))

        ax[0].plot(df["Time (s)"], df["SOC (%)"], color="green")
        ax[0].set_ylabel("SOC (%)")
        ax[0].grid(True)

        ax[1].plot(df["Time (s)"], df["Voltage (V)"], color="blue")
        ax[1].set_ylabel("Voltage (V)")
        ax[1].grid(True)

        ax[2].plot(df["Time (s)"], df["Current (A)"], color="red")
        ax[2].set_ylabel("Current (A)")
        ax[2].set_xlabel("Time (s)")
        ax[2].grid(True)

        st.pyplot(fig, clear_figure=True)
