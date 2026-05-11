<div align="center">
  <h1>🚀 YouTube Skill Plugin untuk Pi Agent</h1>
  <p><i>Kontrol manajemen YouTube melalui Pi CLI dan REST API</i></p>
</div>

---

## 🎯 1. Latar Belakang & Target Capaian

> **Tujuan Utama:** Membuat *skill* kustom untuk **Pi Coding Agent** ([pi.dev](https://pi.dev)) yang memungkinkan agen untuk mengontrol manajemen channel YouTube (autentikasi, upload video, dan edit metadata).

### 🌟 Visi ke Depan
**Target capaian** dari proyek ini adalah menambah skill baru untuk *live streaming*, termasuk kontrol penuh streaming dari OBS ke YouTube yang dapat dilakukan sepenuhnya melalui **Bot Telegram**.

Skill ini berjalan sebagai service mandiri yang diekspor melalui **REST API**, sehingga dapat dipanggil dan dikontrol 100% oleh pengguna menggunakan CLI bawaan dari Pi Agent.

---

## 📊 2. Status Saat Ini (Progres: 66%)

Proyek sudah mencapai fase integrasi utama antara modul *skill* YouTube dan REST API Server.

✅ **Komponen yang sudah berjalan:**
- Autentikasi Google OAuth (`client_secrets.json` & `token.pickle`)
- Skill YouTube untuk **upload video** dan **edit metadata**
- REST API Server (Flask) dengan endpoint: `/upload`, `/edit`, `/status`, `/execute`
- Integrasi *wrapper* untuk Pi Agent CLI

⚠️ *Catatan: Saat ini fitur streaming langsung maupun integrasi OBS belum tersedia (hanya fitur upload dan edit). Fitur kontrol streaming via bot Telegram ini akan dikembangkan pada fase berikutnya.*

---

## 🏗️ 3. Arsitektur Proyek

Alur kerja sistem dirancang secara modular:

```text
[ Telegram Bot ] ➔ [ Pi Agent CLI (yang dibekali dengan Model Claude Sonnet 4.6) ] ➔ [ REST API Server (Flask) ] ➔ [ Pi Agent Core ] ➔ [ Skill Modules ] ➔ [ YouTube API ]
```

---

## 🧩 4. Komponen Utama

### 🌐 4.1 REST API Server (`pi_agent_rest_api.py`)
- Menjadi jembatan antara Pi Agent CLI dan *core logic* YouTube.
- Menyediakan endpoint HTTP untuk setiap fungsi skill.
- Mengembalikan response JSON yang mudah diproses oleh agen.

### 🎥 4.2 Skill YouTube (`skills/youtube/`)
- Mengunggah video ke YouTube beserta metadata yang relevan.
- Mengedit judul, deskripsi, dan privasi video.
- Mengelola sesi autentikasi OAuth Google.

### 🧠 4.3 Pi Agent Core (`core/pi_agent_core.py`)
- **Orchestrator** yang mengelola translasi dari *command* menjadi eksekusi fungsi.
- Menangani manajemen parameter dan *error handling*.

### 🔌 4.4 Integrasi CLI (`pi_agent_cli_integration.py`)
- Skrip *wrapper* untuk integrasi langsung dengan environment Pi Agent.

---

## 🏆 5. Pencapaian Teknis (Saat Ini)

- 🏗️ Struktur proyek **modular** dan sangat mudah untuk diekspansi.
- ⚡ REST API berjalan lancar dengan kapabilitas fungsional yang lengkap.
- 🎬 Skill YouTube berfungsi dengan baik (Upload & Edit).
- 🔗 Terintegrasi penuh dengan **Pi Agent CLI**.

---

## 💻 6. Bukti Fungsionalitas (Live Demo)

1️⃣ **Jalankan REST API Server**
```bash
python pi_agent_rest_api.py
# Server berjalan di http://localhost:5000
```

2️⃣ **Gunakan CLI untuk Eksekusi Perintah**
```bash
# Cek status autentikasi
curl http://localhost:5000/status

# Upload video
curl -X POST http://localhost:5000/upload -d '{"file_path": "/path/video.mp4", "title": "Judul"}'
```

---

## 🛠️ 7. Tantangan yang Berhasil Diatasi

- ✔️ Membungkus logika kompleks Google API menjadi endpoint REST sederhana.
- ✔️ Memastikan format response API sesuai dengan ekspektasi Pi Agent.
- ✔️ Menyelesaikan alur autentikasi OAuth untuk skenario aplikasi CLI/Desktop tanpa *browser* langsung.

---

## 🚀 8. Rencana Lanjutan (Next Steps)

1. 🛡️ **Optimasi API**: Peningkatan *error handling* dan penambahan *rate limiting* pada REST API.
2. 🖼️ **Fitur Lanjutan YouTube**: Pengaturan *thumbnail* otomatis dan penjadwalan (*scheduled upload*).
3. 🔴 **Skill Live Streaming**: Pembuatan skill baru khusus untuk *live streaming* dan integrasi **OBS ke YouTube** yang dikontrol penuh melalui **Bot Telegram**.

---

<div align="center">
  <h3>✨ Kesimpulan ✨</h3>
  <p>Proyek ini telah sukses membangun fondasi kokoh untuk <b>YouTube Skill pada Pi Coding Agent</b>. Dengan arsitektur berbasis REST API, skill ini sangat <b>fleksibel</b>, <b>independen</b>, dan siap dikendalikan secara komprehensif melalui antarmuka Pi Agent CLI.</p>
</div>
