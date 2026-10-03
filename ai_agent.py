import requests

from trade_tools import (
    get_top_trade_relationships,
    get_top_trade_countries,
    get_top_commodities,
    get_high_value_trade,
    get_trade_flow,
    get_countries_above_value,
    get_commodities_above_value,
    get_commercial_opportunities,
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:1.7b"


def ask_ollama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a trade intelligence assistant. "
                        "Provide short, evidence-grounded business insights only. "
                        "Use only the context supplied in the prompt. "
                        "Do not reproduce database numbers unless explicitly requested. "
                        "Do not invent currency, units, countries, commodities, "
                        "demand, pricing, market conditions, strategy, risk levels, "
                        "or causes. "
                        "Clearly distinguish observed database patterns from possible "
                        "business implications. Use cautious language such as "
                        "'may indicate' or 'could suggest' for interpretations. "
                        "Never claim that a relationship is a proven opportunity."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "stream": False,
            "think": False,
        },
        timeout=120,
    )

    response.raise_for_status()
    return response.json()["message"]["content"]


def extract_value_threshold(question):
    import re

    q = question.lower().replace(",", "")

    match = re.search(r"(?:above|over|greater than|more than)\s+(\d+(?:\.\d+)?)\s*(million|billion|m|bn)?", q)

    if not match:
        return None

    value = float(match.group(1))
    unit = match.group(2)

    if unit in ("billion", "bn"):
        value *= 1_000_000_000
    elif unit in ("million", "m"):
        value *= 1_000_000

    return value


def classify_question(question):
    q = question.lower()

    if any(term in q for term in [
        "high value",
        "highest value per mass",
        "value per mass",
        "high value trade"
    ]):
        return "high_value"

    if any(term in q for term in [
        "opportunity",
        "opportunities",
        "commercial opportunity",
        "commercial opportunities"
    ]):
        return "opportunities"

    if any(term in q for term in [
        "trade flow",
        "trade flows",
        "eu export",
        "eu exports",
        "non-eu export",
        "non-eu exports"
    ]):
        return "trade_flow"

    if any(term in q for term in [
        "country",
        "countries",
        "market",
        "markets",
        "destination",
        "destinations"
    ]):
        return "countries"

    if any(term in q for term in [
        "commodity",
        "commodities",
        "product",
        "products",
        "goods"
    ]):
        return "commodities"

    return "relationships"

def get_database_data(question):
    category = classify_question(question)
    threshold = extract_value_threshold(question)

    if threshold is not None and category == "countries":
        return get_countries_above_value(threshold, 10)

    if threshold is not None and category == "commodities":
        return get_commodities_above_value(threshold, 10)

    if category == "countries":
        return get_top_trade_countries(10)

    if category == "commodities":
        return get_top_commodities(10)

    if category == "trade_flow":
        return get_trade_flow()

    if category == "high_value":
        return get_high_value_trade(10)

    if category == "opportunities":
        return get_commercial_opportunities(
            minimum_value=1000000,
            minimum_mass=1000,
            limit=10
        )

    return get_top_trade_relationships(10)


def format_country_results(data):
    rows = []

    for row in data:
        rows.append({
            "country": row[0],
            "trade_records": row[1],
            "commodities": row[2],
            "total_value": float(row[3]),
            "total_mass": float(row[4]),
        })

    rows.sort(key=lambda x: x["total_value"], reverse=True)

    return rows


def format_commodity_results(data):
    rows = []

    for row in data:
        rows.append({
            "commodity": row[0],
            "trade_records": row[1],
            "countries": row[2],
            "total_value": float(row[3]),
            "total_mass": float(row[4]),
        })

    rows.sort(key=lambda x: x["total_value"], reverse=True)

    return rows


