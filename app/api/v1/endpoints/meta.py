from fastapi import APIRouter, HTTPException, Depends
from core.property_registry import get_entity_schema

router = APIRouter()

@router.get("/schemas/{entity_type}")
async def get_schema(entity_type: str):
    """
    Returns the property schema for the given entity type.
    """
    schema = get_entity_schema(entity_type)
    if not schema:
        # Instead of 404, return empty list if valid entity concept but no properties?
        # For now, let's return [] to be safe if it's just undefined
        return []
    
    return schema
