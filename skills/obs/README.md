# OBS Control Skill

Skill untuk mengontrol OBS Studio via WebSocket API langsung dari Python.

## Fitur

### Scene Management
- List scenes
- Switch scene
- Create/Remove scene

### Recording Control
- Start/Stop/Pause/Resume recording
- Get recording status

### Streaming Control
- Start/Stop streaming
- Get streaming status
- Send stream captions

### Source Management
- List sources
- Show/Hide/Toggle source visibility
- Create/Remove sources
- Get/Set source settings

### Audio Control
- Mute/Unmute/Toggle mute
- Get/Set volume (dB)

### Transitions
- List transitions
- Set transition
- Set transition duration

### Studio Mode
- Enable/Disable studio mode
- Get/Set preview scene
- Trigger transition

### Virtual Camera & Replay Buffer
- Start/Stop virtual camera
- Start/Stop/Save replay buffer

### Filters
- List filters
- Create/Remove/Toggle filters

### Screenshots
- Get screenshot (base64)
- Save screenshot to file

### Browser Sources
- Refresh browser source

### Profiles & Collections
- List/Set profiles
- List/Set scene collections

## Konfigurasi

Tambahkan ke `.env`:

```env
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=your_password
```

## Penggunaan via REST API

### Cek Status OBS
```bash
curl http://localhost:5000/obs/status
```

### Switch Scene
```bash
curl -X POST http://localhost:5000/obs/scene \
  -H "Content-Type: application/json" \
  -d '{"scene_name": "Main Scene"}'
```

### Control Recording
```bash
# Start
curl -X POST http://localhost:5000/obs/recording \
  -H "Content-Type: application/json" \
  -d '{"command": "start"}'

# Stop
curl -X POST http://localhost:5000/obs/recording \
  -H "Content-Type: application/json" \
  -d '{"command": "stop"}'

# Status
curl -X POST http://localhost:5000/obs/recording \
  -H "Content-Type: application/json" \
  -d '{"command": "status"}'
```

### Control Streaming
```bash
curl -X POST http://localhost:5000/obs/streaming \
  -H "Content-Type: application/json" \
  -d '{"command": "start"}'
```

### Source Visibility
```bash
# Show source
curl -X POST http://localhost:5000/obs/source \
  -H "Content-Type: application/json" \
  -d '{
    "command": "show",
    "scene_name": "Main Scene",
    "source_name": "Webcam"
  }'

# Hide source
curl -X POST http://localhost:5000/obs/source \
  -H "Content-Type: application/json" \
  -d '{
    "command": "hide",
    "scene_name": "Main Scene",
    "source_name": "Webcam"
  }'
```

### Audio Control
```bash
# Mute
curl -X POST http://localhost:5000/obs/audio \
  -H "Content-Type: application/json" \
  -d '{"command": "mute", "input_name": "Mic/Aux"}'

# Set volume
curl -X POST http://localhost:5000/obs/audio \
  -H "Content-Type: application/json" \
  -d '{
    "command": "set_volume",
    "input_name": "Desktop Audio",
    "volume_db": -10.0
  }'
```

### Execute Any Command
```bash
curl -X POST http://localhost:5000/obs/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "list_scenes"
  }'
```

## Penggunaan via Natural Language

Kirim perintah bahasa alami ke `/execute`:

```bash
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "obs status"
  }'

curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "switch scene Main Scene"
  }'

curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "start recording"
  }'

curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "mute Mic/Aux"
  }'
```

## Setup OBS Studio

1. Buka OBS Studio
2. Pergi ke **Tools → WebSocket Server Settings**
3. Enable WebSocket server (default port: 4455)
4. Set password (opsional tapi direkomendasikan)
5. Simpan konfigurasi ke `.env`

## Perbandingan dengan agentic-obs

| Fitur | agentic-obs (Go/MCP) | OBS Skill ini (Python) |
|-------|---------------------|----------------------|
| Bahasa | Go | Python |
| Protocol | MCP (stdio) | REST API / WebSocket langsung |
| Transport | stdio | HTTP/WebSocket |
| Scene Management | ✅ | ✅ |
| Recording | ✅ | ✅ |
| Streaming | ✅ | ✅ |
| Source Control | ✅ | ✅ |
| Audio Control | ✅ | ✅ |
| Filters | ✅ | ✅ |
| Transitions | ✅ | ✅ |
| Studio Mode | ✅ | ✅ |
| Virtual Cam | ✅ | ✅ |
| Replay Buffer | ✅ | ✅ |
| Screenshots | ✅ | ✅ |
| Browser Refresh | ✅ | ✅ |
| Automation Rules | ✅ | ❌ (bisa ditambah) |
| TUI Dashboard | ✅ | ❌ |
| Web Dashboard | ✅ | ❌ |

Skill ini memberikan kontrol OBS langsung tanpa perlu install Go atau MCP server.
