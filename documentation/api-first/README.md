# FastAPI Docker Sandbox API

A temporary sandbox environment designed to verify that interactive Swagger UI and external network/HTTP requests function flawlessly inside a Docker container (simulating how the application will later consume Google APIs or cloud services).

---

## Project Structure

```text
api-first/
├── app/
│   └── main.py              # FastAPI main application & endpoints
├── .env                     # Environment configuration (defines API_PORT)
├── Dockerfile               # Production-ready slim Docker environment
├── docker-compose.yml       # Docker Compose config with live-reload mounting
├── requirements.txt         # Project package dependencies
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
