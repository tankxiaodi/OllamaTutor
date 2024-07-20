from google.cloud import texttospeech
import pyaudio
from constants import *

class GoogleTTSClient:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.voice = texttospeech.VoiceSelectionParams(
            language_code=GOOGLE_TTS_LANGUAGE_CODE, 
            name=GOOGLE_TTS_NAME
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            speaking_rate=GOOGLE_TTS_SPEAKING_RATE
        )

    def play_stream(self, text):
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            response = self.client.synthesize_speech(
                input=synthesis_input, voice=self.voice, audio_config=self.audio_config
            )
            
            audio_content = response.audio_content
            
            if self.stream is None:
                self.stream = self.p.open(format=self.p.get_format_from_width(2),
                                          channels=1,
                                          rate=16000,
                                          output=True)
            
            # 跳过前1个音频块，防止爆音
            chunk_size = 64
            audio_content = audio_content[chunk_size:]
            
            # 播放音频
            self.stream.write(audio_content)
            
        except Exception as e:
            print(f"Error in play_stream: {e}")

    def close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
