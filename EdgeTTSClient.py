import asyncio
import edge_tts
import pyaudio
import io
from pydub import AudioSegment
from constants import *

class EdgeTTSClient:
    def __init__(self):
        self.p = pyaudio.PyAudio()

    async def _generate_audio(self, text, voice):
        communicate = edge_tts.Communicate(text, voice)
        audio_data = b""

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
            elif chunk["type"] == "WordBoundary":
                #print(f"WordBoundary: {chunk}")
                pass

        return audio_data

    def _play_audio(self, audio_data):
        if len(audio_data) == 0:
            return
        audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
        pcm_data = audio.raw_data

        stream = self.p.open(format=self.p.get_format_from_width(audio.sample_width),
                             channels=audio.channels,
                             rate=audio.frame_rate,
                             output=True)

        stream.write(pcm_data)
        stream.stop_stream()
        stream.close()

    def play_stream(self, text):
        audio_data = asyncio.run(self._generate_audio(text, EDGE_TTS_VOICE))
        self._play_audio(audio_data)

    def __del__(self):
        self.p.terminate()

if __name__ == "__main__":
    edge_tts_client = EdgeTTSClient()
    edge_tts_client.play_stream(
        "Hello, this is a test of the EdgeTTS Client."
    )
