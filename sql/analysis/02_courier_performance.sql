-- Courier ranking for sufficient completed volume.
SELECT c.Courier_Name,c.Assigned_Region,c.Vehicle_Type,COUNT(*) assigned,
SUM(s.Delivery_Status='Delivered') delivered,
ROUND(100.0*SUM(s.Delivery_Status='Delivered')/NULLIF(SUM(s.Delivery_Status IN ('Delivered','Failed','Returned')),0),2) success_pct,
ROUND(100.0*SUM(s.Delivery_Status='Delivered' AND s.Actual_Delivery_Date<=s.Expected_Delivery_Date)/NULLIF(SUM(s.Delivery_Status='Delivered'),0),2) on_time_pct
FROM shipments s JOIN couriers c ON s.Courier_ID=c.Courier_ID GROUP BY c.Courier_ID HAVING delivered>=75 ORDER BY on_time_pct DESC;
