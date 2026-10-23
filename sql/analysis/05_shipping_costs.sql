-- Costs across delivery services and distance bands.
SELECT Service_Type,COUNT(*) shipments,ROUND(SUM(Shipping_Cost_PHP),2) total_php,
ROUND(AVG(Shipping_Cost_PHP),2) avg_php FROM shipments GROUP BY Service_Type;
SELECT CASE WHEN Distance_KM<50 THEN '<50' WHEN Distance_KM<200 THEN '50-199' WHEN Distance_KM<500 THEN '200-499' ELSE '500+' END distance_band,
COUNT(*) shipments,ROUND(AVG(Shipping_Cost_PHP),2) avg_php FROM shipments GROUP BY distance_band ORDER BY avg_php;
