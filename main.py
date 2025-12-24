from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

import database as db
from llm_service import llm_brain

# создание таблиц
db.Base.metadata.create_all(bind=db.engine)

app = FastAPI(
    title="Idea Creator",
    description="API для генерации идей с помощью LLM (Mistral)",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/brainstorm", response_model=db.BrainstormResponse, summary="Генерация идей")
def brainstorm(request: db.TopicCreate, session: Session = Depends(db.get_db)):
    """
    Принимает тему, генерирует идеи через LLM и сохраняет в БД.
    """
    # генерация
    generated_ideas = llm_brain.generate_ideas(request.title, request.count)
    
    # сохранение 
    db.create_brainstorm_session(session, request.title, generated_ideas)
    
    return {"topic": request.title, "ideas": generated_ideas}

@app.get("/topics", response_model=List[db.TopicSchema], summary="Получение списка всех тем")
def list_topics(session: Session = Depends(db.get_db)):
    """
    Возвращает список всех когда-либо созданных тем для генерации.
    """
    topics = db.get_all_topics(session)
    return topics

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')