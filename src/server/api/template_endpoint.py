from fastapi import APIRouter
from src.services.template.client import create_entity

router = APIRouter()

@router.post("/api/custom_command/template_create")
async def template_create_endpoint(payload: dict):
    id, url = await create_entity(payload)
    return {"id": id, "url": url} 