import sys
import asyncio
from datetime import datetime, timedelta
import aiohttp

API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

if len(sys.argv) > 1:
    try:
        days = int(sys.argv[1])
    except ValueError:
        print("Аргумент має бути числом")
        sys.exit(1)
else:
    days = 1

if days > 10:
    days = 10

dates = []
now = datetime.now()
for i in range(days):
    date_i = (now - timedelta(days=i)).strftime("%d.%m.%Y")
    dates.append(date_i)


async def fetch_rate(session, date):
    url = API_URL + date
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Помилка HTTP {resp.status} для {date}")
                return None
            data = await resp.json()
            result = {}
            for item in data.get("exchangeRate", []):
                if item.get("currency") in ("USD", "EUR"):
                    result[item["currency"]] = {
                        "sale": item.get("saleRate", 0),
                        "purchase": item.get("purchaseRate", 0)
                    }
            return {date: result}
    except aiohttp.ClientError as e:
        print(f"Помилка мережі для {date}: {e}")
        return None

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_rate(session, d) for d in dates]
        results = await asyncio.gather(*tasks)
        # відфільтрувати None
        results = [r for r in results if r]
        print(results)

if __name__ == "__main__":
    asyncio.run(main())
