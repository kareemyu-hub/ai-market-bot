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
    tw_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
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
                headlines.append(f"{sentiment} {title}\n{entry.link}")
                if len(headlines) >= 5:
                    return headlines
        except:
            continue
    return headlines

# ------------------ 加密 ------------------
def get_crypto(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        res = requests.get(url, timeout=10).json()
        price = float(res["lastPrice"])
        change = float(res["priceChangePercent"])
        return round(change,2), round(price,2)
    except:
        return None, None

# ------------------ 生成報告 ------------------
def generate_report():
    tw_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
    message = f"📊 AI市場雷達 {tw_now}\n\n"

    # 💰 加密
    message += "💰 加密市場：\n"
    for k,v in {"BTC":"BTCUSDT","ETH":"ETHUSDT"}.items():
        change,price = get_crypto(v)
        arrow = "⚪️" if change is None else ("⬆️" if change>0 else "⬇️")
        price_text = f"{price:.2f}" if price else "暫無價格"
        change_text = f"{change:+.2f}%" if change is not None else "暫無資料"
        message += f"{k} {change_text} {arrow} ({price_text}) (更新 {tw_now}), "
    message = message.rstrip(", ") + "\n\n"

    # 📰 新聞
    headlines = fetch_news()
    if headlines:
        message += "📰 最新新聞摘要：\n" + "\n".join(headlines) + "\n\n"

    # 📅 今日重要事件
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
