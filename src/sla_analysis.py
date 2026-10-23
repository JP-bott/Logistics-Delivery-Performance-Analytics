"""SLA service reporting."""
from src.delivery_metrics import rate

def sla_summary(df):
    done=df[df.Delivered]
    late=done[done.Late]
    return {"sla_rate":rate(done.On_Time.sum(),len(done)),"late_count":len(late),
      "avg_delay":late.Delay_Days.mean(),"median_days":done.Delivery_Days.median(),
      "p90_days":done.Delivery_Days.quantile(.9),
      "first_attempt":rate(done.First_Attempt.sum(),len(done))}

def pareto(df,field="Destination_Region"):
    result=df[df.Late].groupby(field).size().sort_values(ascending=False).rename("breaches").reset_index()
    result["cumulative_percent"]=result.breaches.cumsum()/max(1,result.breaches.sum())*100
    return result
