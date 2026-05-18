#!/usr/bin/env python3
"""
REST API Server for Pi Agent Integration

Run this server to expose YouTube Pi Agent functionality
via HTTP API that external Pi Agent CLI can call.
"""

import sys
import os
import json
import asyncio
import secrets
from typing import Dict, Any

# Allow OAuth over HTTP (localhost)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify, redirect, session, url_for

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pi_agent_core import get_pi_agent
from skills.youtube.youtube_auth import get_auth_url, save_credentials_from_code, logout, check_api_usage
from skills.obs.obs_control import get_obs_skill

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
agent = get_pi_agent()

@app.route('/', methods=['GET'])
def index():
    """Root endpoint - daftar semua endpoint yang tersedia."""
    return jsonify({
        "service": "YouTube Pi Agent REST API",
        "status": "running",
        "endpoints": {
            "GET  /health": "Health check",
            "GET  /capabilities": "Daftar kemampuan skill",
            "GET  /status": "Status autentikasi YouTube",
            "GET  /auth/login": "Login OAuth Google",
            "POST/GET /auth/logout": "Logout OAuth",
            "GET  /usage": "Cek kuota YouTube API",
            "POST /execute": "Jalankan perintah natural language",
            "POST /upload": "Upload video langsung",
            "POST /edit": "Edit metadata video",
            "POST /livestream/create": "Buat livestream baru",
            "POST /livestream/start": "Mulai livestream",
            "POST /livestream/end": "Akhiri livestream",
            "POST /livestream/bind-obs": "Bind broadcast ke OBS",
            "POST /livestream/privacy": "Ubah privacy broadcast",
            "GET  /livestream/status": "Status livestream",
            "GET  /obs/status": "OBS status",
            "POST /obs/execute": "Execute OBS command",
            "POST /obs/scene": "Switch OBS scene",
            "POST /obs/recording": "Control OBS recording",
            "POST /obs/streaming": "Control OBS streaming",
            "POST /obs/source": "Control OBS source visibility",
            "POST /obs/audio": "Control OBS audio",
            "GET/POST /obs/sources": "List/create/remove sources",
            "GET/POST /obs/sources/<name>/settings": "Get/update source settings",
            "GET /obs/scenes/<name>/items": "List scene items",
            "POST /obs/transform": "Set source transform"
        },
        "tip": "Coba akses /health untuk cek status server"
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "youtube_pi_agent"})

@app.route('/capabilities', methods=['GET'])
def capabilities():
    """Return skill capabilities."""
    caps = {
        "name": "pi_agent",
        "description": "YouTube + OBS management via Pi Agent",
        "skills": {
            "youtube": {
                "endpoints": [
                    "/execute - Execute natural language commands",
                    "/upload - Direct upload endpoint",
                    "/edit - Direct edit endpoint",
                    "/status - Check authentication status"
                ],
                "commands": [
                    "upload video from /path/to/file.mp4 titled 'Title'",
                    "edit video VIDEO_ID with new title 'New Title'",
                    "check youtube authentication status"
                ]
            },
            "obs": {
                "endpoints": [
                    "/obs/status - Get OBS status",
                    "/obs/execute - Execute OBS command",
                    "/obs/scene - Switch scene",
                    "/obs/recording - Recording control",
                    "/obs/streaming - Streaming control",
                    "/obs/source - Source visibility",
                    "/obs/audio - Audio control",
                    "/obs/sources - Create/list/remove sources",
                    "/obs/sources/<name>/settings - Source settings",
                    "/obs/scenes/<name>/items - Scene items",
                    "/obs/transform - Source transform"
                ],
                "commands": [
                    "obs status",
                    "switch scene 'Scene Name'",
                    "start recording",
                    "stop recording",
                    "start streaming",
                    "stop streaming",
                    "show source 'Source Name' in scene 'Scene Name'",
                    "hide source 'Source Name' in scene 'Scene Name'",
                    "mute 'Mic/Aux'",
                    "set volume 'Desktop Audio' to -10"
                ]
            }
        }
    }
    return jsonify(caps)

