from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases.auth_use_case import AuthUseCase
from app.presentation.dependencies import get_auth_use_case
from app.presentation.schemas import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, use_case: AuthUseCase = Depends(get_auth_use_case)):
    try:
        result = await use_case.register(email=body.email, password=body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return TokenResponse(access_token=result.access_token)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, use_case: AuthUseCase = Depends(get_auth_use_case)):
    try:
        result = await use_case.login(email=body.email, password=body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenResponse(access_token=result.access_token)
