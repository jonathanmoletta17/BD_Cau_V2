from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from src.core.database import get_db
from .service import service

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

@router.post("/learn/{ticket_id}")
async def learn_ticket_endpoint(
    ticket_id: int, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger learning process for a specific ticket.
    Runs in background to avoid blocking.
    """
    # We can run this in background
    # background_tasks.add_task(service.learn_ticket, db, ticket_id) 
    # Note: For simplicity in this demo/validation, we will await it.
    try:
        entry = await service.learn_ticket(db, ticket_id)
        return {"status": "success", "message": f"Learned ticket {ticket_id}", "entry_id": entry.id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_endpoint(
    q: str,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Semantic search for tickets based on query.
    """
    try:
        results = await service.search(db, q, limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
