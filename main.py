from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


import traceback

import models
from database import engine

# ================= ROUTERS =================
from auth import router as auth_router
from patients import router as patient_router
from appointments import router as appointment_router
from prescriptions import router as prescription_router
from subscription_manual import router as subscription_router
from payments import router as payments_router


app = FastAPI()

# ================= DB INIT =================
models.Base.metadata.create_all(bind=engine)

# ================= CORS =================
# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://clinic-saas-frontend-chi.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= ROUTES =================
app.include_router(auth_router, prefix="/api/auth")
app.include_router(patient_router, prefix="/api/patients")
app.include_router(appointment_router, prefix="/api/appointments")
app.include_router(prescription_router, prefix="/api/prescriptions")
app.include_router(subscription_router, prefix="/api/subscription")
app.include_router(payments_router, prefix="/api/payments")


# ================= ROOT =================
@app.get("/")
def root():
    return {"status": "API running"}


# ================= GLOBAL ERROR HANDLER =================
@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    print("\n🔥 FULL BACKEND ERROR:")
    traceback.print_exc()

    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )