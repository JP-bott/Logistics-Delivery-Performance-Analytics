"""Shared shipment feature engineering and filters."""
import pandas as pd

def prepare_shipments(frame):
    df=frame.copy()
    for c in ["Shipment_Date","Dispatch_Date","Expected_Delivery_Date","Actual_Delivery_Date"]:
        df[c]=pd.to_datetime(df[c],errors="coerce")
    df["Delivered"]=df.Delivery_Status.eq("Delivered")
    df["Resolved"]=df.Delivery_Status.isin(["Delivered","Failed","Returned"])
    df["Delivery_Days"]=(df.Actual_Delivery_Date-df.Dispatch_Date).dt.total_seconds()/86400
    df["On_Time"]=df.Delivered & df.Actual_Delivery_Date.le(df.Expected_Delivery_Date)
    df["Late"]=df.Delivered & ~df.On_Time
    df["Delay_Days"]=(df.Actual_Delivery_Date-df.Expected_Delivery_Date).dt.days.clip(lower=0).where(df.Delivered)
    df["First_Attempt"]=df.Delivered & df.Delivery_Attempts.eq(1)
    df["Month"]=df.Shipment_Date.dt.to_period("M").dt.to_timestamp()
    df["Route"]=df.Origin_Region+" → "+df.Destination_Region
    return df

def filter_shipments(df,dates=None,regions=None,couriers=None,statuses=None,services=None):
    result=df
    if dates and len(dates)==2:
        result=result[result.Shipment_Date.dt.date.between(*dates)]
    for field,values in [("Destination_Region",regions),("Courier_ID",couriers),("Delivery_Status",statuses),("Service_Type",services)]:
        if values: result=result[result[field].isin(values)]
    return result.copy()
