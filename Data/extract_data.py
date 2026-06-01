import pandas as pd
from sqlalchemy import create_engine
import config

engine = create_engine(
    f"postgresql+psycopg2://{config.DB_USER}:{config.DB_PASSWORD}"
    f"@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
)

df = pd.read_sql("""
    SELECT 
        log_id,
        user_id,
        role,
        store_id_accessed,
        query_type,
        execution_time_ms,
        rows_returned,
        queries_in_last_60s,
        EXTRACT(HOUR FROM timestamp) as hour_of_day,
        EXTRACT(DOW FROM timestamp)  as day_of_week,
        is_anomaly,
        anomaly_type
    FROM query_log
    ORDER BY log_id
""", engine)

df.to_csv("query_raw.csv", index=False)
print(f"Saved {len(df):,} rows to query_raw.csv")
print(df.dtypes)