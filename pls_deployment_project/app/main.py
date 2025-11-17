from __future__ import annotations

import time

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse

from app.config import GenerationDefaults, get_settings
from app.generator import PLSGenerator
from app.schemas import (
    BulkClassificationRequest,
    BulkClassificationResponse,
    ClassificationRequest,
    ClassificationResponse,
    HealthResponse,
    ReadabilityBreakdown,
    ReadabilityMetrics,
    SummarizeRequest,
    SummarizeResponse,
)
from src.classifier import BinaryPLSClassifier
from src.readability import readability_from_text

settings = get_settings()
generator = PLSGenerator(settings)
classifier = BinaryPLSClassifier(
    model_path=settings.classifier_model_path,
    meta_path=settings.classifier_meta_path,
)

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    default_response_class=ORJSONResponse,
)
app.add_middleware(GZipMiddleware, minimum_size=2_048)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=settings.allowed_origins,
)

router = APIRouter(prefix=settings.api_prefix)


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", detail="PLS generator ready", config=settings.summary())


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest) -> SummarizeResponse:
    overrides = GenerationDefaults(
        min_new_tokens=request.min_new_tokens or settings.generation.min_new_tokens,
        max_new_tokens=request.max_new_tokens or settings.generation.max_new_tokens,
        temperature=request.temperature or settings.generation.temperature,
        top_p=request.top_p or settings.generation.top_p,
        no_repeat_ngram_size=request.no_repeat_ngram_size or settings.generation.no_repeat_ngram_size,
        repetition_penalty=request.repetition_penalty or settings.generation.repetition_penalty,
    )
    source_metrics = ReadabilityMetrics(**readability_from_text(request.article))
    started = time.perf_counter()
    candidate = generator.generate(request.article, overrides, best_of=request.best_of)
    elapsed = int((time.perf_counter() - started) * 1000)
    return SummarizeResponse(
        summary=candidate.text,
        latency_ms=elapsed,
        generator=generator.generator_name,
        readability=ReadabilityBreakdown(source=source_metrics, generated=candidate.metrics),
    )


@router.post("/classify", response_model=ClassificationResponse)
def classify_text(request: ClassificationRequest) -> ClassificationResponse:
    result = classifier.predict([request.text])[0]
    return ClassificationResponse(**result)


@router.post("/classify/batch", response_model=BulkClassificationResponse)
def classify_batch(request: BulkClassificationRequest) -> BulkClassificationResponse:
    results = classifier.predict(request.texts)
    return BulkClassificationResponse(results=[ClassificationResponse(**res) for res in results])


app.include_router(router)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.dry_run)
