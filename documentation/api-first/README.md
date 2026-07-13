# FastAPI Docker Sandbox API

A temporary sandbox environment designed to verify that interactive Swagger UI and external network/HTTP requests function flawlessly inside a Docker container (simulating how the application will later consume Google APIs or cloud services).

---

## Project Structure

```text
api-first/
├── app/
│   ├── main.py              # Gateway configuration & sub-app mounting
│   ├── openapi_loader.py    # Merges openapi/{version}/{lang}/*.yaml specs dynamically
│   └── router_loader.py     # Dynamically registers APIRouters under routes/{version}/
├── routes/                  # Python route handlers (APIRouter) outside app/
│   └── v1/                  # V1 Route handlers (shared across languages)
│       └── welcome-example/
│           └── welcome-example.py # V1 Welcome example route
├── openapi/                 # Declarative OpenAPI specs
│   └── v1/                  # V1 Specifications
│       ├── es/              # Spanish Swagger specs
│       │   ├── README.md    # Folder documentation (Spanish)
│       │   ├── main.yaml    # OpenAPI root entrypoint for V1 (Spanish)
│       │   └── welcome-example/
│       │       └── welcome-example.yaml
│       └── en/              # English Swagger specs
│           ├── README.md    # Folder documentation (English)
│           ├── main.yaml    # OpenAPI root entrypoint for V1 (English)
│           └── welcome-example/
│               └── welcome-example.yaml
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

This project organizes specifications and implementations separately by API Version and supports multi-language OpenAPI specifications:

* **`openapi/{version}/{language}/`**: Holds version and language-specific API specifications (e.g. `openapi/v2/es/` and `openapi/v2/en/`).
* **`routes/{version}/`**: Holds version-specific Python routes (`APIRouter`) to handle requests (shared across all languages to avoid code duplication).

### How It Works:
1. **API Gateway & Mounting**: The main gateway [app/main.py](file:///home/jose/Git/a-lot-of-thinks/documentation/api-first/app/main.py) scans directories in `openapi/` for version folders. If a version folder contains language subdirectories (`es`, `en`), it mounts dedicated FastAPI sub-applications under the prefix `/{version}/{language}` (e.g., `/v2/es` and `/v2/en`). If no language folders exist, it mounts directly under `/{version}` for backward compatibility.
2. **Version and Language-Specific Documentation**: Each version and language combination serves its own separate interactive Swagger UI:
   - **V1 Spanish docs**: `http://localhost:8102/v1/es/docs`
   - **V1 English docs**: `http://localhost:8102/v1/en/docs`
   - **V2 Spanish docs**: `http://localhost:8102/v2/es/docs`
   - **V2 English docs**: `http://localhost:8102/v2/en/docs`
3. **Visual/Mock Endpoints**: Adding a path in `.yaml` files automatically renders it in the versioned Swagger UI. Attempting to execute the query returns `404 Not Found` until the corresponding router logic is written.
4. **Dynamic Router Autodiscovery**: The router loader scans `routes/{version}/` and automatically attaches the controller to all language sub-applications of that version.

### Adding a New Version (e.g. V2):
1. Create directories: `openapi/v2/es/`, `openapi/v2/en/`, and `routes/v2/`.
2. Add a `main.yaml` inside both `openapi/v2/es/` and `openapi/v2/en/`.
3. Declare your v2 APIs in YAML files inside the respective language folders.
4. Implement the endpoints in Python under `routes/v2/` using `APIRouter` (which will be shared for both languages).
*The Gateway automatically detects, registers, and mounts the version and languages at startup.*
 
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

Use this skill when you want to create a new endpoint. Just provide the API contract or description to the agent in the chat UI or terminal. The agent will present a single configuration form to choose all parameters at once, making it extremely fast.

