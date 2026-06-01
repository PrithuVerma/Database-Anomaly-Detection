import pandas as pd 
import psycopg2 
import matplotlib 
matplotlib.use('Agg') 
import matplotlib.pyplot as plt 
import config
from sqlalchemy import create_engine 

engine = create_engine(
    f"postgresql+psycopg2://{config.DB_USER}:{config.DB_PASSWORD}"
    f"@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
)

df = pd.read_sql("""
    SELECT 
        user_id,
        store_id_accessed,
        query_type,
        execution_time_ms,
        rows_returned,
        queries_in_last_60s,
        EXTRACT(HOUR FROM timestamp) as hour_of_day,
        EXTRACT(DOW FROM timestamp) as day_of_week,
        is_anomaly,
        anomaly_type
    FROM query_log
""", engine)


print("Dataset shape:", df.shape)
print("\nClass distribution:")
print(df['is_anomaly'].value_counts())
print("\nAnomaly type breakdown:")
print(df['anomaly_type'].value_counts())
print("\nFeature statistics:")
print(df.describe())

print("Execution time by anomaly type:")
print(df.groupby('anomaly_type')['execution_time_ms'].describe())
print("\nExecution time for normal queries:")
print(df[df['is_anomaly']==False]['execution_time_ms'].describe())

print("store_id_accessed for normal queries:")
print(df[df['is_anomaly']==False]['store_id_accessed'].value_counts())

print("\nstore_id_accessed for security anomalies:")
print(df[df['anomaly_type']=='security']['store_id_accessed'].value_counts())

# Check 1 — weekday distribution
print(df[df['is_anomaly']==False]['day_of_week'].value_counts().sort_index())

# Check 2 — execution time separation
print(df.groupby('anomaly_type')['execution_time_ms'].describe())

# Check 3 — confirm anomaly counts still correct
print(df['anomaly_type'].value_counts(dropna=False))