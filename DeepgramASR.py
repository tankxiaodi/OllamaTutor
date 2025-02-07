from dotenv import load_dotenv
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

load_dotenv()

class DeepgramASR:
    def __init__(self):
        self.deepgram = DeepgramClient()
        self.dg_connection = None
        self.microphone = None
        self.is_finals = []
        self.callbacks = {}

    def set_callback(self, event, callback):
        self.callbacks[event] = callback

    def _on_open(self, connection, open, **kwargs):
        print("Connection Open")
        if 'open' in self.callbacks:
            self.callbacks['open']()

    def _on_close(self, connection, close, **kwargs):
        print("Connection Closed")
        if 'close' in self.callbacks:
            self.callbacks['close']()

    def _on_message(self, connection, result, **kwargs):
        sentence = result.channel.alternatives[0].transcript
        if len(sentence) == 0:
            return
        if result.is_final:
            self.is_finals.append(sentence)
            if result.speech_final:
                utterance = " ".join(self.is_finals)
                #print(f"Speech Final: {utterance}")
                if 'data' in self.callbacks:
                    self.callbacks['data'](utterance)
                self.is_finals = []

    def _on_error(self, connection, error, **kwargs):
        print(f"Handled Error: {error}")
        if 'error' in self.callbacks:
            self.callbacks['error'](error)

    def start(self):
        self.dg_connection = self.deepgram.listen.live.v("1")
        
        self.dg_connection.on(LiveTranscriptionEvents.Open, self._on_open)
        self.dg_connection.on(LiveTranscriptionEvents.Close, self._on_close)
        self.dg_connection.on(LiveTranscriptionEvents.Transcript, self._on_message)
        self.dg_connection.on(LiveTranscriptionEvents.Error, self._on_error)

        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            vad_events=True,
            endpointing=300,
        )

        try:
            self.dg_connection.start(options)
            self.microphone = Microphone(self.dg_connection.send)
            self.microphone.start()
            return True
        except Exception as e:
            print(f"Failed to start ASR: {e}")
            return False

    def stop(self):
        if self.microphone:
            self.microphone.finish()
        if self.dg_connection:
            self.dg_connection.finish()
        print("ASR Stopped")
