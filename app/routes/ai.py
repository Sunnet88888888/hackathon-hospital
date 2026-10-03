import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from openai import AsyncOpenAI, OpenAIError

from app.config import settings
from app.models import User
from app.routes.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])
logger = logging.getLogger(__name__)


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

