from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.property_registry import get_entity_schema, apply_user_preferences
from api.deps import get_current_user
from models.user import User
from models.preference import PropertyPreference

router = APIRouter()

@router.get("/schemas/{entity_type}")
async def get_schema(
    entity_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the property schema for the given entity type, personalized with user preferences.
    """
    schema = get_entity_schema(entity_type)
    if not schema:
        return []
    
    # Query PropertyPreference for this user and entity type
    query = select(PropertyPreference).where(
        PropertyPreference.user_id == current_user.id,
        PropertyPreference.entity_type == entity_type
    )
    result = await db.execute(query)
    user_pref_record = result.scalars().first()
    
    entity_prefs = user_pref_record.preferences if user_pref_record else {}
    
    personalized_schema = apply_user_preferences(schema, entity_prefs)
    
    return personalized_schema

@router.patch("/schemas/{entity_type}/properties")
async def update_property_preference(
    entity_type: str,
    preference: dict = Body(...), # Expecting {"key": "status", "visible": false}
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a user's preference for a specific property.
    """
    prop_key = preference.get("key")
    if not prop_key:
         raise HTTPException(status_code=400, detail="Property key is required")
         
    # Validate that property exists in registry
    schema = get_entity_schema(entity_type)
    if not any(p["key"] == prop_key for p in schema):
        raise HTTPException(status_code=404, detail=f"Property '{prop_key}' not found for entity '{entity_type}'")

    # Fetch existing preference or create new one
    query = select(PropertyPreference).where(
        PropertyPreference.user_id == current_user.id,
        PropertyPreference.entity_type == entity_type
    )
    result = await db.execute(query)
    user_pref_record = result.scalars().first()
    
    if not user_pref_record:
        user_pref_record = PropertyPreference(
            user_id=current_user.id,
            entity_type=entity_type,
            preferences={}
        )
        db.add(user_pref_record)
        # Flush to get ID if needed, but not strictly necessary here before modifying preferences
    
    # Update the preferences dict
    # We must ensure we're working with a mutable dict or re-assigning it
    current_prefs = dict(user_pref_record.preferences) if user_pref_record.preferences else {}
    
    if prop_key not in current_prefs:
        current_prefs[prop_key] = {}
        
    if "visible" in preference:
        current_prefs[prop_key]["visible"] = preference["visible"]
        
    # Re-assign to trigger change detection
    user_pref_record.preferences = current_prefs
    
    await db.commit()
    await db.refresh(user_pref_record)
    
    return {"status": "success", "preferences": user_pref_record.preferences}
