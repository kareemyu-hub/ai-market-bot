import os
import requests
import datetime
import feedparser
import traceback
import time

# ---------- 模式選擇 ----------
# True → 測試模式，每分鐘發一次，方便確認
# False → 正式模式，每天固定時間由 Railway Scheduler 執行
TEST_MODE = True

# ---------- 環境變數 ----------
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ---------- 發送 Telegram ----------
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        r = requests.post(url, data=data, timeout=10)
        if r.status_code == 200:
            print("✅ Telegram 發送成功")
        else:
            print(f"❌ Telegram 發送失敗: {r.text}")
    except Exception as e:
        print("❌ Telegram Exception:", e)
        print(traceback.format_exc())

# ---------- 抓新聞 ----------
NEWS_FEEDS = [
    "https://www.reuters.com/rssFeed/wealth",
    "https://tw.finance.yahoo.com/rss/"
]

def fetch_news():
    headlines = []
    for feed_url in NEWS_FEEDS:
        try:
            d = feedparser.parse(feed_url)
            for entry in d.entries[:3]:
                headlines.append(f"- {entry.title}\n{entry.link}")
        except:
            headlines.append("- 無法抓取新聞")
    return headlines

# ---------- 生成訊息 ----------
def generate_report():
    today = datetime.date.today()
    headlines = fetch_news()
    message = f"📊 AI市場雷達 {today}\n\n"
    message += "🌎 全球市場: S&P500 +0.8%, NASDAQ +1.2%, 市場情緒偏多\n\n"
    message += "🇹🇼 台股可能影響: 半導體↑, AI供應鏈↑, 航運↓\n\n"
    message += "💰 加密市場: BTC震盪偏多, ETH穩定\n\n"
    message += "📰 今日新聞:\n" + "\n".join(headlines[:5]) + "\n\n"
    message += "🎯 今日熱門股票: NVDA, TSMC, AAPL, TSLA, AMD\n\n"
    message += "📅 今日重要事件:\n21:30 美國 CPI, 22:45 製造業 PMI\n"
    return message

# ---------- 發送晨報 ----------
def send_daily_report():
    print("DEBUG: send_daily_report 被呼叫")
    report = generate_report()
    send_telegram(report)

# ---------- 主程式 ----------
if __name__ == "__main__":
    if TEST_MODE:
        # 測試模式：每分鐘發一次訊息，連續 3 次
        for i in range(3):
            send_daily_report()
            print(f"⏱ 等待 60 秒後發送下一次 ({i+1}/3)")
            time.sleep(60)
    else:
        # 正式模式：每天由 Railway Scheduler 執行一次
        send_daily_report()
