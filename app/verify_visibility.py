import sys
import os
from pydantic import BaseModel
from typing import Optional

# Add current directory to path so we can import modules
sys.path.append(os.getcwd())

from core.property_factory import create_pydantic_model_from_schema
from core.property_registry import PROPERTIES_REGISTRY, PropertyType

def test_visibility():
    print("Testing Visibility Filter...")
    
    # modify registry temporarily for testing
    PROPERTIES_REGISTRY["test_entity"] = [
        {"key": "visible_field", "type": PropertyType.TEXT, "label": "Visible", "visible": True},
        {"key": "hidden_field", "type": PropertyType.TEXT, "label": "Hidden", "visible": False},
        {"key": "default_field", "type": PropertyType.TEXT, "label": "Default"}, # Should be visible
    ]
    
    Model = create_pydantic_model_from_schema("test_entity")
    
    data = {
        "visible_field": "I am visible",
        "hidden_field": "I am hidden but present in data",
        "default_field": "I am default visible"
    }
    
    instance = Model(**data)
    
    # Check what model_dump returns
    dumped = instance.model_dump()
    print(f"Dumped data keys: {list(dumped.keys())}")
    
    if "hidden_field" in dumped:
        print("FAILED: hidden_field is present in model_dump()")
    else:
        print("PASSED: hidden_field is excluded from model_dump()")

    if "visible_field" in dumped:
        print("PASSED: visible_field is present")
    else:
        print("FAILED: visible_field is missing")
        
def test_project_properties():
    print("\nTesting Project Properties Configuration...")
    ProjectProps = create_pydantic_model_from_schema("project")
    
    # Check fields
    fields = ProjectProps.model_fields
    
    # Check status required
    status_field = fields.get("status")
    if status_field and status_field.is_required() is False:
        print("PASSED: status is optional")
    else:
        print(f"FAILED: status required state is {status_field.is_required() if status_field else 'Missing'}")
        
    # Check project_title required
    title_field = fields.get("project_title")
    if title_field and title_field.is_required() is True:
        print("PASSED: project_title is required")
    else:
        print(f"FAILED: project_title required state is {title_field.is_required() if title_field else 'Missing'}")

if __name__ == "__main__":
    try:
        test_visibility()
        test_project_properties()
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
