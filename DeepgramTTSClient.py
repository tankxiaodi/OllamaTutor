import os
from dotenv import load_dotenv
import pyaudio
from pydub import AudioSegment
from io import BytesIO

from deepgram import (
    DeepgramClient,
    SpeakOptions,
)

load_dotenv()

class DeepgramTTSClient:
    def __init__(self):
        self.client = DeepgramClient(api_key=os.getenv("DG_API_KEY"))
        self.model = os.getenv("DG_MODEL")
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.options = SpeakOptions(
            model=self.model,
        )

    def play_stream(self, text):
        try:
            # Generate audio content
            speak_options = {"text": text}
            response = self.client.speak.v("2").stream(speak_options, self.options)
            
            # Convert MP3 to raw audio data
            audio = AudioSegment.from_mp3(BytesIO(response.stream.getbuffer()))
            raw_data = audio.raw_data

            # Initialize stream if not already done
            if self.stream is None:
                self.stream = self.p.open(
                    format=self.p.get_format_from_width(audio.sample_width),
                    channels=audio.channels,
                    rate=audio.frame_rate,
                    output=True
                )

            # Play audio
            chunk_size = 1024
            data = raw_data
            while len(data) > 0:
                chunk = data[:chunk_size]
                self.stream.write(chunk)
                data = data[chunk_size:]

        except Exception as e:
            print(f"Error in play_stream: {e}")
