import pandas as pd
import sqlite3
import uuid

def load_csv_to_sqlite(uploaded_file):
    unique_id = uuid.uuid4().hex[:8]
    original_name = uploaded_file.name.replace(".csv", "").replace(" - ", "_").replace(" ", "_").replace("-", "_")
    db_name = f"{original_name}_{unique_id}.db"
    df = pd.read_csv(uploaded_file, encoding='latin1')
    
    # detect and convert date columns to ISO format
    for col in df.columns:
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
                print(f"Converted date column: {col}")
            except:
                pass
    
    conn = sqlite3.connect(db_name)
    df.to_sql(original_name, conn, if_exists="replace", index=False)
    conn.close()
    print(f"Total rows imported: {len(df)}")
    return db_name