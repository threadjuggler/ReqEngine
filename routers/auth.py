import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from datetime import datetime
from models import User, UserCreate, UserLogin, UserUpdate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_user_or_404(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user


@router.get("/users", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.name == user.name).first():
        raise HTTPException(status_code=400, detail="username already exists")
    db_user = User(
        name=user.name,
        role=user.role,
        hashed_password=hashlib.sha256(user.password.encode()).hexdigest(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=UserResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == credentials.name).first()
    hashed = hashlib.sha256(credentials.password.encode()).hexdigest()
    if not user or user.hashed_password != hashed:
        raise HTTPException(status_code=401, detail="invalid username or password")
    user.log_in_active = 1
    user.last_log_in = datetime.now()
    db.commit()
    db.refresh(user)
    return user


@router.get("/users/by-name/{name}", response_model=UserResponse)
async def get_user_by_name(name: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == name).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user


@router.get("/users/by-role/{role}", response_model=List[UserResponse])
async def list_users_by_role(role: str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == role).all()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    return _get_user_or_404(user_id, db)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def edit_user(user_id: int, updates: UserUpdate, db: Session = Depends(get_db)):
    db_user = _get_user_or_404(user_id, db)
    if updates.name is not None:
        if db.query(User).filter(User.name == updates.name, User.id != user_id).first():
            raise HTTPException(status_code=400, detail="username already exists")
        db_user.name = updates.name
    if updates.role is not None:
        db_user.role = updates.role
    if updates.password is not None:
        db_user.hashed_password = hashlib.sha256(updates.password.encode()).hexdigest()
    if updates.log_in_active is not None:
        db_user.log_in_active = updates.log_in_active
    if updates.last_log_in is not None:
        db_user.last_log_in = updates.last_log_in
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = _get_user_or_404(user_id, db)
    db.delete(db_user)
    db.commit()
