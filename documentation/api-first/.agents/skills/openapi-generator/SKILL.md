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

### Step 1: Prompt the User for Selections (Single Dialog)
To avoid asking the user multiple questions one-by-one, always present a single `ask_question` call containing all 5 questions at once.
Before calling `ask_question`:
1. Find existing API versions by listing directories inside `openapi/` using `list_dir` (e.g. `v1`).
2. Find existing domains by listing directories inside `openapi/{version}/` using `list_dir` (e.g. `welcome-example`).
3. Call `ask_question` with the following 5 questions:
   * **Question 1 (API Version)**: Options listing existing versions, and a write-in option for a new version.
   * **Question 2 (Domain)**: Options listing existing domains, and a write-in option for a new domain.
   * **Question 3 (Endpoint Name)**: A prompt to enter the endpoint filename (e.g., `get-users`).
   * **Question 4 (Route Code Generation)**: Options:
     * `Simulated (FastAPI route with mock data)`
     * `Empty (FastAPI route skeleton)`
     * `None (only OpenAPI YAML spec)`
   * **Question 5 (Target Language)**: Options:
     * `Spanish (Español)`
     * `English (Inglés)`

### Step 2: Run the Selector Script (Non-Interactive Mode)
Once the user submits the selections:
1. Execute the selection script with CLI arguments using the `run_command` tool:
   `python3 .agents/skills/openapi-generator/scripts/interactive_prompts.py --version {version} --domain {domain} --endpoint {endpoint_name} --route-type {route_type} --language {language}`
   *Note*: Map the route type to one of `simulated`, `empty`, or `none`, and language to `spanish` or `english`.
2. This will silently generate `.agents/skills/openapi-generator/scratch/config.json` without asking the user for any confirmations or inputs.

### Step 3: Read the Selection Metadata
1. View the contents of the configuration file `.agents/skills/openapi-generator/scratch/config.json` using the `view_file` tool to obtain the selected:
   - `version`
   - `domain`
   - `endpoint_name`
   - `route_type`
   - `language`

### Step 4: Generate OpenAPI Specification (.yaml)
1. Parse the API contract/description provided by the user.
2. Generate the OpenAPI 3.0.3 specification YAML file.
3. Save it to `openapi/{version}/{domain}/{endpoint_name}.yaml`.
4. Follow these best practices:
   * **Language**: The OpenAPI contract (description, summary, parameter descriptions, schema descriptions, error messages) MUST be written in the language specified in the configuration (`spanish` or `english`). If the input was in another language, translate it to the target language.
   * **Parameter Descriptions**: Provide a clear description for every parameter (path, query, header) and schema property.
   * **Schemas**: Move request and response models to the `components/schemas` section to ensure they are reusable and clean.
   * **Examples**: Provide realistic examples for all properties to help documentation users.
   * **No Auth references**: Ensure that the endpoints are designed appropriately. If no security is specified, do not add dummy auth keys.

### Step 5: Generate Python Route Handler (If requested)
1. If the `route_type` in the metadata is `"simulated"` or `"empty"`:
   * Generate the FastAPI Python route handler.
   * Save it to `routes/{version}/{domain}/{endpoint_name}.py`.
   * **Language**: Any comments, docstrings, and mock/simulated responses (such as mock names, titles, statuses, or error descriptions) returned by `"simulated"` routes MUST be in the language specified in the configuration (`spanish` or `english`).
   * For `"simulated"`, implement the FastAPI route to return mock/simulated responses based on the OpenAPI contract.
   * For `"empty"`, implement the FastAPI route with empty functions (using `pass` or basic schema structures) so the user can fill in the logic.
   * Ensure correct inputs, imports, and output structure.

### Step 6: Verification & Confirmation
1. Run syntax validation using `python3 -m py_compile` on the newly generated Python file to ensure it compiles correctly.
2. Inform the user of the successfully created files and show their paths.
3. Clean up the configuration file `.agents/skills/openapi-generator/scratch/config.json`.
