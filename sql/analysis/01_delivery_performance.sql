-- Total shipment outcomes and the resolved-denominator success rate.
SELECT COUNT(*) shipments,SUM(Delivery_Status='Delivered') delivered,
ROUND(100.0*SUM(Delivery_Status='Delivered')/NULLIF(SUM(Delivery_Status IN ('Delivered','Failed','Returned')),0),2) success_pct,
ROUND(AVG(CASE WHEN Delivery_Status='Delivered' THEN JULIANDAY(Actual_Delivery_Date)-JULIANDAY(Dispatch_Date) END),2) avg_delivery_days FROM shipments;
SELECT SUBSTR(Shipment_Date,1,7) month,COUNT(*) shipments FROM shipments GROUP BY month ORDER BY month;
