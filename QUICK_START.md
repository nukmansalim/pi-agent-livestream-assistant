# ⚡ Quick Start - YouTube Skill REST API

Gunakan panduan ini jika Anda sudah melakukan setup dependencies.

## 1. Pastikan Credentials Siap
Pastikan file `client_secrets.json` sudah ada di folder proyek (dibutuhkan untuk akses Google API).

## 2. Jalankan REST API Server
```bash
cd "/home/nukman/Dokumen/Pi to Youtube"
source yt-agent-env/bin/activate
python pi_agent_rest_api.py
```

## 3. Verifikasi Server
Buka terminal lain dan jalankan perintah:
```bash
curl http://localhost:5000/health
```
*(Jika muncul status "healthy", maka API telah aktif dan siap dikonsumsi oleh Pi Agent CLI!)*

---

*Catatan: Fitur kontrol Telegram dan *streaming* langsung (OBS) belum tersedia di rilis saat ini dan masih merupakan target capaian pengembangan di masa depan.*
