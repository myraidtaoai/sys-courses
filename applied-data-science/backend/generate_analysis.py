from __future__ import annotations

import json
import math
import re
import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesScalerMeanVariance


ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "database" / "bikes.db"
NOTEBOOK_PATH = ROOT_DIR / "notebooks" / "SeoulBikeMidReport.ipynb"

CLUSTER_META = {
    0: {
        "name": "Low usage days",
        "description": "Lower demand days with flatter hourly shape and weaker commute peaks.",
    },
    1: {
        "name": "Regular commuter days",
        "description": "Weekday-oriented demand with clear morning and evening commute peaks.",
    },
    2: {
        "name": "Weekend and leisure days",
        "description": "Leisure-style demand with later activity and softer morning commute behavior.",
    },
}


def normalize(profile: list[float]) -> list[float]:
    mean = sum(profile) / len(profile)
    variance = sum((value - mean) ** 2 for value in profile) / len(profile)
    std = math.sqrt(variance) or 1.0
    return [(value - mean) / std for value in profile]


def distance(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def time_series_kmeans(profiles: list[list[float]], k: int = 3) -> tuple[list[int], dict[int, list[float]], np.ndarray]:
    """Cluster 24-hour daily demand profiles with DTW TimeSeriesKMeans."""
    series = np.array(profiles, dtype=float)
    scaled = TimeSeriesScalerMeanVariance().fit_transform(series)
    model = TimeSeriesKMeans(n_clusters=k, metric="dtw", random_state=0, n_init=3)
    labels = model.fit_predict(scaled).tolist()
    centers = {
        label: model.cluster_centers_[label].reshape(-1).astype(float).tolist()
        for label in range(k)
    }
    return labels, centers, scaled


def remap_labels(raw_rows: list[dict], labels: list[int]) -> list[int]:
    stats = {}
    for label in sorted(set(labels)):
        members = [row for row, assigned in zip(raw_rows, labels) if assigned == label]
        total = sum(row["daily_total"] for row in members) / len(members)
        weekend_share = sum(row["weekday"] in ("Saturday", "Sunday") or row["holiday"] != "No Holiday" for row in members) / len(members)
        commute = sum(row["commute_share"] for row in members) / len(members)
        stats[label] = {"total": total, "weekend": weekend_share, "commute": commute}

    low_label = min(stats, key=lambda label: stats[label]["total"])
    remaining = [label for label in stats if label != low_label]
    leisure_label = max(remaining, key=lambda label: (stats[label]["weekend"], -stats[label]["commute"]))
    commuter_label = [label for label in remaining if label != leisure_label][0]
    mapping = {low_label: 0, commuter_label: 1, leisure_label: 2}
    return [mapping[label] for label in labels]


def create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS analysis_day_clusters (
            date TEXT PRIMARY KEY,
            cluster_id INTEGER NOT NULL,
            cluster_name TEXT NOT NULL,
            daily_total REAL NOT NULL,
            weekday TEXT NOT NULL,
            holiday TEXT NOT NULL,
            season TEXT NOT NULL,
            distance_score REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS analysis_cluster_profiles (
            cluster_id INTEGER PRIMARY KEY,
            cluster_name TEXT NOT NULL,
            description TEXT NOT NULL,
            day_count INTEGER NOT NULL,
            avg_daily_total REAL NOT NULL,
            weekend_share REAL NOT NULL,
            holiday_share REAL NOT NULL,
            peak_hour INTEGER NOT NULL,
            hourly_profile_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS analysis_model_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            forecast_type TEXT NOT NULL,
            r_squared REAL,
            rmse REAL,
            rmsle REAL,
            mape REAL,
            UNIQUE(model_name, forecast_type)
        );
        """
    )


def load_daily_profiles(conn: sqlite3.Connection) -> list[dict]:
    query = """
        SELECT
            date,
            hour,
            rented_bike_count,
            seasons,
            holiday
        FROM stg_bike_rentals_hourly
        ORDER BY date, hour
    """
    grouped: dict[str, dict] = {}
    for date, hour, count, season, holiday in conn.execute(query):
        item = grouped.setdefault(
            date,
            {
                "date": date,
                "profile": [0.0] * 24,
                "season": season or "Unknown",
                "holiday": holiday or "Unknown",
            },
        )
        item["profile"][int(hour)] = float(count)

    rows = []
    for item in grouped.values():
        parsed = datetime.strptime(item["date"], "%Y-%m-%d")
        daily_total = sum(item["profile"])
        commute_total = sum(item["profile"][hour] for hour in [7, 8, 9, 17, 18, 19])
        rows.append(
            {
                **item,
                "weekday": parsed.strftime("%A"),
                "daily_total": daily_total,
                "commute_share": commute_total / daily_total if daily_total else 0.0,
            }
        )
    return rows


def populate_clusters(conn: sqlite3.Connection) -> None:
    raw_rows = load_daily_profiles(conn)
    raw_profiles = [row["profile"] for row in raw_rows]
    raw_labels, raw_centers, scaled = time_series_kmeans(raw_profiles)
    labels = remap_labels(raw_rows, raw_labels)
    label_mapping = {raw: mapped for raw, mapped in zip(raw_labels, labels)}
    centers = {label_mapping[raw_label]: center for raw_label, center in raw_centers.items() if raw_label in label_mapping}

    profile_groups: dict[int, list[dict]] = defaultdict(list)
    for row, label, profile in zip(raw_rows, labels, scaled):
        flat_profile = profile.reshape(-1).astype(float).tolist()
        profile_groups[label].append(row)
        row["cluster_id"] = label
        row["distance_score"] = distance(flat_profile, centers[label])

    conn.execute("DELETE FROM analysis_day_clusters")
    conn.execute("DELETE FROM analysis_cluster_profiles")

    for row in raw_rows:
        meta = CLUSTER_META[row["cluster_id"]]
        conn.execute(
            """
            INSERT INTO analysis_day_clusters
            (date, cluster_id, cluster_name, daily_total, weekday, holiday, season, distance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["date"],
                row["cluster_id"],
                meta["name"],
                row["daily_total"],
                row["weekday"],
                row["holiday"],
                row["season"],
                row["distance_score"],
            ),
        )

    for cluster_id, members in sorted(profile_groups.items()):
        meta = CLUSTER_META[cluster_id]
        hourly_profile = [
            {
                "hour": hour,
                "avg_bikes": round(sum(member["profile"][hour] for member in members) / len(members), 2),
            }
            for hour in range(24)
        ]
        avg_daily = sum(member["daily_total"] for member in members) / len(members)
        weekend_share = sum(member["weekday"] in ("Saturday", "Sunday") for member in members) / len(members)
        holiday_share = sum(member["holiday"] != "No Holiday" for member in members) / len(members)
        peak_hour = max(hourly_profile, key=lambda item: item["avg_bikes"])["hour"]
        conn.execute(
            """
            INSERT INTO analysis_cluster_profiles
            (cluster_id, cluster_name, description, day_count, avg_daily_total, weekend_share,
             holiday_share, peak_hour, hourly_profile_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cluster_id,
                meta["name"],
                meta["description"],
                len(members),
                round(avg_daily, 2),
                round(weekend_share, 4),
                round(holiday_share, 4),
                peak_hour,
                json.dumps(hourly_profile),
            ),
        )


def notebook_text() -> str:
    if not NOTEBOOK_PATH.exists():
        return ""
    notebook = json.loads(NOTEBOOK_PATH.read_text())
    chunks = []
    for cell in notebook.get("cells", []):
        for output in cell.get("outputs", []):
            chunks.extend(output.get("text", []))
    return "\n".join(chunks)


def populate_model_metrics(conn: sqlite3.Connection) -> None:
    text = notebook_text()
    metric_matches = re.findall(
        r"Testing R-squared:\s*([0-9.eE+-]+).*?Testing MAPE:\s*([0-9.eE+-]+).*?Tesing RMSE:\s*([0-9.eE+-]+).*?Testing RMSLE:\s*([0-9.eE+-]+)",
        text,
        flags=re.DOTALL,
    )
    defaults = [
        ("Linear Regression", "Next hour", 0.9030906300531152, 150.32961750821426, 1.021624465965804, 1.687516881912534e16),
        ("LightGBM", "Next hour", 0.9695128521134836, 84.31795525336805, 0.7421389769834914, 7193757363292339.0),
    ]
    parsed = []
    for (name, forecast_type, *_), match in zip(defaults, metric_matches):
        r_squared, mape, rmse, rmsle = [float(value) for value in match]
        parsed.append((name, forecast_type, r_squared, rmse, rmsle, mape))
    records = parsed or defaults

    conn.execute("DELETE FROM analysis_model_metrics")
    for record in records:
        conn.execute(
            """
            INSERT INTO analysis_model_metrics
            (model_name, forecast_type, r_squared, rmse, rmsle, mape)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(model_name, forecast_type) DO UPDATE SET
                r_squared = excluded.r_squared,
                rmse = excluded.rmse,
                rmsle = excluded.rmsle,
                mape = excluded.mape
            """,
            record,
        )


def main() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        create_tables(conn)
        populate_clusters(conn)
        populate_model_metrics(conn)
        conn.commit()

        cluster_count = conn.execute("SELECT COUNT(*) FROM analysis_day_clusters").fetchone()[0]
        profile_count = conn.execute("SELECT COUNT(*) FROM analysis_cluster_profiles").fetchone()[0]
        metric_count = conn.execute("SELECT COUNT(*) FROM analysis_model_metrics").fetchone()[0]

    print(f"Inserted {cluster_count} clustered days")
    print(f"Inserted {profile_count} cluster profiles")
    print(f"Inserted {metric_count} model metric rows")


if __name__ == "__main__":
    main()
