# ── Database ──────────────────────────────────────────
DB_HOST     = "localhost"
DB_PORT     = 5432
DB_USER     = "postgres"
DB_PASSWORD = "2392"
DB_NAME     = "pagila"

# ── Simulation Parameters ─────────────────────────────
TOTAL_QUERIES        = 10_000
ANOMALY_RATE         = 0.0725        # 7.25% of all queries are anomalous

# Anomaly type distribution (must sum to 1.0)
PERF_ANOMALY_SHARE   = 0.45
TEMP_ANOMALY_SHARE   = 0.30
SEC_ANOMALY_SHARE    = 0.25

# Security threshold — max queries allowed per user per 60 seconds
QUERY_RATE_LIMIT     = 15

# Performance threshold — queries above this ms are flagged
EXEC_TIME_THRESHOLD  = 3000          # 3 seconds

# Business hours (temporal anomalies happen outside these)
BUSINESS_HOURS_START = 8             # 8am
BUSINESS_HOURS_END   = 20            # 8pm

# ── User Generation ───────────────────────────────────
# Roles and how many per store
# (role, count_per_store)
ROLES = [
    ("manager",        1),
    ("analyst",        2),
    ("auditor",        1),
    ("billing_staff",  3),   # works in shifts — more than 1
    ("support_staff",  3),   # works in shifts — more than 1
    ("admin",          1),
]

STORE_IDS = [1, 2]