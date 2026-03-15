from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api import crud, db

router = APIRouter()

def get_db():
    database = db.SessionLocal()
    try:
        yield database
    finally:
        database.close()

@router.get("/data")
def read_all(limit: int = 100, db_session: Session = Depends(get_db)):
    return crud.get_all_data(db_session, limit)

@router.get("/data/by-date")
def read_by_date(start_date: str, end_date: str, db_session: Session = Depends(get_db)):
    return crud.get_by_date_range(db_session, start_date, end_date)

@router.get("/data/by-plant")
def read_by_plant(plant_code: str, db_session: Session = Depends(get_db)):
    return crud.get_by_plant(db_session, plant_code)



