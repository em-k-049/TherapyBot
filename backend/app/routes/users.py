from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..schemas import UserCreate, UserRead, RoleUpdate
from ..models import User, Role
from ..security import get_password_hash
from ..deps import get_db, require_role

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/consultants", response_model=List[UserRead])
def get_consultants(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    consultant_role = db.query(Role).filter(Role.name == "consultant").first()
    consultants = db.query(User).filter(User.role_id == consultant_role.id).all()
    
    return [
        UserRead(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.name
        )
        for user in consultants
    ]

@router.post("/consultants", response_model=UserRead)
def create_consultant(
    user: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    # Check if user exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Get consultant role
    consultant_role = db.query(Role).filter(Role.name == "consultant").first()
    if not consultant_role:
        raise HTTPException(status_code=500, detail="Consultant role not found")
    
    # Create consultant
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role_id=consultant_role.id
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

@router.put("/users/{user_id}/role", response_model=UserRead)
def update_user_role(
    user_id: UUID,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    """Update user role (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get the new role
    new_role = db.query(Role).filter(Role.name == role_update.role).first()
    if not new_role:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Update user role
    user.role_id = new_role.id
    db.commit()
    db.refresh(user)
    
    return UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.name
    )

@router.delete("/consultants/{user_id}")
def delete_consultant(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role.name != "consultant":
        raise HTTPException(status_code=400, detail="User is not a consultant")
    
    db.delete(user)
    db.commit()
    
    return {"message": "Consultant deleted successfully"}

@router.get("/users", response_model=List[UserRead])
def get_all_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    """Get all users (admin only)"""
    users = db.query(User).all()
    return [
        UserRead(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.name
        )
        for user in users
    ]