# Pi Agent - YouTube Manager dengan Telegram Integration

## 📁 Struktur Proyek

```
Pi to Youtube/
├── core/                          # Core Pi Agent orchestrator
│   ├── __init__.py
│   └── pi_agent_core.py           # Main agent logic, skills registry, intent parsing
│
├── skills/                        # Skill modules
│   ├── __init__.py
│   └── youtube/                   # YouTube skill (upload, edit, auth)
│       ├── __init__.py
│       ├── upload_video.py        # Video upload implementation
│       ├── edit_metadata.py       # Video metadata editing
│       └── youtube_auth.py        # Google OAuth authentication
│
├── interfaces/                    # User interfaces
│   ├── __init__.py
│   └── telegram/                  # Telegram bot interface
│       ├── __init__.py
│       └── telegram_bot_interface.py
│
├── main.py                        # Entry point (launcher)
├── README.md                      # This file
└── requirements.txt               # Python dependencies
```

## 🎯 Arsitektur

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram User Interface                   │
│              (telegram_bot_interface.py)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Natural Language Parsing
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Pi Agent Core (Orchestrator)                │
│              (pi_agent_core.py)                              │
│                                                              │
│  - Intent Parser: Converts natural language to skills       │
│  - Context Manager: Manages credentials & user sessions     │
│  - Skill Registry: YouTube, Auth, Status, etc.             │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────┐
        │            │            │          │
        ▼            ▼            ▼          ▼
   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
   │YouTube │  │YouTube │  │Google  │  │Status  │
   │Upload  │  │ Edit   │  │ Auth   │  │ Skill  │
   └────────┘  └────────┘  └────────┘  └────────┘
        │            │            │          │
        └────────────┴────────────┴──────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Google YouTube API  │
          │  + Credentials       │
          └──────────────────────┘
```

## Fitur

✅ **Upload Video** - Upload ke YouTube dengan metadata  
✅ **Edit Metadata** - Ubah judul, deskripsi, privacy status  
✅ **Auth Management** - OAuth flow untuk autentikasi Google  
✅ **Status Check** - Cek status token dan autentikasi  
✅ **Natural Language** - Parse intent dari pesan conversational  
✅ **Command Support** - Support command-style untuk power users  

## Setup

### 1. Install Dependencies
```bash
python3 -m venv yt-agent-env
source yt-agent-env/bin/activate
pip install -r requirements.txt
```

### 2. Setup Google OAuth
- Buat project di [Google Cloud Console](https://console.cloud.google.com/)
- Enable YouTube API v3
- Buat OAuth 2.0 credential (Desktop app)
- Download sebagai `client_secrets.json`
- Letakkan di project root

### 3. Setup Telegram Bot Token
```bash
export TELEGRAM_BOT_TOKEN='your_telegram_bot_token_here'
```

Dapatkan token dari [@BotFather](https://t.me/botfather) di Telegram.

### 4. Jalankan Bot

**Dengan main.py (recommended):**
```bash
cd /home/nukman/Dokumen/Pi\ to\ Youtube/
yt-agent-env/bin/python main.py telegram
```

**Atau langsung:**
```bash
yt-agent-env/bin/python interfaces/telegram/telegram_bot_interface.py
```

## Penggunaan

### Command-Style (Power Users)

```
/upload "/path/video.mp4" "Judul Video" "Deskripsi" tag1,tag2
/edit <video_id> "Judul Baru" "Deskripsi Baru" privacy
/status
/auth
/code <GOOGLE_CODE>
```

### Natural Language (User-Friendly)

```
"Upload video dari /home/user/video.mp4 judulnya Tutorial Coding"
"Edit video dQw4w9WgXcQ judul Judul Baru privacy unlisted"
"Cek status autentikasi"
```

## Examples

### Upload Video
**Command:**
```
/upload "/home/nukman/Dokumen/AIDhoto/output.mp4" "AI Streaming Demo" "Demonstrasi AI streaming" ai,streaming,demo
```

**Natural Language:**
```
Upload video dari /home/nukman/Dokumen/AIDhoto/output.mp4 judulnya "AI Streaming Demo"
```

### Edit Metadata
**Command:**
```
/edit dQw4w9WgXcQ "New Title" "New Description" unlisted
```

**Natural Language:**
```
Edit video dQw4w9WgXcQ judul "New Title" deskripsi "New Description" unlisted
```

### Check Status
```
/status
```

or

```
Cek status autentikasi
```

## Files

- `pi_agent_core.py` - Core orchestrator dengan skill system
- `telegram_bot_interface.py` - Telegram bot interface (NEW)
- `upload_video.py` - YouTube upload implementation
- `edit_metadata.py` - YouTube metadata edit implementation
- `youtube_auth.py` - Google OAuth authentication
- `agent.py` - Legacy agent (deprecated, use Pi Agent instead)
- `telegram_agent.py` - Legacy Telegram bot (deprecated)

## Troubleshooting

### Bot tidak merespons
- Pastikan bot sudah di-restart
- Check bot token dengan `/start`
- Lihat logs di terminal

### File tidak ditemukan
- Gunakan path absolut (dari /)
- Untuk path dengan spasi, gunakan quotes: "/path/dengan spasi/file.mp4"

### Autentikasi gagal
- Hapus `token.pickle`
- Jalankan `/auth` lagi
- Follow link OAuth dari bot

## Struktur Skill

Untuk menambah skill baru, extend class `Skill`:

```python
class MySkill(Skill):
    def __init__(self):
        super().__init__("skill_name", "Skill description")
    
    async def execute(self, context: PiAgentContext, **kwargs):
        # Implementation
        return {"success": True, "message": "..."}

# Register in PiAgent._register_skills()
```

## Roadmap

- [ ] LLM integration untuk NLP lebih baik
- [ ] Inline buttons untuk easy interaction
- [ ] Video thumbnail preview
- [ ] Batch upload support
- [ ] Webhook support untuk Telegram
- [ ] Database untuk store history
- [ ] Multi-user session management

---

**Created with ❤️ for Raspberry Pi automation**
