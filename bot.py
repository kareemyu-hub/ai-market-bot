import os
import requests
import datetime
import feedparser
import traceback
import yfinance as yf
import time

# ------------------ 環境變數 ------------------
TOKEN = os.environ.get("TOKEN")       # Telegram Bot Token
CHAT_ID = os.environ.get("CHAT_ID")   # Telegram Chat ID
FINNHUB_KEY = os.environ.get("FINNHUB_KEY")  # Finnhub API Key

# ------------------ 新聞來源 ------------------
NEWS_FEEDS = [
    "https://www.reuters.com/rssFeed/wealth",
    "https://tw.finance.yahoo.com/rss/"
]

# ------------------ 熱門股票 ------------------
TOP_STOCKS = ["TSMC","NVDA","AAPL","TSLA","AMD"]

# ------------------ Telegram 發送 ------------------
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        r = requests.post(url, data=data, timeout=10)
        if r.status_code == 200:
            print(f"✅ Telegram 發送成功: {datetime.datetime.now()}")
        else:
            print(f"❌ Telegram 發送失敗: {r.text}")
    except Exception as e:
        print("❌ Telegram Exception:", e)
        print(traceback.format_exc())

# ------------------ 新聞抓取 + 情緒分析 ------------------
def fetch_news():
    headlines = []
    for feed_url in NEWS_FEEDS:
        try:
            d = feedparser.parse(feed_url)
            for entry in d.entries[:5]:
                title = entry.title
                summary = getattr(entry,"summary","")
                sentiment = analyze_sentiment(title + summary)
                headlines.append(f"{sentiment} {title}\n{entry.link}")
        except:
            headlines.append("- 無法抓取新聞")
    return headlines

def analyze_sentiment(text):
    text = text.lower()
    if any(k in text for k in ["上漲","利多","看好","漲"]):
        return "📈利多"
    elif any(k in text for k in ["下跌","利空","警告","跌"]):
        return "📉利空"
    else:
        return "⚖️中性"

# ------------------ 台股即時漲跌 ------------------
def fetch_tw_stock(stock_no):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={stock_no}&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        c = float(data.get("c",0))  # 最新價
        o = float(data.get("o",0))  # 開盤價
        change = ((c - o)/o)*100 if o>0 else 0
        return round(change,2)
    except:
        return 0.0

# ------------------ 美股 / Crypto ------------------
def fetch_yf_change(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1d", interval="5m")
        change = ((data['Close'][-1]-data['Close'][0])/data['Close'][0])*100
        return round(change,2)
    except:
        return 0.0

# ------------------ 生成晨報訊息 ------------------
def generate_report():
    today = datetime.date.today()
    headlines = fetch_news()

    # 台股
    tw_map = {"TSMC":"2330.TW"}
    tw_stock = {name: fetch_tw_stock(no) for name,no in tw_map.items()}

    # 美股
    global_map = {"S&P500":"^GSPC","NASDAQ":"^IXIC"}
    global_change = {k: fetch_yf_change(v) for k,v in global_map.items()}

    # Crypto
    crypto_symbols = {"BTC":"BTC-USD","ETH":"ETH-USD"}
    crypto = {k: fetch_yf_change(v) for k,v in crypto_symbols.items()}

    # --------- 組訊息 ----------
    message = f"📊 AI市場雷達 {today}\n\n"

    gm_text = "🌎 全球市場：\n"
    for k,v in global_change.items():
        arrow = "⬆️" if v>0 else "⬇️" if v<0 else "⏺️"
        gm_text += f"{k} {v:+.2f}% {arrow}, "
    message += gm_text.rstrip(", ") + "\n\n"

    tw_text = "🇹🇼 台股市場：\n"
    for k,v in tw_stock.items():
        arrow = "⬆️" if v>0 else "⬇️" if v<0 else "⏺️"
        tw_text += f"{k} {v:+.2f}% {arrow}, "
    message += tw_text.rstrip(", ") + "\n\n"

    crypto_text = "💰 加密市場：\n"
    for k,v in crypto.items():
        arrow = "⬆️" if v>0 else "⬇️" if v<0 else "⏺️"
        crypto_text += f"{k} {v:+.2f}% {arrow}, "
    message += crypto_text.rstrip(", ") + "\n\n"

    message += "📰 最新新聞摘要：\n" + "\n".join(headlines) + "\n\n"

    message += "🎯 今日熱門股票：\n"
    for s in TOP_STOCKS:
        change = fetch_yf_change(s) if s!="TSMC" else tw_stock["TSMC"]
        arrow = "⬆️" if change>0 else "⬇️" if change<0 else "⏺️"
        message += f"{s} {change:+.2f}% {arrow}, "
    message = message.rstrip(", ") + "\n\n"

    message += "📅 今日重要事件：\n21:30 美國 CPI, 22:45 製造業 PMI\n"

    return message

# ------------------ 發送晨報 ------------------
def send_daily_report():
    report = generate_report()
    send_telegram(report)

# ------------------ 自動循環，每 2 小時執行 ------------------
INTERVAL = 2 * 60 * 60  # 兩小時 = 7200 秒

if __name__ == "__main__":
    while True:
        print(f"⏰ 執行晨報程式: {datetime.datetime.now()}")
        send_daily_report()
        print(f"💤 等待 {INTERVAL/3600} 小時後再次執行...")
        time.sleep(INTERVAL)
