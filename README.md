# YouTube Skill Plugin untuk Pi Agent

Repositori ini berisi implementasi *skill* kustom untuk **Pi Coding Agent** (pi.dev) yang memungkinkan agen untuk mengontrol manajemen channel YouTube (autentikasi, upload video, dan edit metadata) melalui **REST API**.

## 🎯 Target & Capaian Saat Ini

**Capaian Saat Ini:**
- ✅ Skill YouTube untuk **upload video** dan **edit metadata**
- ✅ Skill YouTube untuk **live streaming** (buat, mulai, akhiri broadcast)
- ✅ REST API Server (Flask)
- ✅ Autentikasi Google OAuth (`client_secrets.json` & `token.pickle`)
- ✅ Integrasi *wrapper* untuk Pi Agent CLI

**Target Kedepan (Future Goals):**
- 🔲 Integrasi OBS ke YouTube yang dikontrol penuh melalui Bot Telegram.
- 🔲 Thumbnail otomatis dan penjadwalan upload.

## 📁 Struktur Proyek Utama

```text
Pi to Youtube/
├── core/                          # Orchestrator routing
├── skills/
│   └── youtube/
│       ├── upload_video.py        # Upload skill
│       ├── edit_metadata.py       # Edit metadata skill
│       ├── youtube_auth.py        # Google OAuth
│       └── livestream.py          # 🔴 Livestream skill (baru!)
├── interfaces/                    # Interfaces seperti Telegram
├── pi_agent_rest_api.py           # Entry point utama (REST API Server)
├── pi_agent_cli_integration.py    # Integrasi CLI Pi Agent
├── README.md                      
└── requirements.txt               
```

## 🚀 Instalasi & Setup

### 1. Install Dependencies
```bash
python3 -m venv yt-agent-env
source yt-agent-env/bin/activate
pip install -r requirements.txt
```

### 2. Setup Google OAuth
- Buat project di [Google Cloud Console](https://console.cloud.google.com/)
- Enable YouTube Data API v3
- Buat OAuth 2.0 credential (Desktop app)
- Download sebagai `client_secrets.json` dan letakkan di root proyek.

### 3. Jalankan REST API Server
```bash
yt-agent-env/bin/python pi_agent_rest_api.py
```
Server akan berjalan di `http://localhost:5000`.

## 💡 Cara Penggunaan (via Pi Agent CLI)

Proyek ini didesain untuk dikonsumsi oleh Pi Agent CLI. Contoh integrasinya:

```bash
# Cek status autentikasi
curl http://localhost:5000/status

# Upload video
curl -X POST http://localhost:5000/upload -H "Content-Type: application/json" -d '{
  "file_path": "/path/video.mp4",
  "title": "Tutorial Coding",
  "description": "Deskripsi video",
  "privacy": "private"
}'

# Buat livestream baru
curl -X POST http://localhost:5000/livestream/create -H "Content-Type: application/json" -d '{
  "title": "Pi Agent Live",
  "description": "Streaming via Pi Agent",
  "privacy": "private"
}'

# Mulai / akhiri livestream
curl -X POST http://localhost:5000/livestream/start -H "Content-Type: application/json" -d '{"broadcast_id": "BROADCAST_ID"}'
curl -X POST http://localhost:5000/livestream/end   -H "Content-Type: application/json" -d '{"broadcast_id": "BROADCAST_ID"}'
```

*(Lihat `PI_AGENT_INTEGRATION.md` untuk detail integrasi yang lebih lengkap).*
