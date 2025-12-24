import os
from datetime import datetime
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# настройка БД
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# модели для хранения в БД
class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    ideas = relationship("Idea", back_populates="topic", cascade="all, delete-orphan")

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

def create_brainstorm_session(db: Session, topic_text: str, ideas_list: List[str]):
    db_topic = Topic(title=topic_text)
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    
    for idea_text in ideas_list:
        db.add(Idea(text=idea_text, topic_id=db_topic.id))
    
    db.commit()
    return db_topic

def get_all_topics(db: Session):
    return db.query(Topic).order_by(Topic.created_at.desc()).all()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()