import sqlite3
from src.database import read_shipments,DB_PATH
from src.data_processing import prepare_shipments
from src.delivery_metrics import overview
def test_kpis():
    df=prepare_shipments(read_shipments())
    assert df.Shipment_ID.is_unique
    assert df.Delivered.sum()>0
    k=overview(df)
    assert abs(k["on_time_rate"]-100*df.On_Time.sum()/df.Delivered.sum())<.001
def test_foreign_keys():
    with sqlite3.connect(DB_PATH) as db:
        assert db.execute("PRAGMA foreign_key_check").fetchall()==[]
