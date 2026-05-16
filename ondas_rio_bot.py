 
import requests, schedule, time
from datetime import datetime

BOT_TOKEN  = "8201425911:AAE6aedoTWkIT-2t4uWX_DBjADgdrjQK72s"
CHAT_ID    = CHAT_IDS = [
    "6087428840",   # Alexandre
]
HORA_ENVIO = "07:00"
ALERTA_MIN = 1.0

PRAIAS = {
  "Ipanema / Arpoador": (-22.9868, -43.2075),
  "Leblon":             (-22.9869, -43.2268),
  "Copacabana":         (-22.9714, -43.1851),
  "Barra da Tijuca":    (-23.0068, -43.3653),
  "Recreio":            (-23.0213, -43.4672),
  "Prainha":            (-23.0443, -43.5122),
  "Grumari":            (-23.0551, -43.5231),
}

def get_ondas(lat, lon):
    url = "https://marine-api.open-meteo.com/v1/marine"
    r = requests.get(url, params={
        "latitude": lat, "longitude": lon,
        "hourly": "wave_height,wave_period,wave_direction",
        "timezone": "America/Sao_Paulo",
        "forecast_days": 1
    })
    data = r.json()["hourly"]
    hora_atual = datetime.now().hour
    return {
        "altura":  data["wave_height"][hora_atual],
        "periodo": data["wave_period"][hora_atual],
        "direcao": data["wave_direction"][hora_atual],
    }

def send_msg(texto):
    for chat_id in CHAT_IDS:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": texto, "parse_mode": "HTML"}
        )
        print("Resposta Telegram:", r.json())
def enviar_previsao():
    hoje = datetime.now().strftime("%d/%m/%Y")
    msg = f"🌊 <b>Previsão de Ondas — {hoje}</b>\n\n"
    for praia, (lat, lon) in PRAIAS.items():
        print(f"Buscando {praia}...")
        d = get_ondas(lat, lon)
        h = d["altura"]; p = d["periodo"]
        emoji = "🟢" if h >= 1.0 else ("🟡" if h >= 0.5 else "🔴")
        msg += f"{emoji} <b>{praia}</b>: {h:.1f}m · {p:.0f}s\n"
        print(f"{praia}: {h:.1f}m OK")
    msg += "\n🟢 ≥1m  🟡 0.5-1m  🔴 <0.5m"
    print("Enviando mensagem...")
    send_msg(msg)
    print("Enviado!")

def checar_alertas():
    for praia, (lat, lon) in PRAIAS.items():
        d = get_ondas(lat, lon)
        if d["altura"] >= ALERTA_MIN:
            send_msg(
                f"🚨 <b>ALERTA</b> — {praia}\n"
                f"Ondas de {d['altura']:.1f}m agora!\n"
                f"Período: {d['periodo']:.0f}s"
            )

schedule.every().day.at(HORA_ENVIO).do(enviar_previsao)
schedule.every(3).hours.do(checar_alertas)

print("🏄 Bot rodando... (Ctrl+C para parar)")
enviar_previsao()

while True:
    schedule.run_pending()
    time.sleep(60)
