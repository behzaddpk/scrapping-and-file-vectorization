import logging
from fastapi import FastAPI, APIRouter, UploadFile, File, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.models.Data_model import Data
from app.models.Vectorize_model import VectorizeData
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import uuid
import shutil
from app.utilities.Services import VectorizationService
from app.db.database import get_db
from typing import List

router = APIRouter(tags=['Vectorization'])

class FileBase(BaseModel):
    file: str

@router.post("/file-vectorization")
async def file_vectorization(file: UploadFile = File(...), db: Session = Depends(get_db)):
    extension = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{extension}"
    metadata = {"file_name": unique_name}

    file_path = f"documents/{unique_name}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)

    documents = VectorizationService.load_documents(file_path, extension, metadata)

    
    vector_service = VectorizationService()
    vectors, chunks = vector_service.vector_document(documents)
    
    for vector, chunk in zip(vectors, chunks):
        new_data = VectorizeData(
            resource=file_path,
            content=chunk,
            vector=vector
        )
        db.add(new_data)
    db.commit()
    return {"message": "File Processed Successfully", "documents": documents}

@router.get('/search')
async def search_similar(prompt: str, db: Session = Depends(get_db)):
    vector_service = VectorizationService()
    results = vector_service.search_similar(prompt, db)
    return {"results": [result.page_content for result in results]}

from pydantic import BaseModel

class VectorizeDataSchema(BaseModel):
    id: int
    resource: str
    content: str
    vector: list

    class Config:
        orm_mode = True

@router.get('/Vectors-file', response_model=List[VectorizeDataSchema])
async def get_vectors(db: Session = Depends(get_db)):
    vectors = db.query(VectorizeData).all()
    return vectors


@router.delete('/delete-vector/{id}')
async def deletevector(id: int, db: Session = Depends(get_db)):
    vector= db.query(VectorizeData).filter(VectorizeData.id == id).first()
    if not vector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data isn't Exist on this id: {id}")
    db.delete(vector)
    db.commit()
    return {"message": "Vector Deleted Successfully"}