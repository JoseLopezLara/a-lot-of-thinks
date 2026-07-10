import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.openapi.utils import get_openapi
import httpx
from app.openapi_loader import load_combined_openapi

app = FastAPI(
    title="Sandbox API Verification",
    description="A temporary sandbox FastAPI application loaded dynamically from modular, domain-grouped OpenAPI YAML files.",
    version="1.0.0"
)

# Resolve path to our declarative OpenAPI specifications directory
OPENAPI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "openapi"))

def custom_openapi():
    """
    Overrides the default FastAPI openapi generation to return the combined YAML spec instead.
    """
    if app.openapi_schema:
        return app.openapi_schema
    try:
        schema = load_combined_openapi(OPENAPI_DIR)
        app.openapi_schema = schema
        return app.openapi_schema
    except Exception as e:
        # Fallback to standard generated OpenAPI on parsing errors to keep the server alive
        return get_openapi(
            title=app.title,
            version=app.version,
            description=f"Error loading custom YAML spec: {str(e)}",
            routes=app.routes,
        )

# Inject custom schema loader into FastAPI
app.openapi = custom_openapi

@app.get("/", tags=["Health"])
async def root():
    """
    Basic health check endpoint.
    """
    return {"status": "ok", "message": "FastAPI sandbox is running successfully!"}

@app.get("/test-external-api")
async def test_external_api():
    """
    Performs an HTTP GET request to JSONPlaceholder to test external routing.
    """
    target_url = "https://jsonplaceholder.typicode.com/posts/1"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"External API returned an error status code: {exc.response.status_code}"
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to the external API: {str(exc)}"
            )

@app.post("/mock-google-auth")
async def mock_google_auth(payload: Dict[str, Any]):
    """
    Mock Google authentication endpoint.
    Retrieves and echoes back parameters validated by the OpenAPI specification schema.
    """
    token = payload.get("token")
    client_id = payload.get("client_id")
    if not token or not client_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing token or client_id in payload"
        )
    return {
        "authenticated": True,
        "message": "Token structure is valid. OAuth authentication simulation successful.",
        "received_payload": {
            "token": token,
            "client_id": client_id
        }
    }
