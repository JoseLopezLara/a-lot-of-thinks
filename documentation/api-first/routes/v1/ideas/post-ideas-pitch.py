from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from enum import Enum
import uuid

router = APIRouter()

# ---------------------------------------------------------
# Request Models
# ---------------------------------------------------------

class PitchRequest(BaseModel):
    title: str = Field(..., description="Nombre comercial propuesto para la idea.", example="NeonPath")
    one_liner: str = Field(..., description="Propuesta de valor o gancho comercial en una sola línea.", example="A serverless IDE built directly into Discord channels.")
    problem_statement: str = Field(..., description="Explicación detallada del dolor de mercado o problema técnico que se intenta resolver.", example="Context switching. Developers lose 30% of their time jumping between IDEs, terminals, and communication apps.")
    solution_mechanics: str = Field(..., description="Descripción arquitectónica o mecánica de cómo funciona la solución propuesta.", example="We use WebContainers to spin up ephemeral Node.js environments inside Discord threads.")
    monetization_model: str = Field(..., description="Estrategia de ingresos sugerida.", example="b2b_saas")
    team_size: int = Field(..., description="Cantidad estimada de personas requeridas para construir la primera versión.", example=3)
    time_to_mvp_weeks: int = Field(..., description="Tiempo estimado en semanas para tener un Producto Mínimo Viable.", example=4)
    seeking_roles: List[str] = Field(..., description="Roles que el usuario busca reclutar para el equipo.", example=["backend", "devops"])

# ---------------------------------------------------------
# Response Models: Scenario 1 (INVALID_INPUT)
# ---------------------------------------------------------

class InvalidInputReasonCode(str, Enum):
    EMPTY_OR_GIBBERISH = "EMPTY_OR_GIBBERISH"
    NON_BUSINESS_PROMPT = "NON_BUSINESS_PROMPT"
    LACKS_PROBLEM_DEFINITION = "LACKS_PROBLEM_DEFINITION"
    LACKS_SOLUTION_MECHANICS = "LACKS_SOLUTION_MECHANICS"
    OUT_OF_SCOPE_PHYSICAL = "OUT_OF_SCOPE_PHYSICAL"
    OTHER_INVALID = "OTHER_INVALID"

class InvalidInputFeedback(BaseModel):
    reason_code: InvalidInputReasonCode = Field(..., description="Categoriza el fallo de validación semántica rápida.")
    message: str = Field(..., description="Mensaje amigable explicando el descarte.")

class InvalidInputResponse(BaseModel):
    evaluation_status: str = Field("INVALID_INPUT", description="Identificador del estado de la evaluación.")
    judge_feedback: InvalidInputFeedback
    data: Optional[None] = Field(None, description="Nulo ya que no se generó información adicional.")

# ---------------------------------------------------------
# Response Models: Scenario 2 (REJECTED)
# ---------------------------------------------------------

class RejectedReasonCode(str, Enum):
    EXACT_RAG_COLLISION = "EXACT_RAG_COLLISION"
    MARKET_SATURATION = "MARKET_SATURATION"
    OTHER_COLLISION = "OTHER_COLLISION"
    TECHNICAL_IMPOSSIBILITY = "TECHNICAL_IMPOSSIBILITY"
    RESOURCE_MISMATCH = "RESOURCE_MISMATCH"
    FINANCIAL_UNVIABILITY = "FINANCIAL_UNVIABILITY"
    TOS_VIOLATION = "TOS_VIOLATION"
    OTHER_VIABILITY_REJECTION = "OTHER_VIABILITY_REJECTION"

class CriticalFlawSeverity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class CriticalFlaw(BaseModel):
    category: str = Field(..., description="Área del fallo (ej. Architecture, FinOps).")
    severity: CriticalFlawSeverity = Field(..., description="Nivel de gravedad.")
    issue: str = Field(..., description="Descripción detallada del error.")

class RagCollision(BaseModel):
    id: str = Field(..., description="Identificador de la idea colisionante.")
    title: str = Field(..., description="Título de la idea similar.")
    similarity: float = Field(..., description="Nivel de similitud de coseno calculado.")
    public_feed_url: str = Field(..., description="Enlace permanente para ver la idea similar.")

class RejectedFeedback(BaseModel):
    reason_code: RejectedReasonCode = Field(..., description="Categoriza el motivo del rechazo profundo.")
    executive_summary: str = Field(..., description="Resumen ejecutivo del rechazo.")
    critical_flaws: List[CriticalFlaw] = Field(..., description="Fallas específicas encontradas.")
    pivot_suggestions: List[str] = Field(..., description="Sugerencias generadas por la IA para pivotar.")

