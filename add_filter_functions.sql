CREATE OR REPLACE FUNCTION get_countries_above_value(
    minimum_value NUMERIC,
    result_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    country_name TEXT,
    total_value NUMERIC,
    total_mass NUMERIC,
    trade_records BIGINT
)
LANGUAGE SQL
AS $$
    SELECT
        country_name::TEXT,
        SUM(trade_value) AS total_value,
        SUM(net_mass) AS total_mass,
        COUNT(*)::BIGINT AS trade_records
    FROM trade_enriched
    WHERE country_name <> 'Estimates'
      AND commodity_id >= 0
    GROUP BY country_name
    HAVING SUM(trade_value) >= minimum_value
    ORDER BY total_value DESC
    LIMIT result_limit;
$$;


CREATE OR REPLACE FUNCTION get_commodities_above_value(
    minimum_value NUMERIC,
    result_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    commodity_id INTEGER,
    total_value NUMERIC,
    total_mass NUMERIC,
    trade_records BIGINT
)
LANGUAGE SQL
AS $$
    SELECT
        commodity_id,
        SUM(trade_value) AS total_value,
        SUM(net_mass) AS total_mass,
        COUNT(*)::BIGINT AS trade_records
    FROM trade_enriched
    WHERE country_name <> 'Estimates'
      AND commodity_id >= 0
    GROUP BY commodity_id
    HAVING SUM(trade_value) >= minimum_value
    ORDER BY total_value DESC
    LIMIT result_limit;
$$;
