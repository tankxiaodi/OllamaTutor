"""
Ollama AI 语音助手

本模块实现了一个集成以下功能的会话式AI助手:
- 语音转文字 (使用 AssemblyAI)
- 大语言模型交互 (使用 Ollama/OpenAI)
- 文字转语音 (支持多个提供商: Google, Edge, Azure, Deepgram)

该助手可以维持连续对话，处理实时语音输入，并通过语音和文字进行回应。
"""

import assemblyai as aai
import subprocess
import platform
import threading
import os
import signal
import sys
import time
from dotenv import load_dotenv
if platform.system() == 'Windows':
    import winsound
from constants import *
from utilities import *
from GoogleTTSClient import *
from EdgeTTSClient import *
from AzureTTSClient import *
from DeepgramTTSClient import *
from LLM import *
from utilities import *


class AI_Assistant:
    """
    AI助手主类，协调语音识别、LLM交互和语音合成。
    
    该类处理:
    - 实时语音转录
    - 与LLM的对话管理
    - 文字转语音合成
    - 信号处理实现优雅关闭
    """
    
    def __init__(self):
        """
        初始化AI助手，设置必要的API密钥和客户端。
        配置语音识别、TTS和对话历史。
        """
        # 初始化AssemblyAI语音识别
        assemblyai_api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not assemblyai_api_key:
                raise ValueError("Assemblyai API key not found in environment variables")
        aai.settings.api_key = assemblyai_api_key
        
        # 根据环境配置初始化相应的TTS客户端
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
        elif tts_api == 'Deep':
            self.tts_client = DeepgramTTSClient()
        else:
            print("Please set TTS api")

        # 初始化转录和状态变量
        self.transcriber = None
        self.running = True
        
        # 设置信号处理器以实现优雅关闭
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 使用系统提示初始化对话历史
        sys_prompt = generate_sys_prompt()
        print("system prompt: " + sys_prompt)
        self.full_transcript = [
            {"role":"system", "content":sys_prompt},
        ]
        
        # 初始化状态跟踪变量
        self.transcripted_text = ''  # 累积当前人类语音
        self.last_asr_updated_time = 0  # 跟踪最后ASR更新时间戳
        
        # 配置LLM提供商(OpenAI或Ollama)
        if os.getenv('OPENAI') == 'True':
            self.use_openai = True
        else:
            self.use_openai = False

    def cleanup(self):
        """关闭前清理资源"""
        if self.transcriber:
            self.transcriber.close()

    def signal_handler(self, signum, frame):
        """处理终止信号以实现优雅关闭"""
        print("\nReceived signal to terminate. Cleaning up...")
        self.running = False
        
        # 保存易读格式对话记录
        formatted_transcript = format_transcript(self.full_transcript)
        
        history_path = save_conversation_history(formatted_transcript)
        print(f"对话记录已保存到: {history_path}")
        
        # 生成对话总结
        summary = generate_conversation_summary(formatted_transcript, AI_NAME)
        # 生成对话中角色关键信息
        user_key_info = generate_character_key_info(formatted_transcript, 'user', AI_NAME)
        ai_key_info = generate_character_key_info(formatted_transcript, AI_NAME, AI_NAME)
        # 组合以上信息, 并保存对话总结
        summary['user'] = user_key_info
        summary[AI_NAME] = ai_key_info
        summary_path = save_conversation_summary(summary)
        print(f"对话总结已保存到: {summary_path}")
        
        self.cleanup()
        sys.exit(0)
        
    def play_sound_async(self):
        """异步播放通知声音"""
        threading.Thread(target=self.play_sound).start()

    def play_sound(self):
        """根据平台播放系统通知声音"""
        system = platform.system()
        if system == 'Darwin':  # macOS
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"])
        elif system == 'Windows':  # Windows
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS)

    def start_transcription(self):
        """
        使用AssemblyAI启动实时语音转录。
        设置转录器和麦克风流。
        """
        if self.running == False:
            return
        print(f"\nReal-time transcription: ", end="\r\n")
        
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate=16_000,
            on_data=self.on_data,
            on_error=self.on_error,
            on_open=self.on_open,
            on_close=self.on_close,
        )
        
        # 启动麦克风流
        self.transcriber.connect()
        microphone_stream = aai.extras.MicrophoneStream(sample_rate=16_000)
        try: 
            self.transcriber.stream(microphone_stream)
        except Exception as e:
            print(e)
        self.transcriber.close() 

    def stop_transcription(self):
        """停止当前转录会话"""
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None

    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        """
        转录会话打开时的处理程序。
        播放通知声音并重置转录缓冲区。
        """
        self.play_sound_async()
        self.transcripted_text = ''
        return

    def on_data(self, transcript: aai.RealtimeTranscript):
        """
        处理传入的转录数据。
        处理最终转录并检查结束语音标记。
        """
        if not transcript.text:
            return
        
        if isinstance(transcript, aai.RealtimeFinalTranscript):
            self.last_asr_updated_time = time.time()
            print(transcript.text)
            self.transcripted_text += transcript.text  # 累积转录的句子
            if check_end_of_speech(self.transcripted_text.strip()):
                # 如果检测到结束语音，处理转录
                self.stop_transcription()
                self.process_speech()
                return

    def on_error(self, error: aai.RealtimeError):
        """处理转录错误"""
        if len(str(error)) > 0: 
            print("An error occured:", error)
        return

    def on_close(self):
        """处理转录会话关闭"""
        return
    
    def process_speech(self, is_init=False):
        """
        处理转录的语音并生成AI响应。
        
        参数:
            is_init (bool): 是否为初始问候
        """
        if not is_init:
            self.transcripted_text = extract_content_rsplit(self.transcripted_text.strip())
            self.play_sound()
        else:
            # 初始问候
            print("LOADING MODEL...")
            self.transcripted_text = "How are you, " + AI_NAME

        self.generate_ai_response(self.transcripted_text)
        self.is_speaking = False
        self.last_speech_time = None
        self.transcripted_text = ''

    def generate_ai_response(self, transcripted_text):
        """
        使用LLM生成AI响应并使用TTS朗读。
        
        参数:
            transcripted_text (str): 要响应的转录用户输入
        """
        # 将用户消息添加到对话历史
        self.full_transcript.append({"role":"user", "content":transcripted_text})
        print(f"\nUser:{transcripted_text}", end="\r\n")

        # 从环境获取模型配置
        model_name = os.getenv('MODEL_NAME')
        model_num_ctx = int(os.getenv('MODEL_NUM_CTX'))
        is_thinking = False
        # 从LLM生成流式响应
        my_stream = MyLLM.chat(
            model=model_name,
            messages=self.full_transcript,
            options={
                "num_ctx": model_num_ctx
            },
            keep_alive=300,
            use_openai=self.use_openai,
            temperature=0.9,
            base_url=os.getenv('BASE_URL')
        )

        print(AI_NAME + ":", end="")
        # 分块处理流式响应以实现自然语音合成
        text_buffer = ""
        full_text = ""
        for chunk in my_stream:
            if self.use_openai:
                text_buffer += chunk.content
            else:
                if "<think>" in chunk and is_thinking == False:
                    is_thinking = True
                    print(chunk, end="")
                    continue
                elif "</think>" in chunk:
                    is_thinking = False
                    print(chunk, end="")
                    continue

                if is_thinking:
                    print(chunk, end="")
                    continue
                else:
                    text_buffer += chunk
            
            # 朗读完整句子(以句号结尾)
            if text_buffer.endswith('.'):
                text_buffer = text_buffer.strip()
                self.tts_client.play_stream(text_buffer)
                print(text_buffer, end="\n", flush=True)
                full_text += text_buffer
                text_buffer = ""
        
        # 处理剩余文本
        if text_buffer:
            text_buffer = text_buffer.strip()
            print(text_buffer, end="\n", flush=True)
            self.tts_client.play_stream(text_buffer)
            full_text += text_buffer

        # 将AI响应添加到对话历史并重启转录
        self.full_transcript.append({"role":"assistant", "content":full_text})
        self.start_transcription()


if __name__ == '__main__':
    # 从.env文件加载环境变量
    load_dotenv()
    ai_assistant = AI_Assistant()
    ai_assistant.process_speech(True)  # 启动AI对话