class RejectedData(BaseModel):
    rag_collisions: List[RagCollision] = Field(..., description="Enlaces a las ideas similares detectadas.")

class RejectedResponse(BaseModel):
    evaluation_status: str = Field("REJECTED", description="Identificador del estado de la evaluación.")
    judge_feedback: RejectedFeedback
    data: RejectedData

# ---------------------------------------------------------
# Response Models: Scenario 3 (APPROVED)
# ---------------------------------------------------------

class ViabilityScores(BaseModel):
    technical_feasibility: int = Field(..., description="Puntuación de la viabilidad tecnológica (20/40/60/80/100).")
    cost_efficiency: int = Field(..., description="Puntuación del balance entre recursos, tiempo y alcance.")
    market_demand: int = Field(..., description="Puntuación de la urgencia del dolor en el mercado.")
    differentiation: int = Field(..., description="Puntuación de las barreras de entrada.")

class CoreStrength(BaseModel):
    trait: str = Field(..., description="Nombre de la fortaleza.")
    detail: str = Field(..., description="Explicación detallada.")

class IdentifiedRisk(BaseModel):
    risk_type: str = Field(..., description="Tipo de riesgo.")
    mitigation: str = Field(..., description="Estrategia para evitar el riesgo.")

class ApprovedFeedback(BaseModel):
    executive_summary: str = Field(..., description="Veredicto general favorable.")
    viability_scores: ViabilityScores
    core_strengths: List[CoreStrength]
    identified_risks: List[IdentifiedRisk]

class DomainCategory(str, Enum):
    DevTools = "DevTools"
    FinTech = "FinTech"
    HealthTech = "HealthTech"
    EdTech = "EdTech"
    Marketplace = "Marketplace"
    ProductivitySaaS = "Productivity SaaS"
    AIMLWrapper = "AI/ML Wrapper"
    Web3Crypto = "Web3/Crypto"
    SocialCommunity = "Social/Community"

class ApprovedTaxonomy(BaseModel):
    domain_category: DomainCategory = Field(..., description="Dominio permitido asignado.")
    extracted_tags: List[str] = Field(..., description="Etiquetas tecnológicas extraídas.")

class SocialSharingLinks(BaseModel):
    x_intent_url: str = Field(..., description="URL preformateada para compartir en X.")
    linkedin_share_url: str = Field(..., description="URL preformateada para compartir en LinkedIn.")

class ApprovedLinks(BaseModel):
    public_feed_url: str = Field(..., description="URL absoluta de la idea en la plataforma.")
    discord_thread_url: str = Field(..., description="URL absoluta del canal de Discord generado.")
    social_sharing: SocialSharingLinks

class ApprovedData(BaseModel):
    taxonomy: ApprovedTaxonomy
    links: ApprovedLinks

class ApprovedResponse(BaseModel):
    evaluation_status: str = Field("APPROVED", description="Identificador del estado de la evaluación.")
    judge_feedback: ApprovedFeedback
    data: ApprovedData

# ---------------------------------------------------------
# Error Responses
# ---------------------------------------------------------

class BadRequestResponse(BaseModel):
    status: str = Field("error", description="Identificador de estado indicando un error.")
    message: str = Field(..., description="Detalle del atributo del body que falló en la validación.")

class UnauthorizedResponse(BaseModel):
    message: str = Field("Unauthorized", description="Rechazo en la capa de autorización.")

class QuotaExceededResponse(BaseModel):
    status: str = Field("error", description="Identificador de error lógico.")
    error_code: str = Field("DAILY_PITCH_QUOTA_EXCEEDED", description="Código del error para el frontend.")
    message: str = Field(..., description="Mensaje amigable de bloqueo.")

# ---------------------------------------------------------
# Endpoint Logic
# ---------------------------------------------------------

