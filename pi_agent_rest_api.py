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
from typing import Dict, Any
from flask import Flask, request, jsonify

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pi_agent_core import get_pi_agent

app = Flask(__name__)
agent = get_pi_agent()

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
    try:
        user_id = request.args.get('user_id', 'default_user')
        user_id_int = hash(user_id) % 1000000

        result = asyncio.run(agent.execute(user_id_int, "status"))
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
    print("\n🌐 Server running on http://localhost:5000")

    app.run(host='0.0.0.0', port=5000, debug=True)