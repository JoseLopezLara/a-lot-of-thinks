# FastAPI Docker Sandbox API

A temporary sandbox environment designed to verify that interactive Swagger UI and external network/HTTP requests function flawlessly inside a Docker container (simulating how the application will later consume Google APIs or cloud services).

---

## Project Structure

```text
api-first/
├── app/
│   ├── main.py              # Gateway configuration & sub-app mounting
│   ├── openapi_loader.py    # Merges openapi/{version}/*.yaml specs dynamically
│   └── router_loader.py     # Dynamically registers APIRouters under routes/{version}/
├── routes/                  # Python route handlers (APIRouter) outside app/
│   └── v1/                  # V1 Route handlers
│       └── welcome-example/
│           └── welcome-example.py # V1 Welcome example route
├── openapi/                 # Declarative OpenAPI specs
│   └── v1/                  # V1 Specifications
│       ├── main.yaml        # OpenAPI root entrypoint (info, servers) for V1
│       └── welcome-example/
│           └── welcome-example.yaml
├── .env                     # Environment configuration (defines API_PORT)
├── Dockerfile               # Production-ready slim Docker environment
├── docker-compose.yml       # Docker Compose config with live-reload mounting
├── requirements.txt         # Project package dependencies with PyYAML
└── README.md                # Documentation & usage instructions
```

---

## Prerequisites

Before running this project, ensure you have the following installed on your machine:
* **Docker** (v20.10.0 or higher)
* **Docker Compose** (v2.0.0 or higher)

---

## Configuration

You can customize the host port exposed by the application using the `.env` file at the root of the project. By default, it exposes port `8102`:
```env
API_PORT=8102
```

---

## Domain-Driven OpenAPI & Versioned Architecture

This project organizes specifications and implementations separately by API Version:

* **`openapi/{version}/`**: Holds version-specific API specifications (e.g. `v1/`, `v2/`).
* **`routes/{version}/`**: Holds version-specific Python routes (`APIRouter`) to handle requests.

### How It Works:
1. **API Gateway & Mounting**: The main gateway [app/main.py](file:///home/jose-lopez-lara/Git/a-lot-of-thinks/documentation/api-first/app/main.py) automatically scans directories in `openapi/` for version folders. For each version discovered (e.g., `v1`), it mounts a dedicated FastAPI sub-application under the prefix (e.g. `/v1`).
2. **Version-Specific Documentation**: Each version serves its own separate interactive Swagger UI:
   - **V1 Swagger docs**: `http://localhost:8102/v1/docs`
   - **V2 Swagger docs** (if created): `http://localhost:8102/v2/docs`
3. **Visual/Mock Endpoints**: Adding a path in `.yaml` files automatically renders it in the versioned Swagger UI. Attempting to execute the query returns `404 Not Found` until the corresponding router logic is written.
4. **Dynamic Router Autodiscovery**: The router loader scans `routes/{version}/` and automatically attaches the controller to the sub-app.

### Adding a New Version (e.g. V2):
1. Create directories: `openapi/v2/` and `routes/v2/`.
2. Add a `main.yaml` inside `openapi/v2/`.
3. Declare your v2 APIs in YAML files inside `openapi/v2/`.
4. Implement the endpoints in Python under `routes/v2/` using `APIRouter`.
*The Gateway automatically detects, registers, and mounts `/v2/` at startup.*
 
---

## Quick Start Commands

### 1. Build and Start the Application
Run the following command to build the image and start the containerized service:
```bash
docker compose up --build
```
Once the output displays that Uvicorn is running, the API will be accessible at:
* **Gateway Health Check**: `http://localhost:8102/health`
* **V1 Swagger API Documentation**: `http://localhost:8102/v1/docs`

### 2. Stop the Application
To stop and remove the container, run:
```bash
docker compose down
```

---

## Interactive Swagger UI Testing

FastAPI natively exposes interactive documentation. You can test the endpoints directly:

1. Open your browser and navigate to [http://localhost:8102/v1/docs](http://localhost:8102/v1/docs).
2. Expand the `GET /welcome-example` endpoint block (under **Welcome Example**).
3. Click the **"Try it out"** button. An optional `client_name` query parameter will appear.
4. Click **"Execute"**. 
5. Under the **"Response body"**, you should see the successful welcome message:
   ```json
   {
     "message": "Welcome Developer! Sandbox setup was successful. You can view the interactive API documentation at /v1/docs",
     "status": "ready"
   }
   ```

---

## Antigravity CLI Custom Skills

This project includes a custom workspace skill to speed up development by automatically generating OpenAPI specifications and FastAPI route handlers.

### 1. OpenAPI and Route Generator Skill (`openapi-generator`)

Use this skill when you want to create a new endpoint. Just provide the API contract or description to the agent in the chat UI or terminal, and the skill will guide the agent through generating the YAML file and Python code.

#### How to use:
1. Start the `agy` CLI or use the chat interface.
2. Provide your API contract or endpoint description to the agent (e.g. *"Generate a GET /users endpoint that returns a list of users..."*).
3. The agent will detect and execute the `openapi-generator` skill. It will interactively prompt you for:
   - **API Version** (if not specified in your input).
   - **Domain / Directory** (by listing existing domains or letting you create a new one).
   - **Route Code Generation** (whether you want simulated mock responses, an empty skeleton route, or no Python file at all).
4. The agent will then generate the corresponding OpenAPI YAML specification and FastAPI Python route handler in the correct directories under `openapi/` and `routes/`.