def run_agent(question):
    category = classify_question(question)
    data = get_database_data(question)

    # -------------------------
    # COUNTRY INTELLIGENCE
    # -------------------------
    if category == "countries":
        threshold = extract_value_threshold(question)

        if threshold is not None:
            print("\nDatabase filtered country results:\n")

            for i, row in enumerate(data, 1):
                country = row[0]
                total_value = float(row[1])
                total_mass = float(row[2] or 0)
                trade_records = int(row[3])

                print(
                    f"{i}. {country} | "
                    f"Total Value={total_value:,.2f} | "
                    f"Total Mass={total_mass:,.2f} | "
                    f"Trade Records={trade_records:,}"
                )

            print("\nBusiness Insight:")
            print(
                "These countries meet the requested minimum trade-value "
                "threshold based on the database results."
            )

            return

        rows = format_country_results(data)

        print("\nDatabase-ranked results:\n")

        for i, row in enumerate(rows, 1):
            print(
                f"{i}. {row['country']} | "
                f"Total Value={row['total_value']:,.2f} | "
                f"Trade Records={row['trade_records']:,} | "
                f"Commodities={row['commodities']:,} | "
                f"Total Mass={row['total_mass']:,.2f}"
            )

        top_countries = ", ".join(
            row["country"] for row in rows[:5]
        )

        return ask_ollama(
            f"Database analysis shows these leading trade markets: "
            f"{top_countries}. "
            "Give one short qualitative business observation about "
            "what concentration among these markets could mean for "
            "trade strategy. Do not provide numbers, rankings, or "
            "facts not contained in the supplied context."
        )

    # -------------------------
    # COMMODITY INTELLIGENCE
    # -------------------------
    if category == "commodities":
        rows = format_commodity_results(data)

        print("\nDatabase-ranked commodity results:\n")

        for i, row in enumerate(rows, 1):
            print(
                f"{i}. Commodity {row['commodity']} | "
                f"Total Value={row['total_value']:,.2f} | "
                f"Trade Records={row['trade_records']:,} | "
                f"Countries={row['countries']:,} | "
                f"Total Mass={row['total_mass']:,.2f}"
            )

        top_commodities = ", ".join(
            f"Commodity {row['commodity']}" for row in rows[:5]
        )

        return ask_ollama(
            f"Database analysis shows these leading traded commodities: "
            f"{top_commodities}. "
            "Give one short qualitative business observation about "
            "what concentration among these commodities could mean "
            "for trade strategy. Clearly frame implications as "
            "possible considerations, not proven facts. Do not provide "
            "numbers or introduce facts outside the supplied context."
        )

    # -------------------------
    # COMMERCIAL OPPORTUNITY INTELLIGENCE
    # -------------------------
    if category == "opportunities":
        print("\nCommercial opportunity results:\n")

        for i, row in enumerate(data, 1):
            print(
                f"{i}. {row[1]} | Commodity {row[2]} | "
                f"Total Value={float(row[3]):,.2f} | "
                f"Total Mass={float(row[4]):,.2f} | "
                f"Value/Mass={float(row[5]):,.2f}"
            )

        opportunity_context = ", ".join(
            f"{row[1]} / Commodity {row[2]}" for row in data[:5]
        )

        return ask_ollama(
            f"Database analysis identified these leading commercial trade "
            f"relationships: {opportunity_context}. "
            "Give one short qualitative observation about what these "
            "relationships could indicate for commercial analysis. "
            "Frame implications as possible considerations rather than "
            "proven opportunities. Do not provide numbers and do not "
            "invent market, pricing, demand, or geopolitical facts."
        )

    # -------------------------
    # TRADE-FLOW INTELLIGENCE
    # -------------------------
    if category == "trade_flow":
        rows = []

        for row in data:
            rows.append({
                "flow": row[1],
                "trade_records": row[2],
                "countries": row[3],
                "commodities": row[4],
                "total_value": float(row[5]),
                "total_mass": float(row[6]),
            })

        print("\nDatabase trade-flow results:\n")

        for row in rows:
            print(
                f"{row['flow']} | "
                f"Trade Records={row['trade_records']:,} | "
                f"Countries={row['countries']:,} | "
                f"Commodities={row['commodities']:,} | "
                f"Total Value={row['total_value']:,.2f} | "
                f"Total Net Mass={row['total_mass']:,.2f}"
            )

        print("\nBusiness Insight:")

        flow_context = "; ".join(
            f"{row['flow']} covers {row['countries']} countries "
            f"and {row['commodities']} commodities"
            for row in rows
        )

        insight = ask_ollama(
            f"Database results show the following trade-flow coverage: "
            f"{flow_context}. "
            "Compare the flows qualitatively using only this supplied "
            "context. Describe the observed differences in geographic "
            "and commodity coverage. You may mention possible analytical "
            "implications, but do not infer business strategy, market "
            "priorities, diversification, risk management, market access, "
            "competition, demand, pricing, or logistics unless explicitly "
            "supported by the supplied context. Do not provide numbers "
            "and do not invent facts."
        )

        return insight

    # -------------------------
    # HIGH VALUE / VALUE PER MASS
    # -------------------------
    if category == "high_value":
        print("\nDatabase high-value trade results:\n")

        for i, row in enumerate(data, 1):
            print(
                f"{i}. {row[0]} | "
                f"Country={row[1]} | "
                f"Commodity={row[2]} | "
                f"Total Value={float(row[3]):,.2f} | "
                f"Total Mass={float(row[4]):,.2f} | "
                f"Value Per Mass={float(row[5]):,.2f}"
            )

        print("\nBusiness Insight:")

        high_value_context = "; ".join(
            f"{row[0]} / {row[1]} / Commodity {row[2]}"
            for row in data[:5]
        )

        insight = ask_ollama(
            f"Database results identified these high value-per-mass "
            f"trade relationships: {high_value_context}. "
            "Give one short qualitative observation about the "
            "observed pattern. Explain that value per mass is a ratio "
            "and should be interpreted alongside total trade value "
            "and total mass. Do not treat a high ratio as proof of "
            "commercial opportunity. Do not invent pricing, demand, "
            "market conditions, or other facts not supplied."
        )

        return insight

    # -------------------------
    # OTHER QUESTIONS
    # -------------------------
    return ask_ollama(
        f"""
User question:
{question}

Database results:
{data}

Give a short qualitative explanation.
Do not modify or reproduce database numbers.
"""
    )


if __name__ == "__main__":
    print("AI Trade & Commercial Intelligence Agent")
    print("Type 'exit' to quit.")

    while True:
        question = input("\nYou: ")

        if question.lower() == "exit":
            break

        try:
            answer = run_agent(question)

            if answer:
                print("\nAgent:")
                print(answer)

        except Exception as e:
            print(f"\nError: {e}")
