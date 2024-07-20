import azure.cognitiveservices.speech as speechsdk
import os
from constants import *

class AzureTTSClient:
    def __init__(self, subscription_key, region):
        self.speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
        # 设置输出到默认扬声器
        self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    def play_stream(self, text, voice=AZURE_TTS_VOICE, style=AZURE_TTS_STYLE, style_degree=AZURE_TTS_STYLE_DEGREE):
        self.speech_config.speech_synthesis_voice_name = voice

        # 创建SSML字符串
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{voice}">
                <mstts:express-as style="{style}" styledegree="{style_degree}">
                    {text}
                </mstts:express-as>
            </voice>
        </speak>
        """

        # 创建语音合成器
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)

        # 使用SSML合成语音
        speech_synthesizer.speak_ssml(ssml)


# 使用示例
if __name__ == "__main__":
    tts_client = AzureTTSClient(os.getenv('AZURE_SUBSCRIPTION_KEY'), os.getenv('AZURE_REGION'))
    tts_client.play_stream(
        "Hello, this is a test of Azure Text to Speech service with a friendly tone.",
    )
