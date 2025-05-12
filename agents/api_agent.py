import yfinance as yf
from datetime import datetime, timedelta

class APIAgent:
    def __init__(self, tickers):
        self.tickers = tickers

    def get_market_data(self):
        data = {}
        for ticker in self.tickers:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")  # past 2 days
            try:
                prev_close = hist['Close'].iloc[-2]
                curr_close = hist['Close'].iloc[-1]
                change = ((curr_close - prev_close) / prev_close) * 100
                data[ticker] = {
                    "current": curr_close,
                    "previous": prev_close,
                    "change_percent": round(change, 2)
                }
            except Exception as e:
                data[ticker] = {"error": str(e)}
        return data

if __name__ == "__main__":
    tickers = ["TSM", "005930.KS", "0700.HK", "BABA"]
    agent = APIAgent(tickers)
    result = agent.get_market_data()
    print(result)
