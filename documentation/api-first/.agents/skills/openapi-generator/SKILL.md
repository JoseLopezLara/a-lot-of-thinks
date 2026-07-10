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

### Step 1: Run the Selector Script (Prefer Non-Interactive CLI Arguments)
You can run the script in either non-interactive or interactive mode:

#### Option A: Non-Interactive Mode (Preferred)
If you already know the version, domain, endpoint name, and route generation options from the user request:
1. Run the script passing CLI arguments:
   `python3 .agents/skills/openapi-generator/scripts/interactive_prompts.py --version {version} --domain {domain} --endpoint {endpoint_name} --route-type {route_type}`
   using the `run_command` tool.
   *Example*: `python3 .agents/skills/openapi-generator/scripts/interactive_prompts.py --version v1 --domain users --endpoint get-users-me-ideas --route-type simulated`
2. This runs completely silently and instantly generates `.agents/skills/openapi-generator/scratch/config.json` without asking the user for any confirmations or inputs.

#### Option B: Interactive Fallback
If the target details are not clear:
1. Run the terminal selection script with `AGENT_MODE=1` environment variable set:
   `AGENT_MODE=1 python3 .agents/skills/openapi-generator/scripts/interactive_prompts.py`
   using the `run_command` tool.
2. The agent acts as an interactive bridge:
   - Periodically check the task log file (using `view_file`) to see what options the script is waiting for.
   - Use the `ask_question` tool to present the options to the user.
   - Send the user's selection back to the background task using `manage_task` with action `send_input` (ensuring to append a newline `\n` to the input).
3. Once the script finishes, it creates the directory structure and saves a JSON config file at `.agents/skills/openapi-generator/scratch/config.json`.

### Step 2: Read the Selection Metadata
1. View the contents of the configuration file `.agents/skills/openapi-generator/scratch/config.json` using the `view_file` tool to obtain the selected:
   - `version`
   - `domain`
   - `endpoint_name`
   - `route_type`

### Step 3: Generate OpenAPI Specification (.yaml)
1. Parse the API contract/description provided by the user.
2. Generate the OpenAPI 3.0.3 specification YAML file.
3. Save it to `openapi/{version}/{domain}/{endpoint_name}.yaml`.
4. Follow these best practices:
   * **Parameter Descriptions**: Provide a clear description for every parameter (path, query, header) and schema property.
   * **Schemas**: Move request and response models to the `components/schemas` section to ensure they are reusable and clean.
   * **Examples**: Provide realistic examples for all properties to help documentation users.
   * **No Auth references**: Ensure that the endpoints are designed appropriately. If no security is specified, do not add dummy auth keys.

### Step 4: Generate Python Route Handler (If requested)
1. If the `route_type` in the metadata is `"simulated"` or `"empty"`:
   * Generate the FastAPI Python route handler.
   * Save it to `routes/{version}/{domain}/{endpoint_name}.py`.
   * For `"simulated"`, implement the FastAPI route to return mock/simulated responses based on the OpenAPI contract.
   * For `"empty"`, implement the FastAPI route with empty functions (using `pass` or basic schema structures) so the user can fill in the logic.
   * Ensure correct inputs, imports, and output structure.

### Step 5: Verification & Confirmation
1. Run syntax validation using `python3 -m py_compile` on the newly generated Python file to ensure it compiles correctly.
2. Inform the user of the successfully created files and show their paths.
3. Clean up the configuration file `.agents/skills/openapi-generator/scratch/config.json`.
