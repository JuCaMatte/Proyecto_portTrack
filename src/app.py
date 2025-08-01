from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
import os
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Métricas de Prometheus
http_requests_total = Counter('http_requests_total', 'Total HTTP Requests', [
                              'method', 'endpoint', 'status'])
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds', 'HTTP Request Duration', ['method', 'endpoint'])
http_connections_active = Gauge(
    'http_connections_active', 'Active HTTP Connections')

app = FastAPI(title="DevOps Demo App")


@app.middleware("http")
async def add_metrics(request: Request, call_next):
    http_connections_active.inc()
    start_time = time.time()

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as e:
        status_code = 500
        raise e
    finally:
        duration = time.time() - start_time
        http_requests_total.labels(
            method=request.method, endpoint=request.url.path, status=status_code).inc()
        http_request_duration_seconds.labels(
            method=request.method, endpoint=request.url.path).observe(duration)
        http_connections_active.dec()


@app.get("/")
async def root():
    return {"message": "API funcionando correctamente", "version": os.getenv("APP_VERSION", "1.0.0")}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/heavy-task")
async def heavy_task():
    start = time.time()
    # Simular carga
    time.sleep(0.1)
    duration = time.time() - start
    return {"message": "Tarea pesada completada", "duration": f"{duration:.2f}s"}


@app.get("/simulate-error")
async def simulate_error():
    raise Exception("Error simulado para pruebas")


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": str(exc) if os.getenv(
            "ENV") != "production" else "Error interno del servidor"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
