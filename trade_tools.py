import psycopg


DATABASE_URL = "dbname=trade_agent user=postgres password=5900 host=localhost port=5432"


def get_connection():
    return psycopg.connect(DATABASE_URL)


def get_top_trade_relationships(limit=10):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM get_top_trade_relationships(%s);",
                (limit,)
            )
            return cur.fetchall()


def get_top_trade_countries(limit=10):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM get_top_trade_countries(%s);",
                (limit,)
            )
            return cur.fetchall()


def get_top_commodities(limit=10):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM get_top_commodities(%s);",
                (limit,)
            )
            return cur.fetchall()


def get_high_value_trade(limit=10):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM get_high_value_trade(%s);",
                (limit,)
            )
            return cur.fetchall()


def get_trade_flow():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vw_trade_flow;")
            return cur.fetchall()


def get_countries_above_value(minimum_value, limit=10):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM get_countries_above_value(%s::numeric, %s::integer);",
                (minimum_value, limit)
            )
            return cur.fetchall()


def get_commodities_above_value(minimum_value, limit=10):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM get_commodities_above_value(%s::numeric, %s::integer);",
                (minimum_value, limit)
            )
            return cur.fetchall()


def get_commercial_opportunities(
    minimum_value=1000000,
    minimum_mass=1000,
    limit=10
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM get_commercial_opportunities(
                    %s::numeric,
                    %s::numeric,
                    %s::integer
                );
                """,
                (minimum_value, minimum_mass, limit)
            )
            return cur.fetchall()
