# OBS Source Creation Guide

Panduan lengkap membuat dan mengelola source di OBS Studio via REST API.

## Endpoint Source Management

### 1. List All Sources (GET)

```bash
curl http://localhost:5000/obs/sources
```

**Response:**
```json
{
  "success": true,
  "sources": [
    {"name": "Webcam", "kind": "dshow_input", "kind_display": "Video Capture Device"},
    {"name": "Mic/Aux", "kind": "wasapi_input_capture", "kind_display": "Audio Input Capture"},
    {"name": "Desktop Audio", "kind": "wasapi_output_capture", "kind_display": "Audio Output Capture"}
  ]
}
```

### 2. Create New Source (POST)

```bash
curl -X POST http://localhost:5000/obs/sources \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "scene_name": "Main Scene",
    "source_name": "My Text",
    "source_type": "text_gdiplus_v2",
    "settings": {
      "text": "Hello World!",
      "font": {"face": "Arial", "size": 48},
      "color": 4294967295
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Created input 'My Text' in 'Main Scene'",
  "scene_item_id": 42
}
```

### 3. Remove Source (POST)

```bash
curl -X POST http://localhost:5000/obs/sources \
  -H "Content-Type: application/json" \
  -d '{
    "action": "remove",
    "source_name": "My Text"
  }'
```

### 4. List Available Source Types (POST)

```bash
curl -X POST http://localhost:5000/obs/sources \
  -H "Content-Type: application/json" \
  -d '{"action": "list_kinds"}'
```

## Source Types yang Umum Digunakan

| Type | Deskripsi | Settings Contoh |
|------|-----------|-----------------|
| `text_gdiplus_v2` | Text source | `{"text": "Hello", "font": {"size": 24}}` |
| `browser_source` | Browser/web page | `{"url": "https://example.com", "width": 1920, "height": 1080}` |
| `image_source` | Image file | `{"file": "C:/path/to/image.png"}` |
| `color_source_v3` | Solid color | `{"color": 4278190080, "width": 1920, "height": 1080}` |
| `ffmpeg_source` | Media/video file | `{"local_file": "C:/path/to/video.mp4", "looping": true}` |
| `dshow_input` | Video capture device | `{"device": "Webcam Name"}` |
| `wasapi_input_capture` | Audio input | `{"device": "Microphone"}` |
| `wasapi_output_capture` | Audio output | `{"device": "Default"}` |
| `monitor_capture` | Display capture | `{"monitor": 0}` |
| `window_capture` | Window capture | `{"window": "App Name"}` |
| `game_capture` | Game capture | `{"capture_mode": "any_fullscreen"}` |

## Source Settings

### Get Source Settings

```bash
curl http://localhost:5000/obs/sources/My%20Text/settings
```

### Update Source Settings

```bash
curl -X POST http://localhost:5000/obs/sources/My%20Text/settings \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "text": "Updated Text!",
      "color": 4294901760
    }
  }'
```

## Scene Items (Sources in a Scene)

### List Items in a Scene

```bash
curl http://localhost:5000/obs/scenes/Main%20Scene/items
```

**Response:**
```json
{
  "success": true,
  "scene": "Main Scene",
  "items": [
    {"id": 1, "name": "Webcam", "enabled": true},
    {"id": 2, "name": "My Text", "enabled": true}
  ]
}
```

## Source Transform (Position, Scale, Rotation)

### Set Transform

```bash
curl -X POST http://localhost:5000/obs/transform \
  -H "Content-Type: application/json" \
  -d '{
    "scene_name": "Main Scene",
    "source_name": "My Text",
    "transform": {
      "positionX": 100,
      "positionY": 200,
      "scaleX": 1.5,
      "scaleY": 1.5,
      "rotation": 0,
      "cropTop": 0,
      "cropBottom": 0,
      "cropLeft": 0,
      "cropRight": 0
    }
  }'
```

### Transform Fields

| Field | Type | Deskripsi |
|-------|------|-----------|
| `positionX` | float | X position (pixels) |
| `positionY` | float | Y position (pixels) |
| `scaleX` | float | Horizontal scale |
| `scaleY` | float | Vertical scale |
| `rotation` | float | Rotation (degrees) |
| `cropTop` | int | Crop from top |
| `cropBottom` | int | Crop from bottom |
| `cropLeft` | int | Crop from left |
| `cropRight` | int | Crop from right |

## Contoh Lengkap: Create Text Overlay

```bash
# 1. Create text source
curl -X POST http://localhost:5000/obs/sources \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "scene_name": "Live",
    "source_name": "Title Overlay",
    "source_type": "text_gdiplus_v2",
    "settings": {
      "text": "🔴 LIVE - Coding Session",
      "font": {"face": "Arial", "flags": 1, "size": 36},
      "color": 4294967295,
      "outline": true,
      "outline_size": 2,
      "outline_color": 4278190080,
      "drop_shadow": true
    }
  }'

# 2. Position it at top-left
curl -X POST http://localhost:5000/obs/transform \
  -H "Content-Type: application/json" \
  -d '{
    "scene_name": "Live",
    "source_name": "Title Overlay",
    "transform": {
      "positionX": 20,
      "positionY": 20,
      "scaleX": 1.0,
      "scaleY": 1.0
    }
  }'

# 3. Update text dynamically
curl -X POST http://localhost:5000/obs/sources/Title%20Overlay/settings \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "text": "🔴 LIVE - Now: Building API"
    }
  }'
```

## Contoh: Create Browser Source (Alerts)

```bash
curl -X POST http://localhost:5000/obs/sources \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "scene_name": "Live",
    "source_name": "Stream Alerts",
    "source_type": "browser_source",
    "settings": {
      "url": "https://streamlabs.com/alert-box/v3/YOUR_ID",
      "width": 800,
      "height": 600,
      "fps": 60,
      "shutdown": false,
      "restart_when_active": true
    }
  }'
```

## Contoh: Create Image Source (Logo)

```bash
curl -X POST http://localhost:5000/obs/sources \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "scene_name": "Live",
    "source_name": "Channel Logo",
    "source_type": "image_source",
    "settings": {
      "file": "/home/user/logo.png"
    }
  }'
```

## Via Natural Language (/execute)

```bash
# Create source
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "create source Title Overlay in scene Live type text_gdiplus_v2"
  }'

# Hide source
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "hide source Title Overlay in scene Live"
  }'
```

## Tips

1. **Source names are case-sensitive** in OBS
2. **Scene must exist** before adding sources to it
3. **Settings format** varies by source type - check OBS docs
4. **Transform** uses pixel coordinates (0,0 = top-left)
5. **Color values** are in ARGB format (e.g., `4294967295` = white)
