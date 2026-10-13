-- 1. Impact of Late Deliveries on Customer Review Scores
WITH delivery_performance AS (
    SELECT 
        o.order_id,
        r.review_score,
        JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_estimated_delivery_date) AS delay_days,
        CASE 
            WHEN JULIANDAY(o.order_delivered_customer_date) > JULIANDAY(o.order_estimated_delivery_date) THEN 'Late'
            ELSE 'On-Time/Early'
        END AS delivery_status
    FROM orders o
    JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
)
SELECT 
    delivery_status,
    COUNT(order_id) AS total_orders,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(AVG(CASE WHEN delay_days > 0 THEN delay_days ELSE 0 END), 1) AS avg_delay_days
FROM delivery_performance
GROUP BY delivery_status;

-- 2. Monthly Revenue and Order Volume Trends
SELECT 
    STRFTIME('%Y-%m', o.order_purchase_timestamp) AS year_month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(p.payment_value), 2) AS total_revenue
FROM orders o
JOIN order_payments p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY year_month
ORDER BY year_month ASC;


