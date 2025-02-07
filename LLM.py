import ollama
from outlines.models import openai
import outlines
from pydantic import BaseModel
from langchain_openai import ChatOpenAI


class MyLLM:
    def __init__(self):
        #self.model_name = model_name
        pass

    @staticmethod
    def chat(model, messages, options={}, keep_alive=300, temperature=0.9, use_openai=False, base_url='https://api.openai.com/v1'):
        """
        流式对话接口
        """  
        if use_openai == False:
            stream = ollama.chat(
                model=model,
                messages=messages,
                stream=True,
                options=options,
                keep_alive=keep_alive
            )

            return MyLLM.stream_generator(stream)
        else:
            chat = ChatOpenAI(model=model, streaming=True, base_url=base_url,temperature=temperature)
            return chat.stream(messages)


    @staticmethod
    def stream_generator(stream):
        for chunk in stream:
            token = chunk['message']['content']
            # 替换所有的星号
            token = token.replace('*', ' ')
            yield token

    @staticmethod
    def chat_sync(model, messages, options={},format=None, use_openai=False, keep_alive=300, temperature=0.9, base_url='https://api.openai.com/v1'):
        """
        非流式对话接口
        """ 

        # 使用Ollama的非流式接口
        response = ollama.chat(
                model=model,
                messages=messages,
                stream=False,
                options=options,
                format=format, # json格式
                keep_alive=keep_alive
            )
        return response
