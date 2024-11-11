from app.db.database import Base
from sqlalchemy import Column, Integer, String, Text, JSON
from app.db.database import engine

class VectorizeData(Base):
    __tablename__ = "Vectorize_data"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    resource = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    vector = Column(JSON, nullable=True)

    def __repr__(self):
        return f"ScrapeData(id='{self.id}', url='{self.url}', content='{self.content}', vector='{self.vector}')"