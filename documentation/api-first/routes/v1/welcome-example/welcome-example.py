from fastapi import APIRouter

router = APIRouter()

@router.get("/welcome-example")
async def welcome(client_name: str = "Developer"):
    """
    Generic welcome endpoint.
    """
    return {
        "message": f"Welcome {client_name}! Sandbox setup was successful. You can view the interactive API documentation at /v1/docs",
        "status": "ready"
    }
