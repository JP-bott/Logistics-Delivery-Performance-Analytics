"""Point-based analysis; no invented geographic polygons."""
import geopandas as gpd
from pyproj import Geod
WGS84=Geod(ellps="WGS84")

def geodesic_km(a,b,c,d):
    return abs(WGS84.inv(b,a,d,c)[2])/1000

def destination_points(df):
    g=df.groupby(["Destination_Region","Destination_Province","Destination_City","Destination_Latitude","Destination_Longitude"],as_index=False).agg(shipments=("Shipment_ID","size"),on_time=("On_Time","sum"),delivered=("Delivered","sum"))
    g["on_time_rate"]=g.apply(lambda r:100*r.on_time/r.delivered if r.delivered else 0,axis=1)
    return gpd.GeoDataFrame(g,geometry=gpd.points_from_xy(g.Destination_Longitude,g.Destination_Latitude),crs="EPSG:4326")

def route_flows(df):
    return df.groupby(["Hub_Name","Origin_Latitude","Origin_Longitude","Destination_City","Destination_Latitude","Destination_Longitude"],as_index=False).size().rename(columns={"size":"shipments"}).sort_values("shipments",ascending=False)
