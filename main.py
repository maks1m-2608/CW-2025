from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from contextlib import asynccontextmanager

import database as db
from llm_service import llm_brain

@asynccontextmanager
async def lifespan(app: FastAPI):
    # создание таблиц при старте
    async with db.engine.begin() as conn:
        await conn.run_sync(db.Base.metadata.create_all)
    yield

app = FastAPI(
    title="Idea Creator",
    description="API для генерации идей с помощью LLM (Mistral) [Async]",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/brainstorm", response_model=db.BrainstormResponse, summary="Генерация идей")
async def brainstorm(request: db.TopicCreate, session: AsyncSession = Depends(db.get_db)):
    """
    Принимает тему, генерирует идеи через LLM и сохраняет в БД асинхронно.
    """
    # генерация
    generated_ideas = await llm_brain.generate_ideas(request.title, request.count)
    
    # сохранение 
    await db.create_brainstorm_session(session, request.title, generated_ideas)
    
    return {"topic": request.title, "ideas": generated_ideas}

@app.get("/topics", response_model=List[db.TopicSchema], summary="Получение списка всех тем")
async def list_topics(session: AsyncSession = Depends(db.get_db)):
    """
    Возвращает список всех когда-либо созданных тем для генерации.
    """
    topics = await db.get_all_topics(session)
    return topics

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')