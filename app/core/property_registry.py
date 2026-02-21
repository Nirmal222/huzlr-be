from typing import List, Dict, Any, Optional
from enum import Enum

class PropertyType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    DATE = "date"
    USER = "user"
    STATUS = "status"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    RICH_TEXT = "rich_text"
    JSON = "json"



PROPERTIES_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    "project": [
        {
            "key": "project_title",
            "type": PropertyType.TEXT,
            "label": "Project Title",
            "required": True
        },
        {
            "key": "short_summary",
            "type": PropertyType.TEXT,
            "label": "Short Summary"
        },
        {
            "key": "status",
            "type": PropertyType.STATUS,
            "label": "Status",
            "options": ["Backlog", "Planning", "In Progress", "Paused", "Done", "Canceled"],
            "default": "Backlog",
            "required": True,
            "visible": True
        },
        {
            "key": "priority",
            "type": PropertyType.SELECT,
            "label": "Priority",
            "options": ["Urgent", "High", "Medium", "Low", "None"],
            "default": "None"
        },
        {
            "key": "lead",
            "type": PropertyType.USER,
            "label": "Lead"
        },
        {
            "key": "members",
            "type": PropertyType.MULTI_SELECT, # Should assume User Multi-Select conceptually
            "label": "Members",
            "default": []
        },
        {
            "key": "start_date",
            "type": PropertyType.DATE,
            "label": "Start Date"
        },
        {
            "key": "target_date",
            "type": PropertyType.DATE,
            "label": "Target Date"
        },
        {
            "key": "labels",
            "type": PropertyType.MULTI_SELECT,
            "label": "Labels",
            "default": []
        },
        {
            "key": "dependencies",
            "type": PropertyType.MULTI_SELECT, # Should assume Project Multi-Select conceptually
            "label": "Dependencies",
            "default": []
        },
        {
            "key": "description",
            "type": PropertyType.RICH_TEXT,
            "label": "Description"
        },
        {
            "key": "milestones",
            "type": PropertyType.JSON,
            "label": "Milestones",
            "default": []
        }
    ]
}

def get_entity_schema(entity_type: str) -> List[Dict[str, Any]]:
    return PROPERTIES_REGISTRY.get(entity_type, [])

def apply_user_preferences(schema: List[Dict[str, Any]], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Applies user preferences to the schema.
    Overrides the 'visible' attribute if the key exists in preferences.
    preferences structure: {"property_key": {"visible": bool}}
    Always returns a deep copy to avoid mutating the global registry.
    """
    import copy
    schema_copy = copy.deepcopy(schema)

    if not preferences:
        return schema_copy

    for prop in schema_copy:
        key = prop.get("key")
        if key in preferences:
            user_pref = preferences[key]
            if "visible" in user_pref:
                prop["visible"] = user_pref["visible"]

    return schema_copy
