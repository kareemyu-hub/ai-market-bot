import yfinance as yf
import requests
import time
from datetime import datetime


def get_stock(symbol):
    try:
        data = yf.download(symbol, period="1d", progress=False)

        if data.empty:
            return "暫無資料 ⚪️"

        close = float(data["Close"].iloc[-1])
        open_price = float(data["Open"].iloc[-1])

        change = ((close - open_price) / open_price) * 100
        emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪️"

        return f"{change:.2f}% {emoji}"

    except:
        return "暫無資料 ⚪️"


def get_crypto(coin):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd&include_24hr_change=true"
        data = requests.get(url).json()

        change = data[coin]["usd_24h_change"]
        emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪️"

        return f"{change:.2f}% {emoji}"

    except:
        return "暫無資料 ⚪️"


def generate_report():

    sp500 = get_stock("SPY")
    nasdaq = get_stock("QQQ")

    tsmc = get_stock("TSM")
    nvda = get_stock("NVDA")
    aapl = get_stock("AAPL")
    tsla = get_stock("TSLA")
    amd = get_stock("AMD")

    btc = get_crypto("bitcoin")
    eth = get_crypto("ethereum")

    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    message = f"""
📊 AI市場雷達 {today}

🌎 全球市場：
S&P500 {sp500}, NASDAQ {nasdaq}

🇹🇼 台股市場：
TSMC {tsmc}

💰 加密市場：
BTC {btc}, ETH {eth}

🎯 今日熱門股票：
TSMC {tsmc}, NVDA {nvda}, AAPL {aapl}, TSLA {tsla}, AMD {amd}

📅 今日重要事件：
21:30 美國 CPI, 22:45 製造業 PMI
"""

    print(message)


# 每1小時執行一次
while True:
    generate_report()
    time.sleep(3600)
