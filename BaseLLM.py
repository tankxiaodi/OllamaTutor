import ollama
import os
from langchain_openai import ChatOpenAI


class BaseLLM:
    def __init__(self):
        pass

    @staticmethod
    def chat(model, prompt, options, keep_alive):
        stream = ollama.generate(
            model=model,
            prompt=prompt,
            stream=True,
            options=options,
            keep_alive=keep_alive,
        )

        for chunk in stream:
            yield chunk['response']

    @staticmethod
    def get_response(model, prompt, options, keep_alive=300):
        response = ""
        for chunk in BaseLLM.chat(model, prompt, options, keep_alive=keep_alive):
            response += chunk
            if "Cloud:" in response:
                break
        return response.split("Cloud:")[0].rstrip() # 只保留用户名左边的部分，删除右边缘换行符号等
    
    