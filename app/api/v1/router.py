from fastapi import APIRouter

from app.api.v1.endpoints import currency_information

main_router = APIRouter()

main_router.include_router(currency_information.router, prefix="/currency_information", tags=["currency_information"])
