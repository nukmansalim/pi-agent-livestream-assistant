# Panduan Setup: YouTube Skill REST API di Raspberry Pi

Panduan ini ditujukan untuk mengatur dan menjalankan server `pi_agent_rest_api.py` secara terus-menerus (persistent) di environment Raspberry Pi agar dapat diakses oleh Pi Agent CLI.

## 📋 Prerequisites
1. **Credentials**: `client_secrets.json` (dari Google Cloud Console)
2. **Environment**: Python 3.7+ dan Virtual Environment terinstall

## 🚀 Cara Run di Raspberry Pi

### 1. Setup Environment
```bash
cd "/home/nukman/Dokumen/Pi to Youtube"
python3 -m venv yt-agent-env
source yt-agent-env/bin/activate
pip install -r requirements.txt
```

### 2. Run API Server (Test)
```bash
python pi_agent_rest_api.py
```

## 📝 Run in Background (Persistent)

Gunakan `systemd` agar REST API berjalan otomatis setiap kali Raspberry Pi dinyalakan.

Buat file `/etc/systemd/system/pi-agent-youtube-api.service`:

```ini
[Unit]
Description=Pi Agent YouTube REST API
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/nukman/Dokumen/Pi to Youtube
ExecStart=/home/nukman/Dokumen/Pi to Youtube/yt-agent-env/bin/python pi_agent_rest_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Jalankan perintah berikut:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pi-agent-youtube-api
sudo systemctl start pi-agent-youtube-api
sudo systemctl status pi-agent-youtube-api
```

*Catatan: Integrasi Bot Telegram dan OBS untuk Live Streaming akan ditambahkan pada fase pengembangan berikutnya (belum diimplementasi).*
