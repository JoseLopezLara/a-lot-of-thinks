from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import httpx

app = FastAPI(
    title="Sandbox API Verification",
    description="A temporary sandbox FastAPI application to verify external network calls and interactive Swagger UI functionality.",
    version="1.0.0"
)

class GoogleAuthRequest(BaseModel):
    token: str = Field(..., description="Mock OAuth2 token received from client identity provider.")
    client_id: str = Field(..., description="OAuth2 client ID associated with the mock request.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "token": "ya29.a0AfB_byE_mock_token_1234567890",
                "client_id": "1234567890-mockclientid.apps.googleusercontent.com"
            }
        }
    }

@app.get("/", tags=["Health"])
async def root():
    """
    Basic health check endpoint returning the API status.
    """
    return {"status": "ok", "message": "FastAPI sandbox is running successfully!"}

@app.get("/test-external-api", tags=["External Calls"])
async def test_external_api():
    """
    Performs an asynchronous HTTP GET request to a reliable mock public API (JSONPlaceholder).
    This simulates consuming a live Google API or other cloud services from within the Docker container.
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

@app.post("/mock-google-auth", tags=["Authentication"], status_code=status.HTTP_200_OK)
async def mock_google_auth(payload: GoogleAuthRequest):
    """
    Mock Google authentication endpoint.
    Validates the structure of a POST request body using Pydantic, demonstrating interactive Swagger payload testing.
    """
    # Simply echo the payload back with authentication status for testing purposes
    return {
        "authenticated": True,
        "message": "Token structure is valid. OAuth authentication simulation successful.",
        "received_payload": {
            "token": payload.token,
            "client_id": payload.client_id
        }
    }
