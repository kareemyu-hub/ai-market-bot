import requests
import datetime

TOKEN = "你的BOT TOKEN"
CHAT_ID = "你的CHAT ID"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)

today = datetime.date.today()

message = f"""
📊 AI市場晨報 {today}

🌎 美股觀察
留意科技股與AI股

🇹🇼 台股影響
半導體
AI供應鏈

💰 加密市場
BTC趨勢觀察

📅 今日重要事件
CPI / 利率政策

🎯 市場焦點
AI
半導體
科技股
"""

send_message(message)
