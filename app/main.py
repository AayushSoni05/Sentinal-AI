from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.customer import router as customer_router
from app.api.investigation import router as investigation_router
from app.api.decision import router as decision_router

from app.database.connection import engine, Base
from app.database.models import (
    Customer,
    Investigation,
    InvestigationDecision
)

from app.config.settings import settings

from app.utils.logger import logger


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Powered Due Diligence Platform"
)


# Create any missing database tables.
Base.metadata.create_all(bind=engine)


# Register API routers.
app.include_router(customer_router)
app.include_router(investigation_router)
app.include_router(decision_router)


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception(
        f"Unexpected error: {request.method} {request.url}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal server error occurred."
        }
    )


@app.get("/")
def home():
    return {
        "application": settings.app_name,
        "version": settings.app_version,
        "status": "Running",
        "message": "Welcome to Sentinel AI 🚀"
    }