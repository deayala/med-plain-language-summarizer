from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from .config import get_settings
from .schemas import AlignScoreRequest, AlignScoreResponse, HealthResponse
from .scorer import AlignScoreEngine

settings = get_settings()
engine = AlignScoreEngine(settings)

API_DESCRIPTION = (
    "Servicio de AlignScore para medir la similitud factual entre texto técnico y resumen.\n\n"
    "- `/health`: estado del microservicio y configuración activa.\n"
    "- `/align`: devuelve puntaje de alineación, modelo, dispositivo y batch size."
)
API_TAGS_METADATA = [
    {"name": "health", "description": "Estado del servicio y configuración activa."},
    {"name": "align", "description": "Cálculo de AlignScore dado un texto técnico y su generación."},
]

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    default_response_class=ORJSONResponse,
    description=API_DESCRIPTION,
    openapi_tags=API_TAGS_METADATA,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", detail="AlignScore service ready", config=settings.summary())


@app.post("/align", response_model=AlignScoreResponse, tags=["align"])
def score(request: AlignScoreRequest) -> AlignScoreResponse:
    try:
        result = engine.score(request.technical_text, request.generation)
    except FileNotFoundError as exc:  # missing checkpoint on disk
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - alignscore runtime errors
        raise HTTPException(status_code=500, detail=f"AlignScore failed: {exc}") from exc
    return AlignScoreResponse(
        align_score=result.score,
        model_name=result.model_name,
        device=result.device,  # type: ignore[arg-type]
        batch_size=result.batch_size,
    )


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("services.alignscore.app.main:app", host=settings.host, port=settings.port, reload=False)
