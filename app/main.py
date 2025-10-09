from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.base import Base, engine
from app.api.v1.routes import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Database connected and tables created")
    yield 
    print("app shutting down")


app = FastAPI(title="Zenskar Customer Sync Service", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Server is up"}
