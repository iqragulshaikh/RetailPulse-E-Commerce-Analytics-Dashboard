import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

# Path setup: Root is one level up from 'notebooks/'
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "retailpulse.db"
CLEAN_DIR = BASE_DIR / "data" / "cleaned"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

def process_and_export():
    print(f"Connecting to database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    query_master = """
    SELECT 
        o.order_id,
        c.customer_unique_id,
        c.customer_state,
        c.customer_city,
        o.order_purchase_timestamp,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        p.payment_value,
        p.payment_type,
        r.review_score,
        r.review_comment_message,
        i.product_id,
        pt.product_category_name_english AS product_category
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN order_payments p ON o.order_id = p.order_id
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    LEFT JOIN order_items i ON o.order_id = i.order_id
    LEFT JOIN products pr ON i.product_id = pr.product_id
    LEFT JOIN product_category_translation pt ON pr.product_category_name = pt.product_category_name
    WHERE o.order_status = 'delivered';
    """

    df = pd.read_sql_query(query_master, conn)
    conn.close()

    print(f"Loaded {len(df)} rows. Processing data...")

    date_cols = ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    df['actual_delivery_days'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    df['delay_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days
    df['is_late'] = np.where(df['delay_days'] > 0, 1, 0)
    df['delivery_status'] = np.where(df['is_late'] == 1, 'Late', 'On-Time/Early')
    df['product_category'] = df['product_category'].fillna('Unknown')

    master_path = CLEAN_DIR / "cleaned_sales_master.csv"
    df.to_csv(master_path, index=False)
    print(f"SUCCESS: Exported {master_path}")

    # Build cohort retention
    df_cohort = df[['customer_unique_id', 'order_purchase_timestamp']].dropna().copy()
    df_cohort['order_month'] = df_cohort['order_purchase_timestamp'].dt.to_period('M')
    df_cohort['cohort_month'] = df_cohort.groupby('customer_unique_id')['order_purchase_timestamp'] \
                                         .transform('min').dt.to_period('M')

    def get_month_index(df_sub, col):
        return df_sub[col].dt.year * 12 + df_sub[col].dt.month

    order_idx = get_month_index(df_cohort, 'order_month')
    cohort_idx = get_month_index(df_cohort, 'cohort_month')
    df_cohort['cohort_index'] = order_idx - cohort_idx

    cohort_data = df_cohort.groupby(['cohort_month', 'cohort_index'])['customer_unique_id'].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='customer_unique_id')

    cohort_path = CLEAN_DIR / "cohort_retention.csv"
    cohort_pivot.to_csv(cohort_path)
    print(f"SUCCESS: Exported {cohort_path}")

if __name__ == "__main__":
    process_and_export()