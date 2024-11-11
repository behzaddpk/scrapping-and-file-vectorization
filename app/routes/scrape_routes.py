from fastapi import FastAPI, APIRouter, Request, status, HTTPException, Depends
from pydantic import BaseModel
from app.utilities.scrapper import Scrapper
from app.models.Scrapped_model import ScrapedData
import openai
import os
from dotenv import load_dotenv
import json
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.utilities.Services import EmbeddingService
from typing import List
# Load environment variables
load_dotenv()

router = APIRouter(tags=['Data Scrapping'])

class ScraperBase(BaseModel):
    url: str

@router.post('/scrape-data')
async def scrape_data(url: ScraperBase, request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    model_name = payload.get("model_name", "text-embedding-3-small")
    url = payload.get('url')
    
    scraper_content = Scrapper(url)
    content_str = json.dumps(scraper_content)
    print(f"content is: {content_str}")
    
    try:
        embedding_service = EmbeddingService(model_name=model_name)
        embedding = embedding_service.embeddings.embed_documents([content_str])[0]
        
        
        existing_content = db.query(ScrapedData).filter(ScrapedData.url==url).first()
        if existing_content:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Content Already Exist")
        
        
        data = ScrapedData(url=url, content=content_str, embeddings=embedding)
        db.add(data)
        db.commit()
        db.refresh(data)


        return {"Message": "Content and Embeddings are stored Successfully..", "Content": content_str, "Embedding": embedding}
    
    except openai.OpenAIError as e:
        return {"error": str(e)}

class ScrapDataSchema(BaseModel):
    id: int
    url: str
    content: str
    embeddings: list

    class Config:
        orm_mode = True


@router.get('/scrap-data', response_model=List[ScrapDataSchema])
async def scrap_data(db: Session = Depends(get_db)):
    data = db.query(ScrapedData).all()
    return data


@router.delete('/delete-scrap/{id}')
async def deletevector(id: int, db: Session = Depends(get_db)):
    scrap= db.query(ScrapedData).filter(ScrapedData.id == id).first()
    if not scrap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data isn't Exist on this id: {id}")
    db.delete(scrap)
    db.commit()
    return {"message": "Vector Deleted Successfully"}