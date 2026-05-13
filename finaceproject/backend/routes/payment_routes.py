"""
Payment Routes
REST API endpoints for handling payments and subscriptions
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import stripe
import json
import logging
import os

from backend.models.payment_models import (
    CheckoutSessionRequest, CheckoutSessionResponse, SubscriptionResponse,
    CreateSubscriptionRequest, UpgradeSubscriptionRequest, CancelSubscriptionRequest,
    PaymentResponse, InvoiceResponse, PRICING_PLANS
)
from backend.services.payment_service import PaymentService
from backend.models.schemas import UserResponse

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

# Stripe webhook secret
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")


# ===========================
# DEPENDENCY INJECTION
# ===========================

def get_payment_service(db: Session = Depends(lambda: None)) -> PaymentService:
    """Get payment service instance"""
    return PaymentService(db)


# ===========================
# PRICING & PLANS
# ===========================

@router.get("/plans")
async def get_pricing_plans():
    """Get all available pricing plans"""
    return {
        "plans": PRICING_PLANS,
        "currency": "usd",
        "message": "All pricing plans available"
    }


@router.get("/plans/{tier}")
async def get_plan_details(tier: str):
    """Get details for a specific pricing tier"""
    
    if tier not in PRICING_PLANS:
        raise HTTPException(status_code=404, detail="Tier not found")
    
    plan = PRICING_PLANS[tier]
    return {
        "tier": tier,
        "details": plan
    }


# ===========================
# CHECKOUT & PAYMENT
# ===========================

@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Create Stripe checkout session"""
    
    try:
        session = payment_service.create_checkout_session(
            email=request.email,
            tier=request.tier,
            billing_interval=request.billing_interval
        )
        
        return CheckoutSessionResponse(**session)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail="Payment processing failed")
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/payment-intent")
async def create_payment_intent(
    email: str,
    amount: float,
    description: str = "",
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Create payment intent for one-time payment"""
    
    try:
        intent = payment_service.create_payment_intent(email, amount, description)
        return intent
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail="Payment processing failed")


@router.get("/checkout-success")
async def checkout_success(session_id: str):
    """Handle successful checkout"""
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        return {
            "status": "success",
            "session_id": session_id,
            "subscription_id": session.subscription,
            "customer_email": session.customer_details.email
        }
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail="Session retrieval failed")


# ===========================
# SUBSCRIPTION MANAGEMENT
# ===========================

@router.post("/subscribe", response_model=SubscriptionResponse)
async def subscribe(
    user_id: int,
    tier: str,
    stripe_subscription_id: str,
    db: Session = Depends(lambda: None),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Create subscription after payment"""
    
    try:
        # Get user email (you would get this from your user DB)
        subscription = payment_service.subscribe_user(
            user_id=user_id,
            email="user@example.com",  # Get from DB in production
            tier=tier,
            stripe_subscription_id=stripe_subscription_id,
            db=db
        )
        
        return SubscriptionResponse.from_orm(subscription)
    
    except Exception as e:
        logger.error(f"Subscription error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upgrade")
async def upgrade_subscription(
    user_id: int,
    request: UpgradeSubscriptionRequest,
    db: Session = Depends(lambda: None),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Upgrade subscription to higher tier"""
    
    try:
        subscription = payment_service.upgrade_subscription(
            user_id=user_id,
            new_tier=request.new_tier,
            db=db
        )
        
        return {
            "status": "success",
            "message": f"Upgraded to {request.new_tier}",
            "subscription": SubscriptionResponse.from_orm(subscription)
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upgrade error: {str(e)}")
        raise HTTPException(status_code=500, detail="Upgrade failed")


@router.post("/cancel")
async def cancel_subscription(
    user_id: int,
    request: CancelSubscriptionRequest,
    db: Session = Depends(lambda: None),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Cancel active subscription"""
    
    try:
        subscription = payment_service.cancel_subscription(
            user_id=user_id,
            db=db,
            reason=request.reason
        )
        
        return {
            "status": "success",
            "message": "Subscription cancelled",
            "subscription": SubscriptionResponse.from_orm(subscription)
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Cancellation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Cancellation failed")


# ===========================
# WEBHOOKS
# ===========================

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(lambda: None),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Handle Stripe webhook events"""
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    try:
        # Process the event
        payment_service.process_webhook(event, db)
        
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


# ===========================
# USAGE & LIMITS
# ===========================

@router.get("/usage/{user_id}")
async def get_usage(
    user_id: int,
    db: Session = Depends(lambda: None),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get user's current usage and limits"""
    
    try:
        usage = payment_service.check_usage_limits(user_id, db)
        return usage
    
    except Exception as e:
        logger.error(f"Usage check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# INVOICING
# ===========================

@router.get("/invoices/{user_id}")
async def get_invoices(
    user_id: int,
    db: Session = Depends(lambda: None),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get all invoices for a user"""
    
    try:
        invoices = payment_service.get_user_invoices(user_id, db)
        
        return {
            "user_id": user_id,
            "invoices": [
                {
                    "id": inv.id,
                    "number": inv.invoice_number,
                    "amount": inv.amount,
                    "date": inv.invoice_date,
                    "status": inv.status
                }
                for inv in invoices
            ]
        }
    
    except Exception as e:
        logger.error(f"Invoice retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve invoices")


# ===========================
# ADMIN REPORTING
# ===========================

@router.get("/admin/revenue")
async def get_revenue_report(
    days: int = 30,
    db: Session = Depends(lambda: None),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get revenue report (admin only)"""
    
    # In production, verify admin role here
    
    try:
        report = payment_service.get_revenue_report(db, days)
        return report
    
    except Exception as e:
        logger.error(f"Revenue report error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate report")


@router.get("/admin/health")
async def payment_health_check():
    """Check if payment system is operational"""
    
    try:
        # Test Stripe connection
        stripe.Account.retrieve()
        
        return {
            "status": "healthy",
            "stripe": "connected",
            "timestamp": str(datetime.now())
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment system unavailable")
