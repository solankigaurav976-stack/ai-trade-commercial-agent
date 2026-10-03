import requests


def get_live_exchange_rates(base="GBP"):
    url = f"https://open.er-api.com/v6/latest/{base}"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()

    return {
        "base": data["base_code"],
        "updated": data.get("time_last_update_utc"),
        "rates": data["rates"],
    }


if __name__ == "__main__":
    data = get_live_exchange_rates("GBP")

    print("Live exchange-rate data:")
    print(f"Base currency: {data['base']}")
    print(f"Updated: {data['updated']}")

    for currency in ["USD", "EUR", "INR"]:
        print(f"{currency}: {data['rates'].get(currency)}")
