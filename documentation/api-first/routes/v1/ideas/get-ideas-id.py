from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

router = APIRouter()

class IdeaPitch(BaseModel):
    title: str = Field(..., description="Nombre o título comercial de la idea.")
    one_liner: str = Field(..., description="Descripción corta o gancho comercial de una sola línea.")
    problem_statement: str = Field(..., description="Declaración detallada del problema o dolor detectado en el mercado.")
    solution_mechanics: str = Field(..., description="Explicación técnica de cómo la solución resuelve el problema planteado.")

class AuthorProfile(BaseModel):
    name: str = Field(..., description="Nombre público del autor recuperado desde su cuenta de Google.")
    avatar_url: str = Field(..., description="URL absoluta de la fotografía de perfil del autor en Google.")

class IdeaMetrics(BaseModel):
    votes: int = Field(..., description="Total acumulado de votos positivos recibidos por la comunidad.")
    time_to_mvp_weeks: int = Field(..., description="Estimación temporal (en semanas) propuesta por el autor para construir la primera versión.")
    team_size: int = Field(..., description="Cantidad de personas previstas por el autor para ejecutar el MVP.")

class IdeaTaxonomy(BaseModel):
    domain_category: str = Field(..., description="Categoría principal asignada por el LLM.")
    seeking_roles: List[str] = Field(..., description="Lista de perfiles de ingeniería o negocio que el autor necesita para el proyecto (ej. backend, frontend, devops).")
    monetization_model: str = Field(..., description="Estrategia comercial planteada (ej. b2b_saas, freemium).")
    extracted_tags: List[str] = Field(..., description="Palabras clave e integraciones de software específicas identificadas de forma dinámica por la IA.")

class ViabilityScores(BaseModel):
    technical_feasibility: int = Field(..., description="Viabilidad tecnológica contrastada contra limitaciones reales de hardware/APIs.")
    cost_efficiency: int = Field(..., description="Eficiencia financiera y congruencia del alcance vs. el tamaño de equipo y tiempo propuestos.")
    market_demand: int = Field(..., description="Nivel de urgencia, dolor y tamaño de mercado direccionable del problema planteado.")
    differentiation: int = Field(..., description="Grado de innovación y existencia de barreras de entrada (moat) frente a soluciones actuales.")

class CoreStrength(BaseModel):
    trait: str = Field(..., description="Área de éxito o ventaja competitiva identificada.")
    detail: str = Field(..., description="Explicación lógica o justificación detallada de la ventaja competitiva.")

class IdentifiedRisk(BaseModel):
    risk_type: str = Field(..., description="Categoría del peligro o riesgo potencial.")
    mitigation: str = Field(..., description="Plan de mitigación sugerido por la IA para contrarrestar el riesgo.")

class JudgeFeedback(BaseModel):
    executive_summary: str = Field(..., description="Conclusión o veredicto general redactado por el Juez IA que justifica su aprobación.")
    viability_scores: ViabilityScores
    core_strengths: List[CoreStrength]
    identified_risks: List[IdentifiedRisk]

class SocialSharingLinks(BaseModel):
    x_intent_url: str = Field(..., description="URL de intención preformateada para compartir la idea aprobada en X/Twitter.")
    linkedin_share_url: str = Field(..., description="URL de intención preformateada para compartir la idea aprobada en LinkedIn.")

class IdeaLinks(BaseModel):
    discord_thread_url: str = Field(..., description="URL del canal o hilo creado automáticamente en Discord para iniciar la colaboración del equipo.")
    social_sharing: SocialSharingLinks

class IdeaDetailResponse(BaseModel):
    id: str = Field(..., description="Identificador único (UUID) de la idea consultada.")
    pitch: IdeaPitch
    author_profile: AuthorProfile
    metrics: IdeaMetrics
    taxonomy: IdeaTaxonomy
    judge_feedback: JudgeFeedback
    links: IdeaLinks
    created_at: str = Field(..., description="Marca de tiempo (ISO 8601) de la aprobación del registro.")

