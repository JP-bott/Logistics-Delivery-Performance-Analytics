"""NexRoute reproducible synthetic Philippine logistics events."""
import csv
from pathlib import Path
from datetime import date,datetime,timedelta
import numpy as np
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/"data"/"raw"
RAW.mkdir(parents=True,exist_ok=True)
RNG=np.random.default_rng(20261107)
CITIES=[
 ("NCR","Metro Manila","Quezon City",14.676,121.0437,18),
 ("NCR","Metro Manila","Manila",14.5995,120.9842,11),
 ("NCR","Metro Manila","Pasig",14.5764,121.0851,10),
 ("NCR","Metro Manila","Taguig",14.5176,121.0509,10),
 ("NCR","Metro Manila","Makati",14.5547,121.0244,7),
 ("NCR","Metro Manila","Caloocan",14.6507,120.9668,6),
 ("Central Luzon","Bulacan","Malolos",14.8433,120.8114,6),
 ("Central Luzon","Bulacan","Meycauayan",14.736,120.96,5),
 ("Central Luzon","Pampanga","San Fernando",15.0285,120.6898,5),
 ("Central Luzon","Pampanga","Angeles",15.145,120.5887,4),
 ("CALABARZON","Cavite","Bacoor",14.4624,120.9645,6),
 ("CALABARZON","Cavite","Dasmariñas",14.3294,120.9367,5),
 ("CALABARZON","Laguna","Santa Rosa",14.3122,121.1114,6),
 ("CALABARZON","Laguna","Calamba",14.2117,121.1653,5),
 ("CALABARZON","Rizal","Antipolo",14.6255,121.1245,6),
 ("CALABARZON","Rizal","Cainta",14.5786,121.1222,4),
 ("CALABARZON","Batangas","Batangas City",13.7565,121.0583,4),
 ("CALABARZON","Batangas","Lipa",13.9411,121.1622,4),
 ("Central Visayas","Cebu","Cebu City",10.3157,123.8854,7),
 ("Central Visayas","Cebu","Mandaue",10.3236,123.9225,4),
 ("Central Visayas","Cebu","Lapu-Lapu City",10.3103,123.9494,3),
 ("Western Visayas","Iloilo","Iloilo City",10.7202,122.5621,5),
 ("Western Visayas","Iloilo","Pavia",10.7758,122.5453,2),
 ("Davao Region","Davao del Sur","Davao City",7.0731,125.6128,7)
]
HUBS=[
 ("H01","Quezon City Hub","NCR","Metro Manila","Quezon City",14.676,121.0437,"Primary"),
 ("H02","Pasig Distribution Center","NCR","Metro Manila","Pasig",14.5764,121.0851,"Sorting"),
 ("H03","Manila Central Hub","NCR","Metro Manila","Manila",14.5995,120.9842,"Primary"),
 ("H04","Bulacan Sorting Facility","Central Luzon","Bulacan","Malolos",14.8433,120.8114,"Sorting"),
 ("H05","Pampanga Regional Hub","Central Luzon","Pampanga","San Fernando",15.0285,120.6898,"Regional"),
 ("H06","Cavite Delivery Hub","CALABARZON","Cavite","Dasmariñas",14.3294,120.9367,"Delivery"),
 ("H07","Laguna Delivery Hub","CALABARZON","Laguna","Calamba",14.2117,121.1653,"Delivery"),
 ("H08","Rizal Delivery Hub","CALABARZON","Rizal","Antipolo",14.6255,121.1245,"Delivery"),
 ("H09","Batangas Regional Hub","CALABARZON","Batangas","Batangas City",13.7565,121.0583,"Regional"),
 ("H10","Cebu Distribution Center","Central Visayas","Cebu","Cebu City",10.3157,123.8854,"Regional"),
 ("H11","Iloilo Regional Hub","Western Visayas","Iloilo","Iloilo City",10.7202,122.5621,"Regional"),
 ("H12","Davao Regional Hub","Davao Region","Davao del Sur","Davao City",7.0731,125.6128,"Regional")
]
SERVICES=["Same Day","Express","Standard","Economy"]
BASE_DAYS={"Same Day":0,"Express":1,"Standard":2,"Economy":4}
SERVICE_FACTOR={"Same Day":1.85,"Express":1.55,"Standard":1.0,"Economy":.78}
VEHICLES={"Motorcycle":.88,"Van":1.0,"Light Truck":1.19,"Delivery Truck":1.37}
FAILURES=["Recipient unavailable","Incorrect address","Delivery refused","Weather disruption","Damaged parcel","Access restriction"]
GEO=Geod(ellps="WGS84")
CUTOFF=date(2025,12,31)

