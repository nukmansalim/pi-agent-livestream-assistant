# Python Integration Example

import requests
import json

class PiAgentYouTubeClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url

    def check_status(self, user_id="default"):
        """Check YouTube authentication status"""
        response = requests.get(f"{self.base_url}/status", params={"user_id": user_id})
        return response.json()

    def upload_video(self, user_id, file_path, title, description="", tags=None, privacy="private"):
        """Upload video to YouTube"""
        data = {
            "user_id": user_id,
            "file_path": file_path,
            "title": title,
            "description": description,
            "tags": tags or [],
            "privacy": privacy
        }
        response = requests.post(f"{self.base_url}/upload", json=data)
        return response.json()

    def edit_video(self, user_id, video_id, title=None, description=None, privacy=None):
        """Edit video metadata"""
        data = {
            "user_id": user_id,
            "video_id": video_id,
            "title": title,
            "description": description,
            "privacy": privacy
        }
        response = requests.post(f"{self.base_url}/edit", json=data)
        return response.json()

    def execute_command(self, user_id, command):
        """Execute natural language command"""
        data = {
            "user_id": user_id,
            "command": command
        }
        response = requests.post(f"{self.base_url}/execute", json=data)
        return response.json()

# Usage Example
if __name__ == "__main__":
    client = PiAgentYouTubeClient()

    # Check status
    status = client.check_status("my_user")
    print("Status:", status)

    # Upload video
    result = client.upload_video(
        user_id="my_user",
        file_path="/path/to/video.mp4",
        title="My Video",
        description="Description",
        tags=["tag1", "tag2"]
    )
    print("Upload result:", result)

    # Edit video
    result = client.edit_video(
        user_id="my_user",
        video_id="VIDEO_ID",
        title="New Title"
    )
    print("Edit result:", result)

    # Natural language
    result = client.execute_command(
        user_id="my_user",
        command="upload video from /path/video.mp4 titled 'My Video'"
    )
    print("Command result:", result)