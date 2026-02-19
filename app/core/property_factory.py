from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field, create_model
from core.property_registry import PropertyType, get_entity_schema

def create_pydantic_model_from_schema(
    entity_type: str, 
    base_class: Type[BaseModel] = BaseModel
) -> Type[BaseModel]:
    """
    Dynamically creates a Pydantic model based on the property registry for the given entity type.
    
    Args:
        entity_type: The entity type (e.g., "project")
    """
    schema = get_entity_schema(entity_type)
    fields = {}

    for prop in schema:
        # No more storage type filtering - all are JSON properties in the DB
            
        field_name = prop["key"]
        
        # Determine Python type based on PropertyType
        field_type = object # Default fallback
        default_value = prop.get("default", None)
        
        if prop["type"] == PropertyType.NUMBER:
            field_type = float | int
        elif prop["type"] == PropertyType.DATE:
            from datetime import datetime
            field_type = datetime
        elif prop["type"] in (PropertyType.SELECT, PropertyType.STATUS, PropertyType.TEXT, PropertyType.RICH_TEXT):
             field_type = str
        elif prop["type"] == PropertyType.MULTI_SELECT:
            field_type = List[str | int]
            if default_value is None:
                default_value = []
        elif prop["type"] == PropertyType.USER:
            field_type = str | int
        elif prop["type"] == PropertyType.JSON:
             field_type = Dict[str, Any] | List[Any]
        
        # Handle Union types for flexibility (from original schema)
        if prop["key"] == "purpose":
             field_type = dict | list | str
        
        # Handle visibility
        visible = prop.get("visible", True)
        field_info_kwargs = {}
        if not visible:
            field_info_kwargs["exclude"] = True

        # Handle required vs optional
        if prop.get("required", False):
            if default_value is not None:
                fields[field_name] = (Optional[field_type], Field(default=default_value, **field_info_kwargs))
            else:
                 fields[field_name] = (field_type, Field(..., **field_info_kwargs))
        else:
             fields[field_name] = (Optional[field_type], Field(default=default_value, **field_info_kwargs))

    # Allow extra fields for flexibility
    model_config = {"extra": "allow"}
    
    model_name = f"{entity_type.capitalize()}Properties"
    
    return create_model(
        model_name,
        __config__=model_config,
        **fields
    )

def validate_properties(entity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    Model = create_pydantic_model_from_schema(entity_type)
    instance = Model(**data)
    return instance.model_dump(exclude_unset=True)
