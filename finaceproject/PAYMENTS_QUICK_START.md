# ⚡ **Quick Payment Setup Reference**

## 🎯 **Do This First (15 minutes)**

### 1. Create Stripe Account
```
https://stripe.com → Sign Up → Verify Email
```

### 2. Get Credentials
```
Dashboard → Developers → API Keys
Copy: pk_test_... and sk_test_...
```

### 3. Update .env
```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### 4. Test
```bash
# Terminal 1
python -m uvicorn backend.main:app --reload

# Terminal 2
streamlit run frontend/app.py
```

Visit: http://localhost:8501 → Go to "💳 Pricing & Billing" tab

## 💳 **Test Card Numbers**

| Type | Number | Expires | CVC |
|------|--------|---------|-----|
| Visa | 4242 4242 4242 4242 | Any | Any |
| Mastercard | 5555 5555 5555 4444 | Any | Any |
| Amex | 3782 822463 10005 | Any | Any |
| Declined | 4000 0000 0000 0002 | Any | Any |

## 📊 **4 Pricing Tiers**

| Tier | Price | Uploads | Q&A | Comparison | API |
|------|-------|---------|-----|-----------|-----|
| Free | $0 | 2/mo | 5/mo | ❌ | ❌ |
| Starter | $29 | 50/mo | ∞ | 2 docs | 1K |
| Pro | $99 | ∞ | ∞ | 10 docs | 50K |
| Enterprise | Custom | ∞ | ∞ | ∞ | ∞ |

## 🎁 **What You Get**

✅ Complete payment processing
✅ Google Pay support
✅ PayPal support
✅ Subscription management
✅ Automatic invoicing
✅ Usage tracking
✅ Revenue reporting
✅ 1,750+ lines of code
✅ Production-ready

## 📁 **Files Added**

```
backend/models/payment_models.py       (450 lines)
backend/services/payment_service.py    (550 lines)
backend/routes/payment_routes.py       (350 lines)
frontend/pages/5_💳_Pricing_Billing.py (400 lines)

STRIPE_SETUP.md                        (Setup guide)
PAYMENTS_GUIDE.md                      (This guide)
```

## 🚀 **What's Next**

1. **Setup Stripe** - 5 min
2. **Add Credentials** - 2 min
3. **Test Payments** - 5 min
4. **Go Live** - When ready

## 💻 **Payment Flow**

```
User → Pricing Tab → Choose Plan → Checkout → 
Stripe Payment → Subscription Activated → Dashboard Updated
```

## 🔑 **3 Important Files**

1. **`STRIPE_SETUP.md`** - Detailed configuration
2. **`PAYMENTS_GUIDE.md`** - Full implementation guide
3. **`.env`** - Your API keys (keep secret!)

## 📞 **One Command to Install**

```bash
pip install stripe sqlalchemy psycopg2-binary fastapi-users
```

## 🎓 **That's It!**

Your app now accepts:
- 💳 Credit cards
- 🔷 Google Pay
- 🅿️ PayPal
- 🍎 Apple Pay

**Start making money! 💰**
