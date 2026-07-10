from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

router = APIRouter()

class AuthorProfile(BaseModel):
    name: str = Field(..., description="Nombre público del autor recuperado desde su cuenta de Google.")
    avatar_url: str = Field(..., description="URL absoluta de la fotografía de perfil del autor en Google.")

class FeedMetrics(BaseModel):
    votes: int = Field(..., description="Número entero que representa los votos acumulados por la comunidad.")
    time_to_mvp_weeks: int = Field(..., description="Número entero con la estimación en semanas para lanzar el Producto Mínimo Viable (MVP).")
    team_size: int = Field(..., description="Número entero que indica cuántas personas se necesitan para construir el MVP.")

class FeedTaxonomy(BaseModel):
    domain_category: str = Field(..., description="Categoría principal asignada por el LLM.")
    seeking_roles: List[str] = Field(..., description="Arreglo de cadenas de texto detallando los perfiles profesionales que el autor busca reclutar.")
    monetization_model: str = Field(..., description="Cadena de texto indicando la estrategia de ingresos propuesta.")
    extracted_tags: List[str] = Field(..., description="Arreglo dinámico de palabras clave tecnológicas generadas por la IA para mejorar las búsquedas textuales.")

class FeedLinks(BaseModel):
    public_feed_url: str = Field(..., description="URL absoluta (permalink) para acceder a la vista detallada de la idea en la web.")
    discord_thread_url: str = Field(..., description="URL absoluta que redirige al usuario directamente al hilo/canal de Discord asociado a esta idea.")

class FeedItem(BaseModel):
    id: str = Field(..., description="Identificador único (UUID) de la idea.")
    title: str = Field(..., description="Título comercial o nombre de la idea.")
    one_liner: str = Field(..., description="Descripción corta o propuesta de valor resumida en una sola frase.")
    author_profile: AuthorProfile
    metrics: FeedMetrics
    taxonomy: FeedTaxonomy
    links: FeedLinks
    created_at: str = Field(..., description="Fecha y hora exacta (ISO 8601) de la creación de la idea.")

class FeedPaginationMetadata(BaseModel):
    next_cursor: Optional[str] = Field(None, description="Cadena codificada en Base64 para solicitar la siguiente página. Null si no hay más resultados.")
    has_more: bool = Field(..., description="Booleano que confirma si existen más resultados (true) o no (false).")

class IdeasFeedResponse(BaseModel):
    items: List[FeedItem]
    pagination: FeedPaginationMetadata

class FeedBadRequestError(BaseModel):
    status: str = Field("error", description="Identificador de estado indicando un error.")
    message: str = Field(..., description="Cadena de texto descriptiva que explica exactamente qué parámetro de la solicitud falló la validación.")

# In-memory mock database
MOCK_IDEAS = [
    {
        "id": "uuid-1234-5678",
        "title": "NeonPath",
        "one_liner": "A serverless IDE built directly into Discord channels.",
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
            "extracted_tags": ["WebRTC", "Discord Bot"]
        },
        "links": {
            "public_feed_url": "https://dev.midominio.com/idea/uuid-1234-5678",
            "discord_thread_url": "https://discord.com/channels/123/456"
        },
        "created_at": "2026-07-07T10:00:00Z"
    },
    {
        "id": "uuid-5678-1234",
        "title": "PayFlow",
        "one_liner": "A streamlined payment orchestration gateway for multi-tenant SaaS.",
        "author_profile": {
            "name": "Lucia Gomez",
            "avatar_url": "https://lh3.googleusercontent.com/a/..."
        },
        "metrics": {
            "votes": 95,
            "time_to_mvp_weeks": 6,
            "team_size": 2
        },
        "taxonomy": {
            "domain_category": "FinTech",
            "seeking_roles": ["backend", "frontend"],
            "monetization_model": "freemium",
            "extracted_tags": ["Stripe", "Payment Gateway"]
        },
        "links": {
            "public_feed_url": "https://dev.midominio.com/idea/uuid-5678-1234",
            "discord_thread_url": "https://discord.com/channels/123/789"
        },
        "created_at": "2026-07-08T09:00:00Z"
    },
    {
        "id": "uuid-9012-3456",
        "title": "HealthSync",
        "one_liner": "IoT dashboard aggregating wearable health metrics for remote clinical evaluation.",
        "author_profile": {
            "name": "Andres Moreno",
            "avatar_url": "https://lh3.googleusercontent.com/a/..."
        },
        "metrics": {
            "votes": 210,
            "time_to_mvp_weeks": 8,
            "team_size": 4
        },
        "taxonomy": {
            "domain_category": "HealthTech",
            "seeking_roles": ["mobile", "data_scientist"],
            "monetization_model": "b2b_saas",
            "extracted_tags": ["Wearables", "IoT"]
        },
        "links": {
            "public_feed_url": "https://dev.midominio.com/idea/uuid-9012-3456",
            "discord_thread_url": "https://discord.com/channels/123/012"
        },
        "created_at": "2026-07-09T14:30:00Z"
    }
]

