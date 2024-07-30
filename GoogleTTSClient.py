from google.cloud import texttospeech
import pyaudio
from pydub import AudioSegment
import io
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
            audio_encoding=texttospeech.AudioEncoding.MP3,
            sample_rate_hertz=16000,
            speaking_rate=GOOGLE_TTS_SPEAKING_RATE
        )

    def play_stream(self, text):
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            response = self.client.synthesize_speech(
                input=synthesis_input, voice=self.voice, audio_config=self.audio_config
            )
            
            # 将 MP3 数据转换为 PCM
            audio = AudioSegment.from_mp3(io.BytesIO(response.audio_content))
            pcm_data = audio.raw_data
            
            if self.stream is None:
                self.stream = self.p.open(format=self.p.get_format_from_width(audio.sample_width),
                                          channels=audio.channels,
                                          rate=audio.frame_rate,
                                          output=True)
            
            # 播放音频
            self.stream.write(pcm_data)
            
        except Exception as e:
            print(f"Error in play_stream: {e}")

    def close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
