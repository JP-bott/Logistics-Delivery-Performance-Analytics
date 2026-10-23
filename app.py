"""NexRoute | Logistics Intelligence. Streamlit operations control tower."""
from datetime import date
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.database import read_shipments,read_table,DB_PATH
from src.data_processing import prepare_shipments,filter_shipments
from src.delivery_metrics import overview,grouped_performance
from src.sla_analysis import sla_summary,pareto
from src.geospatial_analysis import destination_points,route_flows
from src.visualizations import theme,bars,COLORS

st.set_page_config(page_title="NexRoute | Logistics Intelligence",page_icon="◈",layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=IBM+Plex+Mono:wght@600&display=swap');
.stApp{background:#0B1420;color:#E8EEF5;font-family:Inter,Arial}
[data-testid="stSidebar"]{background:#111F2E;border-right:1px solid #29394B}
[data-testid="stMetric"]{background:#172738;border:1px solid #29394B;padding:17px;border-radius:5px}
[data-testid="stMetricValue"]{font-family:IBM Plex Mono,monospace;color:#E8EEF5;font-size:1.5rem}
[data-testid="stMetricLabel"]{color:#95A7B8;text-transform:uppercase;letter-spacing:1px;font-size:11px}
.block-container{padding-top:25px;max-width:1540px}
h1,h2,h3{letter-spacing:-.03em}
</style>""",unsafe_allow_html=True)
@st.cache_data
def load():
    return prepare_shipments(read_shipments()),read_table("hubs"),read_table("delivery_events")
if not DB_PATH.exists():
    st.error("First create the database: python scripts/generate_data.py && python scripts/load_database.py")
    st.stop()
all_data,hubs,events=load()
with st.sidebar:
    st.markdown("### ◈ NEXROUTE")
    st.caption("LOGISTICS INTELLIGENCE / CONTROL TOWER")
    page=st.radio("WORKSPACES",["Operations Overview","Geographic Delivery Analysis","Courier Performance","SLA & Delay Analytics","Shipping Cost Analysis","Shipment Explorer"])
    st.divider()
    dates=st.date_input("Date range",(date(2024,1,1),date(2025,12,31)),min_value=date(2024,1,1),max_value=date(2025,12,31))
    regions=st.multiselect("Destination region",sorted(all_data.Destination_Region.unique()))
    services=st.multiselect("Service type",sorted(all_data.Service_Type.unique()))
    statuses=st.multiselect("Delivery status",sorted(all_data.Delivery_Status.unique()))
    couriers=st.multiselect("Courier ID",sorted(all_data.Courier_ID.unique()))
    st.divider()
    st.caption("SYNTHETIC DATA · 2024–2025\n\nREPORTING CUTOFF · DEC 31, 2025")
df=filter_shipments(all_data,dates if len(dates)==2 else None,regions,couriers,statuses,services)
st.caption(f"NEXROUTE / {page.upper()} / {len(df):,} SELECTED SHIPMENTS")
st.title(page)
st.caption("Fictional company and modeled logistics operations across Philippine cities.")

def chart(fig):
    st.plotly_chart(theme(fig),use_container_width=True,config={"displaylogo":False})
def cards(items):
    for start in range(0,len(items),4):
        for col,(name,value) in zip(st.columns(4),items[start:start+4]):
            col.metric(name,value)
def amount(x,prefix="",suffix="",digits=1):
    return "—" if pd.isna(x) else prefix+f"{x:,.{digits}f}"+suffix
def no_data():
    st.info("No records match the selected filters.")
if df.empty:
    no_data()
elif page=="Operations Overview":
    k=overview(df)
    cards([("Total shipments",f'{k["shipments"]:,}'),("Delivered",f'{k["delivered"]:,}'),("Success rate",amount(k["success_rate"],suffix="%")),("On-time delivery",amount(k["on_time_rate"],suffix="%")),
           ("Avg delivery days",amount(k["avg_delivery_days"],suffix=" d")),("Average cost",amount(k["avg_cost"],prefix="₱")),("Failed rate",amount(k["failed_rate"],suffix="%")),("First-attempt success",amount(k["first_attempt_rate"],suffix="%"))])
    freq=st.radio("Shipment volume aggregation",["Daily","Weekly","Monthly"],index=2,horizontal=True)
    trend=df.set_index("Shipment_Date").resample({"Daily":"D","Weekly":"W","Monthly":"MS"}[freq]).size().rename("Shipments").reset_index()
    trend["Rolling average"]=trend.Shipments.rolling(7,min_periods=1).mean()
    a,b=st.columns([1.65,1])
    with a:chart(px.line(trend,x="Shipment_Date",y=["Shipments","Rolling average"],title="Shipment volume & rolling mean",color_discrete_sequence=COLORS))
    with b:chart(px.bar(df.Delivery_Status.value_counts().reset_index(),x="count",y="Delivery_Status",orientation="h",title="Delivery status mix",color_discrete_sequence=COLORS))
    done=df[df.Delivered]
    rate=done.groupby("Month",as_index=False).On_Time.mean()
    rate["On-time %"]=rate.On_Time*100
    a,b=st.columns(2)
    with a:chart(px.line(rate,x="Month",y="On-time %",title="Monthly on-time delivery"))
    with b:
        matrix=done.pivot_table(index="Destination_Region",columns="Month",values="On_Time",aggfunc="mean")*100
        matrix.columns=matrix.columns.strftime("%b %y")
        chart(px.imshow(matrix,aspect="auto",color_continuous_scale="Viridis",title="Regional SLA heatmap"))
    if df.Month.nunique()>1:
        months=sorted(df.Month.unique());first,last=months[0],months[-1]
        services_list=sorted(df.Service_Type.unique())
        start=int(df.loc[df.Month.eq(first),"On_Time"].sum())
        delta=[int(df.loc[df.Month.eq(last)&df.Service_Type.eq(s),"On_Time"].sum()-df.loc[df.Month.eq(first)&df.Service_Type.eq(s),"On_Time"].sum()) for s in services_list]
        wf=go.Figure(go.Waterfall(x=["First month"]+services_list+["Last month"],measure=["absolute"]+["relative"]*len(delta)+["total"],y=[start]+delta+[0]))
        chart(wf)
        st.caption("Waterfall exactly decomposes the first-to-last selected month change in on-time delivery counts by service.")
    st.caption("Success = Delivered / resolved (Delivered + Failed + Returned). On-time = on-time delivered / delivered. Cancelled and unresolved parcels are excluded from resolved rates.")
elif page=="Geographic Delivery Analysis":
    points=destination_points(df)
    mode=st.radio("Geographic view",["Shipment density","On-time performance","Origin-destination flows"],horizontal=True)
    fig=go.Figure()
    fig.update_geos(scope="asia",projection_type="mercator",showland=True,landcolor="#1A3044",showocean=True,oceancolor="#0B1420",showcoastlines=True,coastlinecolor="#40566B",lataxis_range=[4,21],lonaxis_range=[116,127])
    if mode=="Origin-destination flows":
        flows=route_flows(df).head(30)
        for row in flows.itertuples():
            fig.add_trace(go.Scattergeo(lon=[row.Origin_Longitude,row.Destination_Longitude],lat=[row.Origin_Latitude,row.Destination_Latitude],mode="lines",name=f"{row.Hub_Name} → {row.Destination_City}",showlegend=False,line=dict(color="#4C9AFF",width=max(1,5*row.shipments/max(1,flows.shipments.max())))))
    else:
        column="shipments" if mode=="Shipment density" else "on_time_rate"
        fig.add_trace(go.Scattergeo(lon=points.Destination_Longitude,lat=points.Destination_Latitude,text=points.Destination_City,mode="markers",marker=dict(size=(8+22*np.sqrt(points.shipments/points.shipments.max())),color=points[column],colorscale="Viridis",showscale=True,opacity=.85),name="Destinations"))
    active=hubs[hubs.Hub_ID.isin(df.Origin_Hub_ID.unique())]
    fig.add_trace(go.Scattergeo(lon=active.Longitude,lat=active.Latitude,text=active.Hub_Name,mode="markers",marker=dict(symbol="diamond",size=9,color="#2DD4BF"),name="Hubs"))
    chart(fig)
    st.caption("Markers are city-center points; lines indicate aggregate corridors, NOT road routes. Distances are straight-line WGS84 geodesics. No fabricated administrative polygons.")
    a,b=st.columns(2)
    by=grouped_performance(df,"Destination_Region")
    with a:chart(bars(by,"Destination_Region","shipments","Shipments by region"))
    with b:chart(bars(by,"Destination_Region","avg_cost","Mean cost by region"))
    st.dataframe(by.round(2),hide_index=True,use_container_width=True)
elif page=="Courier Performance":
    g=grouped_performance(df,["Courier_ID","Courier_Name","Assigned_Region","Vehicle_Type"])
    minimum=st.slider("Minimum completed shipments",10,500,75)
    score=st.selectbox("Ranking metric",["on_time_rate","success_rate","first_attempt_rate","avg_days"])
    qualified=g[g.delivered>=minimum]
    a,b=st.columns(2)
    with a:chart(bars(qualified.nlargest(15,score),"Courier_Name",score,"Courier ranking"))
    with b:chart(px.scatter(qualified,x="delivered",y="avg_days",size="shipments",color="on_time_rate",hover_name="Courier_Name",title="Courier efficiency"))
    if not qualified.empty:
        selected=st.multiselect("Compare couriers (up to 5)",qualified.Courier_ID.tolist(),default=qualified.Courier_ID.head(3).tolist(),max_selections=5)
        cmp=qualified[qualified.Courier_ID.isin(selected)].melt(id_vars="Courier_Name",value_vars=["on_time_rate","success_rate","first_attempt_rate"],var_name="KPI",value_name="Percent")
        if not cmp.empty:chart(px.bar(cmp,x="Courier_Name",y="Percent",color="KPI",barmode="group",title="Courier KPI comparison"))
    chart(px.box(df[df.Delivered],x="Vehicle_Type",y="Delivery_Days",points=False,title="Delivery days by vehicle"))
    st.dataframe(g.round(2),hide_index=True,use_container_width=True)
elif page=="SLA & Delay Analytics":
    k=sla_summary(df)
    cards([("SLA compliance",amount(k["sla_rate"],suffix="%")),("Late deliveries",f'{k["late_count"]:,}'),("Avg days late",amount(k["avg_delay"])),("Median days",amount(k["median_days"])),("P90 days",amount(k["p90_days"])),("First attempt",amount(k["first_attempt"],suffix="%"))])
    done=df[df.Delivered]
    a,b=st.columns(2)
    with a:chart(px.histogram(done[done.Late],x="Delay_Days",title="Delivery delay distribution"))
    with b:
        matrix=done.pivot_table(index="Destination_Region",columns="Service_Type",values="On_Time",aggfunc="mean")*100
        chart(px.imshow(matrix,title="Service × region SLA",color_continuous_scale="Viridis"))
    a,b=st.columns(2)
    with a:chart(px.box(done,x="Service_Type",y="Delivery_Days",title="Delivery duration by service"))
    with b:
        reasons=df[df.Delivery_Status.isin(["Failed","Returned"])].Failure_Reason.value_counts().reset_index()
        chart(px.bar(reasons,x="count",y="Failure_Reason",orientation="h",title="Failure reasons"))
    p=pareto(df)
    if not p.empty:
        fig=go.Figure([go.Bar(x=p.Destination_Region,y=p.breaches,name="Breach count"),go.Scatter(x=p.Destination_Region,y=p.cumulative_percent,yaxis="y2",name="Cumulative %")])
        fig.update_layout(yaxis2=dict(overlaying="y",side="right",range=[0,105]))
        chart(fig)
    st.caption("Late delivery is classified only for Delivered shipments, when actual date exceeds promised date.")
elif page=="Shipping Cost Analysis":
    delivered=df[df.Delivered]
    cards([("Total shipping cost",amount(df.Shipping_Cost_PHP.sum(),prefix="₱",digits=0)),("Cost per shipment",amount(df.Shipping_Cost_PHP.mean(),prefix="₱")),("Cost per delivered",amount(delivered.Shipping_Cost_PHP.mean(),prefix="₱")),("Cost per geodesic km",amount(df.Shipping_Cost_PHP.sum()/max(1,df.Distance_KM.sum()),prefix="₱"))])
    by=grouped_performance(df,"Destination_Region")
    a,b=st.columns(2)
    with a:
        monthly=df.groupby("Month",as_index=False).Shipping_Cost_PHP.sum()
        chart(px.area(monthly,x="Month",y="Shipping_Cost_PHP",title="Monthly shipping cost"))
    with b:chart(bars(by,"Destination_Region","avg_cost","Average cost by region"))
    a,b=st.columns(2)
    with a:chart(px.scatter(df.sample(min(len(df),3000),random_state=42),x="Distance_KM",y="Shipping_Cost_PHP",color="Service_Type",title="Distance / cost relationship"))
    with b:chart(px.box(df,x="Vehicle_Type",y="Shipping_Cost_PHP",title="Cost by vehicle"))
    chart(px.scatter(by,x="avg_cost",y="success_rate",size="shipments",color="on_time_rate",hover_name="Destination_Region",title="Cost-efficiency matrix"))
    chart(bars(grouped_performance(df,"Route").nlargest(12,"avg_cost"),"Route","avg_cost","Highest modeled cost corridors"))
    st.caption("Costs are simulated, not commercial Philippine courier rates. Straight-line geodesics are not road distance; correlation does not establish causality.")
else:
    text=st.text_input("Search shipment ID").upper().strip()
    found=df[df.Shipment_ID.str.contains(text,regex=False)] if text else df
    columns=["Shipment_ID","Courier_Name","Hub_Name","Destination_City","Service_Type","Shipment_Date","Expected_Delivery_Date","Actual_Delivery_Date","Delivery_Status","Delivery_Days","On_Time","Shipping_Cost_PHP"]
    st.dataframe(found[columns],hide_index=True,use_container_width=True,height=450)
    st.download_button("Export filtered shipments CSV",found.to_csv(index=False).encode("utf-8"),file_name="nexroute_filtered_shipments.csv",mime="text/csv")
    if not found.empty:
        chosen=st.selectbox("Shipment timeline",found.Shipment_ID.head(1000).tolist())
        for event in events[events.Shipment_ID.eq(chosen)].sort_values("Event_DateTime").itertuples():
            st.markdown(f"**{event.Event_Type}** · {event.Event_DateTime}  \n{event.Event_Description}")
