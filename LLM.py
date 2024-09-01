import ollama
import os
from langchain_openai import ChatOpenAI


class MyLLM:
    def __init__(self):
        #self.model_name = model_name
        pass

    @staticmethod
    def chat(model, messages, options=None, keep_alive=300, use_openai=False):
        if options is None:
            options = {}
            
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
            chat = ChatOpenAI(model=model, streaming=True)
            return chat.stream(messages)


    @staticmethod
    def stream_generator(stream):
        for chunk in stream:
            token = chunk['message']['content']
            # 替换所有的星号
            token = token.replace('*', ' ')
            yield token
    
    