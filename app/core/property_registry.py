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
            "key": "project_budget",
            "type": PropertyType.NUMBER,
            "label": "Project Budget",
        },
        {
            "key": "description",
            "type": PropertyType.TEXT,
            "label": "Description"
        },
        {
            "key": "source",
            "type": PropertyType.SELECT,
            "label": "Source",
            "options": ["native", "jira", "linear", "github"],
            "default": "native"
        },
        {
            "key": "external_id",
            "type": PropertyType.TEXT,
            "label": "External ID"
        },
        {
            "key": "external_url",
            "type": PropertyType.TEXT,
            "label": "External URL"
        },
        {
            "key": "status",
            "type": PropertyType.STATUS,
            "label": "Status",
            "options": ["Draft", "Planning", "Active", "Completed", "Archived", "Backlog"],
            "default": "Draft",
            "required": True
        },
        {
            "key": "type",
            "type": PropertyType.SELECT,
            "label": "Section Type",
            "options": ["Focus Documents", "Past Performance", "Key Personnel"],
            "default": "Focus Documents"
        },
        {
            "key": "target",
            "type": PropertyType.NUMBER,
            "label": "Target",
            "default": 2000
        },
        {
            "key": "limit",
            "type": PropertyType.NUMBER,
            "label": "Limit",
            "default": 5000
        },
        {
            "key": "reviewer",
            "type": PropertyType.USER,
            "label": "Reviewer",
            "default": "Assign reviewer"
        },
        {
            "key": "priority",
            "type": PropertyType.SELECT,
            "label": "Priority",
            "options": ["Urgent", "High", "Medium", "Low", "None"],
            "default": "None"
        },
         {
            "key": "health",
            "type": PropertyType.SELECT,
            "label": "Health",
             "options": ["On Track", "At Risk", "Off Track"],
            "default": "On Track"
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
            "key": "purpose",
            "type": PropertyType.RICH_TEXT,
            "label": "Purpose"
        }
    ],
    "issue": [
        {
            "key": "status",
            "type": PropertyType.STATUS,
            "label": "Status",
            "options": ["Open", "In Progress", "Resolved", "Closed"],
            "default": "Open",
            "required": True,

        },
        {
            "key": "priority",
            "type": PropertyType.SELECT,
            "label": "Priority",
            "options": ["Critical", "High", "Medium", "Low"],
            "default": "Medium"
        },
        {
            "key": "assignee",
            "type": PropertyType.USER,
            "label": "Assignee"
        }
    ]
}

def get_entity_schema(entity_type: str) -> List[Dict[str, Any]]:
    return PROPERTIES_REGISTRY.get(entity_type, [])
