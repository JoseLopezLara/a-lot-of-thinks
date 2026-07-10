from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional

router = APIRouter()
security = HTTPBearer()

class UserProfileResponse(BaseModel):
    user_id: str = Field(..., description="Identificador único del usuario extraído de Cognito.")
    name: str = Field(..., description="Nombre completo del usuario.")
    email: str = Field(..., description="Dirección de correo electrónico del usuario.")
    avatar_url: Optional[str] = Field(None, description="URL a la imagen de avatar del usuario.")

class UnauthorizedError(BaseModel):
    message: str = Field("Unauthorized", description="Mensaje descriptivo del error de autenticación.")

class NotFoundError(BaseModel):
    status: str = Field("error", description="Identificador de estado indicando que ocurrió un error.")
    message: str = Field("User profile not found.", description="Mensaje explicando la razón del error.")

@router.get(
    "/users/me/profile",
    response_model=UserProfileResponse,
    responses={
        200: {
            "model": UserProfileResponse,
            "description": "Perfil de usuario recuperado exitosamente."
        },
        401: {
            "model": UnauthorizedError,
            "description": "El token provisto es inválido, expiró o no existe."
        },
        404: {
            "model": NotFoundError,
            "description": "El perfil de usuario no se encuentra en la base de datos."
        }
    },
    tags=["Users"]
)
async def get_users_me_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Recupera los datos del perfil del usuario extraído del claim del token JWT de Cognito.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
        
    return UserProfileResponse(
        user_id="google-oauth2|123456789",
        name="Jose Lopez Lara",
        email="jose.lopez@example.com",
        avatar_url="https://avatar.example.com/jose.png"
    )
