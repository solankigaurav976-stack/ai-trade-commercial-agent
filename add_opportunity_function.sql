CREATE OR REPLACE FUNCTION get_commercial_opportunities(
    minimum_value NUMERIC DEFAULT 1000000,
    minimum_mass NUMERIC DEFAULT 1000,
    result_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    flow_type TEXT,
    country_name TEXT,
    commodity_id INTEGER,
    total_value NUMERIC,
    total_mass NUMERIC,
    value_per_mass NUMERIC
)
LANGUAGE SQL
AS $$
    SELECT
        flow_type_name::TEXT,
        country_name::TEXT,
        commodity_id,
        SUM(trade_value) AS total_value,
        SUM(net_mass) AS total_mass,
        ROUND(
            SUM(trade_value) / NULLIF(SUM(net_mass), 0),
            2
        ) AS value_per_mass
    FROM trade_enriched
    WHERE country_name <> 'Estimates'
      AND commodity_id >= 0
      AND net_mass IS NOT NULL
      AND net_mass > 0
    GROUP BY
        flow_type_name,
        country_name,
        commodity_id
    HAVING SUM(trade_value) >= minimum_value
       AND SUM(net_mass) >= minimum_mass
    ORDER BY total_value DESC
    LIMIT result_limit;
$$;
