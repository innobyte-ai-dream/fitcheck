from typing import List, Optional
import requests
import base64

try:
    from configuration import AZURE_OPEN_AI_API_KEY, AZURE_OPEN_AI_URL
except ImportError:
    from backend.configuration import AZURE_OPEN_AI_API_KEY, AZURE_OPEN_AI_URL
import aiohttp
import asyncio


# Configuration
ENDPOINT = AZURE_OPEN_AI_URL

headers = {
    "Content-Type": "application/json",
    "api-key": AZURE_OPEN_AI_API_KEY,
}

IMAGE_PATH = "YOUR_IMAGE_PATH"

# Payload for the request
payload = {
    # "messages": [
    #     {
    #         "role": "system",
    #         "content": [
    #             {
    #                 "type": "text",
    #                 "text": "You are an AI assistant that helps people find information.",
    #             }
    #         ],
    #     },
    #     {
    #         "role": "user",
    #         "content": [
    #             {"type": "text", "text": "\n"},
    #             {
    #                 "type": "image_url",
    #                 "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
    #             },
    #             {"type": "text", "text": "\n"},
    #             {"type": "image_url", "image_url": {"url": "<base64 image>"}},
    #             {"type": "text", "text": "Extract diagnosis from images"},
    #         ],
    #     },
    #     {
    #         "role": "assistant",
    #         "content": [
    #             {
    #                 "type": "text",
    #                 "text": "From the provided images, the diagnoses are as follows:\n\n**Discharge Summary:**\n- **Principal Diagnosis:**\n  - Community acquired pneumonia\n\n- **Comorbidity Diagnosis:**\n  - Hypertension\n  - Diabetes mellitus type 2\n  - Sequela of cerebrovascular accident\n  - Patient ventilator dyssynchrony\n\n**Auto-filled Diagnosis:**\n1. Epilepsy, unspecified (G409) 1217008005\n2. Sequelae of cerebral infarction (I693) 141831000119101\n3. Essential (primary) hypertension (I10) 10725009\n4. Hyperlipidaemia, unspecified (E785) 114831000119107\n5. Senile cataract, unspecified (H259) 193590000",
    #             }
    #         ],
    #     },
    # ],
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 800,
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
                response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
                text = await response.text()
                json = await response.json()
        return _extract_openai_response(json)
    except aiohttp.ClientError as e:
        print("Input:", request)
        print("Response:", response)
        print("Response Text:", text)
        print("Response JSON:", json)
        raise e from e
