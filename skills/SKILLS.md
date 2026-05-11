# Skills Documentation

## Struktur Folder Skills

```text
skills/
├── __init__.py
├── youtube/                    # YouTube Skill
│   ├── __init__.py
│   ├── upload_video.py        # Upload implementation
│   ├── edit_metadata.py       # Edit implementation
│   └── youtube_auth.py        # Auth implementation
```

## YouTube Skill

**Location:** `skills/youtube/`

### Fitur Tersedia Saat Ini
- ✅ Upload video dengan metadata lengkap (judul, deskripsi, tag, privasi)
- ✅ Edit metadata video yang sudah ada
- ✅ Handle large files dengan *chunked upload* (5MB chunks)
- ✅ OAuth2 token management via REST API

### Fitur Masa Depan (Belum Tersedia)
- 🔴 *Live Streaming* (kontrol OBS WebSocket)
- 🔴 Kontrol *streaming* dan upload via Bot Telegram

## Cara Mengekspor Skill ke REST API

Skill di dalam proyek ini didesain agar dibungkus menjadi sebuah endpoint mandiri melalui `pi_agent_rest_api.py`.
Ini memungkinkan **Pi Agent CLI** untuk memanggil skill dengan request `POST` / `GET` biasa.

Contoh integrasi dari sisi Pi Agent CLI:
```bash
pi youtube upload "/path/video.mp4" "Judul" "Desc"
```
*(CLI dari sisi pi.dev kemudian akan memetakan perintah tersebut menjadi HTTP POST request ke server lokal REST API pada proyek ini).*

## Panduan Membuat Skill Baru
1. Buat folder `skills/my_skill`
2. Implementasikan logika Python di dalamnya
3. Ekspos fungsi utamanya di `__init__.py`
4. Tambahkan route baru di `pi_agent_rest_api.py` yang memanggil fungsi tersebut
5. API sudah siap dikonsumsi oleh Pi Agent CLI!
