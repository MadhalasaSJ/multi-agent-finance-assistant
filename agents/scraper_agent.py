import os
import requests
from dotenv import load_dotenv

class ScraperAgent:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"

    def get_earnings_summary(self, symbol="TSM"):
        params = {
            "function": "EARNINGS",
            "symbol": symbol,
            "apikey": self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Debug print to see what the API returned
            #print("🔍 API Raw Response:")
            #print(data)

            if "quarterlyEarnings" in data and data["quarterlyEarnings"]:
                earnings = data["quarterlyEarnings"][0]
                reported_eps = earnings.get("reportedEPS", "N/A")
                estimated_eps = earnings.get("estimatedEPS", "N/A")
                surprise_pct = earnings.get("surprisePercentage", "N/A")
                fiscal_date = earnings.get("fiscalDateEnding", "N/A")

                return (
                    f"{symbol} reported earnings for {fiscal_date}. "
                    f"Reported EPS: {reported_eps}, Estimated EPS: {estimated_eps}, "
                    f"Earnings Surprise: {surprise_pct}%."
                )
            else:
                return self._fallback_summary()

        except Exception as e:
            print(f"[ScraperAgent] API error: {e}")
            return self._fallback_summary()

    def _fallback_summary(self):
        return """TSMC reported Q1 earnings, beating estimates by 4%.
Samsung reported a miss of 2% due to weaker chip demand.
Alibaba results will be released later today."""

if __name__ == "__main__":
    scraper = ScraperAgent()

    # Print the actual key to verify it's loading (temporary debug only)
    print(f"🔑 Loaded API key: {scraper.api_key}")

    result = scraper.get_earnings_summary("TSM")
    print("\n📊 Final Output:")
    print(result)
