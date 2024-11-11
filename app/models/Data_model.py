from app.db.database import Base
from sqlalchemy import Column, Integer, String, Text, JSON
from app.db.database import engine

class Data(Base):
    __tablename__ = "data"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    resource = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    embedtor = Column(JSON, nullable=True)

    def __repr__(self):
        return f"ScrapeData(id='{self.id}', url='{self.url}', content='{self.content}', embeddings='{self.embeddings}')"