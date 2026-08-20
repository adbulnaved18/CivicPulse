from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.complaints import router as complaints_router
from app.services.database import initialize_database


app = FastAPI(title="CivicPulse API")

initialize_database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaints_router)