from fastapi import APIRouter
from src.services.telegram.client import send_message

router = APIRouter()

@router.post("/api/custom_command/telegram_send")
async def telegram_send_endpoint(payload: dict):
    msg_id, text = await send_message(payload['chat_id'], payload['text'])
    return {"message_id": msg_id, "text": text} 