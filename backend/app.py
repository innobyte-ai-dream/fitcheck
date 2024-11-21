from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

try:
    from backend.openai import async_simple_prompt
    from backend.file_to_base64 import read_upload_files
except ImportError:
    from openai import async_simple_prompt
    from file_to_base64 import read_upload_files

from typing import List
from fastapi import UploadFile

app = FastAPI(
    version="0.1.0",
    title="FitCheck API",
    description="An API for the FitCheck app.",
    docs_url="/docs",
)


class TextPrompt(BaseModel):
    prompt: str
    systemPrompt: Optional[str] = None


@app.post("/api/prompt/", name="Simple text prompt")
async def execute_prompt(prompt: TextPrompt):
    return await async_simple_prompt(prompt.prompt, prompt.systemPrompt)


@app.post("/api/prompt/file/", name="Prompt with files")
async def execute_prompt(
    prompt: str,
    files: List[UploadFile],
    systemPrompt: Optional[str] = None,
):
    base64_uris = await read_upload_files(files)
    return await async_simple_prompt(
        user_prompt=prompt,
        system_prompt=systemPrompt,
        images=base64_uris,
    )
