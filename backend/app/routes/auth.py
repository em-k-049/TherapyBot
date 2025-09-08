from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from ..schemas import UserCreate, UserRead, LoginRequest, Token, TwoFASetup, TwoFAVerify
from ..models import User, Role
from ..security import verify_password, get_password_hash, create_access_token
from ..deps import get_db, get_current_user
from ..services.two_factor import generate_totp_secret, generate_qr_code, verify_totp

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserRead)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Get patient role (default)
    patient_role = db.query(Role).filter(Role.name == "patient").first()
    if not patient_role:
        raise HTTPException(status_code=500, detail="Default role not found")
    
    # Create user
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role_id=patient_role.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserRead(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        role=db_user.role.name
    )

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check 2FA if enabled
    if user.is_2fa_enabled:
        if not login_data.otp_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="2FA code required"
            )
        
        if not verify_totp(user.totp_secret, login_data.otp_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 2FA code"
            )
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.name},
        expires_delta=timedelta(hours=24)
    )
    
    return Token(access_token=access_token, token_type="bearer")

@router.post("/2fa/setup", response_model=TwoFASetup)
def setup_2fa(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate 2FA secret and QR code"""
    secret = generate_totp_secret()
    qr_code = generate_qr_code(current_user, secret)
    
    # Store secret but don't enable 2FA yet
    current_user.totp_secret = secret
    db.commit()
    
    return TwoFASetup(secret=secret, qr_code=qr_code)

@router.post("/2fa/verify")
def verify_2fa(
    verify_data: TwoFAVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify 2FA code and enable 2FA"""
    if not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="2FA not set up")
    
    if not verify_totp(current_user.totp_secret, verify_data.otp_code):
        raise HTTPException(status_code=400, detail="Invalid 2FA code")
    
    # Enable 2FA
    current_user.is_2fa_enabled = True
    db.commit()
    
    return {"message": "2FA enabled successfully"}

@router.post("/2fa/disable")
def disable_2fa(
    verify_data: TwoFAVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disable 2FA after verification"""
    if not current_user.is_2fa_enabled:
        raise HTTPException(status_code=400, detail="2FA not enabled")
    
    if not verify_totp(current_user.totp_secret, verify_data.otp_code):
        raise HTTPException(status_code=400, detail="Invalid 2FA code")
    
    # Disable 2FA
    current_user.is_2fa_enabled = False
    current_user.totp_secret = None
    db.commit()
    
    return {"message": "2FA disabled successfully"}