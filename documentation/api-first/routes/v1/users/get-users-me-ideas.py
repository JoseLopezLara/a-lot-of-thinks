from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Literal

router = APIRouter()
security = HTTPBearer()

class IdeaMetrics(BaseModel):
    votes: int = Field(..., description="Cantidad entera total de votos positivos que la idea ha acumulado.")

class IdeaItem(BaseModel):
    id: str = Field(..., description="Identificador único (UUID) de la idea.")
    title: str = Field(..., description="Nombre o título corto asignado a la idea.")
    status: Literal["APPROVED", "REJECTED", "INVALID_INPUT"] = Field(
        ..., 
        description="El estado histórico de la evaluación de la idea. Puede ser APPROVED, REJECTED o INVALID_INPUT."
    )
    metrics: IdeaMetrics = Field(..., description="Objeto que agrupa las estadísticas de interacción de la idea.")
    created_at: datetime = Field(..., description="Fecha y hora exactas en formato ISO 8601 en la que se generó la idea.")

class PaginationMetadata(BaseModel):
    next_cursor: Optional[str] = Field(
        None, 
        description="Cadena de texto (Base64) que el frontend debe enviar en la siguiente petición. Si es null, se alcanzó el final."
    )
    has_more: bool = Field(..., description="Valor booleano que indica si existen más páginas de resultados disponibles.")

class UserIdeasResponse(BaseModel):
    items: List[IdeaItem] = Field(..., description="Arreglo que contiene los objetos de las ideas enviadas por el usuario.")
    pagination: PaginationMetadata = Field(..., description="Objeto que contiene los controles para navegar por el listado.")

class UnauthorizedError(BaseModel):
    message: str = Field("Unauthorized", description="Mensaje explicativo de la falta de credenciales válidas.")

class NotFoundError(BaseModel):
    status: str = Field("error", description="Identificador de estado indicando que ocurrió un error.")
    message: str = Field("User profile not found.", description="Mensaje explicando que no se encontró el registro del usuario.")

@router.get(
    "/users/me/ideas",
    response_model=UserIdeasResponse,
    responses={
        200: {
            "model": UserIdeasResponse,
            "description": "Retorna el arreglo de ideas asociadas al usuario y la metadata de paginación."
        },
        401: {
            "model": UnauthorizedError,
            "description": "El token provisto es inválido, expiró o no existe en la petición."
        },
        404: {
            "model": NotFoundError,
            "description": "El usuario extraído del token de Cognito no tiene un perfil inicializado en la base de datos."
        }
    },
    tags=["Users"]
)
async def get_users_me_ideas(
    limit: int = Query(20, description="Define la cantidad máxima de resultados a devolver. Máximo permitido 50.", ge=1, le=50),
    cursor: Optional[str] = Query(None, description="Token codificado en base64 utilizado para la paginación."),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Recupera el historial paginado de todas las ideas (aprobadas y rechazadas) que el usuario autenticado ha enviado al Juez IA.
    Aísla esta consulta del feed público global para mayor eficiencia.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    
    # Simulates returning an empty state when cursor is specifically set to "empty"
    if cursor == "empty":
        return UserIdeasResponse(
            items=[],
            pagination=PaginationMetadata(
                next_cursor=None,
                has_more=False
            )
        )
        
    # Return simulated mock response matching the specifications
    return UserIdeasResponse(
        items=[
            IdeaItem(
                id="uuid-1234-5678",
                title="NeonPath",
                status="APPROVED",
                metrics=IdeaMetrics(votes=142),
                created_at=datetime.fromisoformat("2026-07-07T10:00:00+00:00")
            ),
            IdeaItem(
                id="uuid-9876-5432",
                title="CryptoLogistics",
                status="REJECTED",
                metrics=IdeaMetrics(votes=0),
                created_at=datetime.fromisoformat("2026-07-06T15:30:00+00:00")
            )
        ],
        pagination=PaginationMetadata(
            next_cursor="base64-encoded-cursor-string",
            has_more=True
        )
    )
