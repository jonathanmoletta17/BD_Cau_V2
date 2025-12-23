"""
Metadata API Routes
Exposes lists of GLPI metadata (Entities, Groups, Categories)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any

from src.core.database import get_db_session

router = APIRouter(prefix="/metadata", tags=["metadata"])

@router.get("/groups")
async def list_groups(
    db: Session = Depends(get_db_session)
):
    """List all active GLPI groups."""
    try:
        query = text("""
            SELECT id, name, completename
            FROM dtic.glpi_groups
            WHERE is_task = 1 OR is_itemgroup = 1
            ORDER BY completename
        """)
        result = db.execute(query)
        return [dict(row._mapping) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/entities")
async def list_entities(
    db: Session = Depends(get_db_session)
):
    """List all GLPI entities."""
    try:
        query = text("""
            SELECT id, name, completename, level
            FROM dtic.glpi_entities
            ORDER BY completename
        """)
        result = db.execute(query)
        return [dict(row._mapping) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
