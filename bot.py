import os
import requests
import datetime
import feedparser
import traceback
import yfinance as yf
import time

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
FINNHUB_KEY = os.environ.get("FINNHUB_KEY")

NEWS_FEEDS = [
    "https://www.reuters.com/rssFeed/wealth",
    "https://tw.finance.yahoo.com/rss/"
]

TOP_STOCKS = ["TSMC","NVDA","AAPL","TSLA","AMD"]
AI_STOCKS = ["NVDA","AMD","TSM","AAPL","TSLA"]

LAST_DATA = {
    "global": {},
    "tw": {},
    "crypto": {},
    "stocks": {}
}

# Telegram 發送
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# 啟動測試
def send_startup_test():
    tw_now = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=8))
    ).strftime("%Y-%m-%d %H:%M")

    message = f"""
🤖 AI市場雷達系統啟動

時間：
{tw_now}

狀態：
✅ 系統正常運作
"""
    send_telegram(message)

# 情緒分析
def analyze_sentiment(text):
    text = text.lower()
    if any(k in text for k in ["上漲","利多","看好","漲"]):
        return "📈利多"
    elif any(k in text for k in ["下跌","利空","警告","跌"]):
        return "📉利空"
    else:
        return "⚖️中性"

# 新聞
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

# yfinance 抓價格（修正版本）
def fetch_yf_change(symbol):

    try:
        ticker = yf.Ticker(symbol)

        price = ticker.fast_info.get("lastPrice")
        prev = ticker.fast_info.get("previousClose")

        if price is None or prev is None:
            return None, None

        change = ((price - prev) / prev) * 100

        return round(change,2), round(price,2)

    except Exception as e:
        print("yfinance error:", e)
        return None, None

# 台股
def fetch_tw_stock(stock_no):

    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={stock_no}&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=10)

        data = r.json()

        c = float(data.get("c",0))
        o = float(data.get("o",0))

        if c == 0:
            c = float(data.get("pc",0))
            o = c

        change = ((c-o)/o)*100 if o!=0 else 0

        return round(change,2), round(c,2)

    except:
        return None, None


def generate_report():

    tw_now = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=8))
    ).strftime("%H:%M")

    today = datetime.date.today()

    headlines = fetch_news()

    message = f"📊 AI市場雷達 {today} {tw_now}\n\n"

    # 全球市場
    global_map = {
        "S&P500":"^GSPC",
        "NASDAQ":"^IXIC"
    }

    message += "🌎 全球市場：\n"

    for k,v in global_map.items():

        change,price = fetch_yf_change(v)

        arrow = "⚪️"

        if change:
            arrow = "⬆️" if change>0 else "⬇️"

        price_text = f"{price:.2f}" if price else "暫無價格"

        message += f"{k} {change:+.2f}% {arrow} ({price_text}) (最後更新 {tw_now}), "

    message = message.rstrip(", ") + "\n\n"

    # 台股
    message += "🇹🇼 台股市場：\n"

    change,price = fetch_tw_stock("TWSE:2330")

    arrow = "⚪️"
    if change:
        arrow = "⬆️" if change>0 else "⬇️"

    price_text = f"{price:.2f}" if price else "暫無價格"

    message += f"TSMC {change:+.2f}% {arrow} ({price_text}) (最後更新 {tw_now})\n\n"

    # Crypto
    message += "💰 加密市場：\n"

    crypto = {
        "BTC":"BTC-USD",
        "ETH":"ETH-USD"
    }

    for k,v in crypto.items():

        change,price = fetch_yf_change(v)

        arrow = "⚪️"

        if change:
            arrow = "⬆️" if change>0 else "⬇️"

        price_text = f"{price:.2f}" if price else "暫無價格"

        message += f"{k} {change:+.2f}% {arrow} ({price_text}) (最後更新 {tw_now}), "

    message = message.rstrip(", ") + "\n\n"

    # 新聞
    if headlines:
        message += "📰 最新新聞摘要：\n"
        message += "\n".join(headlines) + "\n\n"

    # 熱門股票
    message += "🎯 今日熱門股票：\n"

    for s in TOP_STOCKS:

        if s == "TSMC":
            change,price = fetch_tw_stock("TWSE:2330")
        else:
            change,price = fetch_yf_change(s)

        arrow = "⚪️"

        if change:
            arrow = "⬆️" if change>0 else "⬇️"

        price_text = f"{price:.2f}" if price else "暫無價格"

        message += f"{s} {change:+.2f}% {arrow} ({price_text}) (最後更新 {tw_now}), "

    message = message.rstrip(", ") + "\n\n"

    message += "📅 今日重要事件：\n21:30 美國 CPI, 22:45 製造業 PMI\n"

    return message


def send_daily_report():

    report = generate_report()
    send_telegram(report)


INTERVAL = 3600


if __name__ == "__main__":

    print("🚀 AI市場雷達啟動")

    send_startup_test()

    while True:

        print("執行市場更新")

        send_daily_report()

        time.sleep(INTERVAL)
