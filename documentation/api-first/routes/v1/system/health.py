from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime, timezone

router = APIRouter()

class HealthResponse(BaseModel):
    status: str = Field(..., description="Estado general del sistema.")
    timestamp: str = Field(..., description="Marca de tiempo en formato ISO 8601 que indica cuándo se realizó la verificación.")

class HealthErrorResponse(BaseModel):
    status: str = Field(..., description="Identificador de estado indicando que ocurrió un error.")
    message: str = Field(..., description="Mensaje descriptivo del error crítico del servidor.")

@router.get(
    "/health",
    response_model=HealthResponse,
    responses={
        200: {
            "model": HealthResponse,
            "description": "El servicio está operativo y listo para recibir tráfico."
        },
        500: {
            "model": HealthErrorResponse,
            "description": "Fallo crítico en el sistema (ej. error de sintaxis en el código desplegado, fallo de inicialización en la función Lambda)."
        }
    },
    tags=["System"]
)
async def get_health():
    """
    Endpoint de diagnóstico y monitoreo diseñado para validar la salud general del sistema.
    Es consumido principalmente por los pipelines de CI/CD (GitHub Actions) para confirmar que el despliegue fue exitoso o disparar un rollback automático en caso de fallo.
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
