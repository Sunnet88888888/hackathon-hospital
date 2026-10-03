import logging
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.utils.ai_runner import ai_runner
from app.config import settings
from app.database import get_db
from app.models import Conversation, Message, User
from app.routes.auth import get_current_user

router = APIRouter(tags=["AI"])
logger = logging.getLogger(__name__)

MAX_CONTEXT_MESSAGES = 20


class CreateConversationRequest(BaseModel):
    message: str = Field(..., min_length=1)


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str | None
    created_at: datetime
    messages: list[ChatMessageResponse]

    class Config:
        from_attributes = True


class ConversationCreatedResponse(BaseModel):
    conversation: ConversationResponse


class ConversationMessageCreatedResponse(BaseModel):
    conversation_id: int
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse


async def generate_ai_response(messages: list[dict[str, str]]) -> str:
    """Placeholder for the AI agent integration.

    Replace this function body with the agent call. The router handles saving
    the user message, preparing the ordered context, and persisting the reply.
    """
    del messages
    return "AI assistant integration is not configured yet."


def get_last_context_messages(db: Session, conversation_id: int) -> list[Message]:
    """Return up to 20 messages in chronological order for the agent."""
    newest_first = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(MAX_CONTEXT_MESSAGES)
        .all()
    )
    return list(reversed(newest_first))


def to_agent_messages(messages: list[Message]) -> list[dict[str, str]]:
    return [
        {"role": message.role, "content": message.content or ""}
        for message in messages
    ]


async def create_assistant_message(
    db: Session,
    conversation_id: int,
    context: list[Message],
    user_token: str,
) -> Message:
    response_text = await ai_runner(user_token=user_token, context=context)
    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=response_text,
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    return assistant_message





@router.post("/conversations")
async def create_conversation(
    data: CreateConversationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = Conversation(
        user_id=current_user.id,
    )

    db.add(conversation)
    await db.flush()

    message = Message(
        conversation_id=conversation.id,
        role="user",
        content=data.message,
    )

    db.add(message)
    await db.commit()
    
    
    agent_message = await create_assistant_message()
    
    
    

    return {
        "conversation_id": conversation.id,
        "message_id": message.id,
    }














@router.post("/convert_audio_to_text")
async def convert_audio_to_text(
	file: UploadFile = File(...),
	current_user: User = Depends(get_current_user),
):
	"""Transcribe an uploaded audio file in Russian using OpenAI Whisper."""
	if not settings.OPENAI_API_KEY:
		await file.close()
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail="Audio transcription is not configured.",
		)

	try:
		async with AsyncOpenAI(api_key=settings.OPENAI_API_KEY) as client:
			transcription = await client.audio.transcriptions.create(
				model="whisper-1",
				file=(file.filename or "audio", file.file, file.content_type),
				response_format="text",
				language="ru",
			)
	except OpenAIError as exc:
		logger.exception("OpenAI audio transcription failed.")
		raise HTTPException(
			status_code=status.HTTP_502_BAD_GATEWAY,
			detail="Audio transcription failed.",
		) from exc
	finally:
		await file.close()

	return {"text": transcription}





