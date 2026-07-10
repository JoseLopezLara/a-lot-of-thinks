from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

class GamificationQuota(BaseModel):
    daily_votes_limit: int = Field(5, description="Límite duro de votos permitidos por día.")
    daily_votes_used: int = Field(1, description="Cantidad de votos que el usuario ya emitió en la fecha actual.")
    daily_votes_remaining: int = Field(4, description="Votos restantes (límite - usados).")
    ideas_pitched_today: int = Field(0, description="Contador de ideas enviadas al Juez IA en la fecha actual.")
    daily_pitch_limit: int = Field(1, description="Límite de envíos permitidos por día.")
    next_reset_at: datetime = Field(..., description="Timestamp (ISO 8601) que le indica al frontend el momento exacto (medianoche UTC) en el que la ventana actual expira.")

class UserQuotaResponse(BaseModel):
    user_id: str = Field(..., description="Identificador único del usuario extraído del claim del JWT.")
    gamification: GamificationQuota

class UnauthorizedError(BaseModel):
    message: str = Field("Unauthorized", description="Mensaje descriptivo del error de autenticación.")

@router.get(
    "/users/me/quota",
    response_model=UserQuotaResponse,
    responses={
        200: {
            "model": UserQuotaResponse,
            "description": "El sistema calculó exitosamente el estado actual de las cuotas para la ventana de 24 horas del usuario."
        },
        401: {
            "model": UnauthorizedError,
            "description": "La petición fue rechazada debido a que el token es inválido o no se incluyó."
        }
    },
    tags=["Users"]
)
async def get_users_me_quota(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Recupera el estado actual de las cuotas de gamificación del usuario autenticado,
    implementando el enfoque "Lazy Reset" (basado en la evaluación de la fecha en curso).
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    
    # Return simulated mock response matching the specifications
    return UserQuotaResponse(
        user_id="google-oauth2|123456789",
        gamification=GamificationQuota(
            daily_votes_limit=5,
            daily_votes_used=1,
            daily_votes_remaining=4,
            ideas_pitched_today=0,
            daily_pitch_limit=1,
            next_reset_at=datetime.fromisoformat("2026-07-09T00:00:00+00:00")
        )
    )
