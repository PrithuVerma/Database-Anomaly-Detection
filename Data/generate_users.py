import pandas as pd
from faker import Faker
import sqlalchemy as sql
import config as con

fake = Faker()


def generate_users():
    print("Generating users...")
    users = []
    user_id = 1

    for store_id in con.STORE_IDS:
        for role, count in con.ROLES:
            for _ in range(count):
                users.append({
                    'user_id'    : user_id,
                    'username'   : fake.user_name(),
                    'role'       : role,
                    'store_id'   : store_id,
                    'created_at' : fake.date_time_between(start_date='-3y',end_date='now')
                })
                user_id += 1

    df = pd.DataFrame(users)
    print(f"  ✓ Users generated: {len(df)} rows")
    print(f"  Roles breakdown:\n{df['role'].value_counts().to_string()}")
    return df


def load_users(df):
    print("\nLoading users into PostgreSQL...")
    engine = sql.create_engine(
        f'postgresql+psycopg2://{con.DB_USER}:{con.DB_PASSWORD}'
        f'@{con.DB_HOST}:{con.DB_PORT}/{con.DB_NAME}'
    )

    # Create users table explicitly with correct types
    create_table_sql = """
    DROP TABLE IF EXISTS users CASCADE;

    CREATE TABLE users (
        user_id    SERIAL PRIMARY KEY,
        username   VARCHAR(50)  NOT NULL,
        role       VARCHAR(20)  NOT NULL,
        store_id   INT          REFERENCES store(store_id),
        created_at TIMESTAMP    NOT NULL
    );
    """

    with engine.connect() as conn:
        conn.execute(sql.text(create_table_sql))
        conn.commit()

    df.to_sql('users', engine, if_exists='append', index=False)
    print(f"  ✓ Users loaded into pagila.users table")
    return engine


if __name__ == '__main__':
    df = generate_users()
    load_users(df)