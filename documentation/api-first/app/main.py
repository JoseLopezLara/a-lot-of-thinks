# Trigger Uvicorn hot-reload to register newly created version directories
import os
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.openapi_loader import load_combined_openapi
from app.router_loader import register_dynamic_routers

# Primary Gateway Application
app = FastAPI(
    title="Sandbox API Gateway",
    description="Main entry point routing to versioned FastAPI sub-applications.",
    version="1.0.0",
    docs_url=None,       # Disable default root docs to serve versioned docs instead
    redoc_url=None,
    openapi_url=None
)

# Root-level health check
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Base Gateway health check.
    """
    return {"status": "ok", "message": "API Gateway is active."}

# Locate specification and routing root directories
OPENAPI_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "openapi"))
ROUTES_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "routes"))

# Discover all version directories (folders starting with 'v', e.g. 'v1', 'v2')
versions = []
if os.path.exists(OPENAPI_ROOT):
    versions = [
        d for d in os.listdir(OPENAPI_ROOT)
        if os.path.isdir(os.path.join(OPENAPI_ROOT, d)) and d.startswith("v")
    ]
versions.sort()

# Register and mount a sub-application for each version found
for version in versions:
    version_title = f"Sandbox API {version.upper()}"
    version_desc = f"Declarative domain-driven sandbox API for version {version}."
    
    # Initialize versioned sub-application
    sub_app = FastAPI(
        title=version_title,
        description=version_desc,
        version="1.0.0"
    )

    # Setup dynamic openapi loader for this version sub-app
    version_openapi_dir = os.path.join(OPENAPI_ROOT, version)
    
    def make_openapi_closure(v_dir, title, desc):
        def custom_openapi():
            try:
                schema = load_combined_openapi(v_dir)
                sub_app.openapi_schema = schema
                return sub_app.openapi_schema
            except Exception as e:
                return get_openapi(
                    title=title,
                    version="1.0.0",
                    description=f"Error loading custom spec: {str(e)}",
                    routes=sub_app.routes,
                )
        return custom_openapi

    sub_app.openapi = make_openapi_closure(version_openapi_dir, sub_app.title, sub_app.description)

    # Register controllers for this version's router
    version_routes_dir = os.path.join(ROUTES_ROOT, version)
    if os.path.exists(version_routes_dir):
        register_dynamic_routers(sub_app, version_routes_dir, f"routes.{version}")

    # Mount the sub-app on the Gateway under the version prefix (e.g. /v1, /v2)
    app.mount(f"/{version}", sub_app)
