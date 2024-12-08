from typing import List, Optional
import requests

try:
    from configuration import (
        AZURE_OPEN_AI_API_KEY,
        AZURE_OPEN_AI_URL,
        GPT35_AZURE_OPEN_AI_URL,
    )
except ImportError:
    from backend.configuration import (
        AZURE_OPEN_AI_API_KEY,
        AZURE_OPEN_AI_URL,
        GPT35_AZURE_OPEN_AI_URL,
    )
import aiohttp

# Configuration
ENDPOINT = AZURE_OPEN_AI_URL

headers = {
    "Content-Type": "application/json",
    "api-key": AZURE_OPEN_AI_API_KEY,
}

IMAGE_PATH = "YOUR_IMAGE_PATH"

# Payload for the request
payload = {
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 2048,
}


def _simple_prompt(
    user_prompt: str,
    system_prompt: Optional[str] = None,
    images: Optional[List[str]] = None,
):
    messages = []
    if system_prompt:
        messages.append(
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt,
                    }
                ],
            }
        )

    user_message_content = []
    if images:
        for i in images:
            user_message_content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": i},
                },
            )
    if user_prompt:
        user_message_content.append({"type": "text", "text": user_prompt})

    if not user_message_content:
        raise ValueError(f"No user prompt given, user: `{user_prompt}`")
    messages.append({"role": "user", "content": user_message_content})

    # Send request
    request = {
        **payload,
        "messages": messages,
    }
    return request


def _simple_prompt_35(
    user_prompt: str,
    system_prompt: Optional[str] = None,
):
    messages = []
    if system_prompt:
        messages.append(
            {
                "role": "system",
                "content": system_prompt,
            }
        )

    if not user_prompt:
        raise ValueError(f"No user prompt given, user: `{user_prompt}`")
    messages.append({"role": "user", "content": user_prompt})

    # Send request
    request = {
        **payload,
        "messages": messages,
    }
    return request


def _extract_openai_response(response: dict) -> str:
    return response["choices"][0]["message"]["content"]


def simple_prompt(
    user_prompt: str,
    system_prompt: Optional[str] = None,
    images: Optional[List[str]] = None,
):
    request = _simple_prompt(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        images=images,
    )
    response = None
    json = None
    try:
        response = requests.post(
            ENDPOINT,
            headers=headers,
            json=request,
        )
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        json = response.json()
        return _extract_openai_response(json)
    except requests.RequestException as e:
        print("Input:", request)
        print("Response:", response)
        print("Response Text:", getattr(response, "text"))
        print("Response JSON:", json)
        raise e from e


async def async_simple_prompt(
    user_prompt: str,
    system_prompt: Optional[str] = None,
    images: Optional[List[str]] = None,
):
    request = _simple_prompt(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        images=images,
    )
    response = None
    json = None
    text = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                ENDPOINT,
                headers=headers,
                json=request,
            ) as response:
                text = await response.text()
                json = await response.json()
                response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        return _extract_openai_response(json)
    except aiohttp.ClientError as e:
        print("Input:", request)
        print("Response:", response)
        print("Response Text:", text)
        print("Response JSON:", json)
        raise e from e


async def async_simple_prompt_35(
    user_prompt: str,
    system_prompt: Optional[str] = None,
):
    request = _simple_prompt_35(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
    )
    response = None
    json = None
    text = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GPT35_AZURE_OPEN_AI_URL,
                headers=headers,
                json=request,
            ) as response:
                text = await response.text()
                json = await response.json()
                response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        return _extract_openai_response(json)
    except aiohttp.ClientError as e:
        print("Input:", request)
        print("Response:", response)
        print("Response Text:", text)
        print("Response JSON:", json)
        raise e from e
