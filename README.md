# Seoul Bike Rental Story 🚴

**Uncovering Trends, Seasons, and Patterns in Bike Sharing Data**

This project is an applied data science dashboard built to tell the story of Seoul's bike-sharing system. It combines historical data analysis with predictive modeling to provide actionable insights into urban mobility.

## 📖 Project Overview

Every dataset tells a story. This dashboard reveals the fascinating patterns of Seoul's bike-sharing system, exploring how rental demand evolves through time, seasons, and daily cycles.

### Key Features

1.  **📊 Descriptive Analysis (Storytelling)**
    *   **Tendency**: Visualizes long-term trends and year-over-year growth.
    *   **Seasonality**: Analyzes the impact of the four seasons, highlighting how weather drives demand (e.g., the 5x difference between peak Summer and low Winter).
    *   **Periodicity**: Uncovers daily commute patterns with clear morning (7-9 AM) and evening (5-7 PM) peaks.
    *   **Weather Impact**: Demonstrates the strong positive correlation between temperature and bike rentals.

2.  **🔮 Predictive Modeling**
    *   **Forecasting**: Integrated 24-hour and 3-day predictions for bike rental demand.
    *   **Visualization**: Compares historical data (last 7 days) against future predictions to validate trends.
    *   **Metrics**: Provides key metrics like total predicted rentals and peak predicted demand.

## 🛠️ Technologies

*   **Frontend**: [Streamlit](https://streamlit.io/)
*   **Visualization**: [Plotly](https://plotly.com/)
*   **Database**: SQLite
*   **Language**: Python 3.12

## 🚀 Setup & Usage

### Prerequisites

Ensure you have Python installed. You will need the following libraries:
*   `streamlit`
*   `pandas`
*   `plotly`

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd applied-data-science
    ```

2.  Install dependencies:
    ```bash
    pip install streamlit pandas plotly
    ```

### Running the Dashboard

Navigate to the dashboard directory and launch the Streamlit app:

```bash
cd dashboard
streamlit run dashboard.py
```

The dashboard will be available in your browser at `http://localhost:8501`.

## 📂 Project Structure

*   `dashboard/dashboard.py`: Main application script containing the storytelling logic and visualizations.
*   `dashboard/db_connection.py`: Helper module for database interactions.
*   `dashboard/database/bikes.db`: SQLite database containing historical data and prediction results.

## 📊 Data Source

*   **Dataset**: Seoul Bike Sharing System (2017-2018).
*   **Context**: Includes rental counts, meteorological data (Temperature, Humidity, Wind Speed), and temporal information.

## Demo
Demo link: https://seoulrentalbikes.streamlit.app/
---
*Dashboard created for data storytelling.*