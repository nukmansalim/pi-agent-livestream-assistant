# ⚡ Quick Start - Run Immediately

Jika prerequisites sudah ada, jalankan bot dalam 2 detik:

## Prerequisites Check
```bash
ls client_secrets.json    # ✅ Google credentials
echo $TELEGRAM_BOT_TOKEN   # ✅ Bot token (should not be empty)
python3 --version          # ✅ Python 3.x
ls yt-agent-env/bin/python # ✅ Virtual environment
```

## Run Bot (choose one)

### 1️⃣ Recommended (via main.py)
```bash
cd /path/to/Pi\ to\ Youtube
export TELEGRAM_BOT_TOKEN='your_bot_token_here'
yt-agent-env/bin/python main.py telegram
```

### 2️⃣ Direct (if already activated venv)
```bash
source yt-agent-env/bin/activate
export TELEGRAM_BOT_TOKEN='your_token'
python interfaces/telegram/telegram_bot_interface.py
```

### 3️⃣ On Raspberry Pi (one-liner)
```bash
cd /home/nukman/Dokumen/Pi\ to\ Youtube && export TELEGRAM_BOT_TOKEN='your_token' && yt-agent-env/bin/python main.py telegram
```

## ✅ Bot Started Successfully When You See:
```
🤖 Pi Agent Telegram Bot berjalan...
   - Commands: /start, /help, /auth, /upload, /edit, /status
   - Chat natural: Bot bisa parse intent dari pesan normal
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `yt-agent-env/bin/pip install -r requirements.txt` |
| `TELEGRAM_BOT_TOKEN tidak ditemukan` | Run `export TELEGRAM_BOT_TOKEN='...'` before starting |
| `client_secrets.json not found` | Download from Google Cloud Console |
| Bot tidak respond | Check internet, make sure bot is running in terminal |

---

## Apa Bedanya dengan README?

| Aspect | README.md | QUICK_START.md |
|--------|-----------|---|
| Scope | Setup lengkap dari awal | Hanya run (semua sudah setup) |
| Target | First time users | Ready to go users |
| Steps | 1. Install Python 2. Venv 3. Dependencies 4. Run | 1. Set token 2. Run |
| Time | ~5-10 menit | ~30 detik |

**Jika Anda belum setup:**
→ Follow [README.md](README.md)

**Jika Anda sudah setup:**
→ Follow ini (QUICK_START.md)

---

## Next: Persistent Run (Opsional)

Agar bot tetap jalan di background:

```bash
# Using screen (simple)
screen -S pi_agent -d -m bash -c "cd /home/nukman/Dokumen/Pi\ to\ Youtube && export TELEGRAM_BOT_TOKEN='...' && yt-agent-env/bin/python main.py telegram"

# Check
screen -list

# Lihat logs
screen -r pi_agent

# Detach: Ctrl+A, D
```

Atau lihat [PI_SETUP_GUIDE.md](PI_SETUP_GUIDE.md) untuk systemd (permanent).
