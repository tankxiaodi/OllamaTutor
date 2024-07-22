import assemblyai as aai
import ollama
import subprocess
import platform
import threading
import os
import time
from dotenv import load_dotenv
if platform.system() == 'Windows':
    import winsound
from constants import *
from utilities import *
from prompt import *
from GoogleTTSClient import *
from EdgeTTSClient import *
from AzureTTSClient import *



class AI_Assistant:
    def __init__(self):
        assemblyai_api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not assemblyai_api_key:
                raise ValueError("Assemblyai API key not found in environment variables")
        aai.settings.api_key = assemblyai_api_key
        tts_api = os.getenv('TTS_API')
        if tts_api == 'Google':
            self.tts_client = GoogleTTSClient()
        elif tts_api == 'Edge':
            self.tts_client = EdgeTTSClient()
        elif tts_api == 'Azure':
            azure_subscription_key = os.getenv('AZURE_SUBSCRIPTION_KEY')
            azure_region = os.getenv('AZURE_REGION')
            if not azure_subscription_key or not azure_region:
                raise ValueError("Azure credentials not found in environment variables")
            self.tts_client = AzureTTSClient(azure_subscription_key, azure_region)
        else:
            print("Please set TTS api")

        self.transcriber = None
        sys_prompt = generate_sys_prompt()
        print("system prompt: " + sys_prompt)
        # 初始化和AI的聊天记录
        self.full_transcript = [
            {"role":"system", "content":sys_prompt},
        ]
        #
        self.transcripted_text = '' # 累计本次人类说话
        #
        self.last_asr_updated_time = 0
        
    def play_sound_async(self):
        threading.Thread(target=self.play_sound).start()


    def play_sound(self):
        system = platform.system()
        if system == 'Darwin':  # macOS
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"])
        elif system == 'Windows':  # Windows
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS)

###### Step 2: Real-Time Transcription with AssemblyAI ######
        
    def start_transcription(self):
        print(f"\nReal-time transcription: ", end="\r\n")
        
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate=16_000,
            on_data=self.on_data,
            on_error=self.on_error,
            on_open=self.on_open,
            on_close=self.on_close,
        )
        
        # 启动MicrophoneStream
        self.transcriber.connect()
        microphone_stream = aai.extras.MicrophoneStream(sample_rate=16_000)
        self.transcriber.stream(microphone_stream)
        self.transcriber.close()
        

    def stop_transcription(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None
      

    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        # ASR启动, 等待用户说话
        self.play_sound_async()
        self.transcripted_text = ''
        return


    def on_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return
        
        if isinstance(transcript, aai.RealtimeFinalTranscript):
            self.last_asr_updated_time = time.time()
            print(transcript.text)
            self.transcripted_text += transcript.text # 累计转录句子
            if check_end_of_speech(self.transcripted_text.strip()):
                # 若遇到结束语，处理转录
                self.stop_transcription()
                self.process_speech()
                return
        else:
            pass
            #print(transcript.text, end="\r")


    def on_error(self, error: aai.RealtimeError):
        if len(str(error)) > 0: 
            print("An error occured:", error)
        return


    def on_close(self):
        #print("Closing Session")
        return
    
    def process_speech(self, is_init=False):
        if not is_init:
            self.transcripted_text = extract_content_rsplit(self.transcripted_text.strip())
            self.play_sound()
        else:
            # 初始运行
            print("LOADING MODEL...")
            self.transcripted_text = "Hello! " + AI_NAME

        self.generate_ai_response(self.transcripted_text)
        self.is_speaking = False
        self.last_speech_time = None
        self.transcripted_text = ''

    
###### Step 3: Pass real-time transcript to LLM ######
    def generate_ai_response(self, transcripted_text):
        
        self.full_transcript.append({"role":"user", "content":transcripted_text})
        print(f"\nUser:{transcripted_text}", end="\r\n")

        model_name = os.getenv('MODEL_NAME')
        model_num_ctx = int(os.getenv('MODEL_NUM_CTX'))
        ollama_stream = ollama.chat(
            model=model_name,
            messages=self.full_transcript,
            stream=True,
            options={
                    "num_ctx": model_num_ctx
            },
            keep_alive=300 # Ollama模型保活时间
        )

        print(AI_NAME + ":", end="")

        text_buffer = ""
        full_text = ""
        for chunk in ollama_stream:
            text_buffer += chunk['message']['content']
            
            if text_buffer.endswith('.'):
                text_buffer = text_buffer.strip()
                self.tts_client.play_stream(text_buffer)
                print(text_buffer, end="\n", flush=True)
                full_text += text_buffer
                text_buffer = ""
            
        
        if text_buffer:
            text_buffer = text_buffer.strip()
            print(text_buffer, end="\n", flush=True)
            self.tts_client.play_stream(text_buffer)
            full_text += text_buffer

        self.full_transcript.append({"role":"assistant", "content":full_text})
        self.start_transcription()



if __name__ == '__main__':
    # 加载 .env 文件中的环境变量
    load_dotenv()
    ai_assistant = AI_Assistant()
    ai_assistant.process_speech(True) # 启动AI对话
