from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Any
import httpx
import os
from datetime import datetime, timedelta

from api import deps
from models.user import User
from models.jira import JiraConnection
from core.security_utils import encrypt_token

router = APIRouter()

JIRA_CLIENT_ID = os.getenv("JIRA_CLIENT_ID")
JIRA_CLIENT_SECRET = os.getenv("JIRA_CLIENT_SECRET")
JIRA_REDIRECT_URI = os.getenv("JIRA_REDIRECT_URI")
JIRA_AUTH_URL = "https://auth.atlassian.com/authorize"
JIRA_TOKEN_URL = "https://auth.atlassian.com/oauth/token"

@router.get("/authorize", response_model=dict)
def authorize_jira(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Generate the Atlassian authorization URL.
    """
    if not JIRA_CLIENT_ID or not JIRA_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Jira configuration missing")

    # Scopes required for 3LO
    # Adjust scopes as needed based on what you need (e.g., read:jira-work, write:jira-work)
    scopes = ["read:jira-work", "write:jira-work", "offline_access"]
    scope_str = "%20".join(scopes)
    
    # State should be ideally random and verified on callback. 
    # For simplicity, we are passing user_id, but in production use a secure random string mapped to user session.
    state = str(current_user.id) 

    url = (
        f"{JIRA_AUTH_URL}?"
        f"audience=api.atlassian.com&"
        f"client_id={JIRA_CLIENT_ID}&"
        f"scope={scope_str}&"
        f"redirect_uri={JIRA_REDIRECT_URI}&"
        f"state={state}&"
        f"response_type=code&"
        f"prompt=consent"
    )
    
    return {"authorization_url": url}

@router.get("/callback")
async def jira_callback(
    code: str,
    state: str,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Handle the OAuth 2.0 callback from Atlassian.
    """
    # In a real app, verify 'state' against the user session to prevent CSRF.
    # Here we convert it back to int to find the user (simplified).
    try:
        user_id = int(state)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    # Fetch user
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            JIRA_TOKEN_URL,
            json={
                "grant_type": "authorization_code",
                "client_id": JIRA_CLIENT_ID,
                "client_secret": JIRA_CLIENT_SECRET,
                "code": code,
                "redirect_uri": JIRA_REDIRECT_URI,
            },
        )
        
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve tokens: {response.text}")

    data = response.json()
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    expires_in = data.get("expires_in") # in seconds
    scope = data.get("scope")
    
    if not access_token or not refresh_token:
        raise HTTPException(status_code=400, detail="Invalid token response")

    # Encrypt tokens
    encrypted_access_token = encrypt_token(access_token)
    encrypted_refresh_token = encrypt_token(refresh_token)
    
    # Calculate expiry
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    # Store in DB
    # Check if connection exists
    stmt = select(JiraConnection).where(JiraConnection.user_id == user.id)
    result = await db.execute(stmt)
    existing_conn = result.scalar_one_or_none()

    if existing_conn:
        existing_conn.access_token = encrypted_access_token
        existing_conn.refresh_token = encrypted_refresh_token
        existing_conn.expires_at = expires_at
        existing_conn.scope = scope
    else:
        new_conn = JiraConnection(
            user_id=user.id,
            access_token=encrypted_access_token,
            refresh_token=encrypted_refresh_token,
            expires_at=expires_at,
            scope=scope
        )
        db.add(new_conn)
    
    await db.commit()
    
    return {"message": "Jira connected successfully"}
