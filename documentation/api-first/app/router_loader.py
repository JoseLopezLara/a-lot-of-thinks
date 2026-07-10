import importlib
import os
import sys
from fastapi import FastAPI, APIRouter

def register_dynamic_routers(app: FastAPI, package_dir: str, package_name: str):
    """
    Recursively scans the directory for Python files and imports them.
    Looks for the 'router' (APIRouter) instance, and registers it.
    """
    # Ensure parent directory of routes/ is in sys.path
    root_dir = os.path.abspath(os.path.join(package_dir, "..", ".."))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    for root, _, files in os.walk(package_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                # Convert file path to dotted module path relative to root_dir
                # E.g. /app/routes/v1/auth/auth.py -> routes.v1.auth.auth
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_dir)
                module_name = rel_path[:-3].replace(os.sep, ".")
                
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, "router"):
                        router_obj = getattr(module, "router")
                        if isinstance(router_obj, APIRouter):
                            print(f"[Autodiscovery] Registering APIRouter from module: '{module_name}'", flush=True)
                            app.include_router(router_obj)
                except Exception as e:
                    print(f"[Autodiscovery] Error loading router module '{module_name}': {e}", flush=True)
