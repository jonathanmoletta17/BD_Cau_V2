from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import Database
from .models import Setting

router = APIRouter(prefix="/sis/config", tags=["SIS - Config"])

def get_db_session():
    session = Database.get_session(schema="dtic")
    try:
        yield session
    finally:
        session.close()

@router.get("/expediente")
def get_expediente(db: Session = Depends(get_db_session)):
    s = db.query(Setting).filter(Setting.key == 'expediente').first()
    if not s:
        return {"startHour": "08:00", "endHour": "18:00", "timezone": "America/Sao_Paulo"}
    return s.value or {"startHour": "08:00", "endHour": "18:00", "timezone": "America/Sao_Paulo"}

@router.put("/expediente")
def set_expediente(payload: dict, db: Session = Depends(get_db_session)):
    start = payload.get('startHour')
    end = payload.get('endHour')
    tz = payload.get('timezone') or 'America/Sao_Paulo'
    if not start or not end:
        raise HTTPException(status_code=400, detail="startHour e endHour são obrigatórios")
    setting = db.query(Setting).filter(Setting.key == 'expediente').first()
    if not setting:
        setting = Setting(key='expediente', value={"startHour": start, "endHour": end, "timezone": tz})
        db.add(setting)
    else:
        setting.value = {"startHour": start, "endHour": end, "timezone": tz}
    db.commit()
    return setting.value

