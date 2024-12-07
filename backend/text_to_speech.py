import logging
from typing import Dict, Literal, Optional, Set
import azure.cognitiveservices.speech as speechsdk

try:
    from configuration import AZURE_OPEN_AI_API_KEY, AZURE_REGION, VOICE_STREAM_SIZE
except ImportError:
    from backend.configuration import (
        AZURE_OPEN_AI_API_KEY,
        AZURE_REGION,
        VOICE_STREAM_SIZE,
    )

logger = logging.getLogger(__name__)

PATH_VOICE_SSML = "/api/v1/speech/ssml"
VOICE_NAME = {
    "en-US-AmandaMultilingualNeural",  # female
    "en-US-AndrewMultilingualNeural",  # male
    "en-US-AdamMultilingualNeural",  # male
    "en-US-AvaMultilingualNeural",  # female
    "en-US-BrandonMultilingualNeural",  # male
    "en-US-BrianMultilingualNeural",  # male
    "en-US-ChristopherMultilingualNeural",  # male
    "en-US-CoraMultilingualNeural",  # female
    "en-US-DavisMultilingualNeural",  # male
    "en-US-DerekMultilingualNeural",  # male
    "en-US-DustinMultilingualNeural",  # male
    "en-US-EmmaMultilingualNeural",  # female
    "en-US-EvelynMultilingualNeural",  # female
    "en-US-LewisMultilingualNeural",  # male
    "en-US-LolaMultilingualNeural",  # female
    "en-US-NancyMultilingualNeural",  # female
    "en-US-PhoebeMultilingualNeural",  # female
    "en-US-SamuelMultilingualNeural",  # male
    "en-US-SerenaMultilingualNeural",  # female
    "en-US-SteffanMultilingualNeural",  # male
    "en-US-AlloyTurboMultilingualNeural",  # male
    "en-US-EchoTurboMultilingualNeural",  # male
    "en-US-FableTurboMultilingualNeural",  # neutral
    "en-US-NovaTurboMultilingualNeural",  # female
    "en-US-OnyxTurboMultilingualNeural",  # male
    "en-US-ShimmerTurboMultilingualNeural",  # female
    "en-GB-AdaMultilingualNeural",  # female
    "en-GB-OllieMultilingualNeural",  # male
    "de-DE-SeraphinaMultilingualNeural",  # female
    "de-DE-FlorianMultilingualNeural",  # male
    "es-ES-ArabellaMultilingualNeural",  # female
    "es-ES-IsidoraMultilingualNeural",  # female
    "es-ES-TristanMultilingualNeural",  # male
    "es-ES-XimenaMultilingualNeural",  # female
    "fr-FR-LucienMultilingualNeural",  # male
    "fr-FR-VivienneMultilingualNeural",  # female
    "fr-FR-RemyMultilingualNeural",  # male
    "it-IT-AlessioMultilingualNeural",  # male
    "it-IT-GiuseppeMultilingualNeural",  # male
    "it-IT-IsabellaMultilingualNeural",  # female
    "it-IT-MarcelloMultilingualNeural",  # male
    "ja-JP-MasaruMultilingualNeural",  # male
    "ko-KR-HyunsuMultilingualNeural",  # male
    "pt-BR-MacerioMultilingualNeural",  # male
    "pt-BR-ThalitaMultilingualNeural",  # female
    "zh-CN-XiaoxiaoMultilingualNeural",  # female
    "zh-CN-XiaochenMultilingualNeural",  # female
    "zh-CN-XiaoyuMultilingualNeural",  # female
    "zh-CN-YunyiMultilingualNeural",  # male
    "zh-CN-YunfanMultilingualNeural",  # male
    "zh-CN-YunxiaoMultilingualNeural",  # male
    "en-US-AlloyMultilingualNeural3",  # male
    "en-US-EchoMultilingualNeural3",  # male
    "en-US-FableMultilingualNeural3",  # neutral
    "en-US-OnyxMultilingualNeural3",  # male
    "en-US-NovaMultilingualNeural3",  # female
    "en-US-ShimmerMultilingualNeural3",  # female
    "en-US-AlloyMultilingualNeuralHD3",  # male
    "en-US-EchoMultilingualNeuralHD3",  # male
    "en-US-FableMultilingualNeuralHD3",  # neutral
    "en-US-OnyxMultilingualNeuralHD3",  # male
    "en-US-NovaMultilingualNeuralHD3",  # female
    "en-US-ShimmerMultilingualNeuralHD3",  # female
    "en-US-JennyMultilingualNeural2",  # female
    "en-US-RyanMultilingualNeural2",  # male
}

