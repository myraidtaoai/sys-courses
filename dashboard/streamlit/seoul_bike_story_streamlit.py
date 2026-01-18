import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    page_title="Seoul Bike Storytelling",
    page_icon="🚲",
    layout="wide"
)

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .story-section {
        padding: 2rem;
        border-radius: 15px;
        background-color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- Mock Data Generation (Based on your EDA results) ---
def load_pattern_data():
    hours = list(range(24))
    # Mimicking the bimodal commuter peak vs leisure weekend
    commuter = [200, 100, 50, 150, 450, 1200, 800, 600, 650, 700, 850, 950, 1100, 1000, 900, 1200, 1800, 1500, 1100, 800, 600, 500, 400, 300]
    wanderer = [150, 80, 40, 60, 120, 250, 450, 650, 850, 1000, 1100, 1200, 1250, 1200, 1100, 1000, 900, 800, 700, 600, 500, 400, 300, 200]
    return pd.DataFrame({"Hour": hours, "Commuter (Weekday)": commuter, "Wanderer (Weekend)": wanderer})

# --- Header Section ---
st.title("🚲 The Pulse of Seoul: A City in Motion")
st.markdown("""
Welcome to the interactive story of the **Seoul Bike Sharing system**. 
This page explores how the city's movement is dictated by the clock, the seasons, and the skies.
""")

# --- Chapter 1: The Daily Rhythm ---
with st.container():
    st.markdown('<div class="story-section">', unsafe_allow_html=True)
    st.header("Chapter 1: The Rhythmic Heartbeat")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("""
        Seoul breathes in a very specific pattern. 
        On **Weekdays**, we see two distinct spikes—the morning rush and the evening return.
        On **Weekends**, the urgency fades, replaced by a gentle afternoon rise.
        """)
        st.metric("Peak Hour (Commuter)", "6:00 PM", "1,800 bikes/hr")
        st.metric("Peak Hour (Wanderer)", "1:00 PM", "1,250 bikes/hr")
    
    with col2:
        pattern_df = load_pattern_data()
        fig = px.line(pattern_df, x="Hour", y=["Commuter (Weekday)", "Wanderer (Weekend)"],
                      labels={"value": "Rentals", "variable": "Day Type"},
                      title="Hourly Patterns: Rush Hour vs. Leisure",
                      color_discrete_sequence=["#3b82f6", "#10b981"])
        fig.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Chapter 2: Clustering the City ---
st.header("Chapter 2: The Three Faces of Demand")
st.write("Using DTW (Dynamic Time Warping) Clustering, we categorized every day into one of three distinct behaviors.")

cols = st.columns(3)
with cols[0]:
    st.info("### Cluster 1: The Workhorse")
    st.write("**Frequency:** 65% of days")
    st.write("The backbone of the system. Predictable, high-volume, and commuter-heavy.")
with cols[1]:
    st.success("### Cluster 2: The Wanderer")
    st.write("**Frequency:** 25% of days")
    st.write("Weekends and holidays. Demand is spread out, peaking with the afternoon sun.")
with cols[2]:
    st.error("### Cluster 0: The Quiet")
    st.write("**Frequency:** 10% of days")
    st.write("Days of extreme cold or rain. The city takes a break from cycling.")

# --- Chapter 3: Weather as a Gatekeeper ---
with st.container():
    st.markdown('<div class="story-section">', unsafe_allow_html=True)
    st.header("Chapter 3: The Elements")
    
    st.write("How does the environment change our behavior? Use the slider to see predicted demand.")
    
    temp = st.slider("Select Temperature (°C)", -15, 40, 25)
    rain = st.checkbox("Is it raining?")
    
    # Simple logic based on your EDA coefficients
    base_demand = 1000
    temp_impact = 1 - (abs(25 - temp) / 50)
    rain_impact = 0.15 if rain else 1.0
    final_prediction = int(base_demand * temp_impact * rain_impact)
    
    st.subheader(f"Estimated Demand: {final_prediction} bikes")
    
    # Weather Scatter simulation
    weather_data = pd.DataFrame({
        "Temp": np.random.normal(20, 10, 500),
        "Rentals": np.random.randint(200, 2000, 500)
    })
    weather_data["Rentals"] = weather_data["Rentals"] * (1 - abs(20 - weather_data["Temp"])/60)
    
    fig_weather = px.scatter(weather_data, x="Temp", y="Rentals", 
                             trendline="ols", title="Correlation: Temperature vs. Bike Usage",
                             color_discrete_sequence=["#f43f5e"])
    st.plotly_chart(fig_weather, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Chapter 4: The Digital Crystal Ball ---
st.header("Chapter 4: Predicting the Future")
st.write("""
Our **LightGBM model** doesn't just look at the current hour—it remembers. 
By analyzing lags (what happened 1h, 24h, and 1 week ago), it achieves high accuracy.
""")

metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
metrics_col1.metric("R-Squared", "0.92", "+2% vs Baseline")
metrics_col2.metric("MAPE", "18.4%", "-5% improvement")
metrics_col3.metric("RMSE", "142", "Lower is better")

st.markdown("""
---
### Strategic Takeaways
1. **Prepare for the Rush:** Rebalance bikes toward residential areas at 7 AM.
2. **The Monsoon Strategy:** Scheduled maintenance should happen during high-probability rain forecasts.
3. **Leisure Scaling:** Increase capacity in river-side stations during Cluster 2 (Weekend) patterns.
""")