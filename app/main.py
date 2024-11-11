import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from app.db.database import Base, engine
from app.routes.scrape_routes import router as scrap_route
from app.routes.FileVectorization_route import router as vector_route
from fastapi.middleware.cors import CORSMiddleware





def create_table():
    try:
        from app.models.Data_model import Data
        from app.models.Scrapped_model import ScrapedData
        from app.models.Vectorize_model import VectorizeData
        Base.metadata.create_all(engine)
        logging.info("Database TAbe Created Successfully")
    except Exception as e:
        logging.error("Error in creating database table", e)

@asynccontextmanager
async def lifespan(app:FastAPI):
    try:
        create_table()
        logging.info("Database tables created Successfully..")
    except Exception as e:
        logging.error(f"Failed to connect to the database: {e}")
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(scrap_route)
app.include_router(vector_route)


origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


create_table()

@app.get('/')
def index():
    return {'message': 'Hello World'}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080, reload=True)