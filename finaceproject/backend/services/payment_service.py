"""
Payment Service
Handles Stripe integration and payment processing
"""
import os
import stripe
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from sqlalchemy.orm import Session

from backend.models.payment_models import (
    UserProfile, Subscription, Payment, Invoice, 
    PRICING_PLANS, SubscriptionPlan
)

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_key")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_your_key")
DOMAIN = os.getenv("DOMAIN", "http://localhost:8501")


class PaymentService:
    """Handle all payment-related operations"""
    
    def __init__(self, db: Session = None):
        self.db = db
    
    # ===========================
    # SUBSCRIPTION MANAGEMENT
    # ===========================
    
    def create_checkout_session(self, email: str, tier: str, billing_interval: str = "month") -> Dict:
        """Create Stripe checkout session for payment"""
        
        if tier not in PRICING_PLANS:
            raise ValueError(f"Invalid tier: {tier}")
        
        plan = PRICING_PLANS[tier]
        
        if tier == "free":
            # Free tier doesn't need payment
            return {
                "status": "free",
                "message": "Free tier activated"
            }
        
        if tier == "enterprise":
            raise ValueError("Enterprise requires manual setup")
        
        try:
            # Get or create customer
            customer = self._get_or_create_customer(email)
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=["card", "paypal"],
                billing_address_collection="required",
                line_items=[
                    {
                        "price": plan["stripe_price_id"],
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=f"{DOMAIN}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{DOMAIN}/payment-cancelled",
                metadata={
                    "tier": tier,
                    "email": email
                }
            )
            
            logger.info(f"Checkout session created for {email} - {tier}")
            
            return {
                "session_id": session.id,
                "client_secret": session.client_secret,
                "publishable_key": STRIPE_PUBLISHABLE_KEY,
                "url": session.url
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise
    
    def create_payment_intent(self, email: str, amount: float, description: str = "") -> Dict:
        """Create payment intent for one-time payments"""
        
        try:
            customer = self._get_or_create_customer(email)
            
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency="usd",
                customer=customer.id,
                description=description,
                metadata={
                    "email": email
                }
            )
            
            logger.info(f"Payment intent created for {email}")
            
            return {
                "client_secret": intent.client_secret,
                "publishable_key": STRIPE_PUBLISHABLE_KEY,
                "amount": amount,
                "currency": "usd"
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise
    
    def subscribe_user(self, user_id: int, email: str, tier: str, stripe_subscription_id: str, db: Session) -> Subscription:
        """Create subscription record after successful payment"""
        
        plan = PRICING_PLANS.get(tier, PRICING_PLANS["free"])
        
        # Get subscription from Stripe
        try:
            stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)
        except:
            stripe_sub = None
        
        # Create subscription record
        subscription = Subscription(
            user_id=user_id,
            email=email,
            tier=tier,
            stripe_subscription_id=stripe_subscription_id,
            status="active",
            amount=plan["price"],
            currency="usd",
            billing_interval=plan["billing_interval"],
            uploads_limit=plan["uploads_limit"],
            api_calls_limit=plan["api_calls_limit"],
            max_documents_compare=plan["max_documents_compare"],
        )
        
        if stripe_sub:
            subscription.current_period_start = datetime.fromtimestamp(stripe_sub.current_period_start)
            subscription.current_period_end = datetime.fromtimestamp(stripe_sub.current_period_end)
            subscription.billing_cycle_anchor = datetime.fromtimestamp(stripe_sub.billing_cycle_anchor)
        
        db.add(subscription)
        db.commit()
        
        logger.info(f"Subscription created for {email} - {tier}")
        
        return subscription
    
    def upgrade_subscription(self, user_id: int, new_tier: str, db: Session):
        """Upgrade user subscription to a higher tier"""
        
        # Get current subscription
        current = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        ).first()
        
        if not current:
            raise ValueError("No active subscription found")
        
        if new_tier == current.tier:
            raise ValueError("Already on this tier")
        
        new_plan = PRICING_PLANS[new_tier]
        
        try:
            # Update Stripe subscription
            stripe.Subscription.modify(
                current.stripe_subscription_id,
                items=[
                    {
                        "id": current.stripe_subscription_id,
                        "price": new_plan["stripe_price_id"]
                    }
                ],
                proration_behavior="create_prorations"
            )
            
            # Update local subscription
            current.tier = new_tier
            current.amount = new_plan["price"]
            current.uploads_limit = new_plan["uploads_limit"]
            current.api_calls_limit = new_plan["api_calls_limit"]
            current.max_documents_compare = new_plan["max_documents_compare"]
            current.updated_at = datetime.now()
            
            db.commit()
            
            logger.info(f"Subscription upgraded to {new_tier} for user {user_id}")
            
            return current
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error upgrading subscription: {str(e)}")
            raise
    
    def cancel_subscription(self, user_id: int, db: Session, reason: str = ""):
        """Cancel user subscription"""
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        ).first()
        
        if not subscription:
            raise ValueError("No active subscription found")
        
        try:
            # Cancel in Stripe
            stripe.Subscription.delete(subscription.stripe_subscription_id)
            
            # Update local record
            subscription.status = "cancelled"
            subscription.cancelled_at = datetime.now()
            subscription.updated_at = datetime.now()
            
            db.commit()
            
            logger.info(f"Subscription cancelled for user {user_id}")
            
            return subscription
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error cancelling subscription: {str(e)}")
            raise
    
    # ===========================
    # PAYMENT TRACKING
    # ===========================
    
    def record_payment(self, user_id: int, email: str, stripe_charge_id: str, 
                      amount: float, payment_method: str, db: Session) -> Payment:
        """Record a successful payment"""
        
        payment = Payment(
            user_id=user_id,
            email=email,
            stripe_charge_id=stripe_charge_id,
            amount=amount,
            currency="usd",
            payment_method=payment_method,
            status="completed",
            created_at=datetime.now()
        )
        
        db.add(payment)
        db.commit()
        
        logger.info(f"Payment recorded for {email}: ${amount}")
        
        return payment
    
    def handle_payment_failure(self, user_id: int, email: str, reason: str, db: Session) -> Payment:
        """Record a failed payment"""
        
        payment = Payment(
            user_id=user_id,
            email=email,
            status="failed",
            reason=reason,
            created_at=datetime.now()
        )
        
        db.add(payment)
        db.commit()
        
        logger.warning(f"Payment failed for {email}: {reason}")
        
        return payment
    
    def process_webhook(self, event: Dict, db: Session):
        """Process Stripe webhooks"""
        
        try:
            if event['type'] == 'payment_intent.succeeded':
                self._handle_payment_succeeded(event['data']['object'], db)
            
            elif event['type'] == 'payment_intent.payment_failed':
                self._handle_payment_failed(event['data']['object'], db)
            
            elif event['type'] == 'customer.subscription.updated':
                self._handle_subscription_updated(event['data']['object'], db)
            
            elif event['type'] == 'customer.subscription.deleted':
                self._handle_subscription_deleted(event['data']['object'], db)
            
            elif event['type'] == 'charge.refunded':
                self._handle_refund(event['data']['object'], db)
            
            logger.info(f"Webhook processed: {event['type']}")
        
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            raise
    
    def _handle_payment_succeeded(self, payment_intent: Dict, db: Session):
        """Handle successful payment"""
        email = payment_intent['metadata'].get('email')
        amount = payment_intent['amount'] / 100  # Convert from cents
        
        user = db.query(UserProfile).filter(UserProfile.email == email).first()
        if user:
            self.record_payment(user.id, email, payment_intent['id'], amount, 
                              payment_intent['payment_method_types'][0], db)
    
    def _handle_payment_failed(self, payment_intent: Dict, db: Session):
        """Handle failed payment"""
        email = payment_intent['metadata'].get('email')
        reason = payment_intent.get('last_payment_error', {}).get('message', 'Unknown')
        
        user = db.query(UserProfile).filter(UserProfile.email == email).first()
        if user:
            self.handle_payment_failure(user.id, email, reason, db)
    
    def _handle_subscription_updated(self, subscription: Dict, db: Session):
        """Handle subscription update"""
        sub = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription['id']
        ).first()
        
        if sub:
            sub.status = subscription['status']
            sub.current_period_start = datetime.fromtimestamp(subscription['current_period_start'])
            sub.current_period_end = datetime.fromtimestamp(subscription['current_period_end'])
            db.commit()
    
    def _handle_subscription_deleted(self, subscription: Dict, db: Session):
        """Handle subscription cancellation"""
        sub = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription['id']
        ).first()
        
        if sub:
            sub.status = "cancelled"
            sub.cancelled_at = datetime.now()
            db.commit()
    
    def _handle_refund(self, charge: Dict, db: Session):
        """Handle refund"""
        payment = db.query(Payment).filter(
            Payment.stripe_charge_id == charge['id']
        ).first()
        
        if payment:
            payment.status = "refunded"
            payment.refunded_amount = charge['amount_refunded'] / 100
            payment.refunded_at = datetime.now()
            db.commit()
    
    # ===========================
    # CUSTOMER MANAGEMENT
    # ===========================
    
    def _get_or_create_customer(self, email: str):
        """Get existing Stripe customer or create new one"""
        
        try:
            customers = stripe.Customer.list(email=email)
            
            if customers.data:
                return customers.data[0]
            else:
                # Create new customer
                customer = stripe.Customer.create(
                    email=email,
                    metadata={"source": "ai-financial-platform"}
                )
                return customer
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer error: {str(e)}")
            raise
    
    # ===========================
    # INVOICING
    # ===========================
    
    def generate_invoice(self, user_id: int, email: str, amount: float, 
                        description: str, db: Session) -> Invoice:
        """Generate invoice for payment"""
        
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{user_id}"
        
        invoice = Invoice(
            user_id=user_id,
            email=email,
            amount=amount,
            currency="usd",
            description=description,
            invoice_number=invoice_number,
            status="sent",
            invoice_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30)
        )
        
        db.add(invoice)
        db.commit()
        
        logger.info(f"Invoice generated: {invoice_number}")
        
        return invoice
    
    def get_user_invoices(self, user_id: int, db: Session) -> List[Invoice]:
        """Get all invoices for a user"""
        
        return db.query(Invoice).filter(
            Invoice.user_id == user_id
        ).order_by(Invoice.invoice_date.desc()).all()
    
    # ===========================
    # USAGE TRACKING
    # ===========================
    
    def increment_upload_count(self, user_id: int, db: Session):
        """Increment document upload count"""
        
        user = db.query(UserProfile).get(user_id)
        if user:
            user.uploads_used += 1
            db.commit()
    
    def increment_api_calls(self, user_id: int, calls: int = 1, db: Session = None):
        """Increment API call count"""
        
        if db:
            user = db.query(UserProfile).get(user_id)
            if user:
                user.api_calls_used += calls
                db.commit()
    
    def check_usage_limits(self, user_id: int, db: Session) -> Dict:
        """Check if user has exceeded limits"""
        
        user = db.query(UserProfile).get(user_id)
        if not user:
            raise ValueError("User not found")
        
        return {
            "uploads": {
                "used": user.uploads_used,
                "limit": user.uploads_limit,
                "exceeded": user.uploads_used >= user.uploads_limit
            },
            "api_calls": {
                "used": user.api_calls_used,
                "limit": user.api_calls_limit,
                "exceeded": user.api_calls_used >= user.api_calls_limit
            },
            "subscription_tier": user.subscription_tier
        }
    
    # ===========================
    # REPORTING
    # ===========================
    
    def get_revenue_report(self, db: Session, days: int = 30) -> Dict:
        """Get revenue report for admin dashboard"""
        
        start_date = datetime.now() - timedelta(days=days)
        
        payments = db.query(Payment).filter(
            Payment.created_at >= start_date,
            Payment.status == "completed"
        ).all()
        
        total_revenue = sum(p.amount for p in payments)
        total_payments = len(payments)
        
        subscriptions = db.query(Subscription).filter(
            Subscription.status == "active"
        ).all()
        
        mrr = sum(s.amount for s in subscriptions)  # Monthly Recurring Revenue
        
        tier_breakdown = {}
        for sub in subscriptions:
            tier_breakdown[sub.tier] = tier_breakdown.get(sub.tier, 0) + 1
        
        return {
            "total_revenue": total_revenue,
            "total_payments": total_payments,
            "mrr": mrr,
            "subscriptions": len(subscriptions),
            "tier_breakdown": tier_breakdown,
            "period_days": days
        }
