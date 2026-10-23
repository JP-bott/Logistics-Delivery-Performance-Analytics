"""Load local SQLite facts and dimensions."""
import sqlite3
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
DB_PATH=ROOT/"database"/"logistics_analytics.db"
def read_table(name):
    if name not in {"hubs","couriers","sla_rules","shipments","delivery_events"}:raise ValueError("Invalid table")
    with sqlite3.connect(DB_PATH) as c:
        return pd.read_sql_query("SELECT * FROM "+name,c)
def read_shipments():
    with sqlite3.connect(DB_PATH) as c:
        return pd.read_sql_query("""SELECT s.*, c.Courier_Name,c.Courier_Type,c.Vehicle_Type,c.Assigned_Region,
          h.Hub_Name,h.Region AS Origin_Region,h.Latitude AS Origin_Latitude,
          h.Longitude AS Origin_Longitude
          FROM shipments s JOIN couriers c ON s.Courier_ID=c.Courier_ID
          JOIN hubs h ON s.Origin_Hub_ID=h.Hub_ID""",c)
