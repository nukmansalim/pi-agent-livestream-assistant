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
            "GET  /livestream/status": "Status livestream"
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
        "name": "youtube_manager",
        "description": "YouTube video management via Pi Agent",
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

# ====================== LIVESTREAM ENDPOINTS ======================

@app.route('/livestream/create', methods=['POST'])
def livestream_create():
    """Create new livestream"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        user_id_int = hash(user_id) % 1000000

        command = f"livestream create titled {data.get('title', 'Pi Agent Live')}"
        result = asyncio.run(agent.execute(user_id_int, command))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/livestream/start', methods=['POST'])
def livestream_start():
    """Start livestream"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        user_id_int = hash(user_id) % 1000000

        command = f"livestream start {data.get('broadcast_id')}"
        result = asyncio.run(agent.execute(user_id_int, command))
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

        command = f"livestream end {data.get('broadcast_id')}"
        result = asyncio.run(agent.execute(user_id_int, command))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/livestream/status', methods=['GET'])
def livestream_status():
    """Livestream status (can be expanded later)"""
    return jsonify({
        "success": True,
        "message": "Livestream skill is active. Use /livestream/create to start."
    })

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
    print("\n🌐 Server running on http://localhost:5000")

    app.run(host='0.0.0.0', port=5000, debug=True)