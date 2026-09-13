from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.models.user import User, Participant
from app.schemas.user import ParticipantRegister, UserLogin, Token, UserOut
from app.core.logging import log_event

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token or token expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive or not found.")
    return user

def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator privileges required.")
    return user

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_participant(data: ParticipantRegister, db: Session = Depends(get_db)):
    # Prevent duplicate registration using Email, Mobile, PRN
    if db.query(User).filter(User.email == data.email.lower()).first():
        raise HTTPException(status_code=400, detail="A user with this Email address is already registered.")
    
    if db.query(Participant).filter(Participant.mobile_number == data.mobile_number).first():
        raise HTTPException(status_code=400, detail="A participant with this Mobile Number is already registered.")

    if db.query(Participant).filter(Participant.prn_student_id == data.prn_student_id).first():
        raise HTTPException(status_code=400, detail="A participant with this PRN / Student ID is already registered.")

    # Create User
    new_user = User(
        email=data.email.lower(),
        hashed_password=get_password_hash(data.password),
        role="participant"
    )
    db.add(new_user)
    db.flush()

    # Create Participant Profile
    new_participant = Participant(
        user_id=new_user.id,
        full_name=data.full_name,
        mobile_number=data.mobile_number,
        college_name=data.college_name,
        department=data.department,
        year=data.year,
        prn_student_id=data.prn_student_id
    )
    db.add(new_participant)
    db.commit()

    log_event("PARTICIPANT_REGISTERED", f"PRN: {data.prn_student_id}", new_user.id)

    access_token = create_access_token(subject=new_user.id, role="participant")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": "participant",
        "full_name": data.full_name,
        "user_id": new_user.id
    }

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated.")

    full_name = "Administrator"
    if user.role == "participant" and user.participant_profile:
        if user.participant_profile.is_disqualified:
            raise HTTPException(status_code=403, detail=f"Account Disqualified: {user.participant_profile.disqualification_reason or 'Rules Violation'}")
        full_name = user.participant_profile.full_name

    log_event("USER_LOGIN_SUCCESS", f"Role: {user.role}", user.id)

    access_token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "full_name": full_name,
        "user_id": user.id
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    log_event("USER_LOGOUT", f"User logged out", current_user.id)
    return {"message": "Logged out successfully."}
