import json
import os
import time
import requests
import schedule
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

CHAT_ID = "6982718235"

STATE_FILE = "bot_state.json"

# BOTUN HAFIZASI: Maçların eski skorlarını burada tutacağız
onceki_skorlar = {}
# Daha önce aynı maç için gönderilmiş son skor
son_gonderilen_skor = {}

def load_state():
    global onceki_skorlar, son_gonderilen_skor
    if not os.path.exists(STATE_FILE):
        return
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        onceki_skorlar = {int(k): tuple(v) for k, v in state.get("onceki_skorlar", {}).items()}
        son_gonderilen_skor = {int(k): tuple(v) for k, v in state.get("son_gonderilen_skor", {}).items()}
        print("🔁 Önceki bot durumu yüklendi.")
    except Exception as e:
        print(f"❌ Durum yükleme hatası: {e}")


def save_state():
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "onceki_skorlar": {str(k): list(v) for k, v in onceki_skorlar.items()},
                    "son_gonderilen_skor": {str(k): list(v) for k, v in son_gonderilen_skor.items()},
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
    except Exception as e:
        print(f"❌ Durum kaydetme hatası: {e}")


def send_telegram_message(message):
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN ayarlı değil. .env dosyanızı kontrol edin.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        res = requests.post(url, json=payload, timeout=10)
        try:
            body = res.json()
        except Exception:
            body = res.text

        if res.status_code != 200:
            print(f"❌ Telegram API HTTP {res.status_code}: {body}")
            return False
        else:
            # Telegram returns JSON with 'ok': True on success
            if isinstance(body, dict) and not body.get("ok", False):
                print(f"❌ Telegram API hata: {body}")
                return False
            else:
                print("💬 Telegram bildirimi gönderildi.")
                return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Mesaj gönderilemedi (istek hatası): {e}")
        return False
    except Exception as e:
        print(f"❌ Mesaj gönderilemedi: {e}")
        return False

def check_matches():
    print("🔍 Canlı maçlar ve gol durumları kontrol ediliyor...")
    api_url = "https://api.football-data.org/v4/matches?status=IN_PLAY"
    headers = {"X-Auth-Token": API_KEY}

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        data = response.json()

        if "matches" in data and len(data["matches"]) > 0:
            for match in data["matches"]:
                match_id = match["id"]
                home_team = match["homeTeam"]["name"]
                away_team = match["awayTeam"]["name"]
                score = match.get("score", {})
                full_time = score.get("fullTime") or {}
                half_time = score.get("halfTime") or {}

                home_goals = full_time.get("home")
                away_goals = full_time.get("away")
                if home_goals is None or away_goals is None:
                    home_goals = half_time.get("home") if half_time.get("home") is not None else 0
                    away_goals = half_time.get("away") if half_time.get("away") is not None else 0

                home_goals = home_goals if home_goals is not None else 0
                away_goals = away_goals if away_goals is not None else 0
                yeni_skor = (home_goals, away_goals)
                onceki_skor = onceki_skorlar.get(match_id)
                onceki_toplam = sum(onceki_skor) if onceki_skor is not None else None
                yeni_toplam = sum(yeni_skor)

                print(
                    f"▶️ {match_id}: {home_team} {home_goals}-{away_goals} {away_team} "
                    f"(onceki: {onceki_skor if onceki_skor is not None else 'yok'})"
                )

                if match_id not in onceki_skorlar:
                    onceki_skorlar[match_id] = yeni_skor
                    if yeni_toplam > 0:
                        son_gonderilen_skor[match_id] = yeni_skor
                    save_state()
                    print(f"📌 Takip başladı: {home_team} {home_goals} - {away_goals} {away_team}")
                    continue

                if yeni_toplam > onceki_toplam:
                    if son_gonderilen_skor.get(match_id) == yeni_skor:
                        print("⚠️ Aynı gol bildirimi zaten gönderildi, atlanıyor.")
                    else:
                        mesaj = (
                            f"🚨 <b>GOOOOOOOL!</b> ⚽\n\n"
                            f"🏟️ {home_team} <b>{home_goals} - {away_goals}</b> {away_team}\n"
                            f"⚡ Skor değişti!"
                        )
                        if send_telegram_message(mesaj):
                            print(f"✅ Gol tespit edildi: {home_team} {home_goals}-{away_goals} {away_team}")
                            son_gonderilen_skor[match_id] = yeni_skor
                            save_state()
                        else:
                            print("⚠️ Telegram gönderimi başarısız oldu, tekrar denenecek.")
                    onceki_skorlar[match_id] = yeni_skor

                elif yeni_toplam < onceki_toplam:
                    if son_gonderilen_skor.get(match_id) == yeni_skor:
                        print("⚠️ Aynı iptal skoru zaten bildirim gönderildi, atlanıyor.")
                    else:
                        mesaj = (
                            f"❌ <b>GOL İPTAL EDİLDİ! (VAR)</b>\n\n"
                            f"🏟️ {home_team} <b>{home_goals} - {away_goals}</b> {away_team}\n"
                            f"⚠️ Hakem veya VAR kararıyla skor geri alındı!"
                        )
                        if send_telegram_message(mesaj):
                            print(f"⚠️ Gol iptali tespit edildi: {home_team} {home_goals}-{away_goals} {away_team}")
                            son_gonderilen_skor[match_id] = yeni_skor
                            save_state()
                        else:
                            print("⚠️ Telegram gönderimi başarısız oldu, tekrar denenecek.")
                    onceki_skorlar[match_id] = yeni_skor
                else:
                    if yeni_skor != onceki_skor:
                        print("ℹ️ Skor değişti ama toplam gol aynı; veri tekrar kontrol edilecek.")
                    else:
                        print("ℹ️ Skor değişmedi.")
        else:
            print("ℹ️ Şu anda canlı oynanan maç yok.")

    except Exception as e:
        print(f"❌ API Hatası: {e}")

def main():
    load_state()
    # İlk çalıştırmada mevcut skorları hafızaya kaydeder
    check_matches()

    # Her 1 dakikada bir gol kontrolü yap
    schedule.every(1).minutes.do(check_matches)

    print("🤖 Canlı Gol ve İptal Takip Botu Başladı... Kapatmak için CTRL+C")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()