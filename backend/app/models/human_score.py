from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class HumanFeedback(Base):
    __tablename__ = "human_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("model_responses.id"), nullable=False)
    score = Column(Float, nullable=False)
    reviewer_name = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    response = relationship("ModelResponse", backref="human_feedback")
