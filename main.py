from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from app.database import engine, Base, get_db
from app import models
from app.crud import router as user_router
from sqlalchemy.orm import Session
from sqlalchemy import text

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Connect router
app.include_router(user_router)

@app.get("/")
def root():
    return {"Hello": "World!"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"unhealthy: {e}")