VOICES: Dict[str, Set[str]] = {
    "female": {
        "en-US-AmandaMultilingualNeural",
        "en-US-AvaMultilingualNeural",
        "en-US-CoraMultilingualNeural",
        "en-US-EmmaMultilingualNeural",
        "en-US-EvelynMultilingualNeural",
        "en-US-LolaMultilingualNeural",
        "en-US-NancyMultilingualNeural",
        "en-US-PhoebeMultilingualNeural",
        "en-US-SerenaMultilingualNeural",
        "en-US-NovaTurboMultilingualNeural",
        "en-US-ShimmerTurboMultilingualNeural",
        "en-GB-AdaMultilingualNeural",
        "de-DE-SeraphinaMultilingualNeural",
        "es-ES-ArabellaMultilingualNeural",
        "es-ES-IsidoraMultilingualNeural",
        "es-ES-XimenaMultilingualNeural",
        "fr-FR-VivienneMultilingualNeural",
        "it-IT-IsabellaMultilingualNeural",
        "pt-BR-ThalitaMultilingualNeural",
        "zh-CN-XiaoxiaoMultilingualNeural",
        "zh-CN-XiaochenMultilingualNeural",
        "zh-CN-XiaoyuMultilingualNeural",
        "en-US-NovaMultilingualNeural3",
        "en-US-ShimmerMultilingualNeural3",
        "en-US-NovaMultilingualNeuralHD3",
        "en-US-ShimmerMultilingualNeuralHD3",
        "en-US-JennyMultilingualNeural2",
    },
    "male": {
        "en-US-AndrewMultilingualNeural",
        "en-US-AdamMultilingualNeural",
        "en-US-BrandonMultilingualNeural",
        "en-US-BrianMultilingualNeural",
        "en-US-ChristopherMultilingualNeural",
        "en-US-DavisMultilingualNeural",
        "en-US-DerekMultilingualNeural",
        "en-US-DustinMultilingualNeural",
        "en-US-LewisMultilingualNeural",
        "en-US-SamuelMultilingualNeural",
        "en-US-SteffanMultilingualNeural",
        "en-US-AlloyTurboMultilingualNeural",
        "en-US-EchoTurboMultilingualNeural",
        "en-US-OnyxTurboMultilingualNeural",
        "en-GB-OllieMultilingualNeural",
        "de-DE-FlorianMultilingualNeural",
        "es-ES-TristanMultilingualNeural",
        "fr-FR-LucienMultilingualNeural",
        "fr-FR-RemyMultilingualNeural",
        "it-IT-AlessioMultilingualNeural",
        "it-IT-GiuseppeMultilingualNeural",
        "it-IT-MarcelloMultilingualNeural",
        "ja-JP-MasaruMultilingualNeural",
        "ko-KR-HyunsuMultilingualNeural",
        "pt-BR-MacerioMultilingualNeural",
        "zh-CN-YunyiMultilingualNeural",
        "zh-CN-YunfanMultilingualNeural",
        "zh-CN-YunxiaoMultilingualNeural",
        "en-US-AlloyMultilingualNeural3",
        "en-US-EchoMultilingualNeural3",
        "en-US-OnyxMultilingualNeural3",
        "en-US-AlloyMultilingualNeuralHD3",
        "en-US-EchoMultilingualNeuralHD3",
        "en-US-OnyxMultilingualNeuralHD3",
        "en-US-RyanMultilingualNeural2",
    },
    "neutral": {
        "en-US-FableTurboMultilingualNeural",
        "en-US-FableMultilingualNeural3",
        "en-US-FableMultilingualNeuralHD3",
    },
}


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


async def azure_text_to_speech(
    text: str,
    voice_name: Literal[*VOICE_NAME] = "en-US-AvaMultilingualNeural",  # type: ignore
    stream_size: Optional[int] = None,
):
    if voice_name not in VOICE_NAME:
        raise ValueError(f"Invalid voice name: {voice_name}.")
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_OPEN_AI_API_KEY,
        region=AZURE_REGION,
    )
    speech_config.speech_synthesis_voice_name = voice_name
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio24Khz96KBitRateMonoMp3
    )

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=None,
    )

    result = speech_synthesizer.start_speaking_text_async(text).get()
    stream = speechsdk.AudioDataStream(result)

    audio_buffer = bytes(stream_size or VOICE_STREAM_SIZE)
    while True:
        if result.reason == speechsdk.ResultReason.Canceled:
            raise ValueError(
                f"Error ({result.cancellation_details.reason}: {result.cancellation_details.error_code}): {result.cancellation_details.error_details}"
            )
        buffer_size = stream.read_data(audio_buffer)
        if buffer_size <= 0:
            break
        yield audio_buffer[:buffer_size]


SSML_TEMPLATE = """
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{lang}">
    <voice name="{voice}">
        <mstts:express-as style="{style}">
            <prosody rate="{rate}">
                {word}
            </prosody>
        </mstts:express-as>
    </voice>
</speak>
""".strip()


async def azure_text_to_speech_ssml(
    text: str = "ให้ยกแขนซ้ายให้สูงขึ้นนะ <break/> ขวาทำได้ดีแล้ว! <break/> สู้ๆ! 1 2 <break/> 3",
    voice_name: Literal[*VOICE_NAME] = "en-US-AvaMultilingualNeural",  # type: ignore
    rate: float = 0,
    lang: str = "en-US",
    style: Literal[*VOICE_STYLE] = "default",  # type: ignore
    stream_size: Optional[int] = None,
):
    if voice_name not in VOICE_NAME:
        raise ValueError(f"Invalid voice name: {voice_name}.")
    if rate < -10 or rate > 10:
        raise ValueError(f"Invalid rate: {rate}.")
    # if lang not in ["en-US", "th-TH"]:
    #     raise ValueError(f"Invalid language: {lang}.")
    ssml = SSML_TEMPLATE.format(
        lang=lang,
        voice=voice_name,
        rate=rate,
        word=text,
        style=style,
    )
    logger.info(ssml)
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_OPEN_AI_API_KEY,
        region=AZURE_REGION,
    )
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio48Khz192KBitRateMonoMp3
    )

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=None,
    )

    result: speechsdk.SpeechSynthesisResult = (
        speech_synthesizer.start_speaking_ssml_async(ssml).get()
    )
    stream = speechsdk.AudioDataStream(result)

    audio_buffer = bytes(stream_size or VOICE_STREAM_SIZE)
    total_size = 0
    while True:
        if result.reason == speechsdk.ResultReason.Canceled:
            raise ValueError(
                f"Error ({result.cancellation_details.reason}: {result.cancellation_details.error_code}): {result.cancellation_details.error_details}"
            )

        buffer_size = stream.read_data(audio_buffer)
        total_size += buffer_size
        if buffer_size <= 0:
            logger.info(f"Total size: {total_size}")
            break
        yield audio_buffer[:buffer_size]
