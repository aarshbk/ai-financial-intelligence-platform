"""
Streamlit Payment & Pricing Pages
Frontend UI for payment processing
"""
import streamlit as st
import requests
import os
from datetime import datetime

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def show_pricing_page():
    """Display pricing and subscription options"""
    
    st.markdown("---")
    st.markdown("# 💳 **Pricing Plans**")
    st.markdown("Choose the perfect plan for your financial analysis needs")
    
    # Get pricing plans from backend
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/payments/plans")
        plans = response.json()["plans"]
    except:
        st.error("Failed to load pricing. Please try again later.")
        return
    
    # Display pricing cards
    col1, col2, col3, col4 = st.columns(4)
    
    columns = [col1, col2, col3, col4]
    plan_keys = ["free", "starter", "professional", "enterprise"]
    
    for idx, (col, plan_key) in enumerate(zip(columns, plan_keys)):
        with col:
            plan = plans[plan_key]
            
            # Card styling
            if plan_key == "professional":
                st.markdown("### ⭐ **MOST POPULAR**")
            
            st.markdown(f"### {plan['name']}")
            
            # Price
            if plan['price'] is None:
                st.markdown("### 💼 Custom")
            else:
                st.markdown(f"### ${plan['price']}/month")
            
            # Features
            st.markdown("**Features:**")
            for feature in plan['features'][:5]:  # Show first 5
                st.markdown(f"✓ {feature}")
            
            if len(plan['features']) > 5:
                st.markdown(f"... and {len(plan['features']) - 5} more")
            
            # Action button
            if plan_key == "free":
                if st.button("Get Started", key=f"btn_{plan_key}"):
                    st.session_state.selected_plan = plan_key
                    st.success("Free tier activated! Create an account to get started.")
            
            elif plan_key == "enterprise":
                if st.button("Contact Sales", key=f"btn_{plan_key}"):
                    st.info("Please email: sales@yourplatform.com")
            
            else:
                if st.button("Choose Plan", key=f"btn_{plan_key}"):
                    st.session_state.selected_plan = plan_key
                    st.session_state.show_checkout = True
                    st.rerun()
    
    st.markdown("---")


