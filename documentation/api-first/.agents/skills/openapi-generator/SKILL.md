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

### File Naming Convention & Homologation
* **Exact Matching**: Every requested endpoint documentation file must have the exact same filename across versions, languages, and Python controller files.
* **Naming Pattern**: The `{endpoint_name}` must follow the pattern: `(http_verb)-(path_segment_name)-...-(path_segment_name)-(param_name)-...` using hyphens and lowercase.
  * It must always start with the HTTP verb (e.g., `get`, `post`, `put`, `delete`).
  * It must include all significant path segments and any path parameter IDs.
  * Example: A route like `GET /ideas/{id}` must be named `get-ideas-id.yaml` (for OpenAPI specs) and `get-ideas-id.py` (for the Python route handler) in all respective version, language, and route directories.

---

## Procedure

### Step 1: Prompt the User for Selections (Single Dialog)
To avoid asking the user multiple questions one-by-one, always present a single `ask_question` call containing all 5 questions at once.
Before calling `ask_question`:
1. Find existing API versions by listing directories inside `openapi/` using `list_dir` (e.g. `v1`).
2. Find existing domains by checking subdirectories inside `openapi/{version}/es/` and `openapi/{version}/en/` using `list_dir`.
3. Call `ask_question` with the following 5 questions:
   * **Question 1 (API Version)**: Options listing existing versions, and a write-in option for a new version.
   * **Question 2 (Domain)**: Options listing existing domains, and a write-in option for a new domain.
   * **Question 3 (Endpoint Name)**: A prompt to enter the endpoint filename (e.g., `get-ideas-id`).
   * **Question 4 (Route Code Generation)**: Options:
     * `Simulated (FastAPI route with mock data)`
     * `Empty (FastAPI route skeleton)`
     * `None (only OpenAPI YAML spec)`
   * **Question 5 (Target Language)**: Set `is_multi_select: true` to allow selecting multiple options using checkboxes:
     * `Spanish (Español)`
     * `English (Inglés)`

### Step 2: Run the Selector Script (Non-Interactive Mode)
Once the user submits the selections:
1. Execute the selection script with CLI arguments using the `run_command` tool:
   `python3 .agents/skills/openapi-generator/scripts/interactive_prompts.py --version {version} --domain {domain} --endpoint {endpoint_name} --route-type {route_type} --language {languages}`
   *Note*: Map the route type to one of `simulated`, `empty`, or `none`, and languages to a comma-separated list of selected languages (e.g., `spanish,english`).
2. This will silently generate `.agents/skills/openapi-generator/scratch/config.json` without asking the user for any confirmations or inputs.

### Step 3: Read the Selection Metadata
1. View the contents of the configuration file `.agents/skills/openapi-generator/scratch/config.json` using the `view_file` tool to obtain the selected:
   - `version`
   - `domain`
   - `endpoint_name`
   - `route_type`
   - `languages` (a list of languages, e.g. `["es", "en"]`)

### Step 4: Generate OpenAPI Specification (.yaml)
1. Parse the API contract/description provided by the user.
2. For each language in `languages` (e.g., `"es"` and `"en"`):
   * Generate the OpenAPI 3.0.3 specification YAML file translated into that language (Spanish or English).
   * Save it to `openapi/{version}/{lang}/{domain}/{endpoint_name}.yaml`.
3. Follow these best practices:
   * **Language**: The OpenAPI contract (description, summary, parameter descriptions, schema descriptions, error messages) MUST be written in the target language (`es` or `en`). If the input was in another language, translate it to the target language.
   * **Parameter Descriptions**: Provide a clear description for every parameter (path, query, header) and schema property.
   * **Schemas**: Move request and response models to the `components/schemas` section to ensure they are reusable and clean.
   * **Examples**: Provide realistic examples for all properties to help documentation users.
   * **Valid Examples for Concrete Types**: All example values (`example` keyword) in parameters and schema properties must be valid and conform to their declared format/type.
     * **UUIDs**: If a parameter or schema property uses `format: uuid`, the example MUST be a valid UUID (e.g. `d3b07384-d113-4956-a5db-9c2980fa2a4f`), never an invalid string (like `uuid-1234-5678`). This ensures that clicking "Try out" in Swagger UI generates a valid request out-of-the-box.
   * **No Auth references**: Ensure that the endpoints are designed appropriately. If no security is specified, do not add dummy auth keys.

### Step 5: Generate Python Route Handler (If requested)
1. If the `route_type` in the metadata is `"simulated"` or `"empty"`:
   * Generate a **single** FastAPI Python route handler.
   * Save it to `routes/{version}/{domain}/{endpoint_name}.py` (there is no language folder under `routes/{version}/` to avoid code duplication).
   * Note: The route handler is written in standard Python code. Do NOT add dynamic language-selection logic inside the Python controller handler file itself (to keep the code simple).
   * For `"simulated"`, implement the FastAPI route to return mock/simulated responses based on the OpenAPI contract. Ensure mock database keys and default values in the route handler use the exact same valid concrete types and example values (e.g., the same valid UUID) as the OpenAPI contract, without using custom workarounds or accepting invalid formats.
   * For `"empty"`, implement the FastAPI route with empty functions (using `pass` or basic schema structures) so the user can fill in the logic.
   * Ensure correct inputs, imports, and output structure.

### Step 6: Verification & Confirmation
1. Run syntax validation using `python3 -m py_compile` on the newly generated Python file to ensure it compiles correctly (if one was generated).
2. Touch/update the Gateway entrypoint `app/main.py` using `run_command` (e.g. `touch app/main.py`) to force Uvicorn to reload the configuration and mount the new specs/routes.
3. Inform the user of the successfully created files and show their paths.
4. Clean up the configuration file `.agents/skills/openapi-generator/scratch/config.json`.
