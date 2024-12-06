from datetime import datetime
import json
from typing import Literal, Optional
from fastapi import FastAPI, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

try:
    from backend.openai import async_simple_prompt, async_simple_prompt_35
    from backend.file_to_base64 import read_upload_files
    from backend.coach import text_advice, TextAdvice
except ImportError:
    from openai import async_simple_prompt, async_simple_prompt_35
    from file_to_base64 import read_upload_files
    from coach import text_advice, TextAdvice

try:
    from backend.text_to_speech import azure_text_to_speech
except ImportError:
    from text_to_speech import azure_text_to_speech

from typing import List
from fastapi import UploadFile

app = FastAPI(
    version="0.1.0",
    title="FitCheck API",
    description="An API for the FitCheck app.",
    docs_url="/docs",
)


@app.post("/api/v1/advice/text", name="Simple text prompt")
async def generate_text(input_advice: TextAdvice):
    return await text_advice(input_advice)


class TextPrompt(BaseModel):
    prompt: str
    systemPrompt: Optional[str] = None


@app.post("/api/v1/prompt/", name="Simple text prompt")
async def execute_prompt(prompt: TextPrompt):
    return await async_simple_prompt(prompt.prompt, prompt.systemPrompt)


@app.post("/api/v1/prompt/3.5", name="Simple text prompt")
async def execute_prompt_35(prompt: TextPrompt):
    return await async_simple_prompt_35(prompt.prompt, prompt.systemPrompt)


@app.post("/api/v1/prompt/file/", name="Prompt with files")
async def execute_prompt(
    prompt: str,
    files: List[UploadFile] = File(...),
    systemPrompt: Optional[str] = None,
):
    return await async_simple_prompt(
        user_prompt=prompt,
        system_prompt=systemPrompt,
        images=await read_upload_files(files),
    )


@app.post("/api/v1/speech/", name="Text to speech")
@app.get("/api/v1/speech/", name="Text to speech")
async def text_to_speech(text: str, voice_name: str = "en-US-AvaMultilingualNeural"):
    StreamResponse = StreamingResponse(
        azure_text_to_speech(text, voice_name),
        media_type="audio/mpeg",
    )
    return StreamResponse


@app.get("/", name="Root")
def index():
    return {"message": "Welcome to FitCheck API!", "time": datetime.now()}
