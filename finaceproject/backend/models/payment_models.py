"""
Payment Models
Handles subscriptions, payments, and billing
"""
from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()


# ===========================
# DATABASE MODELS
# ===========================

class SubscriptionTier(PyEnum):
    """Available subscription tiers"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class PaymentStatus(PyEnum):
    """Payment status tracking"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class UserProfile(Base):
    """Extended user profile with subscription info"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    hashed_password = Column(String)
    
    # Subscription details
    subscription_tier = Column(String, default="free")
    stripe_customer_id = Column(String, unique=True)
    stripe_subscription_id = Column(String)
    
    # Usage limits
    uploads_limit = Column(Integer, default=2)
    uploads_used = Column(Integer, default=0)
    api_calls_limit = Column(Integer, default=100)
    api_calls_used = Column(Integer, default=0)
    max_documents_compare = Column(Integer, default=1)
    
    # Account status
    active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Billing info
    billing_name = Column(String)
    billing_email = Column(String)
    billing_address = Column(String)
    billing_city = Column(String)
    billing_state = Column(String)
    billing_zip = Column(String)
    billing_country = Column(String)


class Subscription(Base):
    """Track active subscriptions"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    email = Column(String, nullable=False)
    
    # Subscription details
    tier = Column(String, nullable=False)  # free, starter, professional, enterprise
    stripe_subscription_id = Column(String, unique=True)
    stripe_price_id = Column(String)
    
    # Status
    status = Column(String, default="active")  # active, paused, cancelled
    
    # Billing cycle
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    billing_cycle_anchor = Column(DateTime)
    
    # Pricing
    amount = Column(Float, default=0)  # in USD
    currency = Column(String, default="usd")
    billing_interval = Column(String, default="month")  # month, year
    
    # Features
    uploads_limit = Column(Integer)
    api_calls_limit = Column(Integer)
    max_documents_compare = Column(Integer)
    features = Column(String)  # JSON string of features
    
    # Dates
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    cancelled_at = Column(DateTime)


class Payment(Base):
    """Track all payments"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    email = Column(String, nullable=False)
    
    # Payment details
    stripe_payment_id = Column(String, unique=True)
    stripe_charge_id = Column(String)
    
    # Amount and currency
    amount = Column(Float, nullable=False)  # in cents
    currency = Column(String, default="usd")
    
    # Payment method
    payment_method = Column(String)  # card, google_pay, apple_pay, paypal, etc
    last_4_digits = Column(String)  # Last 4 digits of card
    card_brand = Column(String)  # visa, mastercard, amex, etc
    
    # Status
    status = Column(String, default="pending")
    reason = Column(String)  # Description if failed
    
    # Related to
    subscription_id = Column(Integer)
    invoice_id = Column(Integer)
    
    # Refund tracking
    refunded_amount = Column(Float, default=0)
    refunded_at = Column(DateTime)
    
    # Dates
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Invoice(Base):
    """Track invoices for payments"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    email = Column(String, nullable=False)
    
    # Invoice details
    stripe_invoice_id = Column(String, unique=True)
    invoice_number = Column(String, unique=True)
    
    # Amount
    amount = Column(Float, nullable=False)
    currency = Column(String, default="usd")
    
    # Dates
    invoice_date = Column(DateTime, default=datetime.now)
    due_date = Column(DateTime)
    paid_date = Column(DateTime)
    
    # Status
    status = Column(String, default="draft")  # draft, sent, paid, overdue, cancelled
    
    # Description
    description = Column(String)
    line_items = Column(String)  # JSON string
    
    # PDF URL
    invoice_pdf_url = Column(String)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# ===========================
# PYDANTIC SCHEMAS
# ===========================

class UserProfileResponse(BaseModel):
    id: int
    email: str
    name: str
    subscription_tier: str
    uploads_used: int
    uploads_limit: int
    api_calls_used: int
    api_calls_limit: int
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionPlan(BaseModel):
    """Available subscription plans"""
    tier: str
    name: str
    price: float
    billing_interval: str
    features: list
    uploads_limit: int
    api_calls_limit: int
    max_documents_compare: int
    stripe_price_id: str


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    tier: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    amount: float
    currency: str
    billing_interval: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreateSubscriptionRequest(BaseModel):
    tier: str  # starter, professional, enterprise
    billing_interval: str = "month"  # month or year
    payment_method_id: str  # Stripe payment method ID


class PaymentResponse(BaseModel):
    id: int
    amount: float
    currency: str
    payment_method: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    amount: float
    currency: str
    status: str
    invoice_date: datetime
    paid_date: datetime
    invoice_pdf_url: str
    
    class Config:
        from_attributes = True


class CheckoutSessionRequest(BaseModel):
    tier: str
    email: str
    billing_interval: str = "month"


class CheckoutSessionResponse(BaseModel):
    session_id: str
    client_secret: str
    publishable_key: str
    url: str


class UpgradeSubscriptionRequest(BaseModel):
    new_tier: str
    proration_behavior: str = "create_prorations"  # create_prorations or none


class CancelSubscriptionRequest(BaseModel):
    reason: str = ""
    feedback: str = ""


# ===========================
# PRICING CONFIGURATION
# ===========================

PRICING_PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "billing_interval": "month",
        "features": [
            "2 document uploads/month",
            "Basic metric extraction",
            "Risk analysis",
            "Dashboard view",
            "Limited Q&A (5 questions/month)",
            "Community support"
        ],
        "uploads_limit": 2,
        "api_calls_limit": 0,
        "max_documents_compare": 0,
    },
    "starter": {
        "name": "Starter",
        "price": 29,  # $29/month or $290/year
        "billing_interval": "month",
        "stripe_price_id": "price_1234starter_monthly",  # Set after Stripe setup
        "features": [
            "50 document uploads/month",
            "Advanced metric extraction",
            "Comprehensive risk analysis",
            "Multi-document comparison (2 docs)",
            "Q&A (50 questions/month)",
            "Export reports (PDF, Excel)",
            "Email support",
            "API access (1000 calls/month)"
        ],
        "uploads_limit": 50,
        "api_calls_limit": 1000,
        "max_documents_compare": 2,
    },
    "professional": {
        "name": "Professional",
        "price": 99,  # $99/month or $990/year
        "billing_interval": "month",
        "stripe_price_id": "price_1234pro_monthly",  # Set after Stripe setup
        "features": [
            "Unlimited document uploads",
            "Advanced metric extraction",
            "Comprehensive risk analysis",
            "Multi-document comparison (10 docs)",
            "Unlimited Q&A",
            "Export reports (PDF, Excel, CSV)",
            "Priority email support",
            "API access (50000 calls/month)",
            "Webhook support",
            "Custom metrics configuration",
            "Scheduled analysis",
            "Team collaboration (3 users)"
        ],
        "uploads_limit": 10000,
        "api_calls_limit": 50000,
        "max_documents_compare": 10,
    },
    "enterprise": {
        "name": "Enterprise",
        "price": None,  # Custom pricing
        "billing_interval": "month",
        "stripe_price_id": None,
        "features": [
            "Unlimited everything",
            "Dedicated account manager",
            "Custom metric development",
            "Advanced analytics dashboard",
            "SSO & fine-grained access control",
            "99.9% SLA",
            "24/7 priority support",
            "On-premise deployment option",
            "Custom integrations",
            "Unlimited API calls",
            "Unlimited team members",
            "Advanced security features",
            "Custom reporting"
        ],
        "uploads_limit": 999999,
        "api_calls_limit": 999999,
        "max_documents_compare": 999999,
    }
}
