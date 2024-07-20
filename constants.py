from prompt import * 

# 使用的tts,填 Google 或 Azure , Edge
# Google 语音最自然, 需要key
TTS_API = "Edge"

# google tts 参数
GOOGLE_TTS_LANGUAGE_CODE = "en-US" # tts语言
GOOGLE_TTS_SPEAKING_RATE = 0.9  # 语速稍慢，1.0 是正常语速
GOOGLE_TTS_NAME = 'en-US-Journey-F' # tts语音类型

# azure tts 参数
AZURE_TTS_VOICE = 'en-GB-SoniaNeural' # tts语音类型
AZURE_TTS_STYLE = 'Friendly' # tts风格
AZURE_TTS_STYLE_DEGREE = 2.0 # 风格强度

# edge tts语音类型
EDGE_TTS_VOICE = 'en-US-JennyNeural' 


 # 用系统提示定义AI的角色
SYS_PROMPT = LANGUAGE_TUTOR_PROMPT
#SYS_PROMPT = HEALTH_COACH_PROMPT

# AI对话的上下文
# token数量应该低于MODEL_NUM_CTX的一半
CONTEXT_FILE = "context/Have_Friends_at_Work.txt" # 自定义教材

 # AI使用的语言
AI_LANGUAGE = "English"
AI_NAME = "Sarah" # AI名字

MODEL_NAME = "gemma2" # AI模型
MODEL_NUM_CTX = 8192


