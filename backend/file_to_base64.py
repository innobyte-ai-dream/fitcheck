from fastapi import File, UploadFile
import base64
from typing import List
import asyncio


async def read_file(file: UploadFile):
    contents = await file.read()
    base64_encoded = base64.b64encode(contents).decode("utf-8")
    mime_type = file.content_type
    return f"data:{mime_type};base64,{base64_encoded}"


async def read_upload_files(files: List[UploadFile] = File(...)):
    tasks = [read_file(file) for file in files]
    base64_uris = await asyncio.gather(*tasks)
    return base64_uris