@router.post(
    "/ideas/pitch",
    responses={
        200: {
            "description": "Retorna la evaluación de la propuesta (polimórfica según evaluation_status).",
            "content": {
                "application/json": {
                    "schema": {
                        "oneOf": [
                            {"$ref": "#/components/schemas/ApprovedResponse"},
                            {"$ref": "#/components/schemas/RejectedResponse"},
                            {"$ref": "#/components/schemas/InvalidInputResponse"}
                        ]
                    }
                }
            }
        },
        400: {
            "model": BadRequestResponse,
            "description": "El JSON enviado está malformado o le faltan campos requeridos."
        },
        401: {
            "model": UnauthorizedResponse,
            "description": "Token inválido, expirado o ausente."
        },
        422: {
            "model": QuotaExceededResponse,
            "description": "El usuario ya superó su cuota diaria de ideas."
        }
    },
    tags=["Ideas"]
)
async def pitch_idea(
    payload: PitchRequest,
    authorization: Optional[str] = Header(None, description="Bearer token provisto por AWS Cognito")
):
    """
    Endpoint central del sistema y el de mayor consumo de procesamiento (Heavy Compute).
    Recibe la propuesta de la idea del usuario y orquesta el flujo de evaluación de la Inteligencia Artificial.
    Consume una unidad de la cuota diaria de ideas del usuario.
    """
    # 1. Autenticación (Cognito Bearer token check)
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"message": "Unauthorized"}
        )

    title_lower = payload.title.lower()

    # 2. Simulación de cuota diaria excedida (422)
    # Disparado si el título contiene "quota"
    if "quota" in title_lower:
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "error_code": "DAILY_PITCH_QUOTA_EXCEEDED",
                "message": "Has agotado el límite de ideas permitidas por día. Vuelve a intentarlo mañana."
            }
        )

    # 3. Simulación de entrada inválida (Scenario 1: INVALID_INPUT)
    # Disparado si el título contiene "invalid" o "error"
    if "invalid" in title_lower or "error" in title_lower:
        return JSONResponse(
            status_code=200,
            content={
                "evaluation_status": "INVALID_INPUT",
                "judge_feedback": {
                    "reason_code": "LACKS_SOLUTION_MECHANICS",
                    "message": "La entrada describe un problema válido, pero carece de una mecánica de solución evaluable."
                },
                "data": None
            }
        )

    # 4. Simulación de rechazo por el juez / colisión vector (Scenario 2: REJECTED)
    # Disparado si el título contiene "reject" o "collision"
    if "reject" in title_lower or "collision" in title_lower:
        return JSONResponse(
            status_code=200,
            content={
                "evaluation_status": "REJECTED",
                "judge_feedback": {
                    "reason_code": "TECHNICAL_IMPOSSIBILITY",
                    "executive_summary": "La arquitectura propuesta asume capacidades que las APIs actuales de Discord restringen por políticas de CORS.",
                    "critical_flaws": [
                        {
                            "category": "Architecture",
                            "severity": "HIGH",
                            "issue": "WebContainers no pueden ejecutarse dentro de un entorno embebido no controlado."
                        }
                    ],
                    "pivot_suggestions": [
                        "Desarrollar un bot de Discord que actúe como CLI hacia un entorno de contenedores externo (AWS ECS)."
                    ]
                },
                "data": {
                    "rag_collisions": [
                        {
                            "id": "e3b07384-d113-4956-a5db-9c2980fa2a4f",
                            "title": "DiscordIDE",
                            "similarity": 0.96,
                            "public_feed_url": "https://dev.midominio.com/idea/e3b07384-d113-4956-a5db-9c2980fa2a4f"
                        }
                    ]
                }
            }
        )

    # 5. Simulación de aprobación (Scenario 3: APPROVED)
    # Por defecto
    idea_uuid = str(uuid.uuid4())
    return JSONResponse(
        status_code=200,
        content={
            "evaluation_status": "APPROVED",
            "judge_feedback": {
                "executive_summary": f"Tesis validada para {payload.title}. Capitaliza un dolor de mercado real...",
                "viability_scores": {
                    "technical_feasibility": 80,
                    "cost_efficiency": 80,
                    "market_demand": 60,
                    "differentiation": 60
                },
                "core_strengths": [
                    {
                        "trait": "Go-to-Market",
                        "detail": "Adquisición orgánica nativa. Los usuarios ya residen en la plataforma objetivo."
                    }
                ],
                "identified_risks": [
                    {
                        "risk_type": "Platform Dependency",
                        "mitigation": "Diseñar la capa lógica desacoplada de la API de Discord."
                    }
                ]
            },
            "data": {
                "taxonomy": {
                    "domain_category": "DevTools",
                    "extracted_tags": payload.seeking_roles + ["Discord Bot", "WebContainers"]
                },
                "links": {
                    "public_feed_url": f"https://dev.midominio.com/idea/{idea_uuid}",
                    "discord_thread_url": "https://discord.com/channels/123/456",
                    "social_sharing": {
                        "x_intent_url": f"https://twitter.com/intent/tweet?text=Pitching+{payload.title}",
                        "linkedin_share_url": f"https://www.linkedin.com/sharing/share-offsite/?url=https://dev.midominio.com/idea/{idea_uuid}"
                    }
                }
            }
        }
    )
