---
name: openapi-generator
description: >-
  Use this skill when the user provides an API contract or description and wants
  to generate a corresponding OpenAPI YAML specification and/or a FastAPI route handler.
---

# OpenAPI and Route Generator Skill

This skill enables the agent to take an API contract (in any format, e.g. JSON, markdown, raw text) and generate:
1. A clean, well-documented OpenAPI 3.0.3 specification YAML file.
2. An optional FastAPI Python route handler (simulated or empty).

## Architecture Details
* **OpenAPI Specs**: `openapi/{version}/{domain}/{endpoint_name}.yaml`
* **Route Handlers**: `routes/{version}/{domain}/{endpoint_name}.py`

---

## Procedure

### Step 1: Detect/Ask for API Version
1. Check the user's input for an explicit version (e.g. `v1`, `v2`).
2. If not specified, ask the user interactively (e.g. via text or `ask_question` tool) what version the new endpoint belongs to (e.g., `v1`).

### Step 2: Select/Create Domain (Interactive)
1. List the existing domains by scanning directories under `openapi/{version}/` (excluding file names like `main.yaml`).
2. Present these domains to the user using the `ask_question` tool, offering the options:
   * Select one of the existing domains.
   * Create a new domain.
3. If they choose to create a new domain, ask them for the name of the new domain.

### Step 3: Generate OpenAPI Specification (.yaml)
1. Parse the API contract provided by the user.
2. Build the YAML file at `openapi/{version}/{domain}/{endpoint_name}.yaml`.
3. Follow these best practices:
   * **Parameter Descriptions**: Provide a clear description for every parameter (path, query, header) and schema property.
   * **Schemas**: Move request and response models to the `components/schemas` section to ensure they are reusable and clean.
   * **Examples**: Provide realistic examples for all properties to help documentation users.
   * **No Auth references**: Ensure that the endpoints are designed appropriately. If no security is specified, do not add dummy auth keys.

### Step 4: Ask for Python Route Generation (Interactive)
1. Ask the user (using `ask_question` tool) if they would like to generate the associated Python route handler. The choices should be:
   * **(Recommended) Simulated**: Create the `.py` route handler returning mock/simulated responses based on the OpenAPI contract.
   * **Empty/Skeleton**: Create the `.py` route handler with empty functions (using `pass` or basic schema structures) so the user can fill in the logic.
   * **None**: Only create the OpenAPI YAML specification.
2. If they choose **Simulated** or **Empty**:
   * Write the file to `routes/{version}/{domain}/{endpoint_name}.py`.
   * Ensure it maps to the correct FastAPI methods (e.g. `@router.get`, `@router.post`).
   * Ensure correct inputs, imports, and output structure.

### Step 5: Verification & Confirmation
1. Run syntax validation using `python3 -m py_compile` on the newly generated Python file to ensure it compiles correctly.
2. Let the user know the files were successfully generated and show their locations.
