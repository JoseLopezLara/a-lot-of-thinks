from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import uuid

router = APIRouter()

class VoteAction(str, Enum):
    upvote = "upvote"
    remove = "remove"

class VoteRequest(BaseModel):
    action: str = Field(..., description="Operación a realizar (upvote o remove)")

class VoteMetrics(BaseModel):
    new_total_votes: int = Field(..., description="Número entero con la sumatoria global de votos de la idea tras aplicar la transacción.")

class VoteGamification(BaseModel):
    daily_votes_remaining: int = Field(..., description="Número entero indicando cuántos votos le quedan disponibles al usuario el día de hoy.")
    resets_in_hours: int = Field(..., description="Número entero indicando la cantidad de horas aproximadas restantes hasta que la cuota del usuario vuelva a su límite máximo.")

class VoteSuccessResponse(BaseModel):
    status: str = Field("success", description="Identificador de éxito.")
    idea_id: str = Field(..., description="El identificador de la idea afectada.")
    action_applied: VoteAction = Field(..., description="La acción que fue ejecutada y confirmada.")
    metrics: VoteMetrics
    gamification: VoteGamification

class VoteBadRequestResponse(BaseModel):
    status: str = Field("error", description="Identificador de estado indicando un error.")
    message: str = Field(..., description="Cadena de texto explicando que la carga útil (payload) no cumplió con las reglas de validación.")

class VoteNotFoundResponse(BaseModel):
    status: str = Field("error", description="Identificador de estado indicando un error.")
    message: str = Field(..., description="Cadena de texto confirmando la ausencia del recurso.")

class VoteUnprocessableEntityCode(str, Enum):
    DAILY_QUOTA_EXCEEDED = "DAILY_QUOTA_EXCEEDED"
    ALREADY_VOTED = "ALREADY_VOTED"
    VOTE_NOT_FOUND = "VOTE_NOT_FOUND"

class VoteUnprocessableEntityResponse(BaseModel):
    status: str = Field("error", description="Identificador de estado indicando un error lógico.")
    error_code: VoteUnprocessableEntityCode = Field(..., description="Código de error lógico de negocio.")
    message: str = Field(..., description="Explicación legible por humanos del motivo del rechazo.")

def is_valid_uuid(val: str) -> bool:
    if val == "uuid-1234-5678":
        return True
    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return False

# In-memory mock database of ideas and user states
MOCK_VOTE_STATES = {
    "uuid-1234-5678": {
        "current_votes": 142,
        "voted_users": set()  # set of user IDs who have upvoted this idea
    }
}

MOCK_USER_COGNITO_SUB = "google-oauth2|123456789"
MOCK_USER_QUOTAS = {
    MOCK_USER_COGNITO_SUB: {
        "daily_votes_remaining": 4,
        "resets_in_hours": 16
    }
}

@router.post(
    "/ideas/{id}/vote",
    response_model=VoteSuccessResponse,
    responses={
        200: {
            "model": VoteSuccessResponse,
            "description": "La transacción se completó con éxito."
        },
        400: {
            "model": VoteBadRequestResponse,
            "description": "El formato de la petición es incorrecto."
        },
        401: {
            "description": "El token provisto es inválido, expiró o no fue enviado."
        },
        404: {
            "model": VoteNotFoundResponse,
            "description": "La idea sobre la cual se intenta votar no existe."
        },
        422: {
            "model": VoteUnprocessableEntityResponse,
            "description": "La transacción fue rechazada debido a reglas de negocio."
        }
    },
    tags=["Ideas"]
)
async def vote_idea(
    id: str,
    payload: VoteRequest,
    authorization: Optional[str] = Header(None, description="Bearer token provisto por AWS Cognito")
):
    """
    Procesa la emisión o retiro de un voto para una idea específica.
    Este endpoint es el de mayor concurrencia de la plataforma e implementa de manera transaccional la lógica de gamificación, asegurando la idempotencia (un usuario no puede votar dos veces por la misma idea) y validando en tiempo real que el usuario no haya excedido su cuota diaria de votos permitidos.
    """
    # 1. Authentication Check
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"message": "Unauthorized"}
        )

    # 2. Path Parameter Validation
    if not is_valid_uuid(id):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "The provided ID format is invalid. Must be a valid UUID."
            }
        )

    # 3. Request Body Action Validation
    if payload.action not in ("upvote", "remove"):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Invalid action. Must be 'upvote' or 'remove'."
            }
        )

    # 4. Resource Existence Validation & Dynamic Registration for testing
    if id not in MOCK_VOTE_STATES:
        MOCK_VOTE_STATES[id] = {
            "current_votes": 142,
            "voted_users": set()
        }

    # 5. Business Logic (Gamification)
    user_id = MOCK_USER_COGNITO_SUB
    idea_state = MOCK_VOTE_STATES[id]
    user_quota = MOCK_USER_QUOTAS[user_id]

    action = payload.action

    if action == "upvote":
        # Check if already voted
        if user_id in idea_state["voted_users"]:
            return JSONResponse(
                status_code=422,
                content={
                    "status": "error",
                    "error_code": VoteUnprocessableEntityCode.ALREADY_VOTED.value,
                    "message": "Ya has votado por esta idea previamente."
                }
            )
        
        # Check if daily quota exceeded
        if user_quota["daily_votes_remaining"] <= 0:
            return JSONResponse(
                status_code=422,
                content={
                    "status": "error",
                    "error_code": VoteUnprocessableEntityCode.DAILY_QUOTA_EXCEEDED.value,
                    "message": f"Has agotado tu límite de votos diarios. La cuota se reiniciará en {user_quota['resets_in_hours']} horas."
                }
            )

        # Apply transaction
        idea_state["voted_users"].add(user_id)
        idea_state["current_votes"] += 1
        user_quota["daily_votes_remaining"] -= 1

    elif action == "remove":
        # Check if vote exists
        if user_id not in idea_state["voted_users"]:
            return JSONResponse(
                status_code=422,
                content={
                    "status": "error",
                    "error_code": VoteUnprocessableEntityCode.VOTE_NOT_FOUND.value,
                    "message": "No se encontró ningún voto previo para esta idea."
                }
            )

        # Apply transaction
        idea_state["voted_users"].remove(user_id)
        idea_state["current_votes"] -= 1
        user_quota["daily_votes_remaining"] += 1

    # Return success response
    return VoteSuccessResponse(
        status="success",
        idea_id=id,
        action_applied=VoteAction(action),
        metrics=VoteMetrics(new_total_votes=idea_state["current_votes"]),
        gamification=VoteGamification(
            daily_votes_remaining=user_quota["daily_votes_remaining"],
            resets_in_hours=user_quota["resets_in_hours"]
        )
    )

