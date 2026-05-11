from googleapiclient.http import MediaFileUpload
from .youtube_auth import get_authenticated_service

def upload_video(
    file_path: str,
    title: str,
    description: str,
    tags: list[str],
    category_id: str = "22",       # 22 = People & Blogs
    privacy: str = "private"       # private | unlisted | public
):
    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy,
        }
    }

    media = MediaFileUpload(
        file_path,
        mimetype="video/*",
        resumable=True,       # resumable upload = safe for large files
        chunksize=1024 * 1024 * 5   # 5MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    # Upload with progress tracking
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"✅ Video uploaded! ID: {video_id}")
    print(f"   URL: https://youtube.com/watch?v={video_id}")
    return video_id