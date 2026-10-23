"""Rebuild SQLite database from raw CSVs."""
from pathlib import Path
import sqlite3
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"database"/"logistics_analytics.db"
def run():
    DB.parent.mkdir(exist_ok=True,parents=True)
    with sqlite3.connect(DB) as con:
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript((ROOT/"sql"/"01_create_tables.sql").read_text())
        for table in ["hubs","couriers","sla_rules","shipments","delivery_events"]:
            data=pd.read_csv(ROOT/"data"/"raw"/f"{table}.csv",keep_default_na=False)
            if table=="shipments":data["Actual_Delivery_Date"]=data["Actual_Delivery_Date"].replace("",None)
            if table=="delivery_events":data["Hub_ID"]=data["Hub_ID"].replace("",None)
            data.to_sql(table,con,if_exists="append",index=False,chunksize=1000)
        con.executescript((ROOT/"sql"/"02_create_indexes.sql").read_text())
        bad=con.execute("PRAGMA foreign_key_check").fetchall()
        if bad:raise ValueError(f"Invalid foreign keys: {bad[:5]}")
        print("Created",DB,"with",con.execute("SELECT COUNT(*) FROM shipments").fetchone()[0],"shipments")
if __name__=="__main__":run()
