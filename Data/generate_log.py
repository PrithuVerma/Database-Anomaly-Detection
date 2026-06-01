import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import sqlalchemy as sql
import config as con

fake = Faker()

# ── Query Templates ────────────────────────────────────────────────────────────
# Each role has a set of normal query types they would run
# Format: (query_type, tables_accessed, base_execution_time_ms, rows_returned_range)

ROLE_QUERY_TEMPLATES = {
    "analyst": [
        ("SELECT_RENTAL_SUMMARY",   ["rental", "inventory"],         50,  (10, 200)),
        ("SELECT_FILM_DETAILS",     ["film", "film_category"],        30,  (1, 50)),
        ("SELECT_CUSTOMER_HISTORY", ["customer", "rental"],          80,  (5, 100)),
    ],
    "billing_staff": [
        ("SELECT_PAYMENT",          ["payment"],                      40,  (1, 30)),
        ("INSERT_PAYMENT",          ["payment"],                      20,  (1, 1)),
        ("SELECT_CUSTOMER",         ["customer"],                     25,  (1, 10)),
    ],
    "manager": [
        ("SELECT_STORE_SUMMARY",    ["store", "staff"],               60,  (1, 5)),
        ("SELECT_REVENUE_REPORT",   ["payment", "rental", "store"],  200,  (50, 500)),
        ("SELECT_INVENTORY",        ["inventory", "film"],            70,  (20, 200)),
    ],
    "auditor": [
        ("SELECT_ALL_PAYMENTS",     ["payment"],                     300,  (100, 1000)),
        ("SELECT_STAFF_ACTIVITY",   ["staff", "rental"],             150,  (10, 100)),
        ("SELECT_RENTAL_AUDIT",     ["rental", "customer"],          180,  (50, 300)),
    ],
    "support_staff": [
        ("SELECT_CUSTOMER",         ["customer", "address"],          30,  (1, 10)),
        ("SELECT_RENTAL_STATUS",    ["rental", "inventory"],          40,  (1, 20)),
        ("UPDATE_CUSTOMER",         ["customer"],                     15,  (1, 1)),
    ],
    "admin": [
        ("SELECT_ALL_TABLES",       ["customer", "staff", "store"],  500,  (100, 5000)),
        ("SELECT_SYSTEM_LOGS",      ["rental", "payment"],           400,  (100, 2000)),
        ("UPDATE_STAFF",            ["staff"],                        20,  (1, 1)),
    ],
}

# Tables that belong to each store — used for security anomaly detection
# In Pagila, store_id is present in: store, staff, inventory, customer
STORE_SENSITIVE_TABLES = ["payment", "rental", "inventory", "customer", "staff"]


# ── Helper: Generate a normal timestamp ───────────────────────────────────────

#-------------------#---------#----------------
START_DATE = datetime(2024, 1, 1)

def normal_timestamp():
    """Weekday, business hours, uniformly distributed Mon-Fri"""
    # Pick a random weekday directly — no pushing
    base = START_DATE + timedelta(days=random.randint(0, 180))
    # Find the Monday of that week, then pick a random weekday
    monday = base - timedelta(days=base.weekday())
    weekday_offset = random.randint(0, 4)  # 0=Mon, 4=Fri
    candidate = monday + timedelta(days=weekday_offset)
    
    hour   = random.randint(con.BUSINESS_HOURS_START, 17)  # cap at 5pm
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return candidate.replace(hour=hour, minute=minute, second=second)

def anomalous_timestamp():
    """Weekend OR off-hours (midnight to 5am)"""
    candidate = START_DATE + timedelta(days=random.randint(0, 180))
    if random.random() > 0.5:
        # Force to weekend
        while candidate.weekday() < 5:
            candidate += timedelta(days=1)
        hour = random.randint(10, 14)
    else:
        # Force to off-hours
        hour = random.randint(0, 4)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return candidate.replace(hour=hour, minute=minute, second=second)


import random
from datetime import datetime, timedelta

