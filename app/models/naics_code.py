from sqlalchemy import Column, String, Text

from app.database import Base

class NAICSCode(Base):
    __tablename__ = "naics_codes"
    
    code = Column(String(10), primary_key=True)
    description = Column(Text, nullable=False)