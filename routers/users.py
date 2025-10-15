from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import database
from models.users import Users
from schemas.users import UserModel
from utils.auth import (
    hash_password,
    pwd_context,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    create_refresh_token,
    get_current_user,
)

user_router = APIRouter()


@user_router.post("/sign_up")
def sign_up(form: UserModel, db: Session = Depends(database)):
    user = Users(
        email=form.email,
        password=hash_password(form.password),
        role="user"
    )
    db.add(user)
    db.commit()
    raise HTTPException(201, "Sign up successful !!!")


@user_router.post("/sign_in")
def sign_in(
    db: Session = Depends(database), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = db.query(Users).filter(Users.email == form_data.username).first()
    if user:
        is_validate_password = pwd_context.verify(form_data.password, user.password)
    else:
        is_validate_password = False

    if not is_validate_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login yoki parolda xatolik",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )
    return {
        "id": user.id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@user_router.get("/profil")
def profil(current_user: Users = Depends(get_current_user)):
    return current_user


@user_router.put("/update")
def update_profil(form: UserModel, db: Session = Depends(database),
                    current_user: Users = Depends(get_current_user)):

    db.query(Users).filter(Users.id == current_user.id).update(
        {
            Users.email: form.email,
            Users.password: hash_password(form.password),
        }
    )
    db.commit()
    raise HTTPException(200, "User update successful !!!")


@user_router.delete("/delete")
def delete_profil(db: Session = Depends(database), current_user: Users = Depends(get_current_user)):

    db.query(Users).filter(Users.id == current_user.id).delete()
    db.commit()
    raise HTTPException(200, "User delete successful !!!")
