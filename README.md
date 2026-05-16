# YouTube Skill Plugin untuk Pi Agent

Repositori ini berisi implementasi *skill* kustom untuk **Pi Coding Agent** (pi.dev) yang memungkinkan agen untuk mengontrol manajemen channel YouTube (autentikasi, upload video, dan edit metadata) serta **OBS Studio** melalui **REST API**.

## 🎯 Fitur Utama

- ✅ **YouTube Upload** — Upload video dengan metadata
- ✅ **YouTube Edit** — Edit judul, deskripsi, dan privacy video
- ✅ **YouTube Livestream** — Buat, mulai, dan akhiri live broadcast
- ✅ **OBS Control** — Kontrol scene, recording, streaming, audio, dan source via WebSocket
- ✅ **REST API** — Flask server dengan endpoint lengkap
- ✅ **Google OAuth** — Autentikasi aman

## 📁 Struktur Proyek

```text
Pi to Youtube/
├── core/
│   └── pi_agent_core.py          # Orchestrator skill
├── skills/
│   ├── youtube/                   # YouTube Skill
│   │   ├── upload_video.py
│   │   ├── edit_metadata.py
│   │   ├── youtube_auth.py
│   │   └── livestream.py
│   └── obs/                       # OBS Skill
│       ├── obs_websocket.py
│       ├── obs_control.py
│       └── obs_skill.py
├── pi_agent_rest_api.py           # Entry point REST API
└── requirements.txt
```

## 🚀 Setup

1. **Install dependencies:**
   ```bash
   python3 -m venv yt-agent-env
   source yt-agent-env/bin/activate
   pip install -r requirements.txt
   ```

2. **Setup Google OAuth:**
   - Buat project di [Google Cloud Console](https://console.cloud.google.com/)
   - Enable YouTube Data API v3
   - Download `client_secrets.json` ke root proyek

3. **Setup OBS (opsional):**
   - Tools → WebSocket Server Settings → Enable (port 4455)

4. **Jalankan server:**
   ```bash
   python pi_agent_rest_api.py
   ```

## 💡 Penggunaan

### YouTube

```bash
# Upload video
curl -X POST http://localhost:5000/upload -d '{
  "file_path": "/path/video.mp4",
  "title": "Judul Video",
  "privacy": "public"
}'

# Edit video
curl -X POST http://localhost:5000/edit -d '{
  "video_id": "VIDEO_ID",
  "title": "Judul Baru"
}'
```

### Livestream

```bash
# Buat livestream
curl -X POST http://localhost:5000/livestream/create -d '{
  "title": "Live Stream",
  "privacy": "public"
}'

# Mulai / akhiri
curl -X POST http://localhost:5000/livestream/start -d '{"broadcast_id": "ID"}'
curl -X POST http://localhost:5000/livestream/end   -d '{"broadcast_id": "ID"}'
```

### OBS Control

```bash
# Status
curl http://localhost:5000/obs/status

# Scene
curl -X POST http://localhost:5000/obs/scene -d '{"scene_name": "Scene 1"}'

# Recording
curl -X POST http://localhost:5000/obs/recording -d '{"command": "start"}'

# Streaming
curl -X POST http://localhost:5000/obs/streaming -d '{"command": "start"}'
```

## 📚 Dokumentasi

Dokumentasi tambahan tersedia di folder `docs/`:

- `CHANGELOG.md` — Log perubahan
- `QUICK_START.md` — Panduan cepat
- `PI_AGENT_INTEGRATION.md` — Integrasi Pi Agent CLI

---

*Proyek ini adalah skill provider untuk Pi Agent CLI.*
