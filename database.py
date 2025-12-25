import os
from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# настройка БД
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# модели для хранения в БД
class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    ideas = relationship("Idea", back_populates="topic", cascade="all, delete-orphan", lazy="selectin")

class Idea(Base):
    __tablename__ = "ideas"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    topic = relationship("Topic", back_populates="ideas")


class TopicCreate(BaseModel):
    title: str
    count: int = 10

class BrainstormResponse(BaseModel):
    topic: str
    ideas: List[str]

class TopicSchema(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

async def create_brainstorm_session(db: AsyncSession, topic_text: str, ideas_list: List[str]):
    db_topic = Topic(title=topic_text)
    db.add(db_topic)

    for idea_text in ideas_list:
        db_idea = Idea(text=idea_text, topic=db_topic)
        db.add(db_idea)
    
    await db.commit()
    await db.refresh(db_topic)
    return db_topic

async def get_all_topics(db: AsyncSession):
    result = await db.execute(select(Topic).order_by(Topic.created_at.desc()))
    return result.scalars().all()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session