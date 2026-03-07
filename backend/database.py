from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./campaignx.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    brief = Column(Text)
    strategy = Column(Text)
    content_subject = Column(String)
    content_body = Column(Text)
    segments = Column(Text)  # JSON string of customer IDs
    scheduled_time = Column(String)
    status = Column(String, default="pending")  # pending, approved, rejected, sent
    open_rate = Column(Float, nullable=True)
    click_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
