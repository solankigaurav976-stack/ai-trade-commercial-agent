import psycopg

conn = psycopg.connect(
    "dbname=trade_agent user=postgres password=5900 host=localhost port=5432"
)

print("Connected to PostgreSQL successfully!")

conn.close()