@app.route('/execute', methods=['POST'])
def execute():
    """Execute natural language command."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        user_id = data.get('user_id', 'default_user')
        command = data.get('command', '')

        if not command:
            return jsonify({"error": "No command provided"}), 400

        # Convert user_id to int
        user_id_int = hash(user_id) % 1000000

        # Execute command
        result = asyncio.run(agent.execute(user_id_int, command))

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload():
    """Direct upload endpoint."""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        file_path = data.get('file_path')
        title = data.get('title', 'Untitled')
        description = data.get('description', '')
        tags = data.get('tags', [])
        privacy = data.get('privacy', 'private')

        if not file_path:
            return jsonify({"error": "file_path required"}), 400

        user_id_int = hash(user_id) % 1000000
        command = f"upload {file_path} {title} {description} {','.join(tags)}"
        result = asyncio.run(agent.execute(user_id_int, command))

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/edit', methods=['POST'])
def edit():
    """Direct edit endpoint."""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        video_id = data.get('video_id')
        title = data.get('title')
        description = data.get('description')
        privacy = data.get('privacy')

        if not video_id:
            return jsonify({"error": "video_id required"}), 400

        user_id_int = hash(user_id) % 1000000
        command = f"edit {video_id} {title or ''} {description or ''} {privacy or ''}"
        result = asyncio.run(agent.execute(user_id_int, command))

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Check authentication status."""
    import pickle
    token_file = "token.pickle"
    try:
        if os.path.exists(token_file):
            with open(token_file, "rb") as f:
                service = pickle.load(f)
            authenticated = service is not None
        else:
            authenticated = False

        return jsonify({
            "success": True,
            "authenticated": authenticated,
            "message": "✅ Sudah login ke YouTube." if authenticated else "❌ Belum login. Kunjungi /auth/login untuk autentikasi.",
            "auth_url": "/auth/login" if not authenticated else None
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/auth/login', methods=['GET'])
def auth_login():
    """Redirect to Google OAuth login page."""
    try:
        redirect_uri = request.host_url.rstrip('/') + url_for('oauth2callback')
        auth_url, state, code_verifier = get_auth_url(redirect_uri)
        session['oauth_state'] = state
        if code_verifier:
            session['code_verifier'] = code_verifier
        
        user_agent = request.headers.get('User-Agent', '').lower()
        is_api_client = any(client in user_agent for client in ['curl', 'python', 'postman', 'insomnia'])
        wants_json = request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json'
        
        if is_api_client or wants_json:
            return jsonify({
                "success": True,
                "message": "AI INSTRUCTION: DO NOT open this URL yourself. Ask the human user to open the auth_url. IMPORTANT: You MUST output the auth_url as raw text (e.g. https://...) so the user can easily copy or click it in Telegram. Do NOT hide it inside a markdown link.",
                "auth_url": auth_url
            })
            
        return redirect(auth_url)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/oauth2callback', methods=['GET'])
def oauth2callback():
    """Handle the callback from Google OAuth."""
    try:
        state = session.get('oauth_state')
        code_verifier = session.get('code_verifier')
        
        if not state:
            # Fallback if session is lost
            state = request.args.get('state')
            if not code_verifier:
                return "<h1>Sesi Kadaluarsa</h1><p>Server sepertinya direstart atau sesi hilang. Silakan mulai ulang dari <a href='/auth/login'>/auth/login</a>.</p>", 400
            
        redirect_uri = request.host_url.rstrip('/') + url_for('oauth2callback')
        auth_response_url = request.url
        
        save_credentials_from_code(auth_response_url, redirect_uri, state, code_verifier)
        
        # Refresh service for any active contexts
        for ctx in agent.contexts.values():
            ctx.refresh_service()
            
        return "<h1>Autentikasi Berhasil!</h1><p>Anda dapat menutup halaman ini dan kembali ke klien Anda.</p>"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<h1>Autentikasi Gagal</h1><p>Error: {str(e)}</p>", 500

@app.route('/auth/logout', methods=['POST', 'GET'])
def auth_logout():
    """Logout from Google OAuth."""
    try:
        success = logout()
        if success:
            return jsonify({"success": True, "message": "Successfully logged out. Please restart or refresh the agent if needed."})
        else:
            return jsonify({"success": True, "message": "Already logged out or no token found."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/usage', methods=['GET'])
def api_usage():
    """Check YouTube API Quota/Usage status."""
    result = check_api_usage()
    if result["status"] == "error":
        return jsonify(result), 500
    return jsonify(result)

# ====================== OBS ENDPOINTS ======================

@app.route('/obs/status', methods=['GET'])
def obs_status():
    """Get OBS status."""
    try:
        obs = get_obs_skill()
        result = asyncio.run(obs.execute("status"))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/obs/execute', methods=['POST'])
def obs_execute():
    """Execute OBS command directly."""
    try:
        data = request.get_json() or {}
        action = data.get('action')
        if not action:
            return jsonify({"error": "action required"}), 400
        
        obs = get_obs_skill()
        params = {k: v for k, v in data.items() if k != 'action'}
        result = asyncio.run(obs.execute(action, **params))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/obs/scene', methods=['POST'])
def obs_scene():
    """Switch OBS scene."""
    try:
        data = request.get_json() or {}
        scene_name = data.get('scene_name') or data.get('scene')
        if not scene_name:
            return jsonify({"error": "scene_name required"}), 400
        
        obs = get_obs_skill()
        result = asyncio.run(obs.execute("set_scene", scene_name=scene_name))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/obs/recording', methods=['POST'])
def obs_recording():
    """Control OBS recording."""
    try:
        data = request.get_json() or {}
        command = data.get('command', 'status')
        
        action_map = {
            'start': 'start_recording',
            'stop': 'stop_recording',
            'pause': 'pause_recording',
            'resume': 'resume_recording',
            'status': 'recording_status'
        }
        action = action_map.get(command, 'recording_status')
        
        obs = get_obs_skill()
        result = asyncio.run(obs.execute(action))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/obs/streaming', methods=['POST'])
def obs_streaming():
    """Control OBS streaming."""
    try:
        data = request.get_json() or {}
        command = data.get('command', 'status')
        
        action_map = {
            'start': 'start_streaming',
            'stop': 'stop_streaming',
            'status': 'streaming_status',
            'toggle': 'toggle_streaming'
        }
        action = action_map.get(command, 'streaming_status')
        
        obs = get_obs_skill()
        result = asyncio.run(obs.execute(action))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/obs/source', methods=['POST'])
def obs_source():
    """Control OBS source visibility."""
    try:
        data = request.get_json() or {}
        command = data.get('command', 'list')
        scene_name = data.get('scene_name') or data.get('scene')
        source_name = data.get('source_name') or data.get('source')
        
        obs = get_obs_skill()
        
        if command == 'list':
            if not scene_name:
                return jsonify({"error": "scene_name required for list"}), 400
            result = asyncio.run(obs.execute("list_scene_items", scene_name=scene_name))
        elif command == 'show':
            if not scene_name or not source_name:
                return jsonify({"error": "scene_name and source_name required"}), 400
            result = asyncio.run(obs.execute("show_source", scene_name=scene_name, source_name=source_name))
        elif command == 'hide':
            if not scene_name or not source_name:
                return jsonify({"error": "scene_name and source_name required"}), 400
            result = asyncio.run(obs.execute("hide_source", scene_name=scene_name, source_name=source_name))
        elif command == 'toggle':
            if not scene_name or not source_name:
                return jsonify({"error": "scene_name and source_name required"}), 400
            result = asyncio.run(obs.execute("toggle_source", scene_name=scene_name, source_name=source_name))
        else:
            return jsonify({"error": f"Unknown command: {command}"}), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/obs/audio', methods=['POST'])
def obs_audio():
    """Control OBS audio."""
    try:
        data = request.get_json() or {}
        command = data.get('command', 'list')
        input_name = data.get('input_name') or data.get('source')
        volume_db = data.get('volume_db')
        
        obs = get_obs_skill()
        
        if command == 'list':
            result = asyncio.run(obs.execute("list_sources"))
        elif command == 'mute':
            if not input_name:
                return jsonify({"error": "input_name required"}), 400
            result = asyncio.run(obs.execute("mute", input_name=input_name))
        elif command == 'unmute':
            if not input_name:
                return jsonify({"error": "input_name required"}), 400
            result = asyncio.run(obs.execute("unmute", input_name=input_name))
        elif command == 'toggle_mute':
            if not input_name:
                return jsonify({"error": "input_name required"}), 400
            result = asyncio.run(obs.execute("toggle_mute", input_name=input_name))
        elif command == 'volume':
            if not input_name:
                return jsonify({"error": "input_name required"}), 400
            result = asyncio.run(obs.execute("get_volume", input_name=input_name))
        elif command == 'set_volume':
            if not input_name or volume_db is None:
                return jsonify({"error": "input_name and volume_db required"}), 400
            result = asyncio.run(obs.execute("set_volume", input_name=input_name, volume_db=volume_db))
        else:
            return jsonify({"error": f"Unknown command: {command}"}), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ====================== OBS SOURCE MANAGEMENT ======================

@app.route('/obs/sources', methods=['GET', 'POST'])
def obs_sources():
    """Manage OBS sources - create, list, or remove."""
    try:
        obs = get_obs_skill()
        
        if request.method == 'GET':
            # List all sources
            result = asyncio.run(obs.execute("list_sources"))
            return jsonify(result)
        
        # POST - Create or remove source
        data = request.get_json() or {}
        action = data.get('action')
        
        if action == 'create':
            scene_name = data.get('scene_name') or data.get('scene')
            source_name = data.get('source_name') or data.get('name')
            source_type = data.get('source_type') or data.get('type', 'text_gdiplus_v2')
            settings = data.get('settings', {})
            
            if not scene_name or not source_name:
                return jsonify({"error": "scene_name and source_name required"}), 400
            
            result = asyncio.run(obs.execute(
                "create_input",
                scene_name=scene_name,
                input_name=source_name,
                input_kind=source_type,
                settings=settings
            ))
            return jsonify(result)
            
        elif action == 'remove':
            source_name = data.get('source_name') or data.get('name')
            if not source_name:
                return jsonify({"error": "source_name required"}), 400
            
            result = asyncio.run(obs.execute("remove_input", input_name=source_name))
            return jsonify(result)
            
        elif action == 'list_kinds':
            result = asyncio.run(obs.execute("list_input_kinds"))
            return jsonify(result)
            
        else:
            return jsonify({"error": "action must be 'create', 'remove', or 'list_kinds'"}), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/obs/sources/<source_name>/settings', methods=['GET', 'POST'])
def obs_source_settings(source_name):
    """Get or update source settings."""
    try:
        obs = get_obs_skill()
        
        if request.method == 'GET':
            result = asyncio.run(obs.execute("get_input_settings", input_name=source_name))
            return jsonify(result)
        
        # POST - Update settings
        data = request.get_json() or {}
        settings = data.get('settings', {})
        
        result = asyncio.run(obs.execute(
            "set_input_settings",
            input_name=source_name,
            settings=settings
        ))
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/obs/scenes/<scene_name>/items', methods=['GET'])
def obs_scene_items(scene_name):
    """List all items in a scene."""
    try:
        obs = get_obs_skill()
        result = asyncio.run(obs.execute("list_scene_items", scene_name=scene_name))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/obs/transform', methods=['POST'])
def obs_transform():
    """Set source transform (position, scale, rotation)."""
    try:
        data = request.get_json() or {}
        scene_name = data.get('scene_name') or data.get('scene')
        source_name = data.get('source_name') or data.get('source')
        transform = data.get('transform', {})
        
        if not scene_name or not source_name:
            return jsonify({"error": "scene_name and source_name required"}), 400
        if not transform:
            return jsonify({"error": "transform object required"}), 400
        
        obs = get_obs_skill()
        result = asyncio.run(obs.execute(
            "set_source_transform",
            scene_name=scene_name,
            source_name=source_name,
            transform=transform
        ))
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ====================== LIVESTREAM ENDPOINTS ======================

@app.route('/livestream/create', methods=['POST'])
def livestream_create():
    """Create new livestream"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        user_id_int = hash(user_id) % 1000000

        # Panggil skill langsung — hindari NLP parser yang bisa salah baca judul
        context = agent.get_context(user_id_int)
        skill = agent.skills.get('youtube_livestream')
        result = asyncio.run(skill.execute(
            context,
            action="create",
            title=data.get('title', 'Pi Agent Live'),
            description=data.get('description', ''),
            privacy=data.get('privacy', 'private'),
        ))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/livestream/auto_start', methods=['POST'])
def livestream_auto_start():
    """Create YouTube livestream, sync RTMP key to OBS, and start OBS streaming."""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'default_user')
        user_id_int = hash(user_id) % 1000000

        # 1. Create Livestream on YouTube
        context = agent.get_context(user_id_int)
        yt_skill = agent.skills.get('youtube_livestream')
        yt_result = asyncio.run(yt_skill.execute(
            context,
            action="create",
            title=data.get('title', 'Pi Agent Auto Live'),
            description=data.get('description', ''),
            privacy=data.get('privacy', 'private'),
        ))

        if not yt_result.get("success"):
            return jsonify({"success": False, "error": f"YouTube Create Failed: {yt_result.get('error')}"}), 500

        rtmp_url = yt_result.get("rtmp_url")
        stream_key = yt_result.get("stream_key")
        broadcast_id = yt_result.get("broadcast_id")

        if not rtmp_url or not stream_key:
             return jsonify({"success": False, "error": "Failed to get RTMP details from YouTube"}), 500

        # 2. Sync to OBS
        obs = get_obs_skill()
        
        # Configure OBS for custom RTMP
        settings = {
            "server": rtmp_url,
            "key": stream_key,
            "use_auth": False
        }
        obs_config_result = asyncio.run(obs.execute("set_stream_settings", service_type="rtmp_custom", settings=settings))
        if not obs_config_result.get("success"):
            return jsonify({"success": False, "error": f"OBS Config Failed: {obs_config_result.get('error')}"}), 500
        
        # 3. Start OBS Streaming
        obs_start_result = asyncio.run(obs.execute("start_streaming"))
        if not obs_start_result.get("success"):
            return jsonify({"success": False, "error": f"OBS Start Streaming Failed: {obs_start_result.get('error')}"}), 500

        return jsonify({
            "success": True,
            "message": "Auto start sequence completed successfully",
            "broadcast_id": broadcast_id,
            "youtube": yt_result,
            "obs_config": obs_config_result,
            "obs_start": obs_start_result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/livestream/start', methods=['POST'])
def livestream_start():
    """Start livestream"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        user_id_int = hash(user_id) % 1000000

        broadcast_id = data.get('broadcast_id')
        if not broadcast_id:
            return jsonify({"success": False, "error": "broadcast_id diperlukan"}), 400

        context = agent.get_context(user_id_int)
        skill = agent.skills.get('youtube_livestream')
        result = asyncio.run(skill.execute(
            context,
            action="start",
            broadcast_id=broadcast_id,
        ))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/livestream/end', methods=['POST'])
def livestream_end():
    """End livestream"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        user_id_int = hash(user_id) % 1000000

        broadcast_id = data.get('broadcast_id')
        if not broadcast_id:
            return jsonify({"success": False, "error": "broadcast_id diperlukan"}), 400

        context = agent.get_context(user_id_int)
        skill = agent.skills.get('youtube_livestream')
        result = asyncio.run(skill.execute(
            context,
            action="end",
            broadcast_id=broadcast_id,
        ))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/livestream/bind-obs', methods=['POST'])
def livestream_bind_obs():
    """Bind broadcast to OBS and return stream settings."""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        user_id_int = hash(user_id) % 1000000

        broadcast_id = data.get('broadcast_id')
        if not broadcast_id:
            return jsonify({"success": False, "error": "broadcast_id diperlukan"}), 400

        context = agent.get_context(user_id_int)
        skill = agent.skills.get('youtube_livestream')
        result = asyncio.run(skill.execute(
            context,
            action="bind_obs",
            broadcast_id=broadcast_id,
        ))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/livestream/privacy', methods=['POST'])
def livestream_privacy():
    """Update broadcast privacy status."""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        user_id_int = hash(user_id) % 1000000

        broadcast_id = data.get('broadcast_id')
        privacy = data.get('privacy', 'public')
        if not broadcast_id:
            return jsonify({"success": False, "error": "broadcast_id diperlukan"}), 400

        context = agent.get_context(user_id_int)
        skill = agent.skills.get('youtube_livestream')
        result = asyncio.run(skill.execute(
            context,
            action="update_privacy",
            broadcast_id=broadcast_id,
            privacy=privacy,
        ))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/livestream/status', methods=['GET'])
def livestream_status():
    """Get livestream status by broadcast_id."""
    try:
        broadcast_id = request.args.get('broadcast_id')
        if not broadcast_id:
            return jsonify({
                "success": True,
                "message": "Livestream skill is active. Use ?broadcast_id=ID untuk cek status."
            })

        user_id = request.args.get('user_id', 'default_user')
        user_id_int = hash(user_id) % 1000000

        context = agent.get_context(user_id_int)
        skill = agent.skills.get('youtube_livestream')
        result = asyncio.run(skill.execute(
            context,
            action="status",
            broadcast_id=broadcast_id,
        ))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting YouTube Pi Agent REST API Server...")
    print("📡 Available endpoints:")
    print("   GET  /health - Health check")
    print("   GET  /capabilities - Skill capabilities")
    print("   POST /execute - Execute natural language commands")
    print("   POST /upload - Direct upload")
    print("   POST /edit - Direct edit")
    print("   GET  /status - Check auth status")
    print("   GET  /auth/login - Web OAuth Login")
    print("   POST/GET /auth/logout - Web OAuth Logout")
    print("   GET  /usage - Check API quota usage")
    print("   GET  /obs/status - OBS status")
    print("   POST /obs/execute - Execute OBS command")
    print("   POST /obs/scene - Switch OBS scene")
    print("   POST /obs/recording - Recording control")
    print("   POST /obs/streaming - Streaming control")
    print("   POST /obs/source - Source visibility")
    print("   POST /obs/audio - Audio control")
    print("   GET/POST /obs/sources - Source management")
    print("   GET/POST /obs/sources/<name>/settings - Source settings")
    print("   GET /obs/scenes/<name>/items - Scene items")
    print("   POST /obs/transform - Source transform")
    print("   POST /livestream/bind-obs - Bind broadcast to OBS")
    print("   POST /livestream/privacy - Update broadcast privacy")
    print("   POST /livestream/auto_start - Create YouTube live, sync RTMP, and start OBS")
    print("\n🌐 Server running on http://localhost:5000")

    app.run(host='0.0.0.0', port=5000, debug=True)