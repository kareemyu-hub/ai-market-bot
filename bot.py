import yfinance as yf
import requests
from datetime import datetime

# ===== Telegram =====
BOT_TOKEN = "你的BOT_TOKEN"
CHAT_ID = "你的CHAT_ID"

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=payload)
    except:
        pass


# ===== 股票資料 =====
def get_stock(symbol):

    try:

        data = yf.download(symbol, period="1d", progress=False)

        if data.empty:
            return None

        close = float(data["Close"].iloc[-1])
        open_price = float(data["Open"].iloc[-1])

        change = ((close - open_price) / open_price) * 100

        emoji = "🟢" if change > 0 else "🔴"

        return f"{change:.2f}% {emoji}"

    except:
        return None


# ===== 加密貨幣 =====
def get_crypto(coin):

    try:

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd&include_24hr_change=true"

        data = requests.get(url).json()

        change = data[coin]["usd_24h_change"]

        emoji = "🟢" if change > 0 else "🔴"

        return f"{change:.2f}% {emoji}"

    except:
        return None


# ===== 市場報告 =====
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

    def safe(v):
        return v if v else "暫無資料 ⚪️"

    message = f"""
📊 AI市場雷達 {today}

🌎 全球市場
S&P500 {safe(sp500)}
NASDAQ {safe(nasdaq)}

🇹🇼 台股
TSMC {safe(tsmc)}

💰 加密
BTC {safe(btc)}
ETH {safe(eth)}

🎯 AI熱門股
NVDA {safe(nvda)}
AMD {safe(amd)}
AAPL {safe(aapl)}
TSLA {safe(tsla)}

📅 今日事件
21:30 美國 CPI
22:45 製造業 PMI
"""

    return message


# ===== 系統啟動測試 =====
def send_startup_test():

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    message = f"""
🤖 AI市場雷達系統啟動

系統時間：
{now}

狀態：
✅ 系統正常運作
"""

    send_telegram(message)


# ===== 主程式 =====

send_startup_test()

report = generate_report()

send_telegram(report)
