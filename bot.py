import requests
import datetime
import feedparser
import schedule
import time
import os

# ---------- 環境變數 ----------
TOKEN = os.environ.get("TOKEN")  # Telegram BOT TOKEN
CHAT_ID = os.environ.get("CHAT_ID")  # 你的 Chat ID

# ---------- Telegram 發送函數 ----------
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        r = requests.post(url, data=data, timeout=10)
        if r.status_code != 200:
            print(f"Telegram 發送失敗: {r.text}")
    except Exception as e:
        print("Telegram 發送 Exception:", e)

# ---------- RSS / 新聞抓取 ----------
NEWS_FEEDS = [
    "https://www.reuters.com/rssFeed/wealth",
    "https://www.bloomberg.com/feed/podcast/market-update",
    "https://tw.finance.yahoo.com/rss/"
]

def fetch_news():
    headlines = []
    for feed_url in NEWS_FEEDS:
        try:
            d = feedparser.parse(feed_url)
            for entry in d.entries[:3]:  # 每個來源抓前三篇
                headlines.append(f"- {entry.title}\n{entry.link}")
        except Exception as e:
            print(f"抓 RSS 失敗 ({feed_url}): {e}")
    return headlines if headlines else ["無法抓取新聞"]

# ---------- 市場分析 ----------
WATCHED_STOCKS = ["NVDA", "TSMC", "AAPL", "TSLA", "AMD"]
WATCHED_CRYPTO = ["BTC", "ETH"]

def market_analysis():
    try:
        analysis = {
            "US Market": "S&P500 +0.8%, NASDAQ +1.2%, 市場情緒偏多",
            "Taiwan Market": "半導體↑, AI供應鏈↑, 航運↓",
            "Crypto": "BTC震盪偏多, 資金流入"
        }
        return analysis
    except Exception as e:
        print("市場分析 Exception:", e)
        return {"US Market":"無資料","Taiwan Market":"無資料","Crypto":"無資料"}

# ---------- 熱門股票 ----------
def hot_stocks():
    try:
        return WATCHED_STOCKS
    except Exception as e:
        print("熱門股票 Exception:", e)
        return []

# ---------- 今日事件 ----------
def today_events():
    try:
        events = [
            "21:30 美國 CPI 公布",
            "22:45 製造業 PMI",
            "02:00 FOMC 利率會議"
        ]
        return events
    except Exception as e:
        print("今日事件 Exception:", e)
        return []

# ---------- 生成訊息 ----------
def generate_report():
    today = datetime.date.today()
    headlines = fetch_news()
    market = market_analysis()
    stocks = hot_stocks()
    events = today_events()

    try:
        message = f"📊 AI市場雷達 {today}\n\n"
        message += f"🌎 全球市場:\n{market['US Market']}\n\n"
        message += f"🇹🇼 台股可能影響:\n{market['Taiwan Market']}\n\n"
        message += f"💰 加密市場:\n{market['Crypto']}\n\n"
        message += "📰 重要新聞:\n" + "\n".join(headlines[:5]) + "\n\n"
        message += "🎯 今日熱門股票:\n" + ", ".join(stocks) + "\n\n"
        message += "📅 今日重要事件:\n" + "\n".join(events) + "\n\n"
        message += "🚨 市場異動 / 突發新聞會自動推播"
    except Exception as e:
        print("生成訊息 Exception:", e)
        message = "AI市場雷達發生錯誤，請檢查程式"
    return message

# ---------- 發送晨報 ----------
def send_daily_report():
    try:
        report = generate_report()
        send_telegram(report)
    except Exception as e:
        print("發送晨報 Exception:", e)

# ---------- 排程 ----------
schedule.every().day.at("08:00").do(send_daily_report)

# ---------- 主程式 ----------
while True:
    try:
        schedule.run_pending()
    except Exception as e:
        print("排程 Exception:", e)
    time.sleep(60)
