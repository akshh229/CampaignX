from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./campaignx.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True)
    brief = Column(Text)
    parsed_brief_json = Column(Text, nullable=True)
    strategy = Column(Text)
    content_subject = Column(String)
    content_body = Column(Text)
    content_a_json = Column(Text, nullable=True)
    content_b_json = Column(Text, nullable=True)
    segments = Column(Text)
    scheduled_time = Column(String)
    campaign_ids_json = Column(Text, nullable=True)
    metrics_json = Column(Text, nullable=True)
    status = Column(String, default="pending")
    open_rate = Column(Float, nullable=True)
    click_rate = Column(Float, nullable=True)
    total_eo = Column(Integer, nullable=True)
    total_ec = Column(Integer, nullable=True)
    cohort_size = Column(Integer, nullable=True)
    coverage_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    events = relationship("AgentEvent", back_populates="campaign", cascade="all, delete-orphan")
    approvals = relationship("ApprovalHistory", back_populates="campaign", cascade="all, delete-orphan")
    iterations = relationship("IterationHistory", back_populates="campaign", cascade="all, delete-orphan")


class AgentEvent(Base):
    __tablename__ = "agent_events"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    agent_name = Column(String)
    event_type = Column(String)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="events")


class ApprovalHistory(Base):
    __tablename__ = "approval_history"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    reviewer_notes = Column(Text)
    decision = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    campaign = relationship("Campaign", back_populates="approvals")


class IterationHistory(Base):
    __tablename__ = "iteration_history"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    iteration_number = Column(Integer)
    variant_name = Column(String)
    content_subject = Column(String)
    content_body = Column(Text)
    open_rate = Column(Float, nullable=True)
    click_rate = Column(Float, nullable=True)
    score = Column(Float, nullable=True)
    winner = Column(String, nullable=True)
    action_taken = Column(Text, nullable=True)
    total_eo = Column(Integer, nullable=True)
    total_ec = Column(Integer, nullable=True)
    campaign_external_id = Column(String, nullable=True)
    metrics_snapshot = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="iterations")


def _ensure_sqlite_columns():
    required_columns = {
        "campaigns": {
            "parsed_brief_json": "TEXT",
            "campaign_ids_json": "TEXT",
            "metrics_json": "TEXT",
            "content_a_json": "TEXT",
            "content_b_json": "TEXT",
            "total_eo": "INTEGER",
            "total_ec": "INTEGER",
            "cohort_size": "INTEGER",
            "coverage_count": "INTEGER",
            "updated_at": "DATETIME",
        },
        "iteration_history": {
            "score": "FLOAT",
            "winner": "TEXT",
            "action_taken": "TEXT",
            "total_eo": "INTEGER",
            "total_ec": "INTEGER",
            "campaign_external_id": "TEXT",
            "metrics_snapshot": "TEXT",
        },
    }

    with engine.begin() as conn:
        for table_name, columns in required_columns.items():
            table_info = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
            existing_columns = {row[1] for row in table_info}
            for column_name, ddl in columns.items():
                if column_name not in existing_columns:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}"))


def init_db():
    Base.metadata.create_all(bind=engine)
    _ensure_sqlite_columns()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
