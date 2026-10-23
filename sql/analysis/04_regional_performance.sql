-- Regional operational scorecards.
SELECT Destination_Region,COUNT(*) shipments,SUM(Delivery_Status='Failed') failed,
SUM(Delivery_Status='Delivered' AND Actual_Delivery_Date>Expected_Delivery_Date) late,
ROUND(AVG(Shipping_Cost_PHP),2) avg_cost
FROM shipments GROUP BY Destination_Region ORDER BY shipments DESC;
