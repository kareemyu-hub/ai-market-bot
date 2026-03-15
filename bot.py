import requests
import datetime
import feedparser
import schedule
import time

# ---------- 設定你的 Telegram ----------
TOKEN = "8376472754:AAGm6qABSN8yW5yz7Xd5ZV98hN2Llo1D3ns"
CHAT_ID = "5291962805"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

# ---------- 全球市場新聞 RSS / API ----------

NEWS_FEEDS = [
    "https://www.reuters.com/rssFeed/wealth",      # Reuters 財經
    "https://www.bloomberg.com/feed/podcast/market-update", # Bloomberg 市場更新
    "https://tw.finance.yahoo.com/rss/"           # Yahoo 財經
]

def fetch_news():
    headlines = []
    for feed in NEWS_FEEDS:
        d = feedparser.parse(feed)
        for entry in d.entries[:3]:  # 每個來源抓前三篇
            headlines.append(f"- {entry.title}\n{entry.link}")
    return headlines

# ---------- 市場異動 / 監控股票 ----------

WATCHED_STOCKS = ["NVDA", "TSMC", "AAPL", "TSLA", "AMD"]
WATCHED_CRYPTO = ["BTC", "ETH"]

def market_analysis():
    # 這裡示範抓固定範例數據，可接實際 API
    analysis = {
        "US Market": "S&P500 +0.8%, NASDAQ +1.2%, 市場情緒偏多",
        "Taiwan Market": "半導體↑, AI供應鏈↑, 航運↓",
        "Crypto": "BTC震盪偏多, 資金流入"
    }
    return analysis

# ---------- 熱門股票雷達 ----------

def hot_stocks():
    return WATCHED_STOCKS

# ---------- 今日重要事件 ----------

def today_events():
    events = [
        "21:30 美國 CPI 公布",
        "22:45 製造業 PMI",
        "02:00 FOMC 利率會議"
    ]
    return events

# ---------- 生成完整訊息 ----------

def generate_report():
    today = datetime.date.today()
    headlines = fetch_news()
    market = market_analysis()
    stocks = hot_stocks()
    events = today_events()

    message = f"📊 AI市場雷達 {today}\n\n"

    # 全球市場
    message += f"🌎 全球市場:\n{market['US Market']}\n\n"

    # 台股影響
    message += f"🇹🇼 台股可能影響:\n{market['Taiwan Market']}\n\n"

    # 加密市場
    message += f"💰 加密市場:\n{market['Crypto']}\n\n"

    # 今日重要新聞
    message += "📰 重要新聞:\n" + "\n".join(headlines[:5]) + "\n\n"

    # 今日熱門股票
    message += "🎯 今日熱門股票:\n" + ", ".join(stocks) + "\n\n"

    # 今日事件提醒
    message += "📅 今日重要事件:\n" + "\n".join(events) + "\n\n"

    # 市場異動 / 突發新聞提示
    message += "🚨 市場異動 / 突發新聞會自動推播\n"

    return message

# ---------- 發送晨報 ----------
def send_daily_report():
    report = generate_report()
    send_telegram(report)

# ---------- 排程 ----------
schedule.every().day.at("08:00").do(send_daily_report)

# ---------- 主程式持續運行 ----------
while True:
    schedule.run_pending()
    time.sleep(60)
