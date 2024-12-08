from typing import Literal, Optional
from urllib.parse import urlencode

from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

try:
    from backend.openai import async_simple_prompt
    from backend.text_to_speech import VOICE_NAME, PATH_VOICE_SSML, VOICE_STYLE
except ImportError:
    from openai import async_simple_prompt
    from text_to_speech import VOICE_NAME, PATH_VOICE_SSML, VOICE_STYLE

from fastapi import APIRouter

coach_router = APIRouter()

TYPE_VOICE_STYLE = Literal[VOICE_STYLE]


TYPE_GENDER = Literal["male", "female"]


class TextAdvice(BaseModel):
    position: str = (
        "Overhead press: The lift is set up by taking either a barbell, a pair of dumbbells or kettlebells, and holding them at shoulder level. The weight is then pressed overhead. While the exercise can be performed standing or seated, standing recruits more muscles as more balancing is required in order to support the lift."
    )
    advice: str = "Left arm: low. Right arm: OK. Move left arm higher."
    gender: TYPE_GENDER = "female"
    character: str = "24 years old, cute, friendly, and energetic"
    language: str = "th-TH"
    voiceName: Literal[*VOICE_NAME] = "en-US-AvaMultilingualNeural"  # type: ignore
    streamSize: Optional[int] = None


class OutputFormat(BaseModel):
    advice: str
    mood: TYPE_VOICE_STYLE  # type: ignore
    rate: float = 1
    url: str = PATH_VOICE_SSML

    def format(self):
        return f"{self.rate}\n{self.mood}\n{self.advice}"

    @classmethod
    def parse_text(
        cls,
        text: str,
        input_advice: TextAdvice,
        path_voice: str = PATH_VOICE_SSML,
    ):
        lines = text.split("\n", 3)
        try:
            rate = float(lines[0])
        except Exception:
            rate = 1

        mood = lines[1] if len(lines) > 1 else "assistant"
        advice = lines[2] if len(lines) > 2 else "Great!"

        url = (
            path_voice
            + "?"
            + urlencode(
                dict(
                    text=advice,
                    voice_name=input_advice.voiceName,
                    rate=rate,
                    lang=input_advice.language,
                    style=mood,
                    stream_size=input_advice.streamSize,
                )
            )
        )
        return cls(rate=rate, mood=mood, advice=advice, url=url)


EXAMPLE_1 = OutputFormat(
    rate=1.25,
    advice="Keep your back straight and chest up. <break/> You're doing great!",
    mood="excited",
)


EXAMPLE_2 = OutputFormat(
    rate=2,
    advice="Hey! <break/> แปด <break/> เก้า <break/> สิบ เก่งมาก!",
    mood="cheerful",
)

_voice_style = "\n".join(VOICE_STYLE)
SYSTEM_PROMPT_TEMPLATE = (
    """
Act as fitness coach.
Your character is {gender}, {character}.
Give advice correct position and cheer-up to user from exercise <position> and motion <interpret> from input.
Give "advice" in 1 - 2 phrase/sentences with "mood" of trainer voice.
Adjust "rate" of speech to give tempo to trainee and depend on "mood" and correctness of trainee.
Use '<break/>' for 750ms pause between word - to emphasize, simulate coach breathing, or give tempo to trainee.
Advice must be in {language} language. Mix of English phrase and {language} is allowed.
Return in text in <output> tag - first line is "rate" of speech, second line is "mood", remain lines are "advice".
"""
    + f"""
Here is choice of mood:
```
{_voice_style}
```
Example advice in English in "excited" mood:
<output>
{EXAMPLE_1.format()}
</output>

Example advice in Thai with English in "cheerful" mood:
<output>
{EXAMPLE_2.format()}
</output>
"""
)


INPUT_PROMPT_TEMPLATE = (
    "<position>{position}</position><interpret>{interpret}</interpret>"
)
# "<position>Overhead press: The lift is set up by taking either a barbell, a pair of dumbbells or kettlebells, and holding them at shoulder level. The weight is then pressed overhead. While the exercise can be performed standing or seated, standing recruits more muscles as more balancing is required in order to support the lift.</position><interpret>Left arm: low. Right arm: OK. Move left arm higher.</interpret>"


def extract_output(text: str):
    if "<output>" in text:
        text = text.split("<output>")[1].split("</output>")[0].strip()
    elif "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```yaml" in text:
        text = text.split("```yaml")[1].split("```")[0].strip()
    elif "```yml" in text:
        text = text.split("```yml")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return text


@coach_router.post("/text", name="Response advice in text format")
async def text_advice(input_advice: TextAdvice):
    sys_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        gender=input_advice.gender,
        character=input_advice.character,
        language=input_advice.language,
    ).strip()
    prompt = INPUT_PROMPT_TEMPLATE.format(
        position=input_advice.position,
        interpret=input_advice.advice,
    ).strip()
    response = await async_simple_prompt(prompt, sys_prompt)
    return OutputFormat.parse_text(
        text=extract_output(response),
        input_advice=input_advice,
        path_voice=PATH_VOICE_SSML,
    )


@coach_router.post(
    "/voice",
    name="Response advice in text and then redirect to URL to get streaming of mp3 audio format",
)
async def voice_advice(input_advice: TextAdvice):
    advice = await text_advice(input_advice)
    # redirect to advice.url
    return ORJSONResponse(content=advice.model_dump(), headers={"Location": advice.url})


# @coach_router.get("/voice", name="Response advice in mp3 audio format")
# async def voice_advice(
#     position: str = (
#         "Overhead press: The lift is set up by taking either a barbell, a pair of dumbbells or kettlebells, and holding them at shoulder level. The weight is then pressed overhead. While the exercise can be performed standing or seated, standing recruits more muscles as more balancing is required in order to support the lift."
#     ),
#     advice: str = "Left arm: low. Right arm: OK. Move left arm higher.",
#     gender: TYPE_GENDER = "female",
#     character: str = "24 years old, cute, friendly, and energetic",
#     language: str = "th-TH",
#     voiceName: Literal[*VOICE_NAME] = "en-US-AvaMultilingualNeural",
# ):
#     input_advice = TextAdvice(
#         position=position,
#         advice=advice,
#         gender=gender,
#         character=character,
#         language=language,
#         voiceName=voiceName,
#     )
#     advice: OutputFormat = await text_advice(input_advice)
#     StreamResponse = StreamingResponse(
#         azure_text_to_speech_ssml(
#             text=advice.advice,
#             voice_name=input_advice.voiceName,
#             rate=advice.rate,
#             lang=input_advice.language,
#             style=advice.mood,
#         ),
#         media_type="audio/mpeg",
#         headers={
#             "x-tts-rate": str(advice.rate),
#             "x-tts-lang": input_advice.language,
#             "x-tts-voice": input_advice.voiceName,
#             "x-tts-text": quote(advice.advice),
#             "x-tts-mood": advice.mood,
#         },
#     )
#     return StreamResponse
