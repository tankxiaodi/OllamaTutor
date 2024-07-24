
import re
import os
from constants import *


def generate_sys_prompt():
    # 构建context.txt的完整路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    context_file = os.getenv('CONTEXT_FILE')
    context_path = os.path.join(script_dir, context_file)
    with open(context_path, "r", encoding="utf-8") as f:
        context = f.read()

    # 填充内容
    sys_prompt_file = os.getenv('SYS_PROMPT')
    sys_prompt_path = os.path.join(script_dir, sys_prompt_file)
    with open(sys_prompt_path, "r", encoding="utf-8") as f:
        sys_prompt = f.read()
    prompt = sys_prompt.replace("{AI_NAME}", AI_NAME)
    prompt = prompt.replace("{AI_LANGUAGE}", AI_LANGUAGE)
    prompt = prompt.replace("{CONTEXT}", context)

    return prompt

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