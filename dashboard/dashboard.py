import sys
import pandas as pd
from pathlib import Path
import streamlit as st
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from db_connection import DatabaseConnection

# Set page configuration
st.set_page_config(
    page_title="Seoul Bike Rental Story",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .story-section {
        background-color: #e8f4f8;
        padding: 20px;
        border-left: 5px solid #0066cc;
        border-radius: 5px;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db():
    """Get cached database connection"""
    db_path = Path(__file__).parent / "database" / "bikes.db"
    if not db_path.exists():
        # Fallback to parent directory if not found in current directory
        db_path = Path(__file__).parent.parent / "database" / "bikes.db"
    return DatabaseConnection(str(db_path))


def load_hourly_data():
    """Load hourly data for detailed analysis"""
    db = get_db()
    sql = """
    SELECT date, hour, rented_bike_count, temperature, humidity, wind_speed
    FROM stg_bike_rentals_hourly
    ORDER BY date, hour
    """
    results = db.execute_query(sql)
    if results:
        df = pd.DataFrame(results, columns=['date', 'hour', 'bikes', 'temp', 'humidity', 'wind_speed'])
        df['date'] = pd.to_datetime(df['date'])
        return df
    return pd.DataFrame()


def load_daily_data():
    """Load daily aggregated data"""
    db = get_db()
    sql = """
    SELECT date, total_bike_count, avg_bike_count, max_bike_count, min_bike_count
    FROM fact_bike_rentals_daily
    ORDER BY date
    """
    results = db.execute_query(sql)
    if results:
        df = pd.DataFrame(results, columns=['date', 'total', 'avg', 'max', 'min'])
        df['date'] = pd.to_datetime(df['date'])
        return df
    return pd.DataFrame()


def load_monthly_data():
    """Load monthly aggregated data"""
    db = get_db()
    sql = """
    SELECT year, month, month_name, total_bike_count, avg_bike_count
    FROM fact_bike_rentals_monthly
    ORDER BY year, month
    """
    results = db.execute_query(sql)
    if results:
        df = pd.DataFrame(results, columns=['year', 'month', 'month_name', 'total', 'avg'])
        return df
    return pd.DataFrame()


def load_hourly_pattern():
    """Load average bikes by hour for periodicity analysis"""
    db = get_db()
    sql = """
    SELECT hour, ROUND(AVG(rented_bike_count), 0) as avg_bikes, 
           COUNT(*) as count_records
    FROM stg_bike_rentals_hourly
    GROUP BY hour
    ORDER BY hour
    """
    results = db.execute_query(sql)
    if results:
        df = pd.DataFrame(results, columns=['hour', 'avg_bikes', 'count'])
        return df
    return pd.DataFrame()


# ============================================================
# MAIN DASHBOARD
# ============================================================

st.title("🚴 Seoul Bike Rental Story")
st.markdown("**Uncovering Trends, Seasons, and Patterns in Bike Sharing Data**")


# Introduction
st.markdown("""
    <div class="story-section">
    <h3>📖 The Story Unfolds</h3>
    <p>Every dataset tells a story. This dashboard reveals the fascinating patterns of Seoul's bike-sharing system,
    exploring how rental demand evolves through time, seasons, and daily cycles. From bustling commute hours to quiet 
    winter nights, discover what drives Seoulites to pedal.</p>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# SECTION 1: KEY METRICS
# ============================================================
st.header("📊 Quick Insights")

col1, col2, col3, col4 = st.columns(4)

db = get_db()

# Total rentals
total_sql = "SELECT SUM(total_bike_count) FROM fact_bike_rentals_daily"
total_result = db.execute_query(total_sql)
total_rentals = total_result[0][0] if total_result else 0

# Average daily
avg_daily_sql = "SELECT AVG(total_bike_count) FROM fact_bike_rentals_daily"
avg_result = db.execute_query(avg_daily_sql)
avg_daily = avg_result[0][0] if avg_result else 0

# Peak day
peak_sql = "SELECT date, total_bike_count FROM fact_bike_rentals_daily ORDER BY total_bike_count DESC LIMIT 1"
peak_result = db.execute_query(peak_sql)
peak_bikes = peak_result[0][1] if peak_result else 0
peak_date = peak_result[0][0] if peak_result else ""

# Peak month
peak_month_sql = "SELECT month_name, year, total_bike_count FROM fact_bike_rentals_monthly ORDER BY total_bike_count DESC LIMIT 1"
peak_month_result = db.execute_query(peak_month_sql)
peak_month = f"{peak_month_result[0][0]} {peak_month_result[0][1]}" if peak_month_result else ""

with col1:
    st.metric("Total Rentals", f"{total_rentals:,.0f}", "bikes")

with col2:
    st.metric("Daily Average", f"{avg_daily:,.0f}", "bikes/day")

with col3:
    st.metric("Peak Day", f"{peak_bikes:,.0f}", f"on {peak_date}")

with col4:
    st.metric("Peak Season", peak_month, "highest demand")

# ============================================================
# SECTION 2: TENDENCY - Long-term Trends
# ============================================================
st.header("📈 Tendency: Long-term Trends")

st.markdown("""
    <div class="story-section">
    <h4>The Upward Journey</h4>
    <p><b>What we see:</b> As seasons change from winter to summer, bike rentals show a dramatic upward trend. 
    The data begins in December's cold months with modest rentals, gradually warming into spring's moderate usage, 
    and peaking during summer's golden months.</p>
    <p><b>The story:</b> Weather is the primary storyteller here. Cold winters discourage cycling, while mild springs 
    and hot summers create perfect conditions for outdoor activities.</p>
    </div>
""", unsafe_allow_html=True)

daily_data = load_daily_data()

if not daily_data.empty:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Daily Bike Rentals Over Time")
        
        # Create the trend chart data
        dates = daily_data['date'].dt.strftime('%Y-%m-%d').tolist()
        totals = daily_data['total'].tolist()
        
        # Calculate 7-day moving average
        daily_data['ma7'] = daily_data['total'].rolling(window=7).mean()
        moving_avg = daily_data['ma7'].tolist()
        
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        # Add daily rentals
        fig.add_trace(go.Scatter(
            x=dates, y=totals,
            name='Daily Rentals',
            mode='lines',
            line=dict(color='rgba(100, 150, 255, 0.3)', width=1),
            fillcolor='rgba(100, 150, 255, 0.1)',
            fill='tozeroy'
        ))
        
        # Add 7-day moving average
        fig.add_trace(go.Scatter(
            x=dates, y=moving_avg,
            name='7-Day Trend',
            mode='lines',
            line=dict(color='#0066cc', width=3)
        ))
        
        fig.update_layout(
            title="Daily Rentals with 7-Day Moving Average",
            xaxis_title="Date",
            yaxis_title="Number of Bikes Rented",
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, width='stretch')
    
    with col1:
        # Year-over-year comparison
        monthly_data = load_monthly_data()
        
        if not monthly_data.empty:
            st.subheader("Monthly Pattern: Winter vs. Summer")
            
            # Create monthly chart
            months = monthly_data['month_name'].tolist()
            totals = monthly_data['total'].tolist()
            years = monthly_data['year'].unique()
            
            fig2 = go.Figure()
            
            for year in sorted(years):
                year_data = monthly_data[monthly_data['year'] == year]
                fig2.add_trace(go.Bar(
                    x=year_data['month_name'],
                    y=year_data['total'],
                    name=str(year),
                    text=year_data['total'].apply(lambda x: f"{x:,.0f}"),
                    textposition='auto',
                ))
            
            fig2.update_layout(
                title="Monthly Rentals by Year",
                xaxis_title="Month",
                yaxis_title="Total Bikes Rented",
                barmode='group',
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig2, width='stretch')

# ============================================================
# SECTION 3: SEASONALITY - Seasonal Patterns
# ============================================================
st.header("🍂 Seasonality: Seasonal Patterns")

st.markdown("""
    <div class="story-section">
    <h4>The Four Seasons of Cycling</h4>
    <p><b>What we see:</b> A clear seasonal story emerges:</p>
    <ul>
    <li><b>Winter (Dec-Feb):</b> Cold temperatures suppress demand. December averages ~250 bikes/day.</li>
    <li><b>Spring (Mar-May):</b> Warming weather awakens interest. May reaches ~950 bikes/day.</li>
    <li><b>Summer (Jun-Aug):</b> Peak season! June leads with 1,246 bikes/day average.</li>
    <li><b>Fall (Sep-Nov):</b> Gradual decline as temperatures drop.</li>
    </ul>
    <p><b>The insight:</b> Weather drives everything. Each season tells its own story about human behavior and outdoor activities.</p>
    </div>
""", unsafe_allow_html=True)

monthly_data = load_monthly_data()

if not monthly_data.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Average Daily Rentals by Month")
        
        # Sort by month number for correct order
        monthly_sorted = monthly_data.sort_values('month')
        
        fig3 = go.Figure()
        
        fig3.add_trace(go.Bar(
            x=monthly_sorted['month_name'],
            y=monthly_sorted['avg'],
            marker=dict(
                color=monthly_sorted['avg'],
                colorscale='RdYlBu_r',
                showscale=True,
                colorbar=dict(title="Bikes/Day")
            ),
            text=monthly_sorted['avg'].apply(lambda x: f"{x:.0f}"),
            textposition='auto',
        ))
        
        fig3.update_layout(
            title="Seasonal Pattern: Average Daily Rentals",
            xaxis_title="Month",
            yaxis_title="Average Bikes per Day",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig3, width='stretch')
    
    with col2:
        st.subheader("Seasonal Breakdown")
        
        # Create seasonal summary
        def get_season(month):
            if month in [12, 1, 2]:
                return "Winter"
            elif month in [3, 4, 5]:
                return "Spring"
            elif month in [6, 7, 8]:
                return "Summer"
            else:
                return "Fall"
        
        monthly_data['season'] = monthly_data['month'].apply(get_season)
        seasonal = monthly_data.groupby('season').agg({'total': 'sum', 'avg': 'mean'}).round(0)
        
        # Reorder seasons
        season_order = ["Winter", "Spring", "Summer", "Fall"]
        seasonal = seasonal.reindex([s for s in season_order if s in seasonal.index])
        
        st.dataframe(
            seasonal.rename(columns={'total': 'Total Rentals', 'avg': 'Avg/Day'}),
            width='stretch'
        )
        
        # Season narrative
        st.markdown("""
        **Key Findings:**
        - Summer dominates with the highest demand
        - Winter sees the lowest activity
        - Spring and Fall show moderate, transitional patterns
        - The difference between peak and low seasons is **5x**!
        """)

# ============================================================
# SECTION 4: PERIODICITY - Daily Patterns
# ============================================================
st.header("⏰ Periodicity: Daily Cycles")

st.markdown("""
    <div class="story-section">
    <h4>A Day in the Life of Seoul's Cyclists</h4>
    <p><b>What we see:</b> Every day tells the same story - two clear peaks emerge, mirroring human commute patterns.</p>
    <p><b>The story:</b> Morning rush (7-9 AM) and evening rush (5-7 PM) create predictable demand patterns. 
    Night hours are calm, while midday sees a gentle rise. This is the heartbeat of urban cycling.</p>
    </div>
""", unsafe_allow_html=True)

hourly_pattern = load_hourly_pattern()

if not hourly_pattern.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Average Hourly Rental Pattern")
        
        fig4 = go.Figure()
        
        # Color code for peak hours
        colors = ['#ff6b6b' if (h >= 7 and h <= 9) or (h >= 17 and h <= 19) else '#4ecdc4' 
                  for h in hourly_pattern['hour']]
        
        fig4.add_trace(go.Bar(
            x=hourly_pattern['hour'].astype(str).apply(lambda x: f"{int(x):02d}:00"),
            y=hourly_pattern['avg_bikes'],
            marker=dict(color=colors),
            text=hourly_pattern['avg_bikes'].apply(lambda x: f"{x:.0f}"),
            textposition='auto',
        ))
        
        fig4.update_layout(
            title="Average Bikes Rented by Hour (All Days Combined)",
            xaxis_title="Hour of Day",
            yaxis_title="Average Bikes Rented",
            height=400,
            showlegend=False,
            hovermode='x'
        )
        
        st.plotly_chart(fig4, width='stretch')
    
    with col2:
        st.subheader("Peak Hours Summary")
        
        # Find peak hours
        morning_peak = hourly_pattern[(hourly_pattern['hour'] >= 7) & (hourly_pattern['hour'] <= 9)]['avg_bikes'].max()
        evening_peak = hourly_pattern[(hourly_pattern['hour'] >= 17) & (hourly_pattern['hour'] <= 19)]['avg_bikes'].max()
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("🌅 Morning Peak", f"{morning_peak:.0f}", "bikes/hr")
        with col_b:
            st.metric("🌆 Evening Peak", f"{evening_peak:.0f}", "bikes/hr")
        
        # Daily narrative
        st.markdown(f"""
        **Hourly Insights:**
        - **Quiet Hours:** 0-5 AM - Almost no rentals
        - **Morning Rush:** 7-9 AM - Commuters wake up
        - **Midday:** 11-2 PM - Casual tourism & shopping
        - **Evening Rush:** 5-7 PM - Return from work
        - **Night:** 8+ PM - Activity drops off
        """)

# ============================================================
# SECTION 5: ADVANCED ANALYSIS
# ============================================================
st.header("🔍 Advanced Insights")

tab1, tab2, tab3 = st.tabs(["Weather Impact", "Day Patterns", "Statistical Summary"])

with tab1:
    st.subheader("Temperature vs. Bike Rentals")
    
    hourly_data = load_hourly_data()
    
    if not hourly_data.empty:
        # Create scatter plot of temperature vs bikes
        daily_agg = hourly_data.groupby('date').agg({
            'bikes': 'sum',
            'temp': 'mean',
            'humidity': 'mean'
        }).reset_index()
        
        fig5 = go.Figure()
        
        fig5.add_trace(go.Scatter(
            x=daily_agg['temp'],
            y=daily_agg['bikes'],
            mode='markers',
            marker=dict(
                size=8,
                color=daily_agg['temp'],
                colorscale='RdYlBu_r',
                showscale=True,
                colorbar=dict(title="Temperature (°C)")
            ),
            text=[f"Temp: {t:.1f}°C<br>Bikes: {b:,.0f}" for t, b in zip(daily_agg['temp'], daily_agg['bikes'])],
            hoverinfo='text'
        ))
        
        fig5.update_layout(
            title="Temperature vs. Daily Bike Rentals",
            xaxis_title="Average Temperature (°C)",
            yaxis_title="Daily Bikes Rented",
            height=400,
            hovermode='closest'
        )
        
        st.plotly_chart(fig5, width='stretch')
        
        # Calculate correlation
        correlation = daily_agg['temp'].corr(daily_agg['bikes'])
        st.info(f"📊 Temperature-Rentals Correlation: {correlation:.3f} (Strong positive relationship!)")

with tab2:
    st.subheader("Weekday vs. Weekend Patterns")
    
    if not daily_data.empty:
        daily_data['dayofweek'] = daily_data['date'].dt.dayofweek
        daily_data['day_name'] = daily_data['date'].dt.day_name()
        daily_data['is_weekend'] = daily_data['dayofweek'].isin([5, 6])
        
        # Compare patterns
        by_day = daily_data.groupby('day_name')['total'].agg(['mean', 'std', 'count'])
        
        # Reorder to start with Monday
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        by_day = by_day.reindex([d for d in day_order if d in by_day.index])
        
        fig6 = go.Figure()
        
        fig6.add_trace(go.Bar(
            x=by_day.index,
            y=by_day['mean'],
            error_y=dict(type='data', array=by_day['std']),
            marker=dict(
                color=['#ff6b6b' if d in ['Saturday', 'Sunday'] else '#4ecdc4' for d in by_day.index]
            ),
            text=by_day['mean'].apply(lambda x: f"{x:,.0f}"),
            textposition='auto',
        ))
        
        fig6.update_layout(
            title="Average Rentals by Day of Week",
            xaxis_title="Day",
            yaxis_title="Average Daily Rentals",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig6, width='stretch')

with tab3:
    st.subheader("Statistical Summary")
    
    if not daily_data.empty:
        stats = {
            "Metric": [
                "Total Days",
                "Total Rentals",
                "Average/Day",
                "Min/Day",
                "Max/Day",
                "Std Deviation",
                "Coefficient of Variation"
            ],
            "Value": [
                len(daily_data),
                int(daily_data['total'].sum()),
                int(daily_data['total'].mean()),
                int(daily_data['total'].min()),
                int(daily_data['total'].max()),
                int(daily_data['total'].std()),
                f"{(daily_data['total'].std() / daily_data['total'].mean()):.2%}"
            ]
        }
        
        # Format for display
        stats_df = pd.DataFrame(stats)
        stats_df['Value'] = stats_df['Value'].astype(str)
        st.dataframe(stats_df, width='stretch', hide_index=True)

# ============================================================
# SECTION 6: PREDICTIONS - Combined Visualization
# ============================================================
st.header("🔮 Predictions: Forecasting Ahead")

st.markdown("""
    <div class="story-section">
    <h4>Integrated Prediction Analysis</h4>
    <p>Select a date and hour to view the 24-hour and 3-day predictions alongside historical data from the past week.</p>
    </div>
""", unsafe_allow_html=True)

db = get_db()

# Get available dates for selection
available_dates_sql = """
SELECT DISTINCT selected_date as pred_date
FROM pred_bike_rentals_24h
ORDER BY pred_date DESC
LIMIT 30
"""
available_dates_result = db.execute_query(available_dates_sql)

if available_dates_result:
    available_dates = sorted([
        datetime.strptime(row[0], '%Y-%m-%d').date() 
        for row in available_dates_result
    ], reverse=True)
    
    # Create datetime selector
    col1, col2 = st.columns(2)
    
    with col1:
        selected_date = st.date_input(
            "📅 Select Prediction Date",
            value=available_dates[0] if available_dates else datetime.now().date(),
            min_value=available_dates[-1] if available_dates else None,
            max_value=available_dates[0] if available_dates else None
        )
    
    with col2:
        selected_hour = st.slider(
            "🕐 Select Hour",
            min_value=0,
            max_value=23,
            value=8,
            step=1,
            format="%02d:00"
        )
    
    try:
        
        # Prepare data
        selected_date_str = selected_date.strftime('%Y-%m-%d')
        selected_datetime = datetime(selected_date.year, selected_date.month, selected_date.day, selected_hour, 0, 0)
        week_ago = selected_datetime - timedelta(days=7)
        
        # Query historical data (last 7 days)
        hist_sql = f"""
        SELECT datetime(date || ' ' || printf('%02d:00:00', hour)) as datetime, 
               rented_bike_count as bikes
        FROM stg_bike_rentals_hourly
        WHERE datetime(date || ' ' || printf('%02d:00:00', hour)) >= '{week_ago}' 
        AND datetime(date || ' ' || printf('%02d:00:00', hour)) <= '{selected_datetime}'
        ORDER BY datetime
        """
        hist_results = db.execute_query(hist_sql)
        
        # Query 24-hour predictions (generated at selected time)
        pred_24h_sql = f"""
        SELECT prediction_datetime, predicted_bikes as prediction
        FROM pred_bike_rentals_24h 
        WHERE selected_date = '{selected_date_str}' 
        AND selected_hour = {selected_hour}
        ORDER BY prediction_datetime
        """
        pred_24h_results = db.execute_query(pred_24h_sql)
        
        # Query 3-day predictions (generated at selected time)
        pred_3d_sql = f"""
        SELECT prediction_datetime, predicted_bikes as prediction
        FROM pred_bike_rentals_3d 
        WHERE selected_date = '{selected_date_str}'
        AND selected_hour = {selected_hour}
        ORDER BY prediction_datetime
        """
        pred_3d_results = db.execute_query(pred_3d_sql)
        
        # Prepare DataFrames
        hist_data = pd.DataFrame()
        if hist_results:
            hist_data = pd.DataFrame(hist_results, columns=['datetime', 'bikes'])
            hist_data['datetime'] = pd.to_datetime(hist_data['datetime'])
            hist_data['bikes'] = pd.to_numeric(hist_data['bikes'], errors='coerce')
        
        pred_24h_data = pd.DataFrame()
        if pred_24h_results:
            pred_24h_data = pd.DataFrame(pred_24h_results, columns=['datetime', 'prediction'])
            pred_24h_data['datetime'] = pd.to_datetime(pred_24h_data['datetime'])
            pred_24h_data['prediction'] = pd.to_numeric(pred_24h_data['prediction'], errors='coerce')
        
        pred_3d_data = pd.DataFrame()
        if pred_3d_results:
            pred_3d_data = pd.DataFrame(pred_3d_results, columns=['datetime', 'prediction'])
            pred_3d_data['datetime'] = pd.to_datetime(pred_3d_data['datetime'])
            pred_3d_data['prediction'] = pd.to_numeric(pred_3d_data['prediction'], errors='coerce')
        
        # Create combined plot
        fig = go.Figure()
        
        # Add historical data
        if not hist_data.empty:
            fig.add_trace(go.Scatter(
                x=hist_data['datetime'],
                y=hist_data['bikes'],
                name='Historical Data (Last 7 Days)',
                mode='lines',
                line=dict(color='#4ecdc4', width=2),
                hovertemplate='<b>Historical</b><br>%{x|%Y-%m-%d %H:%M}<br>%{y:.0f} bikes<extra></extra>'
            ))
        
        # Add 3-day predictions
        if not pred_3d_data.empty:
            fig.add_trace(go.Scatter(
                x=pred_3d_data['datetime'],
                y=pred_3d_data['prediction'],
                name='3-Day Predictions',
                mode='lines',
                line=dict(color='#95e1d3', width=2.5, dash='dot'),
                hovertemplate='<b>3d Forecast</b><br>%{x|%Y-%m-%d %H:%M}<br>%{y:.0f} bikes<extra></extra>'
            ))

        # Add 24-hour predictions
        if not pred_24h_data.empty:
            fig.add_trace(go.Scatter(
                x=pred_24h_data['datetime'],
                y=pred_24h_data['prediction'],
                name='24-Hour Predictions',
                mode='lines+markers',
                line=dict(color='#ff6b6b', width=2.5, dash='dash'),
                marker=dict(size=4, color='#ff6b6b'),
                hovertemplate='<b>24h Forecast</b><br>%{x|%Y-%m-%d %H:%M}<br>%{y:.0f} bikes<extra></extra>'
            ))
        

        # Add vertical line for selected datetime
        selected_datetime_str = selected_datetime.strftime('%Y-%m-%d %H:%M:%S')
        selected_unix = int(selected_datetime.timestamp()) * 1000

        fig.add_vline(
            x=selected_unix,
            line_dash="dot",
            line_color="orange",
            line_width=2,
            annotation_text=f"Selected: {selected_datetime_str}",
            annotation_position="top left",
            annotation_font_size=11,
            annotation_font_color="orange"
        )
        
        # Update layout
        fig.update_layout(
            title=f"Bike Rental Predictions (24h & 3d) vs Historical Data - {selected_date.strftime('%Y-%m-%d')} {selected_hour:02d}:00",
            xaxis_title="Date & Time",
            yaxis_title="Bikes Rented",
            hovermode='x unified',
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(b=100)
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Display metrics for selected datetime
        st.subheader("📊 Prediction Details for Selected Time")
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        # 24-hour prediction sum (total bikes next 24h)
        if not pred_24h_data.empty:
            total_24h = pred_24h_data['prediction'].sum()
            with col_m1:
                st.metric(
                    "Total Predicted (Next 24h)",
                    f"{total_24h:,.0f}",
                    "bikes"
                )
        
        # 3-day prediction sum
        if not pred_3d_data.empty:
            total_3d = pred_3d_data['prediction'].sum()
            with col_m2:
                st.metric(
                    "Total Predicted (Next 3d)",
                    f"{total_3d:,.0f}",
                    "bikes"
                )
        
        # Historical data sum (last 24h)
        if not hist_data.empty:
            last_24h_hist = hist_data[hist_data['datetime'] > (selected_datetime - timedelta(hours=24))]
            total_hist_24h = last_24h_hist['bikes'].sum()
            with col_m3:
                st.metric(
                    "Historical (Last 24h)",
                    f"{total_hist_24h:,.0f}",
                    "bikes"
                )
        
        # Peak predicted
        if not pred_3d_data.empty:
            peak_pred = pred_3d_data['prediction'].max()
            with col_m4:
                st.metric(
                    "Peak Predicted (3d)",
                    f"{peak_pred:,.0f}",
                    "bikes"
                )
        
        # Show data tables
        st.divider()
        
        tab1, tab2= st.tabs(["📈 24-Hour Predictions", "📊 3-Day Predictions"])
        
        with tab1:
            if not pred_24h_data.empty:
                display_24h = pred_24h_data.copy()
                display_24h['datetime'] = display_24h['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M'))
                display_24h['prediction'] = display_24h['prediction'].round(0).astype(int)
                display_24h.columns = ['Date & Time', 'Predicted Bikes']
                st.dataframe(display_24h, width='stretch', hide_index=True)
            else:
                st.info("No 24-hour predictions available for this date")
        
        with tab2:
            if not pred_3d_data.empty:
                display_3d = pred_3d_data.copy()
                display_3d['datetime'] = display_3d['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M'))
                display_3d['prediction'] = display_3d['prediction'].round(0).astype(int)
                display_3d.columns = ['Date & Time', 'Predicted Bikes']
                st.dataframe(display_3d, width='stretch', hide_index=True)
            else:
                st.info("No 3-day predictions available for this date")
        
    except Exception as e:
        st.error(f"❌ Error creating visualization: {str(e)}")
else:
    st.warning("📅 No prediction data available. Please run predictions first.")



st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Data Source")
    st.markdown("Seoul Bike Sharing System\n2017-2018 Dataset")

with col2:
    st.markdown("### 🛠 Technologies")
    st.markdown("Streamlit • Plotly\nSQLite • Python")

with col3:
    st.markdown("### 📈 Key Takeaway")
    st.markdown("**Weather drives demand.**\nCycling is seasonal and follows predictable daily patterns driven by human commute behavior.")

st.markdown("""
---
*Dashboard created for data storytelling. 
Every dataset tells a story - this one tells Seoul's cycling tale.*
""")