def generate_normal_timestamp(start_date):
    # Pick a random weekday (Monday=0 to Friday=4)
    day_offset = random.randint(0, 13)  # 2 week window
    candidate = start_date + timedelta(days=day_offset)
    
    # If weekend, push to Monday
    while candidate.weekday() > 4:
        candidate += timedelta(days=1)
    
    # Business hours 9am to 6pm
    hour = random.randint(9, 17)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    return candidate.replace(hour=hour, minute=minute, second=second)

# ── Normal Query Generator ─────────────────────────────────────────────────────
def generate_normal_query(user):
    templates = ROLE_QUERY_TEMPLATES.get(user['role'], ROLE_QUERY_TEMPLATES['analyst'])
    query_type, tables, base_exec_time, row_range = random.choice(templates)

    # Small natural variance in execution time (±20%)
    exec_time = int(base_exec_time * np.random.uniform(0.8, 1.2))

    return {
        'user_id'              : user['user_id'],
        'username'             : user['username'],
        'role'                 : user['role'],
        'store_id_accessed'    : user['store_id'],       # accessing own store — normal
        'query_type'           : query_type,
        'tables_accessed'      : ', '.join(tables),
        'execution_time_ms'    : exec_time,
        'rows_returned'        : random.randint(*row_range),
        'timestamp'            : normal_timestamp(),
        'queries_in_last_60s'  : random.randint(1, con.QUERY_RATE_LIMIT - 1),  # under limit
        'is_anomaly'           : False,
        'anomaly_type'         : None
    }


# ── Anomaly Generators ─────────────────────────────────────────────────────────

def generate_performance_anomaly(user):
    """Slow query — execution time far above threshold"""
    templates = ROLE_QUERY_TEMPLATES.get(user['role'], ROLE_QUERY_TEMPLATES['analyst'])
    query_type, tables, base_exec_time, row_range = random.choice(templates)

    exec_time = int(base_exec_time * np.random.uniform(3, 5))

    return {
        'user_id'              : user['user_id'],
        'username'             : user['username'],
        'role'                 : user['role'],
        'store_id_accessed'    : user['store_id'],
        'query_type'           : query_type,
        'tables_accessed'      : ', '.join(tables),
        'execution_time_ms'    : exec_time,
        'rows_returned'        : random.randint(row_range[1], row_range[1] * 10),  # more rows too
        'timestamp'            : normal_timestamp(),
        'queries_in_last_60s'  : random.randint(1, con.QUERY_RATE_LIMIT - 1),
        'is_anomaly'           : True,
        'anomaly_type'         : 'performance'
    }


def generate_temporal_anomaly(user):
    """Query fired outside business hours"""
    templates = ROLE_QUERY_TEMPLATES.get(user['role'], ROLE_QUERY_TEMPLATES['analyst'])
    query_type, tables, base_exec_time, row_range = random.choice(templates)

    exec_time = int(base_exec_time * np.random.uniform(0.8, 1.2))

    return {
        'user_id'              : user['user_id'],
        'username'             : user['username'],
        'role'                 : user['role'],
        'store_id_accessed'    : user['store_id'],
        'query_type'           : query_type,
        'tables_accessed'      : ', '.join(tables),
        'execution_time_ms'    : exec_time,
        'rows_returned'        : random.randint(*row_range),
        'timestamp'            : anomalous_timestamp(),     # <-- the anomaly
        'queries_in_last_60s'  : random.randint(1, con.QUERY_RATE_LIMIT - 1),
        'is_anomaly'           : True,
        'anomaly_type'         : 'temporal'
    }


