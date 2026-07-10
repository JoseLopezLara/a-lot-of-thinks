# FastAPI Docker Sandbox API

A temporary sandbox environment designed to verify that interactive Swagger UI and external network/HTTP requests function flawlessly inside a Docker container (simulating how the application will later consume Google APIs or cloud services).

---

## Project Structure

```text
api-first/
├── app/
│   ├── main.py              # FastAPI main application & endpoints
│   └── openapi_loader.py    # Merges openapi/*.yaml files dynamically
├── openapi/
│   ├── main.yaml            # OpenAPI root entrypoint (info, servers)
│   ├── auth/
│   │   └── google-auth.yaml # Authentication domain specification
│   └── external/
│       └── mock-api.yaml    # External APIs verification domain
├── .env                     # Environment configuration (defines API_PORT)
├── Dockerfile               # Production-ready slim Docker environment with watch dirs
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

## Domain-Driven OpenAPI Architecture

This project is structured for scalable API development where each domain contains its own declarative OpenAPI YAML specification:

* **`openapi/main.yaml`**: The entrypoint defining metadata, versioning, servers, and global configurations.
* **Domain Subfolders (e.g., `openapi/auth/`, `openapi/external/`)**: Put domain-specific YAML specifications inside separate subdirectories (e.g. `user/`, `billing/`).

### How It Works:
1. At startup, [app/openapi_loader.py](file:///home/jose-lopez-lara/Git/a-lot-of-thinks/documentation/api-first/app/openapi_loader.py) walks through the `openapi/` directory.
2. It loads `main.yaml` and recursively merges `paths` and `components` from all sub-YAML files into a single, combined OpenAPI schema dictionary.
3. FastAPI overrides its auto-generated `/docs` schema with this dictionary.
4. During local development, editing any `.yaml` file inside the `openapi/` folder will trigger Uvicorn to hot-reload, refreshing the Swagger UI immediately.

### Adding a New Domain API:
1. Create a new directory under `openapi/`, e.g., `openapi/payments/`.
2. Add a new `.yaml` file (e.g., `openapi/payments/checkout.yaml`) defining routes and components:
   ```yaml
   paths:
     /checkout:
       post:
         tags:
           - Payments
         summary: Process checkout
         responses:
           '200':
             description: Checkout success
   ```
3. Implement the corresponding endpoint in Python inside [app/main.py](file:///home/jose-lopez-lara/Git/a-lot-of-thinks/documentation/api-first/app/main.py):
   ```python
   @app.post("/checkout")
   async def checkout():
       return {"status": "processed"}
   ```

---

## Quick Start Commands

### 1. Build and Start the Application
Run the following command to build the image and start the containerized service:
```bash
docker-compose up --build
```
Once the output displays that Uvicorn is running, the API will be accessible at:
* **Health Check**: `http://localhost:8102/`
* **Swagger API Documentation**: `http://localhost:8102/docs`

### 2. Stop the Application
To stop and remove the container, run:
```bash
docker-compose down
```

---

## Interactive Swagger UI Testing

FastAPI natively exposes interactive documentation. You can test authorization models and live external network calls directly:

1. Open your browser and navigate to [http://localhost:8102/docs](http://localhost:8102/docs).
2. Expand the `GET /test-external-api` endpoint block.
3. Click the **"Try it out"** button.
4. Click **"Execute"**. 
5. Under the **"Response body"**, you should see the JSON output fetched dynamically from the mock external API (`https://jsonplaceholder.typicode.com/posts/1`):
   ```json
   {
     "userId": 1,
     "id": 1,
     "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
     "body": "quia et suscipit\nsuscipit recusandae..."
   }
   ```
6. Expand the `POST /mock-google-auth` endpoint block.
7. Click **"Try it out"**. A pre-populated request body schema (with mock `token` and `client_id` parameters) will appear.
8. Click **"Execute"** to verify that the POST request payloads are processed and responded to successfully.
