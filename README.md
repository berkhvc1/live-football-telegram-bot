# ⚽ Live Football VAR & Goal Tracker Bot

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![Telegram API](https://img.shields.io/badge/Telegram-Bot%20API-blue?style=flat-square&logo=telegram)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)

Dış bir spor API'sini kullanarak dünyadaki tüm canlı futbol maçlarını anlık olarak takip eden, skor değişikliklerini ve VAR (Video Assistant Referee) kararıyla iptal edilen golleri tespit edip Telegram üzerinden bildirim gönderen **olay güdümlü (event-driven)** bir otomasyon botudur.

## 🚀 Proje Mimarisi ve Yetenekler

Bu proje, temel veri çekme (fetching) işlemlerinin ötesine geçerek **Durum Yönetimi (State Management)** ve **Bellek İçi Önbellekleme (In-Memory Caching)** tekniklerini kullanır. 

* **⚡ Anlık Gol Bildirimi:** Takip edilen maçlardan herhangi birinde gol olduğunda, hafızadaki skorla güncel skoru karşılaştırır ve anında bildirim atar.
* **❌ VAR / Gol İptali Tespiti:** API'den gelen toplam skor, hafızadaki skordan daha düşük bir seviyeye gerilerse, sistem bunu bir "Gol İptali" olarak algılar ve kullanıcıyı uyarır.
* **🔄 Otonom Çalışma:** `schedule` modülü sayesinde sürekli insan müdahalesi gerektirmeden arka planda belirlenen periyotlarda çalışır.
* **🔒 Güvenlik:** API anahtarları ve Telegram Token'ları `.env` dosyası ile izole edilerek kod tabanından (hardcoding) uzak tutulmuştur.

## 🛠️ Kullanılan Teknolojiler

* **Programlama Dili:** Python
* **Dış Servisler:** RESTful API (`football-data.org`), Telegram Bot API
* **Temel Kütüphaneler:**
  * `requests` (HTTP istekleri ve JSON veri işleme)
  * `schedule` (Görev zamanlama ve arka plan otomasyonu)
  * `python-dotenv` (Çevre değişkenleri yönetimi)

## 📸 Ekran Görüntüsü

<img width="1600" height="860" alt="Image" src="https://github.com/user-attachments/assets/66c9665c-ddc4-40b5-b8fe-ac26faee36cb" />
<img width="1600" height="860" alt="Image" src="https://github.com/user-attachments/assets/c944e25a-acae-4e15-834b-bafba663f89c" />

## ⚙️ Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda veya sunucunuzda çalıştırmak için aşağıdaki adımları izleyin:

**1. Repoyu Klonlayın ve Bağımlılıkları Yükleyin**
```bash
git clone [https://github.com/](https://github.com/)[Kullanici_Adiniz]/[Repo_Adiniz].git
cd [Repo_Adiniz]
pip install -r requirements.txt
```
**2. Ana dizinde .env adında bir dosya oluşturun ve bilgilerinizi girin:**
```env
API_KEY=sizin_football_data_api_anahtariniz
TELEGRAM_TOKEN=sizin_telegram_bot_tokeniniz
```
**3. main.py dosyası içindeki CHAT_ID değişkenine mesajın gönderileceği Telegram numaranızı girin.**
**4.Botu Başlatın**
```bash
python main.py
```
👨‍💻 Geliştirici
Bekir Berk Kahveci

LinkedIn: www.linkedin.com/in/bekir-berk-kahveci-02771a376

GitHub: @berkhvc1
