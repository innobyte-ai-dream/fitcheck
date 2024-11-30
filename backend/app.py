import json
from typing import Literal, Optional
from fastapi import FastAPI
from pydantic import BaseModel

try:
    from backend.openai import async_simple_prompt, async_simple_prompt_35
    from backend.file_to_base64 import read_upload_files
except ImportError:
    from openai import async_simple_prompt, async_simple_prompt_35
    from file_to_base64 import read_upload_files

from typing import List
from fastapi import UploadFile

app = FastAPI(
    version="0.1.0",
    title="FitCheck API",
    description="An API for the FitCheck app.",
    docs_url="/docs",
)


TYPE_GENDER = Literal["male", "female"]


class OutputFormat(BaseModel):
    advice: str
    mood: Literal["power-up", "neutral", "cool-down"]


EXAMPLE_1 = OutputFormat(
    advice="Keep your back straight and chest up. You're doing great!",
    mood="power-up",
)

SYSTEM_PROMPT_TEMPLATE = """
Act as fitness trainer.
Your character is {gender}, {character}.
Give advice correct position and cheer-up to user from exercise <position> and motion <interpret> from input.
Advice in 1 - 2 phrase/sentences with mood of trainer voice ('power-up', 'neutral', 'cool-down').
Advice must be in {language} language.
Return in json in <output> tag.
"""
SYSTEM_PROMPT_EXAMPLE = f"""
Example of output in English:
<output>
{json.dumps(EXAMPLE_1.model_dump())}
</output>
"""


"""
{
  "prompt": "<position>Overhead press: The lift is set up by taking either a barbell, a pair of dumbbells or kettlebells, and holding them at shoulder level. The weight is then pressed overhead. While the exercise can be performed standing or seated, standing recruits more muscles as more balancing is required in order to support the lift.</position><interpret>Left arm: low. Right arm: OK. Move left arm higher.</interpret>",
  "systemPrompt": "Act as fitness trainer. Your character is 25-year-old woman, cheerful, talkative. Give advice correct position and cheer-up to user from exercise <position> and motion <interpret> from input. Advice in 1 - 2 phrase/sentences with mood"
}
"""

INPUT_PROMPT_TEMPLATE = (
    "<position>{position}</position><interpret>{interpret}</interpret>"
)
# "<position>Overhead press: The lift is set up by taking either a barbell, a pair of dumbbells or kettlebells, and holding them at shoulder level. The weight is then pressed overhead. While the exercise can be performed standing or seated, standing recruits more muscles as more balancing is required in order to support the lift.</position><interpret>Left arm: low. Right arm: OK. Move left arm higher.</interpret>"


class TextAdvice(BaseModel):
    position: str
    advice: str
    gender: TYPE_GENDER
    character: str
    language: str


def extract_output(text: str):
    if "<output>" in text:
        text = text.split("<output>")[1].split("</output>")[0].strip()
    elif "```yaml" in text:
        text = text.split("```yaml")[1].split("```")[0].strip()
    elif "```yml" in text:
        text = text.split("```yml")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return json.loads(text)


@app.post("/api/v1/advice/", name="Simple text prompt")
async def generate_text(input_advice: TextAdvice):
    print(SYSTEM_PROMPT_TEMPLATE)
    sys_prompt = (
        SYSTEM_PROMPT_TEMPLATE.format(
            gender=input_advice.gender,
            character=input_advice.character,
            language=input_advice.language,
        ).strip()
        + SYSTEM_PROMPT_EXAMPLE.strip()
    )
    prompt = INPUT_PROMPT_TEMPLATE.format(
        position=input_advice.position,
        interpret=input_advice.advice,
    ).strip()
    json = await async_simple_prompt(prompt, sys_prompt)
    payload = extract_output(json)
    return OutputFormat(**payload)


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
    systemPrompt: Optional[str] = None,
):
    return await async_simple_prompt(
        user_prompt=prompt,
        system_prompt=systemPrompt,
    )
