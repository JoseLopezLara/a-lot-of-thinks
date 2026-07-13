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

def make_openapi_closure(app_instance, v_dir, title, desc):
    def custom_openapi():
        try:
            schema = load_combined_openapi(v_dir)
            app_instance.openapi_schema = schema
            return app_instance.openapi_schema
        except Exception as e:
            return get_openapi(
                title=title,
                version="1.0.0",
                description=f"Error loading custom spec: {str(e)}",
                routes=app_instance.routes,
            )
    return custom_openapi

# Register and mount a sub-application for each version found
for version in versions:
    version_dir = os.path.join(OPENAPI_ROOT, version)
    
    # Check if there are language subdirectories (es, en) inside the version openapi folder
    languages = []
    if os.path.exists(version_dir):
        languages = [
            d for d in os.listdir(version_dir)
            if os.path.isdir(os.path.join(version_dir, d)) and d in ("es", "en")
        ]
    languages.sort()
    
    version_routes_dir = os.path.join(ROUTES_ROOT, version)
    
    if languages:
        # Multi-language setup: mount separate sub-apps for each language
        for lang in languages:
            lang_title = f"Sandbox API {version.upper()} ({lang.upper()})"
            lang_desc = f"Declarative domain-driven sandbox API for version {version} in {lang.upper()}."
            
            sub_app = FastAPI(
                title=lang_title,
                description=lang_desc,
                version="1.0.0"
            )
            
            lang_openapi_dir = os.path.join(version_dir, lang)
            sub_app.openapi = make_openapi_closure(sub_app, lang_openapi_dir, sub_app.title, sub_app.description)
            
            if os.path.exists(version_routes_dir):
                register_dynamic_routers(sub_app, version_routes_dir, f"routes.{version}")
                
            # Mount under e.g. /v2/es, /v2/en
            app.mount(f"/{version}/{lang}", sub_app)
    else:
        # Single-language legacy setup: mount single sub-app directly on version path
        version_title = f"Sandbox API {version.upper()}"
        version_desc = f"Declarative domain-driven sandbox API for version {version}."
        
        sub_app = FastAPI(
            title=version_title,
            description=version_desc,
            version="1.0.0"
        )
        
        sub_app.openapi = make_openapi_closure(sub_app, version_dir, sub_app.title, sub_app.description)
        
        if os.path.exists(version_routes_dir):
            register_dynamic_routers(sub_app, version_routes_dir, f"routes.{version}")
            
        # Mount under e.g. /v1
        app.mount(f"/{version}", sub_app)