def show_checkout_page():
    """Display checkout/payment page"""
    
    st.markdown("# 💳 **Complete Your Purchase**")
    
    # Get selected plan
    selected_plan = st.session_state.get("selected_plan", "starter")
    
    # Try to load user email
    user_email = st.text_input("Email Address", placeholder="your@email.com")
    
    billing_interval = st.radio(
        "Billing Cycle",
        options=["month", "year"],
        format_func=lambda x: "Monthly" if x == "month" else "Annual (Save 15%)"
    )
    
    st.markdown("---")
    
    # Summary
    st.markdown("### Order Summary")
    response = requests.get(f"{BACKEND_URL}/api/v1/payments/plans/{selected_plan}")
    plan = response.json()["details"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Plan:** {plan['name']}")
        st.write(f"**Billing:** {billing_interval.capitalize()}")
    
    with col2:
        if billing_interval == "month":
            total = plan['price']
        else:
            total = plan['price'] * 12 * 0.85  # 15% discount
        
        st.write(f"**Total:** ${total:.2f}")
    
    st.markdown("---")
    
    # Payment methods info
    st.markdown("### Accepted Payment Methods")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("🔷 **Credit/Debit Cards**")
        st.text("Visa, Mastercard, Amex")
    
    with col2:
        st.markdown("🔵 **Google Pay**")
        st.text("Fast & Secure")
    
    with col3:
        st.markdown("🅿️ **PayPal**")
        st.text("PayPal Balance/Card")
    
    st.markdown("---")
    
    # Checkout button
    if st.button("Proceed to Payment", type="primary", use_container_width=True):
        
        if not user_email or "@" not in user_email:
            st.error("Please enter a valid email address")
            return
        
        # Create checkout session
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/v1/payments/checkout",
                json={
                    "email": user_email,
                    "tier": selected_plan,
                    "billing_interval": billing_interval
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                st.success("Redirecting to secure payment page...")
                st.markdown(f"[Click here if not redirected]({data['url']})")
                st.session_state.checkout_url = data['url']
            else:
                st.error(f"Checkout failed: {response.json()['detail']}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Trust badges
    st.markdown("""
    ✅ **Secure Payment Processing**
    🔒 256-bit SSL Encryption
    📋 PCI DSS Compliant
    🛡️ Fraud Protection
    """)


def show_subscription_dashboard():
    """Display user's subscription and billing info"""
    
    st.markdown("# 📊 **Your Subscription**")
    
    # Get user ID from session
    user_id = st.session_state.get("user_id", 1)
    
    try:
        # Get usage info
        response = requests.get(f"{BACKEND_URL}/api/v1/payments/usage/{user_id}")
        usage = response.json()
        
        # Display subscription status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Current Plan",
                usage['subscription_tier'].title(),
                "Active"
            )
        
        with col2:
            uploads = usage['uploads']
            st.metric(
                "Uploads",
                f"{uploads['used']}/{uploads['limit']}",
                f"{int(uploads['used']/max(uploads['limit'], 1)*100)}% used"
            )
        
        with col3:
            api_calls = usage['api_calls']
            st.metric(
                "API Calls",
                f"{api_calls['used']}/{api_calls['limit']}",
                f"{int(api_calls['used']/max(api_calls['limit'], 1)*100)}% used"
            )
        
        st.markdown("---")
        
        # Billing history
        st.markdown("### 📋 **Billing History**")
        
        try:
            response = requests.get(f"{BACKEND_URL}/api/v1/payments/invoices/{user_id}")
            invoices_data = response.json()
            
            if invoices_data['invoices']:
                for inv in invoices_data['invoices']:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**{inv['number']}**")
                        st.text(inv['date'].split('T')[0])
                    
                    with col2:
                        st.write(f"${inv['amount']:.2f}")
                    
                    with col3:
                        status_color = "🟢" if inv['status'] == "paid" else "🟡"
                        st.write(f"{status_color} {inv['status'].title()}")
            
            else:
                st.info("No invoices yet")
        
        except:
            st.warning("Unable to load billing history")
        
        st.markdown("---")
        
        # Plan upgrade/downgrade
        st.markdown("### ⚙️ **Plan Management**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Upgrade Plan"):
                st.session_state.show_upgrade = True
                st.rerun()
        
        with col2:
            if st.button("Update Payment Method"):
                st.info("Redirect to Stripe customer portal")
        
        with col3:
            if st.button("Cancel Subscription"):
                st.session_state.show_cancel = True
                st.rerun()
    
    except Exception as e:
        st.error(f"Error loading subscription: {str(e)}")


def show_upgrade_dialog():
    """Show upgrade plan dialog"""
    
    st.markdown("### Upgrade Your Plan")
    
    new_plan = st.selectbox(
        "Choose a new plan",
        options=["starter", "professional"],
        format_func=lambda x: x.title()
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Cancel"):
            st.session_state.show_upgrade = False
            st.rerun()
    
    with col2:
        if st.button("Upgrade Now", type="primary"):
            user_id = st.session_state.get("user_id", 1)
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/v1/payments/upgrade",
                    params={"user_id": user_id},
                    json={"new_tier": new_plan}
                )
                
                if response.status_code == 200:
                    st.success("✅ Plan upgraded successfully!")
                    st.session_state.show_upgrade = False
                    st.rerun()
                else:
                    st.error(f"Upgrade failed: {response.json()['detail']}")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")


def show_cancel_dialog():
    """Show cancel subscription dialog"""
    
    st.markdown("### Cancel Subscription")
    st.warning("⚠️ This action cannot be undone")
    
    reason = st.selectbox(
        "Why are you cancelling?",
        options=[
            "Too expensive",
            "Not using it",
            "Found alternative",
            "Other"
        ]
    )
    
    feedback = st.text_area("Additional feedback (optional)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Keep Subscription"):
            st.session_state.show_cancel = False
            st.rerun()
    
    with col2:
        if st.button("Cancel Subscription", type="secondary"):
            user_id = st.session_state.get("user_id", 1)
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/v1/payments/cancel",
                    params={"user_id": user_id},
                    json={"reason": reason, "feedback": feedback}
                )
                
                if response.status_code == 200:
                    st.success("✅ Subscription cancelled")
                    st.session_state.show_cancel = False
                    st.rerun()
                else:
                    st.error(f"Cancellation failed: {response.json()['detail']}")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")


# ===========================
# MAIN PAYMENT PAGES
# ===========================

def payment_page():
    """Main payment management page"""
    
    st.set_page_config(page_title="Pricing & Billing", layout="wide")
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["💰 Pricing", "💳 Billing", "📊 Dashboard"])
    
    with tab1:
        show_pricing_page()
        
        if st.session_state.get("show_checkout"):
            show_checkout_page()
    
    with tab2:
        st.markdown("## 📋 **Billing & Invoices**")
        show_subscription_dashboard()
        
        if st.session_state.get("show_upgrade"):
            show_upgrade_dialog()
        
        if st.session_state.get("show_cancel"):
            show_cancel_dialog()
    
    with tab3:
        st.markdown("## 📊 **Subscription Dashboard**")
        show_subscription_dashboard()
