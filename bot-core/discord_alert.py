import requests
from datetime import datetime
from config import SYMBOL

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1459376997884100800/JFJg9sH-Ul-T4iM-Coj7zswpJK77wCtbnZJZepog8ppE0PZ_1B6pGmz99C1UoFOMcARm"

def enviar_alerta(msg, titulo="BOT MT5"):
    payload = {
        "username": "BOT MT5",
        "embeds": [
            {
                "title": titulo,
                "description": msg,
                "color": 5814783,
                "footer": {
                    "text": f"{SYMBOL} | {datetime.now().strftime('%H:%M:%S')}"
                }
            }
        ]
    }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        print("Erro Discord:", e)