#### How to use:
1. Start the `agy` CLI or use the chat interface.
2. Provide your API contract or endpoint description to the agent (e.g. *"Generate a GET /users endpoint that returns a list of users..."*).
3. The agent will present a single dialog form asking for:
   - **API Version** (choosing or writing a version, e.g., `v2`).
   - **Domain / Directory** (choosing or writing a domain, e.g., `users`).
   - **Endpoint name** (filename for the spec/router, e.g., `get-users`).
   - **Route Code Generation** (Simulated FastAPI routes, Empty skeleton, or None).
   - **Documentation Languages** (Spanish, English, or Both using checkboxes).
4. The agent will run the script non-interactively and generate the corresponding OpenAPI YAML specifications in the selected language directories under `openapi/{version}/{lang}/{domain}/{endpoint_name}.yaml` and a single shared FastAPI Python route handler under `routes/{version}/{domain}/{endpoint_name}.py` (avoiding code duplication).

---

### Plantilla Estándar de Documentación de API / Standard API Input Template

Copia y distribuye esta plantilla para dar entrada al agente cuando se requiera crear o documentar un nuevo endpoint. Los textos entre corchetes `[ ]` son las instrucciones de llenado.

```text
[MÉTODO HTTP] [Ruta del Endpoint]
[Párrafo descriptivo: Debe explicar claramente el propósito del endpoint, quién o qué lo consume, y cuál es la lógica de negocio o validación principal que ejecuta. Mencionar cuotas o impacto transversal si aplica.]

Autenticación / Headers:
[Estado de autenticación. Ej: No requiere autenticación. Acceso público. / Requiere autenticación. Authorization: Bearer (JWT provisto por AWS Cognito).]

Parámetros (Ruta / Query):
[Listado de parámetros. Si es "Ninguno", especificarlo explícitamente.]

    [nombre_parametro] ([Tipo de dato], [requerido/opcional]): [Descripción clara. Incluir límites, valores por defecto y enums permitidos].

Cuerpo de la Solicitud (Body):
[Si no aplica, escribir "Ninguno". Si aplica, incluir un bloque JSON con el payload de ejemplo].
Descripción de campos del body:

    [nombre_campo]: [Tipo de dato]. [Descripción funcional. Si es un Enum, listar explícitamente los valores permitidos y qué hace cada uno].

Respuestas (Status Codes y JSON Bodies):
[Repetir este bloque por cada código de estado HTTP que devuelva el endpoint]

[Código HTTP] [Mensaje Estandar] ([Contexto breve, ej: Con resultados, Lista vacía, Error de Cuota])
[Descripción de 1 o 2 líneas explicando exactamente qué condición dispara este código de estado en la lógica de negocio].
JSON

{
  "ejemplo": "debes incluir un JSON representativo exacto"
}

Descripción de campos de la respuesta:

    [nombre_campo]: [Descripción exacta del campo. Si es un arreglo, usar notación de corchetes ej: items[].id].

Adicionales:

    Lambda Asociada: [Nombre exacto del microservicio o Lambda que procesará la petición].
```

#### Principios de Redacción para el Agente IA / Writing Principles for the AI Agent

Para asegurar que el agente generador de Swagger y controladores no cometa errores, las especificaciones de entrada deben cumplir estrictamente con estos tres principios:

1. **Tipado y Enums Explícitos**: El agente no puede deducir tipos o estructuras ambiguas. La especificación debe indicar explícitamente el tipo (ej. `String`, `UUID`, etc.) y, si aplica, si es opcional/requerido. Para campos con valores restringidos, se debe listar explícitamente la lista de enums (ej. *Valores permitidos: `upvote`, `remove`*). Esto garantiza que el Swagger genere los schemas y validaciones correctamente.
2. **Ceros Ambigüedades en JSONs Polimórficos**: Si un mismo código de estado (ej. `200 OK`) puede devolver diferentes estructuras de JSON dependiendo de un estado interno de negocio, cada escenario debe ser documentado como un bloque de respuesta independiente con su respectivo ejemplo.
3. **Mapeo de Errores de Negocio**: Los códigos de error como `400 BadRequest`, `404 NotFound` y `422 UnprocessableEntity` no deben ser genéricos. Se debe documentar el campo `error_code` interno o el mensaje exacto esperado de modo que el agente pueda mapear correctamente las excepciones en el controlador mock/FastAPI.