class IdeaDetailBadRequestResponse(BaseModel):
    status: str = Field("error", description="Identificador de estado indicando un error.")
    message: str = Field(..., description="Cadena de texto descriptiva detallando la falla de formato en el parámetro de la ruta.")

class IdeaDetailNotFoundResponse(BaseModel):
    status: str = Field("error", description="Identificador de estado indicando un error.")
    message: str = Field(..., description="Cadena de texto que notifica la ausencia del recurso en la base de datos para que el frontend pinte una vista de error 404 personalizada.")

# In-memory mock database
MOCK_IDEA_DETAILS = {
    "d3b07384-d113-4956-a5db-9c2980fa2a4f": {
        "id": "d3b07384-d113-4956-a5db-9c2980fa2a4f",
        "pitch": {
            "title": "NeonPath",
            "one_liner": "A serverless IDE built directly into Discord channels.",
            "problem_statement": "Context switching. Developers lose 30% of their time jumping between IDEs, terminals, and communication apps to debug collaborative issues.",
            "solution_mechanics": "We use WebContainers to spin up ephemeral Node.js environments inside Discord threads, allowing real-time multiplayer code editing."
        },
        "author_profile": {
            "name": "Carlos Rivera",
            "avatar_url": "https://lh3.googleusercontent.com/a/..."
        },
        "metrics": {
            "votes": 142,
            "time_to_mvp_weeks": 4,
            "team_size": 3
        },
        "taxonomy": {
            "domain_category": "DevTools",
            "seeking_roles": ["backend", "devops"],
            "monetization_model": "b2b_saas",
            "extracted_tags": ["WebRTC", "Discord Bot", "WebContainers"]
        },
        "judge_feedback": {
            "executive_summary": "Tesis validada. Capitaliza un dolor de mercado real (Context Switching) utilizando un canal de distribución con alta densidad de desarrolladores.",
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
                    "mitigation": "Diseñar la capa lógica desacoplada de la API de Discord para permitir una futura migración a Slack."
                }
            ]
        },
        "links": {
            "discord_thread_url": "https://discord.com/channels/123/456",
            "social_sharing": {
                "x_intent_url": "https://twitter.com/intent/tweet?text=El%20Juez%20IA%20acaba%20de%20aprobar%20mi%20arquitectura...&url=https://dev.midominio.com/idea/d3b07384-d113-4956-a5db-9c2980fa2a4f",
                "linkedin_share_url": "https://www.linkedin.com/sharing/share-offsite/?url=https://dev.midominio.com/idea/d3b07384-d113-4956-a5db-9c2980fa2a4f"
            }
        },
        "created_at": "2026-07-07T10:00:00Z"
    }
}

def is_valid_uuid4(val: str) -> bool:
    try:
        parsed = uuid.UUID(val)
        return parsed.version == 4
    except ValueError:
        return False

@router.get(
    "/ideas/{id}",
    response_model=IdeaDetailResponse,
    responses={
        200: {
            "model": IdeaDetailResponse,
            "description": "Devuelve el payload absoluto de la idea detallada."
        },
        400: {
            "model": IdeaDetailBadRequestResponse,
            "description": "El identificador enviado en la ruta de la URL no cumple con el estándar de formato UUID v4."
        },
        404: {
            "model": IdeaDetailNotFoundResponse,
            "description": "La petición está bien estructurada, pero el identificador consultado no existe en los registros."
        }
    },
    tags=["Ideas"]
)
async def get_idea_by_id(id: str):
    """
    Recupera la información completa y detallada de una idea aprobada específica utilizando su identificador único (UUID).
    A diferencia del listado general (feed), este endpoint devuelve la tesis original completa redactada por el usuario
    junto con el análisis profundo y estructurado generado por el Juez IA (`judge_feedback`) y los puntajes de viabilidad.
    """
    if not is_valid_uuid4(id):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "The provided ID format is invalid. Must be a valid UUIDv4."
            }
        )

    if id not in MOCK_IDEA_DETAILS:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": "Idea with the specified ID could not be found."
            }
        )

    idea_data = MOCK_IDEA_DETAILS[id]
    return IdeaDetailResponse(**idea_data)
