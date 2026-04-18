from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine

from auth import router as auth_router
from patients import router as patient_router
from appointments import router as appointment_router
from prescriptions import router as prescription_router


# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS (frontend support)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth_router, prefix="/api/auth")
app.include_router(patient_router, prefix="/api/patients")
app.include_router(appointment_router, prefix="/api/appointments")
app.include_router(prescription_router, prefix="/api/prescriptions")


# Health check
@app.get("/")
def root():
    return {"status": "API is running"}
