import stripe
import os

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# =========================
# CREATE CHECKOUT SESSION
# =========================
@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):

    data = await request.json()

    email = data.get("email")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],

            mode="subscription",

            customer_email=email,

            line_items=[
                {
                    "price": "price_1TZAcALNtRRGpUKEX0Ox6KE5",
                    "quantity": 1,
                }
            ],

            success_url="http://localhost:5173/success",
            cancel_url="http://localhost:5173/cancel",
        )

        return {"url": session.url}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# =========================
# STRIPE WEBHOOK
# =========================
@router.post("/webhook")
async def stripe_webhook(request: Request):

    payload = await request.body()

    sig_header = request.headers.get("stripe-signature")

    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            endpoint_secret
        )

    except stripe.error.SignatureVerificationError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid signature"}
        )

    # =========================
    # PAYMENT SUCCESS
    # =========================
    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        customer_email = session.get("customer_email")

        print("Subscription successful:", customer_email)

        # TODO:
        # Update database subscription status here

    return {"status": "success"}