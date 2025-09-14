# project_schema.py - Validation des données des projets
PROJECT_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "number"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "category": {"type": "string", "enum": ["web", "mobile", "data", "api", "other"]},
            "technologies": {"type": "array", "items": {"type": "string"}},
            "image": {"type": "string"},
            "thumbnail": {"type": "string"},
            "live_link": {"type": "string"},
            "github_link": {"type": "string"},
            "completion_date": {"type": "string", "format": "date"},
            "status": {"type": "string", "enum": ["completed", "in-progress", "planned"]},
            "features": {"type": "array", "items": {"type": "string"}},
            "challenges": {"type": "string"},
            "solutions": {"type": "string"}
        },
        "required": ["id", "title", "description", "category"]
    }
}