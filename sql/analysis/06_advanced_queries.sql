-- Month-on-month regional throughput with LAG.
WITH monthly AS (SELECT Destination_Region region,SUBSTR(Shipment_Date,1,7) month,COUNT(*) n FROM shipments GROUP BY region,month)
SELECT region,month,n,LAG(n) OVER(PARTITION BY region ORDER BY month) prev_volume FROM monthly;
-- Regional corridor ranking using multiple joins, window functions and a CTE.
WITH corridors AS (SELECT h.Region origin,s.Destination_Region destination,COUNT(*) volume,
ROUND(AVG(s.Shipping_Cost_PHP),2) cost FROM shipments s JOIN hubs h ON s.Origin_Hub_ID=h.Hub_ID GROUP BY origin,destination)
SELECT *,ROW_NUMBER() OVER(PARTITION BY origin ORDER BY volume DESC) volume_rank,
RANK() OVER(ORDER BY cost DESC) cost_rank FROM corridors;
-- Vehicle outcome mix.
SELECT c.Vehicle_Type,COUNT(*) assigned,SUM(s.Delivery_Status='Delivered') delivered,
SUM(CASE WHEN s.Delivery_Status='Failed' THEN 1 ELSE 0 END) failed
FROM shipments s JOIN couriers c ON s.Courier_ID=c.Courier_ID GROUP BY c.Vehicle_Type;
