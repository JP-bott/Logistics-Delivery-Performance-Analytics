"""Operational KPI definitions; excluded cases are explicit."""
def rate(n,d):
    return 100*float(n)/float(d) if d else 0.0

def overview(df):
    done=df[df.Delivered]
    resolved=df[df.Resolved]
    return {"shipments":len(df),"delivered":len(done),
      "success_rate":rate(len(done),len(resolved)),
      "on_time_rate":rate(done.On_Time.sum(),len(done)),
      "failed_rate":rate(df.Delivery_Status.eq("Failed").sum(),len(resolved)),
      "first_attempt_rate":rate(done.First_Attempt.sum(),len(done)),
      "avg_delivery_days":done.Delivery_Days.mean(),
      "avg_cost":df.Shipping_Cost_PHP.mean()}

def grouped_performance(df,field):
    if df.empty:return df.iloc[:0].copy()
    group=df.groupby(field,dropna=False).agg(shipments=("Shipment_ID","size"),delivered=("Delivered","sum"),resolved=("Resolved","sum"),on_time=("On_Time","sum"),first_attempt=("First_Attempt","sum"),avg_days=("Delivery_Days","mean"),avg_cost=("Shipping_Cost_PHP","mean"),total_cost=("Shipping_Cost_PHP","sum"),late=("Late","sum")).reset_index()
    for name,n,d in [("success_rate","delivered","resolved"),("on_time_rate","on_time","delivered"),("first_attempt_rate","first_attempt","delivered")]:
        group[name]=group.apply(lambda r:rate(r[n],r[d]),axis=1)
    return group
