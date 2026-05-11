# 🔗 Pi Agent CLI Integration Guide

Panduan untuk mengintegrasikan YouTube Pi Agent dengan Pi Agent CLI yang running di local.

## 📋 Status Integrasi

| Method | Status | Kompleksitas | Use Case |
|--------|--------|--------------|----------|
| **REST API** | ✅ Ready | Rendah | Recommended untuk production |
| **CLI Skill Wrapper** | ✅ Ready | Sedang | Jika ingin native CLI integration |
| **Direct Import** | ⚠️ Possible | Tinggi | Untuk development/advanced users |
| **Plugin System** | ❌ Not implemented | Tinggi | Future enhancement |

## 🚀 Quick Start - REST API Integration

### 1. Install Dependencies
```bash
cd "/home/nukman/Dokumen/Pi to Youtube"
yt-agent-env/bin/pip install flask==3.0.0
```

### 2. Start REST API Server
```bash
# Terminal 1 - Start API Server
cd "/home/nukman/Dokumen/Pi to Youtube"
export TELEGRAM_BOT_TOKEN='your_token'  # Optional, for Telegram features
yt-agent-env/bin/python pi_agent_rest_api.py

# Server akan run di: http://localhost:5000
```

### 3. Test API dari Pi Agent CLI
```bash
# Terminal 2 - Test connection
curl http://localhost:5000/health
# Expected: {"status":"healthy","service":"youtube_pi_agent"}

# Test capabilities
curl http://localhost:5000/capabilities

# Test YouTube status
curl "http://localhost:5000/status?user_id=test_user"
```

### 4. Contoh Penggunaan dari Pi Agent CLI

**Upload Video:**
```bash
curl -X POST http://localhost:5000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your_user_id",
    "file_path": "/path/to/video.mp4",
    "title": "My Awesome Video",
    "description": "Video description",
    "tags": ["tutorial", "python"],
    "privacy": "private"
  }'
```

**Edit Video:**
```bash
curl -X POST http://localhost:5000/edit \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your_user_id",
    "video_id": "VIDEO_ID_HERE",
    "title": "New Title",
    "description": "New Description",
    "privacy": "public"
  }'
```

**Natural Language Commands:**
```bash
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your_user_id",
    "command": "upload video from /home/user/video.mp4 titled Tutorial Python"
  }'
```

## 🛠️ Advanced Integration Methods

### Method 2: CLI Skill Wrapper

Jika Pi Agent CLI Anda support custom skills:

```python
# Dalam Pi Agent CLI Anda, import skill wrapper
from pi_agent_cli_integration import get_pi_cli_skill

# Register skill
youtube_skill = get_pi_cli_skill()
# Register dengan CLI system Anda

# Usage
result = youtube_skill.execute(
    user_id="user123",
    command="upload /path/video.mp4 'Title' 'Desc'"
)
```

### Method 3: Direct Python Import

Untuk integration yang sangat tight:

```python
import sys
sys.path.insert(0, '/home/nukman/Dokumen/Pi to Youtube')

from core.pi_agent_core import get_pi_agent

agent = get_pi_agent()
result = await agent.execute(user_id, "upload /path/video.mp4 'Title'")
```

## 📊 API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/capabilities` | GET | Get skill capabilities |
| `/execute` | POST | Execute natural language commands |
| `/upload` | POST | Direct video upload |
| `/edit` | POST | Direct video edit |
| `/status` | GET | Check authentication status |

### Response Format

```json
{
  "success": true|false,
  "message": "Human readable message",
  "result": { ... },  // Full result object
  "error": "Error message if failed"
}
```

## 🔧 Configuration

### Environment Variables
```bash
export TELEGRAM_BOT_TOKEN='your_token'  # Optional
export FLASK_ENV=development           # Optional
```

### Authentication
- YouTube OAuth credentials harus sudah setup (`client_secrets.json`)
- Token akan disimpan di `token.pickle` setelah auth pertama

## 🚦 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: flask` | `pip install flask==3.0.0` |
| `Connection refused` | Pastikan API server running di port 5000 |
| `Authentication failed` | Setup OAuth credentials dulu |
| `File not found` | Pastikan file path absolute dan file exists |

## 🎯 Use Cases

### 1. **CLI Integration**
```bash
# Dalam Pi Agent CLI Anda
pi youtube upload "/path/video.mp4" "Title" "Desc"
pi youtube edit "VIDEO_ID" "New Title"
pi youtube status
```

### 2. **Script Automation**
```python
import requests

def upload_video(file_path, title):
    response = requests.post('http://localhost:5000/upload', json={
        'user_id': 'automation',
        'file_path': file_path,
        'title': title
    })
    return response.json()
```

### 3. **Web Dashboard Integration**
```javascript
// Frontend JavaScript
fetch('/api/youtube/upload', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    file_path: '/path/video.mp4',
    title: 'My Video'
  })
})
```

## 🔮 Future Enhancements

- **WebSocket Support** - Real-time updates
- **Plugin System** - Hot-reload skills
- **Multi-user Sessions** - Better user management
- **Rate Limiting** - API protection
- **Logging & Monitoring** - Better observability

---

## 📞 Support

Jika butuh bantuan integrasi:
1. Pastikan API server running
2. Test dengan curl commands di atas
3. Check logs untuk error details
4. Pastikan credentials YouTube sudah setup