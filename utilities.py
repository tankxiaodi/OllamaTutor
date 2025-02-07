
import re
import os
import json
from datetime import datetime
from datetime import datetime
from LLM import MyLLM
from pydantic import BaseModel
import outlines

from urllib.parse import unquote
from constants import *
from prompt.summary_prompt import *

# 对话总结模版
class ConverastionSummary(BaseModel):
    conversion_datetime: str
    conversion_summary: str

# 对话关键信息模版
class keyInfomation(BaseModel):
    role: str
    key_information: str


def generate_sys_prompt():
    # 构建context.txt的完整路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    context_file = unquote(os.getenv('CONTEXT_FILE'))
    context_path = os.path.join(script_dir, context_file)
    with open(context_path, "r", encoding="utf-8") as f:
        context = f.read()

    # 获取并处理对话历史
    summary_dir = os.path.join(script_dir, "conversation_summary")
    summary_files = [f for f in os.listdir(summary_dir) if f.endswith(".json")]
    
    # 按时间戳排序(从旧到新)
    summary_files.sort(key=lambda x: datetime.strptime(x[:-5], "%Y-%m-%d_%H:%M:%S"), reverse=False)
    
    # 读取并合并内容
    conversation_history = []
    for filename in summary_files:
        with open(os.path.join(summary_dir, filename), "r", encoding="utf-8") as f:
            content = f.read()
            conversation_history.append(content)
    
    # 填充内容
    sys_prompt_file = os.getenv('SYS_PROMPT')
    sys_prompt_path = os.path.join(script_dir, sys_prompt_file)
    with open(sys_prompt_path, "r", encoding="utf-8") as f:
        sys_prompt = f.read()
    prompt = sys_prompt.replace("{AI_NAME}", AI_NAME)
    prompt = prompt.replace("{AI_LANGUAGE}", AI_LANGUAGE)
    prompt = prompt.replace("{ARTICLE}", context)
    prompt = prompt.replace("{CONVERSATION_HISTORY}", "\n".join(conversation_history))

    return prompt.strip()

def check_end_of_speech(text):
    # 检查是否以 "that's it" 后跟标点符号结尾，不区分大小写
    pattern = r"that's it[.!?]\s*$"
    if re.search(pattern, text, re.IGNORECASE):
        return True
    return False

def extract_content_rsplit(text):
    # 移除首尾空白字符
    text = text.strip()
    
    # 使用正则表达式，不区分大小写，匹配 "that's it" 后跟任意标点符号
    pattern = r"(.*?)(?:that's it[.!?])\s*$"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    # 如果没有找到匹配，返回原始文本
    return text

def save_conversation_history(transcript, base_dir="conversation_history"):
    """
    保存对话记录到指定目录
    """
    
    # 创建保存目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_dir = os.path.join(script_dir, base_dir)
    os.makedirs(history_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    filename = f"{timestamp}.json"
    filepath = os.path.join(history_dir, filename)
    
    # 保存对话记录，如果文件已存在会自动覆盖
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)
    
    return filepath

def generate_conversation_summary(transcript , ai_name):
    """使用LLM生成对话总结"""
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 格式化用户提示语
    user_prompt = USER_PROMPT_TEMPLATE.format(
        current_time=current_time,
        assistant=ai_name,
        conversation_history=json.dumps(transcript, indent=2)
    )
    # 调用LLM生成总结
    summary = MyLLM.chat_sync(
        model=os.getenv('SUMMARY_MODEL_NAME'),
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        format=ConverastionSummary.model_json_schema(), # 要求使用JSON格式化输出
        use_openai=os.getenv('OPENAI') == 'True', base_url=os.getenv('BASE_URL')
    )
    
    summary = json.loads(summary['message']['content'])
    return summary 

def generate_character_key_info(transcript , role_name, ai_name):
    """使用LLM生角色关键信息"""
    # 格式化用户提示语
    user_prompt = KEY_INFO_EXTRACT_TEMPLATE.format(
        assistant=ai_name,
        role=role_name,
        conversation_history=transcript
    )


    # 调用LLM生成总结
    key_info = MyLLM.chat_sync(
        model=os.getenv('SUMMARY_MODEL_NAME'),
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        format=keyInfomation.model_json_schema(), # 要求使用JSON格式化输出
        use_openai=(os.getenv('OPENAI') == 'True')
    )

    # 只返回有价值的信息
    if "No key information found" in key_info:
        return None
    else:
        return json.loads(key_info['message']['content']) 
   

def format_transcript(transcript):
    """
    将对话记录转换为易读格式
    """
    formatted = []
    for msg in transcript:
        if msg["role"] == "user":
            formatted.append(f"user: {msg['content']}")
        elif msg["role"] == "assistant":
            formatted.append(f"{AI_NAME}: {msg['content']}") # 把 assistant换成AI名字
    return formatted

def save_conversation_summary(summary, base_dir="conversation_summary"):
    """
    保存对话总结到指定目录
    """
    from datetime import datetime
    
    # 创建保存目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    summary_dir = os.path.join(script_dir, base_dir)
    os.makedirs(summary_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    filename = f"{timestamp}.json"
    filepath = os.path.join(summary_dir, filename)
    
    # 保存总结
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    return filepath
