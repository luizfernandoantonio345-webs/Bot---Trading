import json
import os
from datetime import datetime

# 🔥 CAMINHO ABSOLUTO PARA O APP (CORRIGIDO)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

JSON_PATH = os.path.join(
    BASE_DIR,
    "..", "..", "..",        # sai de bot-core → bot.trading → Desktop
    "app_copilot",
    "data",
    "signals.json"
)

def send_to_copilot(pair, side, confidence, result="OPEN"):
    payload = {
        "bot_status": "ATIVO",
        "signals": [
            {
                "pair": pair,
                "type": side,
                "confidence": int(confidence),
                "time": datetime.now().strftime("%H:%M"),
                "result": result
            }
        ]
    }

    try:
        os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)

        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        print(f"📡 Copilot atualizado | {pair} {side} | {result}")

    except Exception as e:
        print("❌ Erro ao enviar sinal para o Trading Copilot:", e)
