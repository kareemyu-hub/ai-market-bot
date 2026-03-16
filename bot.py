import os
import requests
import datetime
import feedparser
import traceback
import yfinance as yf
import time

# ------------------ 環境變數 ------------------
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
FINNHUB_KEY = os.environ.get("FINNHUB_KEY")

# ------------------ 新聞來源 ------------------
NEWS_FEEDS = [
    "https://www.reuters.com/rssFeed/wealth",
    "https://tw.finance.yahoo.com/rss/"
]

# ------------------ 熱門股票 ------------------
TOP_STOCKS = ["TSMC","NVDA","AAPL","TSLA","AMD"]

# ------------------ AI概念股 ------------------
AI_STOCKS = ["NVDA","AMD","TSM","AAPL","TSLA"]

# ------------------ 緩存最後一次資料 ------------------
LAST_DATA = {
    "global": {},
    "tw": {},
    "crypto": {},
    "ai_strength": None,
    "stocks": {}
}

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

# ------------------ 系統啟動測試訊息 ------------------
def send_startup_test():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    message = f"""
🤖 AI市場雷達系統啟動

時間：
{now}

狀態：
✅ 系統正常運作
"""
    send_telegram(message)

# ------------------ 新聞抓取 + 情緒分析 ------------------
def fetch_news():
    headlines = []
    seen_titles = set()
    for feed_url in NEWS_FEEDS:
        try:
            d = feedparser.parse(feed_url)
            for entry in d.entries[:10]:
                title = entry.title
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                summary = getattr(entry,"summary","")
                sentiment = analyze_sentiment(title + summary)
                headlines.append(f"{sentiment} {title}\n{entry.link}")
                if len(headlines) >= 5:
                    break
            if len(headlines) >= 5:
                break
        except:
            continue
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
        now = datetime.datetime.now()
        if now.hour < 9 or now.hour > 13:
            return None
        url = f"https://finnhub.io/api/v1/quote?symbol={stock_no}&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        c = float(data.get("c", 0))
        o = float(data.get("o", 0))
        if c == 0 or o == 0:
            return None
        change = ((c - o)/o)*100
        return round(change,2)
    except:
        return None

# ------------------ 美股 / Crypto ------------------
def fetch_yf_change(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1d", interval="5m")
        if data.empty or len(data['Close']) < 2:
            return None
        change = ((data['Close'][-1]-data['Close'][0])/data['Close'][0])*100
        return round(change,2)
    except:
        return None

# ------------------ AI概念股強度 ------------------
def fetch_ai_strength():
    count_up = 0
    valid_stocks = 0
    for s in AI_STOCKS:
        change = fetch_yf_change(s)
        if change is not None:
            valid_stocks += 1
            if change>0:
                count_up += 1
    if valid_stocks == 0:
        return "資料不足 ⚪️"
    return f"{count_up}/{len(AI_STOCKS)} 上漲 🔥"

# ------------------ 生成市場報告 ------------------
def generate_report():
    now_time = datetime.datetime.now().strftime("%H:%M")
    today = datetime.date.today()
    headlines = fetch_news()

    message = f"📊 AI市場雷達 {today} {now_time}\n\n"

    # 全球市場
    global_map = {"S&P500":"^GSPC","NASDAQ":"^IXIC"}
    global_change = {}
    for k,v in global_map.items():
        val = fetch_yf_change(v)
        if val is None:
            val = LAST_DATA["global"].get(k)
        else:
            LAST_DATA["global"][k] = val
        global_change[k] = val

    gm_text = "🌎 全球市場：\n"
    for k,v in global_change.items():
        if v is None:
            gm_text += f"{k} 暫無資料 ⚪️, "
        else:
            arrow = "⬆️" if v>0 else "⬇️" if v<0 else "⚪️"
            gm_text += f"{k} {v:+.2f}% {arrow} (最後更新 {now_time}), "
    message += gm_text.rstrip(", ") + "\n\n"

    # 台股
    tw_map = {"TSMC":"TWSE:2330"}
    tw_stock = {}
    for name,no in tw_map.items():
        val = fetch_tw_stock(no)
        if val is None:
            val = LAST_DATA["tw"].get(name)
        else:
            LAST_DATA["tw"][name] = val
        tw_stock[name] = val

    tw_text = "🇹🇼 台股市場：\n"
    for k,v in tw_stock.items():
        if v is None:
            tw_text += f"{k} 非交易時間 ⚪️, "
        else:
            arrow = "⬆️" if v>0 else "⬇️"
            tw_text += f"{k} {v:+.2f}% {arrow} (最後更新 {now_time}), "
    message += tw_text.rstrip(", ") + "\n\n"

    # Crypto
    crypto_symbols = {"BTC":"BTC-USD","ETH":"ETH-USD"}
    crypto = {}
    for k,v in crypto_symbols.items():
        val = fetch_yf_change(v)
        if val is None:
            val = LAST_DATA["crypto"].get(k)
        else:
            LAST_DATA["crypto"][k] = val
        crypto[k] = val

    crypto_text = "💰 加密市場：\n"
    for k,v in crypto.items():
        if v is None:
            crypto_text += f"{k} 暫無資料 ⚪️, "
        else:
            arrow = "⬆️" if v>0 else "⬇️"
            crypto_text += f"{k} {v:+.2f}% {arrow} (最後更新 {now_time}), "
    message += crypto_text.rstrip(", ") + "\n\n"

    # 新聞摘要
    if headlines:
        message += "📰 最新新聞摘要：\n" + "\n".join(headlines) + "\n\n"

    # AI板塊強度
    ai_val = fetch_ai_strength()
    if ai_val != "資料不足 ⚪️":
        LAST_DATA["ai_strength"] = ai_val
    else:
        ai_val = LAST_DATA.get("ai_strength", "資料不足 ⚪️")
    message += f"🧠 AI板塊強度： {ai_val} (最後更新 {now_time})\n\n"

    # 熱門股票
    message += "🎯 今日熱門股票：\n"
    for s in TOP_STOCKS:
        if s=="TSMC":
            val = tw_stock.get("TSMC")
        else:
            val = fetch_yf_change(s)
            if val is None:
                val = LAST_DATA["stocks"].get(s)
            else:
                LAST_DATA["stocks"][s] = val
        if val is None:
            continue
        arrow = "⬆️" if val>0 else "⬇️"
        message += f"{s} {val:+.2f}% {arrow} (最後更新 {now_time}), "
    message = message.rstrip(", ") + "\n\n"

    message += "📅 今日重要事件：\n21:30 美國 CPI, 22:45 製造業 PMI\n"

    return message

# ------------------ 發送晨報 ------------------
def send_daily_report():
    report = generate_report()
    send_telegram(report)

# ------------------ 自動循環，每1小時 ------------------
INTERVAL = 60 * 60  # 1小時

if __name__ == "__main__":
    print("🚀 系統啟動")
    send_startup_test()  # 啟動測試訊息

    while True:
        print(f"⏰ 執行市場雷達: {datetime.datetime.now()}")
        send_daily_report()
        print(f"💤 等待 {INTERVAL/3600} 小時...")
        time.sleep(INTERVAL)
