"""Consistent Plotly styling."""
import plotly.express as px
import plotly.graph_objects as go
COLORS=["#4C9AFF","#2DD4BF","#F59E0B","#EF4444","#9E8EFF"]
def theme(fig,height=355):
    fig.update_layout(height=height,margin=dict(l=15,r=15,t=42,b=25),paper_bgcolor="#111F2E",plot_bgcolor="#111F2E",font=dict(color="#E8EEF5",family="Inter,Arial"),colorway=COLORS,legend=dict(orientation="h",y=-.25))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#29394B",zeroline=False)
    return fig
def bars(df,label,value,title=""):
    if df.empty:return theme(go.Figure())
    return theme(px.bar(df.sort_values(value),x=value,y=label,orientation="h",title=title,color_discrete_sequence=COLORS))