def save(filename,columns,rows):
    with (RAW/filename).open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f);w.writerow(columns);w.writerows(rows)

def run(n=26000):
    regions=sorted({x[2] for x in HUBS})
    by_region={r:[h for h in HUBS if h[2]==r] for r in regions}
    couriers=[]
    names=["Santos","Reyes","Cruz","Garcia","Mendoza","Ramos","Bautista","Flores","Navarro","Villanueva"]
    first=["Alex","Jamie","Morgan","Taylor","Casey","Jordan","Riley","Avery","Sam","Drew"]
    c_by_region={r:[] for r in regions}
    for i in range(60):
        r=regions[i%len(regions)]
        vehicle=str(RNG.choice(list(VEHICLES),p=[.55,.31,.11,.03]))
        cid=f"C{i+1:03}"
        couriers.append((cid,f"{first[i%len(first)]} {names[(i//len(first))%len(names)]} {i+1:02}","Partner" if i%4==0 else "In-House",r,"Active",vehicle,"2023-01-01"))
        c_by_region[r].append((cid,vehicle))
    save("couriers.csv",["Courier_ID","Courier_Name","Courier_Type","Assigned_Region","Employment_Status","Vehicle_Type","Start_Date"],couriers)
    save("hubs.csv",["Hub_ID","Hub_Name","Region","Province","City","Latitude","Longitude","Hub_Type"],HUBS)
    rules=[];rule_lookup={}
    for o in regions:
        for d in regions:
            for service in SERVICES:
                if service=="Same Day" and o!=d:continue
                days=BASE_DAYS[service]+(0 if service=="Same Day" or o==d else 1 if {o,d}.issubset({"NCR","Central Luzon","CALABARZON"}) else 3)
                sid=f"SLA{len(rules)+1:04}"
                rules.append((sid,service,o,d,days))
                rule_lookup[(o,d,service)]=(sid,days)
    save("sla_rules.csv",["SLA_ID","Service_Type","Origin_Region","Destination_Region","SLA_Days"],rules)
    days=np.arange(np.datetime64("2024-01-01"),np.datetime64("2026-01-01"))
    day_weights=[]
    for x in days:
        d=date.fromisoformat(str(x))
        factor=(.72 if d.weekday()>=5 else 1.0)*(1.28 if d.month in [11,12] else 1)
        day_weights.append(factor*(2.4 if (d.month,d.day) in [(11,11),(12,12),(9,9)] else 1))
    day_weights=np.array(day_weights);day_weights/=day_weights.sum()
    city_weights=np.array([x[5] for x in CITIES],dtype=float);city_weights/=city_weights.sum()
    dates=RNG.choice(days,size=n,p=day_weights)
    shipments=[];events=[]
    def event(s,t,typ,h,desc):
        events.append((f"EV{len(events)+1:07}",s,t.isoformat(timespec="seconds"),typ,h,desc))
    for i in range(n):
        city=CITIES[int(RNG.choice(len(CITIES),p=city_weights))]
        dr,province,cityname,lat,lon,_=city
        origin=dr if RNG.random()<.76 else ("NCR" if RNG.random()<.72 else str(RNG.choice(regions)))
        hub=by_region[origin][int(RNG.integers(len(by_region[origin])))]
        service=str(RNG.choice(SERVICES if origin==dr else SERVICES[1:],p=[.06,.2,.52,.22] if origin==dr else [.24,.54,.22]))
        sid,sla=rule_lookup[(origin,dr,service)]
        cid,vehicle=c_by_region[dr][int(RNG.integers(len(c_by_region[dr])))]
        shipped=date.fromisoformat(str(dates[i]))
        dispatched=min(CUTOFF,shipped+timedelta(days=int(RNG.choice([0,1,2],p=[.64,.34,.02]))))
        promised=dispatched+timedelta(days=sla)
        distance=round(abs(GEO.inv(hub[6],hub[5],lon,lat)[2])/1000,2)
        weight=round(float(np.clip(RNG.lognormal(.1,.83),.08,24)),2)
        island=origin in ["Central Visayas","Western Visayas","Davao Region"] or dr in ["Central Visayas","Western Visayas","Davao Region"]
        cost=round(max(35,(49+distance*(.85 if island else .57)+weight*18)*SERVICE_FACTOR[service]*VEHICLES[vehicle]*float(RNG.uniform(.92,1.08))),2)
        fee=round(cost*float(RNG.uniform(1.16,1.32)),2)
        risk=((int(cid[1:])%10)-4.5)*.004
        failure_rate=max(.018,.045+(.017 if island else 0)+(.012 if shipped.month in [11,12] else 0)+risk)
        random=float(RNG.random())
        status="Delivered";reason="";attempts=1;actual=None
        if random<.011:status="Cancelled";attempts=0
        elif random<.011+failure_rate*.78:status="Failed";attempts=2
        elif random<.011+failure_rate:status="Returned";attempts=2
        if status!="Cancelled":
            late=RNG.random()<(.10+(.07 if island else 0)+(.05 if shipped.month in [11,12] else 0))
            delay=int(RNG.integers(1,4)) if late else 0
            duration=max(0,sla-int(RNG.integers(0,max(1,min(3,sla+1))))+delay)
            outcome=dispatched+timedelta(days=duration)
            if outcome>CUTOFF:status="In Transit";attempts=0
            elif status=="Delivered":
                actual=outcome
                attempts=int(RNG.choice([1,2,3],p=[.88,.105,.015]))
            else:reason=str(RNG.choice(FAILURES,p=[.33,.23,.16,.13,.08,.07]))
        shid=f"NR{i+1:06}"
        shipments.append((shid,f"ORD{i+1:06}",f"CUS{int(RNG.integers(1,5300)):05}",cid,hub[0],dr,province,cityname,lat,lon,shipped.isoformat(),dispatched.isoformat(),promised.isoformat(),actual.isoformat() if actual else "",status,attempts,reason,weight,cost,fee,service,distance,sid))
        received=datetime.combine(shipped,datetime.min.time())+timedelta(hours=7)
        sent=datetime.combine(dispatched,datetime.min.time())+timedelta(hours=11)
        event(shid,received,"Order Received",hub[0],"Shipment registered")
        if status=="Cancelled":
            event(shid,received+timedelta(hours=1),"Order Cancelled",hub[0],"Order cancelled")
            continue
        if sent>received+timedelta(hours=1):event(shid,received+timedelta(hours=1),"Package Picked Up",hub[0],"Package accepted")
        event(shid,sent,"Dispatched",hub[0],"Parcel dispatched from origin")
        if status=="In Transit":
            if dispatched<CUTOFF:event(shid,sent+timedelta(hours=1),"Arrived at Hub",hub[0],"Awaiting onward transit")
            continue
        completed=datetime.combine(outcome,datetime.min.time())+timedelta(hours=16)
        event(shid,completed-timedelta(minutes=40),"Out for Delivery",hub[0],"Courier reached delivery area")
        if attempts>1:event(shid,completed-timedelta(minutes=25),"Delivery Attempted",hub[0],"Earlier delivery attempt unsuccessful")
        event(shid,completed,{"Delivered":"Delivered","Failed":"Failed Delivery","Returned":"Returned to Sender"}[status],hub[0],reason or "Delivered to recipient")
    save("shipments.csv",["Shipment_ID","Order_ID","Customer_ID","Courier_ID","Origin_Hub_ID","Destination_Region","Destination_Province","Destination_City","Destination_Latitude","Destination_Longitude","Shipment_Date","Dispatch_Date","Expected_Delivery_Date","Actual_Delivery_Date","Delivery_Status","Delivery_Attempts","Failure_Reason","Package_Weight_KG","Shipping_Cost_PHP","Delivery_Fee_PHP","Service_Type","Distance_KM","SLA_ID"],shipments)
    save("delivery_events.csv",["Event_ID","Shipment_ID","Event_DateTime","Event_Type","Hub_ID","Event_Description"],events)
    print(f"Created {len(shipments)} shipments, {len(events)} events, {len(couriers)} couriers and {len(rules)} SLA rules.")
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--shipments",type=int,default=26000)
    run(p.parse_args().shipments)
