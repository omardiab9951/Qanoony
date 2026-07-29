from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., example="ما هي مدة إجازة الوضع؟")


class ChatResponse(BaseModel):
    answer: str


class ErrorResponse(BaseModel):
    error: str


app = FastAPI(title="Qanoony RAG Backend", version="1.0")

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "Frontend"

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": str(exc)})


@app.get("/", response_class=FileResponse)
async def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/chat", response_model=ChatResponse, responses={500: {"model": ErrorResponse}})
async def chat(request: ChatRequest):
    try:
        from rag import ask_qanoony

        answer = ask_qanoony(request.message)
        return {"answer": str(answer)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
