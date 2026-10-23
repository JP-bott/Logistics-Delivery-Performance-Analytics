-- SLA compliance on delivered orders only.
SELECT Service_Type,COUNT(*) delivered,
SUM(Actual_Delivery_Date>Expected_Delivery_Date) breaches,
ROUND(100.0*SUM(Actual_Delivery_Date<=Expected_Delivery_Date)/COUNT(*),2) compliance_pct
FROM shipments WHERE Delivery_Status='Delivered' GROUP BY Service_Type ORDER BY compliance_pct;
