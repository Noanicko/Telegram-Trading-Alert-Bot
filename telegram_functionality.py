import config as cfg
import requests
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{cfg.TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": cfg.TELEGRAM_CHAT_ID, "text": msg})
    except Exception as e:
        print(f"Telegram Error: {e}")