def generate_security_anomaly(user, all_store_ids):
    """User accesses data from a store they don't belong to"""
    templates = ROLE_QUERY_TEMPLATES.get(user['role'], ROLE_QUERY_TEMPLATES['analyst'])
    query_type, tables, base_exec_time, row_range = random.choice(templates)

    # Pick a different store — not the user's own
    other_stores = [s for s in all_store_ids if s != user['store_id']]
    accessed_store = random.choice(other_stores)

    exec_time = int(base_exec_time * np.random.uniform(0.8, 1.2))

    return {
        'user_id'              : user['user_id'],
        'username'             : user['username'],
        'role'                 : user['role'],
        'store_id_accessed'    : accessed_store,            # <-- the anomaly
        'query_type'           : query_type,
        'tables_accessed'      : ', '.join(tables),
        'execution_time_ms'    : exec_time,
        'rows_returned'        : random.randint(*row_range),
        'timestamp'            : normal_timestamp(),
        'queries_in_last_60s'  : random.randint(1, con.QUERY_RATE_LIMIT - 1),
        'is_anomaly'           : True,
        'anomaly_type'         : 'security'
    }


# ── Master Simulation ──────────────────────────────────────────────────────────
def simulate_query_log(users_df):
    print("Simulating query log...")

    total     = con.TOTAL_QUERIES
    n_anomaly = int(total * con.ANOMALY_RATE)
    n_normal  = total - n_anomaly

    # Anomaly breakdown
    n_perf    = int(n_anomaly * con.PERF_ANOMALY_SHARE)
    n_temp    = int(n_anomaly * con.TEMP_ANOMALY_SHARE)
    n_sec     = n_anomaly - n_perf - n_temp   # remainder goes to security

    print(f"  Total queries    : {total:,}")
    print(f"  Normal           : {n_normal:,}")
    print(f"  Anomalies total  : {n_anomaly:,}")
    print(f"    Performance    : {n_perf:,}")
    print(f"    Temporal       : {n_temp:,}")
    print(f"    Security       : {n_sec:,}")

    users     = users_df.to_dict('records')
    store_ids = con.STORE_IDS
    logs      = []

    # Normal queries
    for _ in range(n_normal):
        user = random.choice(users)
        logs.append(generate_normal_query(user))

    # Performance anomalies
    for _ in range(n_perf):
        user = random.choice(users)
        logs.append(generate_performance_anomaly(user))

    # Temporal anomalies
    for _ in range(n_temp):
        user = random.choice(users)
        logs.append(generate_temporal_anomaly(user))

    # Security anomalies
    for _ in range(n_sec):
        user = random.choice(users)
        logs.append(generate_security_anomaly(user, store_ids))

    df = pd.DataFrame(logs)

    # Sort by timestamp — makes the log realistic
    df = df.sort_values('timestamp').reset_index(drop=True)
    df.insert(0, 'log_id', range(1, len(df) + 1))

    print(f"\n  ✓ Query log generated: {len(df):,} rows")
    print(f"  Anomaly breakdown:\n{df['anomaly_type'].value_counts(dropna=False).to_string()}")
    return df


def load_query_log(df, engine):
    print("\nLoading query log into PostgreSQL...")

    create_table_sql = """
    DROP TABLE IF EXISTS query_log;

    CREATE TABLE query_log (
        log_id               SERIAL PRIMARY KEY,
        user_id              INT,
        username             VARCHAR(50),
        role                 VARCHAR(20),
        store_id_accessed    INT,
        query_type           VARCHAR(50),
        tables_accessed      TEXT,
        execution_time_ms    INT,
        rows_returned        INT,
        timestamp            TIMESTAMP,
        queries_in_last_60s  INT,
        is_anomaly           BOOLEAN,
        anomaly_type         VARCHAR(20)
    );
    """

    with engine.connect() as conn:
        conn.execute(sql.text(create_table_sql))
        conn.commit()

    df.to_sql('query_log', engine, if_exists='append', index=False)
    print("  ✓ Query log loaded into pagila.query_log table")


if __name__ == '__main__':
    from generate_users import generate_users, load_users

    # Generate and load users first
    users_df = generate_users()
    engine   = load_users(users_df)

    # Simulate and load query log
    log_df   = simulate_query_log(users_df)
    load_query_log(log_df, engine)

    print("\n✓ Pipeline complete — users and query_log tables ready in pagila")