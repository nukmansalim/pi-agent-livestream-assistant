# Skills Documentation

## Struktur Folder Skills

```
skills/
├── __init__.py
├── youtube/                    # YouTube Skill
│   ├── __init__.py
│   ├── upload_video.py        # Upload implementation
│   ├── edit_metadata.py       # Edit implementation
│   └── youtube_auth.py        # Auth implementation
│
├── twitter/                   # (Future) Twitter Skill
│   ├── __init__.py
│   ├── post.py
│   └── twitter_auth.py
│
└── [SKILL_NAME]/              # Your own skills here
    ├── __init__.py
    ├── [module_files].py
    └── README.md
```

## YouTube Skill

**Location:** `skills/youtube/`

### Files
- `youtube_auth.py` - Google OAuth2 authentication
- `upload_video.py` - Video upload to YouTube
- `edit_metadata.py` - Edit video metadata (title, description, tags, privacy)

### Usage dalam Pi Agent

```python
from skills.youtube import upload_video, edit_video_metadata, get_authenticated_service
```

### Fitur
- ✅ Upload video dengan metadata lengkap
- ✅ Edit title, description, tags, privacy status
- ✅ Handle large files dengan chunked upload (5MB chunks)
- ✅ OAuth2 token management

## Menambah Skill Baru

### Step 1: Buat folder skill

```bash
mkdir skills/my_skill
touch skills/my_skill/__init__.py
```

### Step 2: Implementasi skill

`skills/my_skill/my_skill.py`:
```python
# Implementation of your skill
def my_function(**kwargs):
    return result
```

### Step 3: Export dari `__init__.py`

`skills/my_skill/__init__.py`:
```python
"""My Skill for Pi Agent."""

from .my_skill import my_function

__all__ = ["my_function"]
```

### Step 4: Register skill dalam Pi Agent

Edit `core/pi_agent_core.py`:

```python
# Tambahkan class untuk skill
class MySkill(Skill):
    def __init__(self):
        super().__init__("my_skill", "My Skill description")
    
    async def execute(self, context: PiAgentContext, **kwargs):
        # Implementation
        return {"success": True, "message": "Done"}

# Dalam _register_skills() method
def _register_skills(self):
    skills = [
        YouTubeUploadSkill(),
        YouTubeEditSkill(),
        StatusSkill(),
        MySkill(),  # <-- Add here
    ]
    for skill in skills:
        self.skills[skill.name] = skill
```

### Step 5: Update intent parser

Dalam `parse_intent()` method, tambahkan parsing untuk skill Anda:

```python
# My skill intent
if any(word in msg for word in ["my_keyword", "action"]):
    params = self._extract_my_params(user_message)
    if params:
        return "my_skill", params
```

## Struktur Skill Class

```python
from pi_agent_core import Skill, PiAgentContext
from typing import Dict, Any

class MySkill(Skill):
    def __init__(self):
        super().__init__(
            name="my_skill",
            description="What my skill does"
        )
    
    async def execute(
        self, 
        context: PiAgentContext, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute skill.
        
        Returns:
            {
                "success": bool,
                "message": str,
                "data": any,  # optional
                "error": str   # if error
            }
        """
        try:
            # Your implementation here
            result = do_something(**kwargs)
            
            return {
                "success": True,
                "message": "Operation successful",
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

## Best Practices

1. **Modular** - Satu folder = satu skill, dengan `__init__.py` untuk export
2. **Documentation** - Sertakan `README.md` di folder skill
3. **Error Handling** - Return proper error structure
4. **Context** - Gunakan `PiAgentContext` untuk credentials/state
5. **Async** - Semua skill execute method harus `async`
6. **Type Hints** - Gunakan type hints untuk clarity
7. **Testing** - Test skill secara independen sebelum integrate

## Export Convention

Setiap skill HARUS punya `__init__.py` yang export main functions:

```python
# skills/youtube/__init__.py
from .upload_video import upload_video
from .edit_metadata import edit_video_metadata
from .youtube_auth import get_authenticated_service

__all__ = [
    "upload_video",
    "edit_video_metadata",
    "get_authenticated_service",
]
```

---

**Pro Tip:** Skill bisa di-reuse di berbagai interface (Telegram, CLI, Web API, dll) karena logik terpisah dari UI.
