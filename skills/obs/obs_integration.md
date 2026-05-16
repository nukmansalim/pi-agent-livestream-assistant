# OBS Integration Guide

## Overview

Fitur OBS Control telah ditambahkan ke proyek Pi to Youtube. Skill ini memungkinkan kontrol penuh OBS Studio via WebSocket API langsung dari Python, tanpa perlu install Go atau MCP server.

## File Baru

```
skills/obs/
├── __init__.py           # Package init
├── obs_websocket.py      # Low-level WebSocket client
├── obs_control.py        # High-level control skill
├── obs_skill.py          # Pi Agent skill wrapper
├── README.md             # Dokumentasi lengkap
└── obs_integration.md    # File ini
```

## File yang Dimodifikasi

```
core/pi_agent_core.py          # + OBS skill registration + intent parsing
pi_agent_rest_api.py           # + 7 OBS endpoints
requirements.txt               # + websockets
.env                           # + OBS config
```

## Endpoint REST API Baru

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/obs/status` | GET | Cek status OBS |
| `/obs/execute` | POST | Execute OBS command |
| `/obs/scene` | POST | Switch scene |
| `/obs/recording` | POST | Recording control |
| `/obs/streaming` | POST | Streaming control |
| `/obs/source` | POST | Source visibility |
| `/obs/audio` | POST | Audio control |

## Setup OBS Studio

1. Buka OBS Studio
2. Pergi ke **Tools → WebSocket Server Settings**
3. Enable WebSocket server (default port: 4455)
4. Set password (opsional)
5. Update `.env`:

```env
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=your_password
```

## Install Dependency

```bash
cd "Pi to Youtube"
source yt-agent-env/bin/activate
pip install websockets
```

## Contoh Penggunaan

### Via REST API

```bash
# Cek status OBS
curl http://localhost:5000/obs/status

# Switch scene
curl -X POST http://localhost:5000/obs/scene \
  -H "Content-Type: application/json" \
  -d '{"scene_name": "Main Scene"}'

# Start recording
curl -X POST http://localhost:5000/obs/recording \
  -H "Content-Type: application/json" \
  -d '{"command": "start"}'

# Mute audio
curl -X POST http://localhost:5000/obs/audio \
  -H "Content-Type: application/json" \
  -d '{"command": "mute", "input_name": "Mic/Aux"}'
```

### Via Natural Language

```bash
# Melalui /execute endpoint
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "obs status"}'

curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "switch scene Main Scene"}'

curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "start recording"}'
```

## Fitur yang Didukung

### Scene Management
- ✅ List scenes
- ✅ Switch scene
- ✅ Create/Remove scene

### Recording
- ✅ Start/Stop/Pause/Resume
- ✅ Get status

### Streaming
- ✅ Start/Stop
- ✅ Get status
- ✅ Toggle
- ✅ Send captions

### Sources
- ✅ List sources
- ✅ Show/Hide/Toggle visibility
- ✅ Create/Remove sources
- ✅ Get/Set settings

### Audio
- ✅ Mute/Unmute/Toggle
- ✅ Get/Set volume (dB)

### Transitions
- ✅ List transitions
- ✅ Set transition
- ✅ Set duration

### Studio Mode
- ✅ Enable/Disable
- ✅ Preview scene
- ✅ Trigger transition

### Virtual Camera & Replay Buffer
- ✅ Start/Stop virtual cam
- ✅ Start/Stop/Save replay

### Filters
- ✅ List/Create/Remove/Toggle

### Screenshots
- ✅ Get screenshot (base64)
- ✅ Save to file

### Browser Sources
- ✅ Refresh browser source

### Profiles & Collections
- ✅ List/Set profiles
- ✅ List/Set scene collections

## Perbandingan dengan agentic-obs

| Aspek | agentic-obs (Go) | OBS Skill (Python) |
|-------|-----------------|-------------------|
| Bahasa | Go | Python |
| Protocol | MCP (stdio) | REST API / WebSocket |
| Install | Go + compile | `pip install websockets` |
| Scene Control | ✅ | ✅ |
| Recording | ✅ | ✅ |
| Streaming | ✅ | ✅ |
| Audio | ✅ | ✅ |
| Filters | ✅ | ✅ |
| Transitions | ✅ | ✅ |
| Studio Mode | ✅ | ✅ |
| Virtual Cam | ✅ | ✅ |
| Replay Buffer | ✅ | ✅ |
| Screenshots | ✅ | ✅ |
| Automation Rules | ✅ | ❌ |
| TUI Dashboard | ✅ | ❌ |
| Web Dashboard | ✅ | ❌ |

## Workflow YouTube + OBS

```
1. Buat livestream YouTube
   POST /livestream/create
   → Dapat RTMP URL + Stream Key

2. Setup OBS Stream Settings
   (Manual atau via API)

3. Start OBS Streaming
   POST /obs/streaming {"command": "start"}
   → OBS mulai stream ke YouTube

4. Switch scene sesuai kebutuhan
   POST /obs/scene {"scene_name": "Live"}

5. Control recording (opsional)
   POST /obs/recording {"command": "start"}

6. Akhiri livestream
   POST /livestream/end {"broadcast_id": "..."}
   POST /obs/streaming {"command": "stop"}
```

## Troubleshooting

### "Failed to connect to OBS"
- Pastikan OBS Studio berjalan
- Pastikan WebSocket server enabled (Tools → WebSocket Server Settings)
- Cek port 4455 tidak diblokir firewall
- Verifikasi password jika di-set

### "ModuleNotFoundError: No module named 'websockets'"
```bash
pip install websockets
```

### Circular Import
Sudah di-fix. `obs_skill.py` menggunakan delayed import untuk menghindari circular dependency dengan `core.pi_agent_core`.
