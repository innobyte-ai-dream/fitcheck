from datetime import datetime
from traceback import print_exc, format_exc
from typing import Optional
from urllib.parse import quote
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import ORJSONResponse, StreamingResponse
import orjson
from pydantic import BaseModel
from typing import List, Literal
import requests
from aiohttp.client_exceptions import ClientResponseError

try:
    from backend.openai import async_simple_prompt, async_simple_prompt_35
    from backend.file_to_base64 import read_upload_files
    from backend.text_to_speech import (
        azure_text_to_speech,
        azure_text_to_speech_ssml,
        PATH_VOICE_SSML,
        VOICE_NAME,
        VOICE_STYLE,
    )
    from backend.coach import coach_router
except ImportError:
    from openai import async_simple_prompt, async_simple_prompt_35
    from file_to_base64 import read_upload_files
    from coach import coach_router
    from text_to_speech import (
        azure_text_to_speech,
        azure_text_to_speech_ssml,
        PATH_VOICE_SSML,
        VOICE_NAME,
        VOICE_STYLE,
    )

app = FastAPI(
    version="0.1.0",
    title="FitCheck API",
    description="An API for the FitCheck app.",
    docs_url="/docs",
)


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # you probably want some kind of logging here
        print_exc()

        detail = {"error": format_exc()}
        try:
            detail["errorObject"] = orjson.loads(orjson.dumps(vars(e), default=str))
        except Exception:
            pass

        if isinstance(e, HTTPException):
            return ORJSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
                headers=e.headers,
            )

        if isinstance(e, requests.RequestException):
            req: requests.Request = getattr(e, "request", None)
            response: requests.Response = getattr(e, "response", None)

            req_detail = {
                "url": getattr(req, "url", None),
                "method": getattr(req, "method", None),
                "headers": getattr(req, "headers", None),
                "body": getattr(req, "body", None),
                "params": getattr(req, "params", None),
            }
            function_req_detail = {
                "url": getattr(request, "url", None),
                "method": getattr(request, "method", None),
                "headers": getattr(request, "headers", None),
                "body": getattr(request, "body", None),
                "params": getattr(request, "params", None),
            }
            response_detail = {
                "status_code": getattr(response, "status_code", None),
                "headers": getattr(response, "headers", None),
                "text": getattr(response, "text", None),
            }
            return ORJSONResponse(
                status_code=response_detail["status_code"] or 500,
                content={
                    **detail,
                    "request": req_detail,
                    "function_request": function_req_detail,
                    "response": response_detail,
                },
                headers=response_detail["headers"],
            )
            # raise HTTPException(
            #     status_code=response_detail["status_code"] or 500,
            #     detail={
            #         **detail,
            #         "request": req_detail,
            #         "function_request": function_req_detail,
            #         "response": getattr(response, "text", None),
            #     },
            #     headers=response_detail["headers"],
            # ) from e
        if isinstance(e, ClientResponseError):
            request_info = getattr(e, "request_info", None)
            request_detail = {
                "url": str(getattr(request_info, "url", "")),
                "method": getattr(request_info, "method", None),
                "headers": str(getattr(request_info, "headers", "")),
                "real_url": str(getattr(request_info, "real_url", "")),
            }
            history = getattr(e, "history", [])
            response_detail = {
                "status_code": getattr(e, "status", None) or getattr(e, "code", None),
                "text": getattr(e, "message", None),
                "headers": str(getattr(e, "headers", "")),
                "history": [
                    {
                        "status_code": h.status,
                        "text": h.text(),
                        "headers": str(h.headers),
                    }
                    for h in history
                ],
            }
            return ORJSONResponse(
                status_code=response_detail["status_code"] or 500,
                content={
                    **detail,
                    "response": response_detail,
                    "request": request_detail,
                },
                # headers=response_detail["headers"],
            )
            # raise HTTPException(
            #     status_code=response_detail["status_code"] or 500,
            #     detail={
            #         **detail,
            #         "response": response_detail,
            #         "request": request_detail,
            #     },
            #     headers=response_detail["headers"],
            # ) from e
        return ORJSONResponse(status_code=500, content=detail)
        # raise HTTPException(status_code=500, detail=detail) from e


app.middleware("http")(catch_exceptions_middleware)

app.include_router(coach_router, prefix="/api/v1/coach", tags=["Coach"])


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


@app.get("/api/v1/speech/simple", name="Text to speech")
async def text_to_speech(text: str, voice_name: str = "en-US-AvaMultilingualNeural"):
    StreamResponse = StreamingResponse(
        azure_text_to_speech(text, voice_name),
        media_type="audio/mpeg",
    )
    return StreamResponse


@app.get(PATH_VOICE_SSML, name="Text to speech")
async def text_to_speech(
    text: str = "ให้ยกแขนซ้ายให้สูงขึ้นนะ <break/> ขวาทำได้ดีแล้ว! <break/> สู้ๆ! 1 2 <break/> 3",
    voice_name: Literal[*VOICE_NAME] = "en-US-AvaMultilingualNeural",  # type: ignore
    rate: float = 1,
    lang: str = "en-US",
    style: Literal[*VOICE_STYLE] = "default",  # type: ignore
    stream_size: Optional[int] = None,
):
    StreamResponse = StreamingResponse(
        azure_text_to_speech_ssml(
            text,
            voice_name=voice_name,
            rate=rate,
            lang=lang,
            style=style,
            stream_size=stream_size,
        ),
        media_type="audio/mp3",
        headers={
            "x-tts-rate": str(rate),
            "x-tts-lang": lang,
            "x-tts-voice": voice_name,
            "x-tts-text": quote(text[:1024]),
            # "Content-Disposition": f'attachment; filename="{voice_name}.mp3"',
        },
    )
    return StreamResponse


@app.get("/", name="Root")
def index():
    return {"message": "Welcome to FitCheck API!", "time": datetime.now()}
