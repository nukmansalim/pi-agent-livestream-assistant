# Push to GitHub - Step by Step

## Step 1: Create Repository di GitHub

1. Buka https://github.com/new
2. Repository name: `pi-agent-youtube-skill` (atau nama favorit Anda)
3. Description: `YouTube Skill plugin for Pi Agent using REST API`
4. Choose: Public or Private
5. **DON'T** initialize with README (kita sudah punya)
6. Click **Create Repository**

## Step 2: Push ke GitHub (Terminal)

Jalankan perintah berikut di dalam direktori `/home/nukman/Dokumen/Pi to Youtube`:

```bash
# Tambahkan perubahan baru
git add .

# Commit perubahan
git commit -m "docs: memperbarui seluruh dokumen menjadi fokus Pi Agent Skill API"

# Push ke GitHub
git push -u origin main
```

*(Catatan: Langkah ini berasumsi Anda sudah mengatur `git remote add origin` dan menginisialisasi Git lokal).*

---

## Troubleshooting

### Error: "Permission denied" / "could not read Username"
Pastikan Anda sudah login GitHub melalui git kredensial atau menggunakan Personal Access Token (PAT).
