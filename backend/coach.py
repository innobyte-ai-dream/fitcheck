from typing import Literal

from pydantic import BaseModel
from backend.openai import async_simple_prompt


VOICE_STYLE = (
    "advertisement_upbeat",
    "affectionate",
    "angry",
    "assistant",
    "calm",
    "chat",
    "cheerful",
    "customerservice",
    "depressed",
    "disgruntled",
    "documentary-narration",
    "embarrassed",
    "empathetic",
    "envious",
    "excited",
    "fearful",
    "friendly",
    "gentle",
    "hopeful",
    "lyrical",
    "narration-professional",
    "narration-relaxed",
    "newscast",
    "newscast-casual",
    "newscast-formal",
    "poetry-reading",
    "sad",
    "serious",
    "shouting",
    "sports_commentary",
    "sports_commentary_excited",
    "whispering",
    "terrified",
    "unfriendly",
)

TYPE_VOICE_STYLE = Literal[VOICE_STYLE]


TYPE_GENDER = Literal["male", "female"]


class OutputFormat(BaseModel):
    advice: str
    mood: TYPE_VOICE_STYLE  # type: ignore
    rate: float = 1

    def format(self):
        return f"{self.rate}\n{self.mood}\n{self.advice}"

    @classmethod
    def parse_text(cls, text: str):
        lines = text.split("\n", 3)
        try:
            rate = float(lines[0])
        except Exception:
            rate = 1

        mood = lines[1] if len(lines) > 1 else "assistant"
        advice = lines[2] if len(lines) > 2 else "Great!"
        return cls(rate=rate, mood=mood, advice=advice)


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
{VOICE_STYLE.join(", ")}
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


class TextAdvice(BaseModel):
    position: str
    advice: str
    gender: TYPE_GENDER
    character: str
    language: str


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
    return OutputFormat.parse_text(text)


async def text_advice(input_advice: TextAdvice):
    print(SYSTEM_PROMPT_TEMPLATE)
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
    return extract_output(response)
