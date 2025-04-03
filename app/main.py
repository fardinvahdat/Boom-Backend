from fastapi import FastAPI
from app.api.v1.api_v1 import api_router
from app.config import settings
from app.database import engine, Base

app = FastAPI(title=settings.PROJECT_NAME)

# Include API routers
app.include_router(api_router, prefix="/api/v1")

# Create database tables (for development)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
