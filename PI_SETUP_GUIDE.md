# Pi Agent - Panduan Menjalankan di Raspberry Pi

## 📋 Prerequisites (WAJIB ada sebelum run)

### 1. **Credentials**
   - ✅ `client_secrets.json` (dari Google Cloud Console)
   - ✅ Telegram Bot Token (dari @BotFather)

### 2. **Python & Dependencies**
   - ✅ Python 3.7+ (biasanya sudah ada di Pi OS)
   - ✅ pip
   - ✅ Virtual environment

---

## 🚀 Cara Run di Raspberry Pi

### Opsi 1: Setup Script (Recommended)

```bash
cd /home/nukman/Dokumen/Pi\ to\ Youtube
bash setup_pi.sh
```

Script ini akan:
- ✅ Check Python
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Show next steps

### Opsi 2: Manual Setup

```bash
# 1. Go to project directory
cd /home/nukman/Dokumen/Pi\ to\ Youtube

# 2. Create virtual environment (first time only)
python3 -m venv yt-agent-env

# 3. Activate it
source yt-agent-env/bin/activate

# 4. Install dependencies (first time only)
pip install -r requirements.txt

# 5. Set bot token
export TELEGRAM_BOT_TOKEN='your_bot_token_from_botfather'

# 6. Run the bot
python main.py telegram
```

---

## ✅ Checklist Sebelum Jalankan

```
Prerequisites:
□ Sudah ada client_secrets.json (Google OAuth credentials)
□ Sudah ada Telegram bot token
□ Pi punya internet connection
□ Python 3.7+ tersedia

Setup:
□ Virtual environment sudah dibuat
□ Dependencies sudah installed
□ TELEGRAM_BOT_TOKEN sudah di-export

Runtime:
□ Pi sudah aktif dan terhubung ke internet
□ Bot bisa menerima pesan (polling active)
```

---

## 🔧 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'telegram'`
**Solusi:** Pastikan virtual environment aktif:
```bash
source yt-agent-env/bin/activate
pip install -r requirements.txt
```

### Error: `TELEGRAM_BOT_TOKEN tidak ditemukan`
**Solusi:** Set environment variable:
```bash
export TELEGRAM_BOT_TOKEN='your_actual_token'
python main.py telegram
```

### Bot tidak menerima pesan
**Solusi:**
- Check internet connection di Pi
- Check bot sudah running (lihat terminal)
- Kirim pesan di Telegram setelah bot start

### Pi tiba-tiba disconnect?
**Solusi:** Gunakan `screen` atau `tmux` untuk persistent session:
```bash
screen -S pi_agent
source yt-agent-env/bin/activate
python main.py telegram

# Detach dengan: Ctrl+A, D
# Reattach dengan: screen -r pi_agent
```

---

## 📝 Persisten Bot (Run in Background)

### Menggunakan Systemd (Permanent)

Buat file `/etc/systemd/system/pi-agent-bot.service`:

```ini
[Unit]
Description=Pi Agent Telegram Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/nukman/Dokumen/Pi to Youtube
Environment="TELEGRAM_BOT_TOKEN=your_token_here"
ExecStart=/home/nukman/Dokumen/Pi to Youtube/yt-agent-env/bin/python main.py telegram
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Lalu jalankan:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pi-agent-bot
sudo systemctl start pi-agent-bot
sudo systemctl status pi-agent-bot
```

### Menggunakan Screen (Simple)

```bash
# Start
screen -S pi_agent -d -m bash -c "cd /home/nukman/Dokumen/Pi\ to\ Youtube && source yt-agent-env/bin/activate && export TELEGRAM_BOT_TOKEN='your_token' && python main.py telegram"

# Check
screen -list

# Attach untuk lihat logs
screen -r pi_agent

# Detach (tetap jalan)
# Ctrl+A, D
```

---

## 🎯 Minimal vs Full Flow

### Minimal (Langsung Run)
```
1. Ada credentials (client_secrets.json, bot token)
2. python main.py telegram
3. Done!
```

### Full (Sesuai README)
```
1. Install Python, venv
2. Setup credentials
3. Activate venv
4. Install dependencies
5. Export env variables
6. Run python main.py telegram
```

**PERBEDAAN:** Kalau semuanya sudah setup (step 1-4 sudah selesai), Anda hanya perlu:
```bash
source yt-agent-env/bin/activate
export TELEGRAM_BOT_TOKEN='...'
python main.py telegram
```

---

## 🔐 Menyimpan Token Safely

Jangan hardcode token di script! Gunakan salah satu:

### Option 1: File .env (local)
```
# .env
TELEGRAM_BOT_TOKEN=your_token_here
```

Lalu load di Python:
```python
from dotenv import load_dotenv
import os
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
```

### Option 2: System environment
```bash
# Add to ~/.bashrc atau ~/.zshrc
export TELEGRAM_BOT_TOKEN='your_token'

# Reload
source ~/.bashrc
```

### Option 3: Systemd environment
Lihat section "Systemd" di atas - set Environment=

---

## 📊 Performance di Pi

**Expected:**
- CPU usage: Low (bot idle, polling active)
- Memory: ~50-100 MB
- Network: Minimal (polling setiap 10s)

**Optimization:**
- Jalankan di background dengan systemd
- Set longer polling timeout jika perlu lebih hemat

---

**Kesimpulan:**
- ✅ Bisa run langsung dengan `python main.py telegram`
- ✅ Tapi prerequisites HARUS ada dulu
- ✅ Di Pi, gunakan systemd atau screen untuk persistent
- ✅ Prosedur sama seperti README, hanya di Pi context
