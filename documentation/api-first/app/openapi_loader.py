import os
import yaml
from typing import Dict, Any

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merges dict2 into dict1.
    """
    for key, value in dict2.items():
        if isinstance(value, dict) and key in dict1 and isinstance(dict1[key], dict):
            merge_dicts(dict1[key], value)
        else:
            dict1[key] = value
    return dict1

def load_combined_openapi(openapi_dir: str) -> Dict[str, Any]:
    """
    Loads openapi/main.yaml and merges all other yaml/yml files under openapi_dir.
    Expands environment variables (like ${API_PORT}) inside the spec.
    """
    main_path = os.path.join(openapi_dir, "main.yaml")
    if not os.path.exists(main_path):
        raise FileNotFoundError(f"Main OpenAPI entrypoint not found at {main_path}")
        
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Dynamically expand environment variables
    expanded_content = os.path.expandvars(content)
    spec = yaml.safe_load(expanded_content) or {}

    # Ensure base keys exist
    if "paths" not in spec:
        spec["paths"] = {}
    if "components" not in spec:
        spec["components"] = {}

    # Walk through openapi_dir and load all other yaml files
    for root, _, files in os.walk(openapi_dir):
        for file in files:
            if file.endswith((".yaml", ".yml")) and file != "main.yaml":
                full_path = os.path.join(root, file)
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                expanded_content = os.path.expandvars(content)
                domain_spec = yaml.safe_load(expanded_content) or {}
                
                # Merge paths
                if "paths" in domain_spec and domain_spec["paths"]:
                    spec["paths"] = merge_dicts(spec["paths"], domain_spec["paths"])
                
                # Merge components (e.g. schemas, securitySchemes, etc.)
                if "components" in domain_spec and domain_spec["components"]:
                    spec["components"] = merge_dicts(spec["components"], domain_spec["components"])

    return spec
