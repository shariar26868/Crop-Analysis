from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.auth import verify_password, create_access_token, ADMIN_PASS_HASH
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_USER

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post('/token')
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    # only admin bootstrap supported for now
    if username != ADMIN_USER:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not verify_password(password, ADMIN_PASS_HASH):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
