from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import stripe
import os
from ..core.database import get_db
from ..core.config import settings
from ..models.user import User
from ..models.payment import Payment, PlanType, PaymentStatus
from ..models.schemas import PaymentCreate, PaymentResponse
from ..utils.auth import get_current_active_user
from ..services.report_generator import ReportGeneratorService
from ..services.email_service import EmailService

router = APIRouter(tags=["payments"])

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Pricing (in cents)
PLAN_PRICES = {
    PlanType.BASIC: 499,      # $4.99
    PlanType.DETAILED: 1499,  # $14.99
    PlanType.PREMIUM: 2999    # $29.99
}

@router.post("/create-payment-intent")
async def create_payment_intent(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe payment intent for the selected plan."""
    
    try:
        # Get price for plan
        amount = PLAN_PRICES.get(payment_data.plan_type)
        if not amount:
            raise HTTPException(status_code=400, detail="Invalid plan type")
        
        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            metadata={
                "user_id": current_user.id,
                "user_email": current_user.email,
                "plan_type": payment_data.plan_type.value,
                "book_title": payment_data.book_title,
                "book_author": payment_data.book_author
            }
        )
        
        # Create payment record in database
        db_payment = Payment(
            user_id=current_user.id,
            stripe_payment_id=intent.id,
            amount=amount / 100,  # Convert cents to dollars
            status=PaymentStatus.PENDING,
            plan_type=payment_data.plan_type,
            book_title=payment_data.book_title,
            book_author=payment_data.book_author
        )
        
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        
        return {
            "clientSecret": intent.client_secret,
            "paymentId": db_payment.id
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_and_send_report(
    payment_id: int,
    user_email: str,
    book_title: str,
    book_author: str,
    plan_type: PlanType,
    db: Session
):
    """Background task to generate report and send via email."""
    
    try:
        # Generate PDF report
        report_service = ReportGeneratorService()
        pdf_path = report_service.generate_report(book_title, book_author, plan_type)
        
        # Send email with PDF
        email_service = EmailService()
        email_service.send_report_email(
            to_email=user_email,
            book_title=book_title,
            author=book_author,
            pdf_path=pdf_path,
            plan_type=plan_type.value
        )
        
        # Update payment record
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if payment:
            payment.pdf_sent = True
            db.commit()
        
        # Clean up PDF file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            
    except Exception as e:
        print(f"Error generating/sending report: {e}")
        # TODO: Implement retry logic or notification

@router.post("/confirm-payment/{payment_id}")
async def confirm_payment(
    payment_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Confirm payment and trigger report generation."""
    
    # Get payment record
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.user_id == current_user.id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Verify payment with Stripe
    try:
        intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_id)
        
        if intent.status == "succeeded":
            # Update payment status
            payment.status = PaymentStatus.COMPLETED
            db.commit()
            
            # Trigger background task to generate and send report
            background_tasks.add_task(
                generate_and_send_report,
                payment_id=payment.id,
                user_email=current_user.email,
                book_title=payment.book_title,
                book_author=payment.book_author,
                plan_type=payment.plan_type,
                db=db
            )
            
            return {
                "status": "success",
                "message": "Payment confirmed. Your report will be sent to your email shortly."
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Payment not completed. Status: {intent.status}"
            )
            
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history", response_model=List[PaymentResponse])
async def get_payment_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's payment history."""
    
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).all()
    
    return payments

@router.get("/plans")
async def get_plans():
    """Get available plans and pricing."""
    
    return {
        "plans": [
            {
                "type": "basic",
                "name": "Basic Literary Analysis",
                "price": PLAN_PRICES[PlanType.BASIC] / 100,
                "pages": "5-7 pages",
                "features": [
                    "Book Statistics",
                    "Synopsis",
                    "Author Presentation",
                    "Copyright Details",
                    "Past Adaptations"
                ]
            },
            {
                "type": "detailed",
                "name": "Detailed Literary Analysis",
                "price": PLAN_PRICES[PlanType.DETAILED] / 100,
                "pages": "12-15 pages",
                "features": [
                    "Everything in Basic",
                    "Thematic Analysis",
                    "Character Study",
                    "Writing Style Analysis",
                    "Impact and Legacy",
                    "Historical Context"
                ]
            },
            {
                "type": "premium",
                "name": "Premium Literary Analysis",
                "price": PLAN_PRICES[PlanType.PREMIUM] / 100,
                "pages": "25-30 pages",
                "features": [
                    "Everything in Detailed",
                    "Critical Reception",
                    "Comparative Literature",
                    "Psychological Interpretations",
                    "Symbolism Study",
                    "Audience Analysis",
                    "Marketing Strategy",
                    "Scholarly Analysis",
                    "Future Prospects"
                ]
            }
        ]
    }