@router.get(
    "/ideas/feed",
    response_model=IdeasFeedResponse,
    responses={
        200: {
            "model": IdeasFeedResponse,
            "description": "Consulta realizada con éxito. Devuelve la lista de ideas y metadata de paginación."
        },
        400: {
            "model": FeedBadRequestError,
            "description": "Algunos parámetros de la consulta tienen un formato inválido o rompen las reglas de validación."
        }
    },
    tags=["Ideas"]
)
async def get_ideas_feed(
    q: Optional[str] = None,
    domain: Optional[str] = None,
    roles: Optional[str] = None,
    monetization: Optional[str] = None,
    sort: Optional[str] = "newest",
    limit: Optional[int] = 20,
    cursor: Optional[str] = None
):
    """
    Recupera el feed público y paginado de ideas.
    Devuelve el arreglo de tarjetas de ideas filtradas por búsqueda, dominio, roles, y monetización.
    """
    if limit is not None and limit > 50:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid pagination limit. Maximum allowed is 50."}
        )

    # Filter items
    filtered_items = []
    for idea in MOCK_IDEAS:
        # Search filter (q)
        if q:
            q_lower = q.lower()
            text_match = (
                q_lower in idea["title"].lower() or
                q_lower in idea["one_liner"].lower() or
                any(q_lower in tag.lower() for tag in idea["taxonomy"]["extracted_tags"])
            )
            if not text_match:
                continue

        # Domain filter
        if domain and idea["taxonomy"]["domain_category"] != domain:
            continue

        # Roles filter (comma separated)
        if roles:
            requested_roles = [r.strip().lower() for r in roles.split(",")]
            idea_roles = [r.lower() for r in idea["taxonomy"]["seeking_roles"]]
            if not any(r in idea_roles for r in requested_roles):
                continue

        # Monetization filter
        if monetization and idea["taxonomy"]["monetization_model"] != monetization:
            continue

        filtered_items.append(idea)

    # Sort items
    if sort == "top_voted":
        filtered_items.sort(key=lambda x: x["metrics"]["votes"], reverse=True)
    else:  # newest is default
        filtered_items.sort(key=lambda x: x["created_at"], reverse=True)

    # Pagination logic (simple slice based on limit)
    # We can mock a next cursor if there are actually more items than the limit
    paginated_items = filtered_items[:limit]
    has_more = len(filtered_items) > limit
    next_cursor = "base64-encoded-next-cursor" if has_more else None

    # Transform to schema models
    response_items = [
        FeedItem(
            id=item["id"],
            title=item["title"],
            one_liner=item["one_liner"],
            author_profile=AuthorProfile(**item["author_profile"]),
            metrics=FeedMetrics(**item["metrics"]),
            taxonomy=FeedTaxonomy(**item["taxonomy"]),
            links=FeedLinks(**item["links"]),
            created_at=item["created_at"]
        )
        for item in paginated_items
    ]

    return IdeasFeedResponse(
        items=response_items,
        pagination=FeedPaginationMetadata(
            next_cursor=next_cursor,
            has_more=has_more
        )
    )
