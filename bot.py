import os
import datetime
import requests
import feedparser
import yfinance as yf
import traceback

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TEST_MODE = False

NEWS_FEEDS = [
    "https://www.reuters.com/rssFeed/wealth",
    "https://tw.finance.yahoo.com/rss/"
]

TOP_STOCKS = ["TSMC", "NVDA", "AAPL", "TSLA", "AMD"]

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

def fetch_news():
    headlines = []
    for feed_url in NEWS_FEEDS:
        try:
            d = feedparser.parse(feed_url)
            for entry in d.entries[:5]:
                title = entry.title
                summary = getattr(entry, "summary", "")
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

def fetch_market_data():
    # 全球市場
    global_market = {}
    for symbol,name in [("^GSPC","S&P500"),("^IXIC","NASDAQ")]:
        try:
            data = yf.Ticker(symbol).history(period="2d")
            change = ((data['Close'][-1]-data['Close'][-2])/data['Close'][-2])*100
            global_market[name] = round(change,2)
        except:
            global_market[name] = 0.0

    # 台股熱門股
    tw_stock = {}
    for stock in TOP_STOCKS:
        try:
            symbol_map = {"TSMC":"2330.TW","NVDA":"NVDA","AAPL":"AAPL","TSLA":"TSLA","AMD":"AMD"}
            symbol = symbol_map[stock]
            data = yf.Ticker(symbol).history(period="2d")
            change = ((data['Close'][-1]-data['Close'][-2])/data['Close'][-2])*100
            tw_stock[stock] = round(change,2)
        except:
            tw_stock[stock] = 0.0

    # 加密貨幣
    crypto = {}
    for coin,symbol in [("BTC","BTC-USD"),("ETH","ETH-USD")]:
        try:
            data = yf.Ticker(symbol).history(period="2d")
            change = ((data['Close'][-1]-data['Close'][-2])/data['Close'][-2])*100
            crypto[coin] = round(change,2)
        except:
            crypto[coin] = 0.0

    return global_market, tw_stock, crypto

def generate_report():
    today = datetime.date.today()
    headlines = fetch_news()
    global_market, tw_stock, crypto = fetch_market_data()

    message = f"📊 AI市場雷達 {today}\n\n"

    gm_text = "🌎 全球市場：\n"
    for k,v in global_market.items():
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
        message += f"{s} {tw_stock[s]:+0.2f}% , "
    message = message.rstrip(", ") + "\n\n"

    message += "📅 今日重要事件：\n21:30 美國 CPI, 22:45 製造業 PMI\n"

    return message

def send_daily_report():
    print("DEBUG: send_daily_report 被呼叫")
    report = generate_report()
    send_telegram(report)

if __name__ == "__main__":
    send_daily_report()
