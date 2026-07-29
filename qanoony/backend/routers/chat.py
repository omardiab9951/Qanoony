from fastapi import APIRouter, HTTPException

from pydantic import BaseModel, Field

from qanoony.backend.rag.router import route_question

chat_router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., example="ما هي مدة إجازة الوضع؟")
    module: str | None = None


class ChatResponse(BaseModel):
    answer: str


class ErrorResponse(BaseModel):
    error: str


@chat_router.post("/chat", response_model=ChatResponse, responses={500: {"model": ErrorResponse}})
async def chat(request: ChatRequest):
    try:
        answer = route_question(request.message, request.module)
        return {"answer": str(answer)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
