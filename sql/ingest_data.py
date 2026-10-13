import sqlite3
import pandas as pd
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "sql" else Path(__file__).resolve().parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
DB_PATH = BASE_DIR / "data" / "retailpulse.db"

# List of CSV files and corresponding table names
files_to_tables = {
    "olist_customers_dataset.csv": "customers",
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv": "product_category_translation"
}

def ingest_data():
    print(f"Connecting to database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    
    for file_name, table_name in files_to_tables.items():
        csv_path = RAW_DATA_DIR / file_name
        if csv_path.exists():
            print(f"Ingesting {file_name} into table '{table_name}'...")
            df = pd.read_csv(csv_path)
            # Write to SQLite
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"  -> Successfully loaded {len(df)} rows.")
        else:
            print(f"  [!] Warning: File {file_name} not found at {csv_path}")

    # Verify ingestion
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\nDatabase Tables Created:")
    for t in tables:
        print(f" - {t[0]}")
        
    conn.close()
    print("\nData ingestion complete!")

if __name__ == "__main__":
    ingest_data()