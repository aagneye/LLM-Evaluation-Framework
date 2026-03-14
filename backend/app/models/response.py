from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ModelResponse(Base):
    __tablename__ = "model_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    response_text = Column(Text, nullable=False)
    latency = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    prompt = relationship("Prompt", backref="responses")
