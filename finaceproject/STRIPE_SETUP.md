"""
PAYMENT SETUP GUIDE
How to configure Stripe and enable payments
"""

# ===========================
# STRIPE SETUP INSTRUCTIONS
# ===========================

## Step 1: Create Stripe Account

1. Go to https://stripe.com
2. Click "Sign Up"
3. Enter email, password, and business info
4. Verify your email
5. Complete account setup with:
   - Business name
   - Business address
   - Bank account details
   - Tax ID (optional)

## Step 2: Get API Keys

1. Log in to Stripe Dashboard
2. Go to: Developers > API Keys
3. Copy your keys:
   - **Publishable Key** (pk_test_...)
   - **Secret Key** (sk_test_...)

⚠️ IMPORTANT: Keep Secret Key safe! Never expose in frontend!

## Step 3: Set Environment Variables

Create/update `.env` file with:

```bash
# Stripe Keys
STRIPE_SECRET_KEY=sk_test_your_actual_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_test_your_webhook_secret

# Application
DOMAIN=http://localhost:8501  # or your production domain
BACKEND_URL=http://localhost:8000
```

## Step 4: Create Products & Prices in Stripe

### Option A: Create via Dashboard

1. Go to Stripe Dashboard > Products
2. Create product "Starter Plan"
   - Price: $29/month (recurring)
   - Copy Price ID

3. Create product "Professional Plan"
   - Price: $99/month (recurring)
   - Copy Price ID

### Option B: Create via API

```bash
# Starter Plan
curl https://api.stripe.com/v1/products \
  -u sk_test_YOUR_KEY: \
  -d name="Starter Plan" \
  -d type=service

curl https://api.stripe.com/v1/prices \
  -u sk_test_YOUR_KEY: \
  -d product=prod_... \
  -d unit_amount=2900 \
  -d currency=usd \
  -d recurring[interval]=month

# Professional Plan
curl https://api.stripe.com/v1/products \
  -u sk_test_YOUR_KEY: \
  -d name="Professional Plan" \
  -d type=service

curl https://api.stripe.com/v1/prices \
  -u sk_test_YOUR_KEY: \
  -d product=prod_... \
  -d unit_amount=9900 \
  -d currency=usd \
  -d recurring[interval]=month
```

## Step 5: Add Price IDs to Code

Update `backend/models/payment_models.py`:

```python
PRICING_PLANS = {
    "starter": {
        "stripe_price_id": "price_1XXXXXXXXX",  # Your actual ID
        ...
    },
    "professional": {
        "stripe_price_id": "price_1YYYYYYYYY",  # Your actual ID
        ...
    }
}
```

## Step 6: Configure Webhooks

1. Go to Stripe Dashboard > Developers > Webhooks
2. Click "Add Endpoint"
3. Enter endpoint URL:
   ```
   https://yourdomain.com/api/v1/payments/webhook
   ```
4. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `charge.refunded`
5. Copy Webhook Secret
6. Add to `.env`:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

## Step 7: Install Updated Dependencies

```bash
pip install -r requirements.txt --upgrade
```

## Step 8: Test Payment Flow

### Test Credentials

Use these test card numbers in development:

- **Visa**: 4242 4242 4242 4242
- **Mastercard**: 5555 5555 5555 4444
- **American Express**: 3782 822463 10005
- **Declined**: 4000 0000 0000 0002

Expiration: Any future date (MM/YY)
CVC: Any 3 digits

### Testing Steps

1. Start backend: `python -m uvicorn backend.main:app --reload`
2. Start frontend: `streamlit run frontend/app.py`
3. Go to Pricing & Billing tab
4. Click "Choose Plan"
5. Enter test email
6. Proceed to payment
7. Use test card above
8. Confirm payment succeeded

## Step 9: Test Webhook

```bash
# From Stripe Dashboard > Webhooks
# Click "Send test event"
# Select payment_intent.succeeded
# Check your logs for webhook processing
```

## Step 10: Setup Database

If using PostgreSQL:

```bash
# Install PostgreSQL
# Create database
createdb financeproject

# Update connection string in .env
DATABASE_URL=postgresql://user:password@localhost/financeproject

# Run migrations
alembic upgrade head
```

## Testing Payments with Different Methods

### Google Pay
- Available in Stripe Checkout automatically
- Requires customer to have Google Pay setup

### PayPal
- Enable in Stripe Dashboard > Settings > Payment Methods
- Customer clicks PayPal button in checkout
- Redirected to PayPal login
- Confirmation returned to Stripe

### Apple Pay
- Available on Safari/Apple devices
- Automatic in Stripe Checkout

## Production Checklist

- [ ] Use Live Stripe keys (sk_live_, pk_live_)
- [ ] Set DOMAIN to production URL
- [ ] Enable HTTPS/SSL
- [ ] Use environment variables from deployment platform
- [ ] Test all payment methods
- [ ] Setup monitoring/alerts
- [ ] Configure backup payment methods
- [ ] Setup customer support for payment issues
- [ ] Enable 3D Secure for fraud prevention
- [ ] Review Stripe billing settings
- [ ] Setup tax compliance (if needed)

## Troubleshooting

### Payment not processing
- Check SECRET KEY is correct
- Verify test/live mode matches
- Check webhook is configured
- Review Stripe Dashboard logs

### Webhook not firing
- Verify webhook URL is accessible
- Check webhook secret in code
- Review Stripe event logs
- Test with "Send test event"

### Customer portal not working
- Ensure PostgreSQL is running
- Check database connection string
- Verify user exists in database

## Support

- Stripe Docs: https://stripe.com/docs
- Stripe Dashboard: https://dashboard.stripe.com
- Stripe Support: https://support.stripe.com
