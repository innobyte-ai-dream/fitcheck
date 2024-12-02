import azure.cognitiveservices.speech as speechsdk

try:
    from configuration import (
        AZURE_OPEN_AI_API_KEY,
        AZURE_REGION,
    )
except ImportError:
    from backend.configuration import (
        AZURE_OPEN_AI_API_KEY,
        AZURE_REGION,
    )


async def azure_text_to_speech(
    text: str, voice_name: str = "en-US-AvaMultilingualNeural"
):
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

    audio_buffer = bytes(9600)
    while True:
        buffer_size = stream.read_data(audio_buffer)
        if buffer_size <= 0:
            break
        yield audio_buffer
