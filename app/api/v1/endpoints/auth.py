from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.core import deps, security
from app.schemas.user import UserCreate, User
from app.models.user import User as UserModel

router = APIRouter()


@router.post("/login")
async def login(request: Request,
                response: Response,
                username: str,
                password: str,
                db: Session = Depends(deps.get_db)):
    """
    TODO: Implement login endpoint using session
    Example:
    - Find user by username
    - Verify password
    - Set user_id in session
    - Return success message
    """
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user or not security.verify_password(
            password, security.get_password_hash(password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")
    request.session["user_id"] = user.id
    return {"message": "Login successful"}


@router.post("/register", response_model=User)
async def register(*, db: Session = Depends(deps.get_db), user_in: UserCreate):
    """
    TODO: Implement user registration
    Example:
    - Check if username/email already exists
    - Hash password
    - Create user in database
    - Return user data
    """
    if db.query(UserModel).filter(
        (UserModel.username == user_in.username) | (UserModel.email == user_in.email)
    ).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

    hashed_password = security.get_password_hash(user_in.password)

    new_user = UserModel(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/logout")
async def logout(request: Request):
    """
    TODO: Implement logout endpoint
    Example:
    request.session.clear()
    return {"message": "Successfully logged out"}
    """
    request.session.clear()
    return {"message": "Successfully logged out"}
