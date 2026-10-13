import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/retailpulse.db")

def run_analytical_queries():
    conn = sqlite3.connect(DB_PATH)
    
    print("--- 1. DELIVERY DELAY VS REVIEW SCORE IMPACT ---")
    query1 = """
    WITH delivery_performance AS (
        SELECT 
            o.order_id,
            r.review_score,
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
        ROUND(AVG(review_score), 2) AS avg_review_score
    FROM delivery_performance
    GROUP BY delivery_status;
    """
    df1 = pd.read_sql_query(query1, conn)
    print(df1)
    
    conn.close()

if __name__ == "__main__":
    run_analytical_queries()