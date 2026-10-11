from fastapi import FastAPI

app = FastAPI(title="Servicio de autenticación – Chat Empresarial")


@app.get("/salud")
def salud() -> dict:
    """Comprobación de que el servicio está activo."""
    return {"estado": "ok"}
