# Push to GitHub - Step by Step

Username: `nukmansalim`

## Step 1: Create Repository di GitHub

1. Go to https://github.com/new
2. Repository name: `pi-agent-youtube` (atau nama favorit Anda)
3. Description: `Pi Agent with Telegram interface for YouTube management`
4. Choose: Public or Private
5. **DON'T** initialize with README (kita sudah punya)
6. Click **Create Repository**

GitHub akan tunjukkan URL: `https://github.com/nukmansalim/pi-agent-youtube`

---

## Step 2: Initialize Git Locally

```bash
cd /home/nukman/Dokumen/Pi\ to\ Youtube

# Initialize git repository
git init

# Configure git (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@gmail.com"

# Add remote
git remote add origin https://github.com/nukmansalim/pi-agent-youtube.git
```

---

## Step 3: Add Files & Commit

```bash
# Check what will be committed
git status

# Add all files (respects .gitignore)
git add .

# Commit with message
git commit -m "Initial commit: Pi Agent YouTube with Telegram integration"
```

---

## Step 4: Push to GitHub

```bash
# Push to main branch (create if doesn't exist)
git branch -M main
git push -u origin main

# Future pushes (simpler)
git push
```

---

## Step 5: Verify

Go to https://github.com/nukmansalim/pi-agent-youtube

Should see:
- ✅ All folders (core, skills, interfaces)
- ✅ All documentation files
- ✅ No credentials (client_secrets.json blocked by .gitignore)
- ✅ No venv files

---

## Complete One-Liner (after repo created)

```bash
cd /home/nukman/Dokumen/Pi\ to\ Youtube && \
git init && \
git config --global user.name "Mohammad Nukman Salim" && \
git config --global user.email "nukmansaleem@gmail.com" && \
git remote add origin https://github.com/nukmansalim/pi-agent-youtube.git && \
git add . && \
git commit -m "Initial commit: Pi Agent YouTube with Telegram integration" && \
git branch -M main && \
git push -u origin main
```

---

## Troubleshooting

### Error: "fatal: not a git repository"
```bash
cd /home/nukman/Dokumen/Pi\ to\ Youtube
git init
```

### Error: "Permission denied (publickey)"
Need SSH setup:
```bash
# Generate SSH key (if not exists)
ssh-keygen -t ed25519 -C "nukmansaleem@gmail.com"

# Copy public key to GitHub
cat ~/.ssh/id_ed25519.pub

# Go to GitHub Settings > SSH and GPG keys > New SSH key
# Paste the key

# Use SSH URL instead:
git remote add origin git@github.com:nukmansalim/pi-agent-youtube.git
```

### Error: "failed to push"
Check:
1. Repository name is correct
2. You have push permission
3. Internet connection OK

---

## After First Push

Future updates:
```bash
# Make changes
git add .
git commit -m "Description of changes"
git push
```

---

**Ready? Execute one-liner or follow step-by-step!**
