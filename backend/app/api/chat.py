from fastapi import APIRouter
from app.schemas.domain import ChatMessageCreate, ChatMessageResponse
from app.models.domain import ChatHistory
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=ChatMessageResponse)
async def send_message(message: ChatMessageCreate):
    # Store user message
    user_msg = ChatHistory(
        session_id=message.session_id,
        role="user",
        content=message.content
    )
    await user_msg.insert()

    # Simulate AI response (this would connect to Orchestrator LLM)
    ai_reply = f"Acknowledged. I have received your message: '{message.content}'. The Orchestrator is processing."
    ai_msg = ChatHistory(
        session_id=message.session_id,
        role="assistant",
        content=ai_reply
    )
    await ai_msg.insert()

    return ChatMessageResponse(
        id=str(ai_msg.id),
        session_id=ai_msg.session_id,
        role=ai_msg.role,
        content=ai_msg.content,
        created_at=ai_msg.created_at
    )

@router.get("/{session_id}")
async def get_history(session_id: str):
    history = await ChatHistory.find({"session_id": session_id}).to_list()
    return {"status": "success", "history": history}
