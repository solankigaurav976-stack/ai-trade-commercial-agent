import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from trade_tools import (
    get_top_trade_relationships,
    get_top_trade_countries,
    get_top_commodities,
    get_high_value_trade,
)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tools = [
    {
        "type": "function",
        "name": "get_top_trade_relationships",
        "description": "Find the highest-value trade relationships by country, commodity and trade flow.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of results to return."
                }
            },
            "required": ["limit"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "get_top_trade_countries",
        "description": "Find countries with the highest total trade value and trade volume.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of countries to return."
                }
            },
            "required": ["limit"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "get_top_commodities",
        "description": "Find commodities with the highest total trade value and volume.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of commodities to return."
                }
            },
            "required": ["limit"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "get_high_value_trade",
        "description": "Find trade relationships with high value relative to net mass.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of results to return."
                }
            },
            "required": ["limit"],
            "additionalProperties": False
        }
    }
]

def run_tool(name, arguments):
    limit = arguments.get("limit", 10)

    if name == "get_top_trade_relationships":
        return get_top_trade_relationships(limit)

    if name == "get_top_trade_countries":
        return get_top_trade_countries(limit)

    if name == "get_top_commodities":
        return get_top_commodities(limit)

    if name == "get_high_value_trade":
        return get_high_value_trade(limit)

    raise ValueError(f"Unknown tool: {name}")


def ask_trade_agent(question):
    response = client.responses.create(
        model="gpt-5.4-mini",
        instructions="""
You are an AI Trade & Commercial Intelligence Agent.

Answer questions using the provided PostgreSQL tools.

Important rules:
- Use database tools when the question requires trade data.
- Do not invent numbers.
- Explain the results clearly.
- Mention countries, commodities, trade flows, values and masses when relevant.
- Treat very high value-per-mass results cautiously because small masses can create extreme ratios.
- The country "Estimates" and negative/special commodity IDs should not be presented as normal commercial opportunities.
""",
        input=question,
        tools=tools,
    )

    while True:
        tool_calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        if not tool_calls:
            break

        tool_outputs = []

        for call in tool_calls:
            arguments = json.loads(call.arguments)

            result = run_tool(call.name, arguments)

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result, default=str),
            })

        response = client.responses.create(
            model="gpt-5.4-mini",
            instructions="""
You are an AI Trade & Commercial Intelligence Agent.

Use the database results to answer the user's question accurately.
Do not invent data.
Explain important findings in plain English.
""",
            previous_response_id=response.id,
            input=tool_outputs,
            tools=tools,
        )

    return response.output_text


if __name__ == "__main__":
    question = input("\nAsk the Trade Agent: ")

    answer = ask_trade_agent(question)

    print("\n" + "=" * 70)
    print("TRADE AGENT")
    print("=" * 70)
    print(answer)
    print("=" * 70)
