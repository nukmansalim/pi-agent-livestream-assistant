from .youtube_auth import get_authenticated_service

def edit_video_metadata(
    video_id: str,
    title: str = None,
    description: str = None,
    tags: list[str] = None,
    category_id: str = None,
    privacy: str = None
):
    youtube = get_authenticated_service()

    # First, fetch current metadata
    current = youtube.videos().list(
        part="snippet,status",
        id=video_id
    ).execute()

    if not current["items"]:
        raise ValueError(f"Video {video_id} not found")

    snippet = current["items"][0]["snippet"]
    status  = current["items"][0]["status"]

    # Merge changes (only update what's provided)
    updated_snippet = {
        "title":       title       or snippet["title"],
        "description": description or snippet["description"],
        "tags":        tags        or snippet.get("tags", []),
        "categoryId":  category_id or snippet["categoryId"],
    }

    updated_status = {
        "privacyStatus": privacy or status["privacyStatus"]
    }

    response = youtube.videos().update(
        part="snippet,status",
        body={
            "id": video_id,
            "snippet": updated_snippet,
            "status":  updated_status,
        }
    ).execute()

    print(f"✅ Metadata updated for video: {response['id']}")
    return response