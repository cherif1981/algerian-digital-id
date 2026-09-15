"""
Algerian National ID — API Entrypoint.

Phase 1: OCR + Validation (Document Intelligence)
Phase 2: Enrollment + Identity Store + SD-JWT VC + OpenID4VCI
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import enrollment, identity, ocr, issuance
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.infra.db.session import init_db, dispose_db
from app.infra.ocr.pipeline import InferencePipeline
from app.infra.crypto.keys import KeyManager
from app.domain.credentials.issuer import CredentialIssuer

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    تهيئة الموارد عند الإقلاع، وتنظيفها عند الإطفاء.
    - DB pool
    - OCR pipeline (Tesseract)
    - KeyManager (KMS / HSM)
    - CredentialIssuer (SD-JWT VC)
    """
    configure_logging()
    logger.info("app.startup", env=settings.ENV)

    # 1. DB
    await init_db()

    # 2. OCR pipeline — singleton (تحميل Tesseract ثقيل)
    app.state.pipeline = InferencePipeline()

    # 3. KeyManager — مفاتيح التوقيع
    app.state.key_manager = KeyManager.from_settings(settings)

    # 4. CredentialIssuer — SD-JWT VC
    app.state.issuer = CredentialIssuer(
        key_manager=app.state.key_manager,
        issuer_id=settings.ISSUER_ID,
    )

    logger.info("app.ready")
    yield

    # Cleanup
    await dispose_db()
    logger.info("app.shutdown")


app = FastAPI(
    title="Algerian National ID — Document Intelligence & Digital Identity",
    description=(
        "**Phase 1** — OCR + Validation + Matching (Document Intelligence)\n\n"
        "**Phase 2** — Enrollment + Identity Store + SD-JWT VC + OpenID4VCI"
    ),
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — عدّلها حسب الحاجة في الإنتاج
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────
# Phase 1 — متوافق خلفيًا
app.include_router(ocr.router,        prefix="/api/v1", tags=["Phase 1 · OCR"])

# Phase 2 — جديد
app.include_router(enrollment.router, prefix="/api/v1", tags=["Phase 2 · Enrollment"])
app.include_router(identity.router,   prefix="/api/v1", tags=["Phase 2 · Identity"])

# OpenID4VCI — له مساراته الخاصة (well-known, token, credential)
app.include_router(issuance.router,   tags=["Phase 2 · OpenID4VCI"])


# ─────────────────────────────────────────────────────────
# Health & Root
# ─────────────────────────────────────────────────────────
@app.get("/", tags=["Meta"])
async def root():
    return {
        "app": "Algerian Digital ID",
        "version": app.version,
        "phase": "2",
        "status": "running",
    }


@app.get("/health", tags=["Meta"])
async def health():
    """Liveness — لا يتحقق من التبعيات."""
    return {"status": "healthy"}


@app.get("/ready", tags=["Meta"])
async def ready():
    """Readiness — يتحقق من DB و KeyManager."""
    checks = {"db": False, "keys": False}
    try:
        from app.infra.db.session import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["db"] = True
    except Exception as exc:  # noqa: BLE001
        logger.warning("readiness.db_failed", error=str(exc))

    try:
        checks["keys"] = app.state.key_manager.is_ready()
    except Exception as exc:  # noqa: BLE001
        logger.warning("readiness.keys_failed", error=str(exc))

    ok = all(checks.values())
    return JSONResponse(
        status_code=200 if ok else 503,
        content={"ready": ok, "checks": checks},
    )


# ─────────────────────────────────────────────────────────
# Global exception handler
# ─────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("unhandled_exception", path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "detail": str(exc)},
    )