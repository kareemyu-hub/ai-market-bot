import os
import requests
import datetime
import time
import feedparser

# ------------------ 環境變數 ------------------
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ------------------ 新聞來源 ------------------
NEWS_FEEDS = [
    "https://www.reuters.com/rssFeed/wealth",
    "https://tw.finance.yahoo.com/rss/"
]

TOP_STOCKS = ["TSMC","NVDA","AAPL","TSLA","AMD"]

# ------------------ Telegram ------------------
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# ------------------ 啟動測試 ------------------
def send_startup_test():
    tw_now = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=8))
    ).strftime("%Y-%m-%d %H:%M")

    message = f"""
🤖 AI市場雷達啟動成功

時間：
{tw_now}

狀態：
✅ 系統正常運作
"""
    send_telegram(message)

# ------------------ 情緒分析 ------------------
def analyze_sentiment(text):
    text = text.lower()
    if any(k in text for k in ["上漲","利多","看好","漲"]):
        return "📈利多"
    elif any(k in text for k in ["下跌","利空","警告","跌"]):
        return "📉利空"
    else:
        return "⚖️中性"

# ------------------ 新聞 ------------------
def fetch_news():
    headlines = []
    seen = set()

    for feed_url in NEWS_FEEDS:
        try:
            d = feedparser.parse(feed_url)

            for entry in d.entries[:10]:
                title = entry.title
                if title in seen:
                    continue

                seen.add(title)

                summary = getattr(entry,"summary","")
                sentiment = analyze_sentiment(title + summary)

                headlines.append(
                    f"{sentiment} {title}\n{entry.link}"
                )

                if len(headlines) >= 5:
                    return headlines
        except:
            continue

    return headlines

# ------------------ 台股（TSMC） ------------------
def get_tsmc_price():
    try:
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&stockNo=2330"
        res = requests.get(url, timeout=10).json()

        data = res["data"][-1]
        price = float(data[1].replace(",", ""))

        return 0.0, price
    except:
        return 0.0, None

# ------------------ 美股 ------------------
def get_us_stock(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        res = requests.get(url, timeout=10).json()

        result = res["chart"]["result"][0]

        price = result["meta"]["regularMarketPrice"]
        prev = result["meta"]["previousClose"]

        change = ((price - prev) / prev) * 100

        return round(change,2), round(price,2)
    except:
        return 0.0, None

# ------------------ 加密 ------------------
def get_crypto(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        res = requests.get(url, timeout=10).json()

        price = float(res["lastPrice"])
        change = float(res["priceChangePercent"])

        return round(change,2), round(price,2)
    except:
        return 0.0, None

# ------------------ 統一抓價 ------------------
def fetch_price(symbol):

    # 台股
    if symbol == "2330.TW":
        return get_tsmc_price()

    # 加密
    if symbol == "BTC-USD":
        return get_crypto("BTCUSDT")

    if symbol == "ETH-USD":
        return get_crypto("ETHUSDT")

    # 美股
    return get_us_stock(symbol)

# ------------------ 報告 ------------------
def generate_report():

    tw_now = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=8))
    ).strftime("%Y-%m-%d %H:%M")

    message = f"📊 AI市場雷達 {tw_now}\n\n"

    # 🌎 全球市場
    message += "🌎 全球市場：\n"

    global_map = {
        "S&P500":"^GSPC",
        "NASDAQ":"^IXIC"
    }

    for k,v in global_map.items():
        change,price = fetch_price(v)

        arrow = "⚪️"
        if change:
            arrow = "⬆️" if change>0 else "⬇️"

        price_text = f"{price:.2f}" if price else "暫無價格"

        message += f"{k} {change:+.2f}% {arrow} ({price_text}) (更新 {tw_now}), "

    message = message.rstrip(", ") + "\n\n"

    # 🇹🇼 台股
    message += "🇹🇼 台股市場：\n"

    change,price = fetch_price("2330.TW")

    arrow = "⚪️"
    if change:
        arrow = "⬆️" if change>0 else "⬇️"

    price_text = f"{price:.2f}" if price else "暫無價格"

    message += f"TSMC {change:+.2f}% {arrow} ({price_text}) (更新 {tw_now})\n\n"

    # 💰 加密
    message += "💰 加密市場：\n"

    crypto = {
        "BTC":"BTC-USD",
        "ETH":"ETH-USD"
    }

    for k,v in crypto.items():
        change,price = fetch_price(v)

        arrow = "⚪️"
        if change:
            arrow = "⬆️" if change>0 else "⬇️"

        price_text = f"{price:.2f}" if price else "暫無價格"

        message += f"{k} {change:+.2f}% {arrow} ({price_text}) (更新 {tw_now}), "

    message = message.rstrip(", ") + "\n\n"

    # 📰 新聞
    headlines = fetch_news()
    if headlines:
        message += "📰 最新新聞摘要：\n"
        message += "\n".join(headlines) + "\n\n"

    # 🎯 熱門股票
    message += "🎯 今日熱門股票：\n"

    for s in TOP_STOCKS:
        if s == "TSMC":
            change,price = fetch_price("2330.TW")
        else:
            change,price = fetch_price(s)

        arrow = "⚪️"
        if change:
            arrow = "⬆️" if change>0 else "⬇️"

        price_text = f"{price:.2f}" if price else "暫無價格"

        message += f"{s} {change:+.2f}% {arrow} ({price_text}) (更新 {tw_now}), "

    message = message.rstrip(", ") + "\n\n"

    message += "📅 今日重要事件：\n21:30 美國 CPI, 22:45 製造業 PMI\n"

    return message

# ------------------ 發送 ------------------
def send_report():
    send_telegram(generate_report())

# ------------------ 主程式 ------------------
INTERVAL = 3600  # 每1小時

if __name__ == "__main__":

    print("🚀 系統啟動")

    send_startup_test()

    while True:
        print("📡 更新市場資料")
        send_report()
        time.sleep(INTERVAL)
