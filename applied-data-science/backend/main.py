from __future__ import annotations

import json
import math
from datetime import datetime, timedelta
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

try:
    from db import DB_PATH, row, rows, scalar
except ModuleNotFoundError:
    from backend.db import DB_PATH, row, rows, scalar


app = FastAPI(title="Seoul Bike Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def strip_deployment_prefix(request, call_next):
    path = request.scope.get("path", "")
    if path in {
        "/health",
        "/date-range",
        "/overview",
        "/trends",
        "/seasonality",
        "/periodicity",
        "/clusters",
        "/correlations",
        "/forecast/options",
        "/forecast",
        "/model-summary",
        "/debug",
    }:
        request.scope["path"] = f"/api{path}"
        request.scope["raw_path"] = request.scope["path"].encode()
    return await call_next(request)


def season_for_month(month: int) -> str:
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Fall"


def date_filter(column: str, start_date: str | None, end_date: str | None) -> tuple[str, list[Any]]:
    clauses = []
    params: list[Any] = []
    if start_date:
        clauses.append(f"{column} >= ?")
        params.append(start_date)
    if end_date:
        clauses.append(f"{column} <= ?")
        params.append(end_date)
    return (" WHERE " + " AND ".join(clauses), params) if clauses else ("", params)


def and_date_filter(column: str, start_date: str | None, end_date: str | None) -> tuple[str, list[Any]]:
    where, params = date_filter(column, start_date, end_date)
    return (where.replace(" WHERE ", " AND ", 1), params) if where else ("", params)


def pearson(items: list[dict], x_key: str, y_key: str) -> float | None:
    pairs = [
        (float(item[x_key]), float(item[y_key]))
        for item in items
        if item.get(x_key) is not None and item.get(y_key) is not None
    ]
    if len(pairs) < 2:
        return None
    xs, ys = zip(*pairs)
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
    denominator_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    denominator_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if denominator_x == 0 or denominator_y == 0:
        return None
    return numerator / (denominator_x * denominator_y)


def slope(items: list[dict], x_key: str, y_key: str) -> float | None:
    pairs = [
        (float(item[x_key]), float(item[y_key]))
        for item in items
        if item.get(x_key) is not None and item.get(y_key) is not None
    ]
    if len(pairs) < 2:
        return None
    xs, ys = zip(*pairs)
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    if denominator == 0:
        return None
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
    return numerator / denominator


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/debug")
def debug() -> dict:
    table_count = None
    daily_count = None
    error = None
    try:
        table_count = scalar("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table'")
        daily_count = scalar("SELECT COUNT(*) FROM fact_bike_rentals_daily")
    except Exception as exc:
        error = str(exc)
    return {
        "status": "ok" if error is None else "error",
        "db_path": str(DB_PATH),
        "db_exists": DB_PATH.exists(),
        "db_size": DB_PATH.stat().st_size if DB_PATH.exists() else 0,
        "table_count": table_count,
        "daily_count": daily_count,
        "error": error,
    }


@app.get("/api/date-range")
def date_range() -> dict:
    result = row("SELECT MIN(date) AS start_date, MAX(date) AS end_date FROM fact_bike_rentals_daily") or {}
    return result


@app.get("/api/overview")
def overview(start_date: str | None = None, end_date: str | None = None) -> dict:
    where, params = date_filter("date", start_date, end_date)
    summary = row(
        f"""
        SELECT
            SUM(total_bike_count) AS total_rentals,
            AVG(total_bike_count) AS daily_average,
            MIN(date) AS start_date,
            MAX(date) AS end_date,
            COUNT(*) AS total_days
        FROM fact_bike_rentals_daily
        {where}
        """,
        tuple(params),
    ) or {}
    peak_day = row(
        f"""
        SELECT date, total_bike_count
        FROM fact_bike_rentals_daily
        {where}
        ORDER BY total_bike_count DESC
        LIMIT 1
        """,
        tuple(params),
    )
    hourly_where, hourly_params = date_filter("date", start_date, end_date)
    peak_month = row(
        f"""
        SELECT
            CAST(strftime('%Y', date) AS INTEGER) AS year,
            CAST(strftime('%m', date) AS INTEGER) AS month,
            CASE CAST(strftime('%m', date) AS INTEGER)
                WHEN 1 THEN 'January'
                WHEN 2 THEN 'February'
                WHEN 3 THEN 'March'
                WHEN 4 THEN 'April'
                WHEN 5 THEN 'May'
                WHEN 6 THEN 'June'
                WHEN 7 THEN 'July'
                WHEN 8 THEN 'August'
                WHEN 9 THEN 'September'
                WHEN 10 THEN 'October'
                WHEN 11 THEN 'November'
                ELSE 'December'
            END AS month_name,
            SUM(rented_bike_count) AS total_bike_count
        FROM stg_bike_rentals_hourly
        {hourly_where}
        GROUP BY year, month
        ORDER BY total_bike_count DESC
        LIMIT 1
        """,
        tuple(hourly_params),
    )
    temperature = row(
        f"""
        SELECT
            AVG(temperature) AS avg_temperature,
            AVG(humidity) AS avg_humidity,
            SUM(rainfall) AS total_rainfall
        FROM stg_bike_rentals_hourly
        {hourly_where}
        """,
        tuple(hourly_params),
    )
    return {
        "summary": summary,
        "peak_day": peak_day,
        "peak_month": peak_month,
        "weather": temperature,
    }


@app.get("/api/trends")
def trends(start_date: str | None = None, end_date: str | None = None) -> dict:
    where, params = date_filter("date", start_date, end_date)
    daily = rows(
        f"""
        SELECT
            date,
            total_bike_count AS total,
            avg_bike_count AS average,
            AVG(total_bike_count) OVER (
                ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ) AS moving_average_7d
        FROM fact_bike_rentals_daily
        {where}
        ORDER BY date
        """,
        tuple(params),
    )
    weekly_where = []
    weekly_params: list[Any] = []
    if start_date:
        weekly_where.append("end_date >= ?")
        weekly_params.append(start_date)
    if end_date:
        weekly_where.append("start_date <= ?")
        weekly_params.append(end_date)
    weekly_clause = " WHERE " + " AND ".join(weekly_where) if weekly_where else ""
    weekly = rows(
        f"""
        SELECT year, week, start_date, end_date, total_bike_count AS total
        FROM fact_bike_rentals_weekly
        {weekly_clause}
        ORDER BY year, week
        """,
        tuple(weekly_params),
    )
    daily_where, daily_params = date_filter("date", start_date, end_date)
    monthly = rows(
        f"""
        SELECT
            CAST(strftime('%Y', date) AS INTEGER) AS year,
            CAST(strftime('%m', date) AS INTEGER) AS month,
            CASE CAST(strftime('%m', date) AS INTEGER)
                WHEN 1 THEN 'January'
                WHEN 2 THEN 'February'
                WHEN 3 THEN 'March'
                WHEN 4 THEN 'April'
                WHEN 5 THEN 'May'
                WHEN 6 THEN 'June'
                WHEN 7 THEN 'July'
                WHEN 8 THEN 'August'
                WHEN 9 THEN 'September'
                WHEN 10 THEN 'October'
                WHEN 11 THEN 'November'
                ELSE 'December'
            END AS month_name,
            SUM(total_bike_count) AS total,
            AVG(avg_bike_count) AS average
        FROM fact_bike_rentals_daily
        {daily_where}
        GROUP BY year, month
        ORDER BY year, month
        """,
        tuple(daily_params),
    )
    return {"daily": daily, "weekly": weekly, "monthly": monthly}


@app.get("/api/seasonality")
def seasonality(start_date: str | None = None, end_date: str | None = None) -> dict:
    daily_where, daily_params = date_filter("date", start_date, end_date)
    monthly = rows(
        f"""
        SELECT
            CAST(strftime('%Y', date) AS INTEGER) AS year,
            CAST(strftime('%m', date) AS INTEGER) AS month,
            CASE CAST(strftime('%m', date) AS INTEGER)
                WHEN 1 THEN 'January'
                WHEN 2 THEN 'February'
                WHEN 3 THEN 'March'
                WHEN 4 THEN 'April'
                WHEN 5 THEN 'May'
                WHEN 6 THEN 'June'
                WHEN 7 THEN 'July'
                WHEN 8 THEN 'August'
                WHEN 9 THEN 'September'
                WHEN 10 THEN 'October'
                WHEN 11 THEN 'November'
                ELSE 'December'
            END AS month_name,
            SUM(total_bike_count) AS total,
            AVG(avg_bike_count) AS average
        FROM fact_bike_rentals_daily
        {daily_where}
        GROUP BY year, month
        ORDER BY year, month
        """,
        tuple(daily_params),
    )
    seasonal_map: dict[str, dict] = {}
    for item in monthly:
        season = season_for_month(int(item["month"]))
        entry = seasonal_map.setdefault(season, {"season": season, "total": 0, "average_values": [], "months": 0})
        entry["total"] += item["total"] or 0
        entry["average_values"].append(item["average"] or 0)
        entry["months"] += 1

    order = ["Winter", "Spring", "Summer", "Fall"]
    seasonal = []
    for season in order:
        entry = seasonal_map.get(season)
        if not entry:
            continue
        values = entry.pop("average_values")
        entry["average"] = round(sum(values) / len(values), 2) if values else 0
        seasonal.append(entry)

    hourly_where, hourly_params = date_filter("date", start_date, end_date)
    weather = rows(
        f"""
        SELECT
            seasons AS season,
            ROUND(AVG(rented_bike_count), 2) AS avg_hourly_rentals,
            ROUND(AVG(temperature), 2) AS avg_temperature,
            ROUND(AVG(humidity), 2) AS avg_humidity
        FROM stg_bike_rentals_hourly
        {hourly_where}
        GROUP BY seasons
        ORDER BY avg_hourly_rentals DESC
        """,
        tuple(hourly_params),
    )
    join_filter, join_params = and_date_filter("d.date", start_date, end_date)
    daily_weather = rows(
        f"""
        SELECT
            d.date,
            d.total_bike_count AS total,
            ROUND(AVG(h.temperature), 2) AS avg_temperature,
            ROUND(AVG(h.humidity), 2) AS avg_humidity,
            SUM(h.rainfall) AS rainfall,
            MAX(h.seasons) AS season
        FROM fact_bike_rentals_daily d
        JOIN stg_bike_rentals_hourly h ON h.date = d.date
        WHERE 1 = 1
        {join_filter}
        GROUP BY d.date, d.total_bike_count
        ORDER BY d.date
        """,
        tuple(join_params),
    )
    bin_filter, bin_params = and_date_filter("d.date", start_date, end_date)
    temperature_bins = rows(
        f"""
        WITH daily_weather AS (
            SELECT
                d.date,
                d.total_bike_count,
                AVG(h.temperature) AS avg_temperature
            FROM fact_bike_rentals_daily d
            JOIN stg_bike_rentals_hourly h ON h.date = d.date
            WHERE 1 = 1
            {bin_filter}
            GROUP BY d.date, d.total_bike_count
        )
        SELECT
            CASE
                WHEN avg_temperature < 0 THEN '< 0 C'
                WHEN avg_temperature < 10 THEN '0-10 C'
                WHEN avg_temperature < 20 THEN '10-20 C'
                WHEN avg_temperature < 30 THEN '20-30 C'
                ELSE '30+ C'
            END AS bin,
            ROUND(AVG(total_bike_count), 2) AS avg_daily_total,
            COUNT(*) AS days
        FROM daily_weather
        GROUP BY bin
        ORDER BY MIN(avg_temperature)
        """,
        tuple(bin_params),
    )
    return {"monthly": monthly, "seasonal": seasonal, "weather": weather, "daily_weather": daily_weather, "temperature_bins": temperature_bins}


@app.get("/api/periodicity")
def periodicity(start_date: str | None = None, end_date: str | None = None) -> dict:
    hourly_where, hourly_params = date_filter("date", start_date, end_date)
    hourly = rows(
        f"""
        SELECT
            hour,
            ROUND(AVG(rented_bike_count), 2) AS avg_bikes,
            MAX(rented_bike_count) AS max_bikes
        FROM stg_bike_rentals_hourly
        {hourly_where}
        GROUP BY hour
        ORDER BY hour
        """,
        tuple(hourly_params),
    )
    daily_where, daily_params = date_filter("date", start_date, end_date)
    weekday = rows(
        f"""
        SELECT
            CASE CAST(strftime('%w', date) AS INTEGER)
                WHEN 0 THEN 'Sunday'
                WHEN 1 THEN 'Monday'
                WHEN 2 THEN 'Tuesday'
                WHEN 3 THEN 'Wednesday'
                WHEN 4 THEN 'Thursday'
                WHEN 5 THEN 'Friday'
                ELSE 'Saturday'
            END AS day_name,
            CAST(strftime('%w', date) AS INTEGER) AS day_number,
            ROUND(AVG(total_bike_count), 2) AS avg_total
        FROM fact_bike_rentals_daily
        {daily_where}
        GROUP BY day_number
        ORDER BY CASE day_number
            WHEN 1 THEN 1
            WHEN 2 THEN 2
            WHEN 3 THEN 3
            WHEN 4 THEN 4
            WHEN 5 THEN 5
            WHEN 6 THEN 6
            ELSE 7
        END
        """,
        tuple(daily_params),
    )
    heatmap = rows(
        f"""
        SELECT
            CASE CAST(strftime('%w', date) AS INTEGER)
                WHEN 0 THEN 'Sunday'
                WHEN 1 THEN 'Monday'
                WHEN 2 THEN 'Tuesday'
                WHEN 3 THEN 'Wednesday'
                WHEN 4 THEN 'Thursday'
                WHEN 5 THEN 'Friday'
                ELSE 'Saturday'
            END AS day_name,
            CAST(strftime('%w', date) AS INTEGER) AS day_number,
            hour,
            ROUND(AVG(rented_bike_count), 2) AS avg_bikes
        FROM stg_bike_rentals_hourly
        {hourly_where}
        GROUP BY day_number, hour
        ORDER BY CASE day_number
            WHEN 1 THEN 1
            WHEN 2 THEN 2
            WHEN 3 THEN 3
            WHEN 4 THEN 4
            WHEN 5 THEN 5
            WHEN 6 THEN 6
            ELSE 7
        END, hour
        """,
        tuple(hourly_params),
    )
    dayparts = rows(
        f"""
        SELECT
            CASE
                WHEN hour BETWEEN 0 AND 5 THEN 'Overnight'
                WHEN hour BETWEEN 6 AND 10 THEN 'Morning'
                WHEN hour BETWEEN 11 AND 15 THEN 'Midday'
                WHEN hour BETWEEN 16 AND 20 THEN 'Evening'
                ELSE 'Late night'
            END AS daypart,
            ROUND(AVG(rented_bike_count), 2) AS avg_bikes
        FROM stg_bike_rentals_hourly
        {hourly_where}
        GROUP BY daypart
        ORDER BY CASE daypart
            WHEN 'Overnight' THEN 1
            WHEN 'Morning' THEN 2
            WHEN 'Midday' THEN 3
            WHEN 'Evening' THEN 4
            ELSE 5
        END
        """,
        tuple(hourly_params),
    )
    return {"hourly": hourly, "weekday": weekday, "heatmap": heatmap, "dayparts": dayparts}


@app.get("/api/clusters")
def clusters(start_date: str | None = None, end_date: str | None = None) -> dict:
    profiles = rows(
        """
        SELECT
            cluster_id,
            cluster_name,
            description,
            day_count,
            avg_daily_total,
            weekend_share,
            holiday_share,
            peak_hour,
            hourly_profile_json
        FROM analysis_cluster_profiles
        ORDER BY cluster_id
        """
    )
    for profile in profiles:
        profile["hourly_profile"] = json.loads(profile.pop("hourly_profile_json"))

    cluster_filter, cluster_params = date_filter("date", start_date, end_date)
    season_mix = rows(
        f"""
        SELECT cluster_id, season, COUNT(*) AS days
        FROM analysis_day_clusters
        {cluster_filter}
        GROUP BY cluster_id, season
        ORDER BY cluster_id, season
        """,
        tuple(cluster_params),
    )
    examples = rows(
        f"""
        SELECT date, cluster_id, cluster_name, daily_total, weekday, holiday, season
        FROM analysis_day_clusters
        {cluster_filter}
        ORDER BY distance_score ASC
        LIMIT 12
        """,
        tuple(cluster_params),
    )
    weekday_mix = rows(
        f"""
        SELECT cluster_id, weekday, COUNT(*) AS days
        FROM analysis_day_clusters
        {cluster_filter}
        GROUP BY cluster_id, weekday
        ORDER BY cluster_id, weekday
        """,
        tuple(cluster_params),
    )
    return {"profiles": profiles, "season_mix": season_mix, "weekday_mix": weekday_mix, "examples": examples}


@app.get("/api/correlations")
def correlations(start_date: str | None = None, end_date: str | None = None) -> dict:
    where, params = date_filter("date", start_date, end_date)
    items = rows(
        f"""
        SELECT
            rented_bike_count,
            hour,
            temperature,
            humidity,
            wind_speed,
            visibility,
            dew_point_temperature,
            solar_radiation,
            rainfall,
            snowfall,
            seasons AS season
        FROM stg_bike_rentals_hourly
        {where}
        """,
        tuple(params),
    )
    feature_labels = {
        "hour": "Hour",
        "temperature": "Temperature",
        "humidity": "Humidity",
        "wind_speed": "Wind speed",
        "visibility": "Visibility",
        "dew_point_temperature": "Dew point",
        "solar_radiation": "Solar radiation",
        "rainfall": "Rainfall",
        "snowfall": "Snowfall",
    }
    result = []
    for key, label in feature_labels.items():
        coefficient = pearson(items, key, "rented_bike_count")
        if coefficient is None:
            continue
        sensitivity = slope(items, key, "rented_bike_count")
        result.append(
            {
                "feature": key,
                "label": label,
                "correlation": round(coefficient, 4),
                "absolute": round(abs(coefficient), 4),
                "sensitivity": round(sensitivity, 2) if sensitivity is not None else None,
                "direction": "positive" if coefficient >= 0 else "negative",
            }
        )
    result.sort(key=lambda item: item["absolute"], reverse=True)
    return {"correlations": result, "samples": items, "rows": len(items)}


@app.get("/api/forecast/options")
def forecast_options() -> dict:
    dates = rows(
        """
        SELECT DISTINCT selected_date AS date
        FROM pred_bike_rentals_24h
        ORDER BY selected_date
        """
    )
    hours = rows(
        """
        SELECT DISTINCT selected_hour AS hour
        FROM pred_bike_rentals_24h
        ORDER BY selected_hour
        """
    )
    default = row(
        """
        SELECT selected_date AS date, selected_hour AS hour
        FROM pred_bike_rentals_24h
        WHERE selected_date = '2018-11-22' AND selected_hour = 8
        LIMIT 1
        """
    ) or row(
        """
        SELECT selected_date AS date, selected_hour AS hour
        FROM pred_bike_rentals_24h
        ORDER BY selected_date, selected_hour
        LIMIT 1
        """
    )
    return {"dates": [item["date"] for item in dates], "hours": [item["hour"] for item in hours], "default": default}


@app.get("/api/forecast")
def forecast(
    date: str = Query("2018-11-22", pattern=r"^\d{4}-\d{2}-\d{2}$"),
    hour: int = Query(8, ge=0, le=23),
) -> dict:
    selected = datetime.strptime(f"{date} {hour:02d}:00:00", "%Y-%m-%d %H:%M:%S")
    week_ago = selected - timedelta(days=7)
    selected_string = selected.strftime("%Y-%m-%d %H:%M:%S")
    week_ago_string = week_ago.strftime("%Y-%m-%d %H:%M:%S")

    historical = rows(
        """
        SELECT
            datetime(date || ' ' || printf('%02d:00:00', hour)) AS datetime,
            rented_bike_count AS bikes
        FROM stg_bike_rentals_hourly
        WHERE datetime(date || ' ' || printf('%02d:00:00', hour)) >= ?
          AND datetime(date || ' ' || printf('%02d:00:00', hour)) <= ?
        ORDER BY datetime
        """,
        (week_ago_string, selected_string),
    )
    pred_24h = rows(
        """
        SELECT prediction_datetime AS datetime, predicted_bikes AS bikes
        FROM pred_bike_rentals_24h
        WHERE selected_date = ? AND selected_hour = ?
        ORDER BY prediction_datetime
        """,
        (date, hour),
    )
    pred_3d = rows(
        """
        SELECT prediction_datetime AS datetime, predicted_bikes AS bikes
        FROM pred_bike_rentals_3d
        WHERE selected_date = ? AND selected_hour = ?
        ORDER BY prediction_datetime
        """,
        (date, hour),
    )

    actual_future = rows(
        """
        SELECT
            datetime(date || ' ' || printf('%02d:00:00', hour)) AS datetime,
            rented_bike_count AS bikes
        FROM stg_bike_rentals_hourly
        WHERE datetime(date || ' ' || printf('%02d:00:00', hour)) > ?
          AND datetime(date || ' ' || printf('%02d:00:00', hour)) <= datetime(?, '+3 days')
        ORDER BY datetime
        """,
        (selected_string, selected_string),
    )

    def total(items: list[dict]) -> float:
        return round(sum((item.get("bikes") or 0) for item in items), 2)

    metrics = {
        "predicted_24h_total": total(pred_24h),
        "predicted_3d_total": total(pred_3d),
        "historical_24h_total": total(historical[-24:]),
        "peak_predicted_3d": round(max((item.get("bikes") or 0) for item in pred_3d), 2) if pred_3d else 0,
    }
    actual_by_time = {item["datetime"]: item["bikes"] for item in actual_future}
    comparison = []
    for item in pred_3d:
        actual = actual_by_time.get(item["datetime"])
        if actual is None:
            continue
        predicted = item["bikes"] or 0
        comparison.append(
            {
                "datetime": item["datetime"],
                "actual": actual,
                "predicted": predicted,
                "error": predicted - actual,
                "absolute_error": abs(predicted - actual),
            }
        )
    if comparison:
        metrics["overlap_hours"] = len(comparison)
        metrics["mae_3d_overlap"] = round(sum(item["absolute_error"] for item in comparison) / len(comparison), 2)
        metrics["bias_3d_overlap"] = round(sum(item["error"] for item in comparison) / len(comparison), 2)
        metrics["actual_3d_total_overlap"] = round(sum(item["actual"] for item in comparison), 2)
    return {
        "selected": {"date": date, "hour": hour, "datetime": selected_string},
        "historical": historical,
        "prediction_24h": pred_24h,
        "prediction_3d": pred_3d,
        "actual_future": actual_future,
        "comparison": comparison,
        "metrics": metrics,
    }


@app.get("/api/model-summary")
def model_summary() -> dict:
    metrics = rows(
        """
        SELECT model_name, forecast_type, r_squared, rmse, rmsle, mape
        FROM analysis_model_metrics
        ORDER BY r_squared DESC
        """
    )
    return {"metrics": metrics}


for path, endpoint in [
    ("/health", health),
    ("/debug", debug),
    ("/date-range", date_range),
    ("/overview", overview),
    ("/trends", trends),
    ("/seasonality", seasonality),
    ("/periodicity", periodicity),
    ("/clusters", clusters),
    ("/correlations", correlations),
    ("/forecast/options", forecast_options),
    ("/forecast", forecast),
    ("/model-summary", model_summary),
]:
    app.add_api_route(path, endpoint, methods=["GET"], include_in_schema=False)
