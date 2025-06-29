from fastapi import APIRouter
from src.services.slack.client import send_message

router = APIRouter()

@router.post("/api/custom_command/slack_send")
async def slack_send_endpoint(payload: dict):
    ts, text = await send_message(payload['channel'], payload['text'])
    return {"ts": ts, "text": text} 