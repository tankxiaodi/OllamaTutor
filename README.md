# OllamaTutor

OllamaTutor 是一个 AI 语言学习助手，采用 Ollama 支持的大型语言模型（LLM），通过实时语音对话帮助用户提高多种语言的口语能力。
特别是针对特定教程，特定主题的对话训练。

## 主要特性

- 实时与 LLM 进行语音口语训练
- 可根据自定义教材，自定义主题进行训练，比如"介绍自己的职业”
- 可定制 LLM 性格和语气，语言习惯等...
- 支持本地部署的Ollama 开源LLM模型，如 Llama3、Gemma2 等...充分保护数据隐私
- 集成多种文本转语音（TTS）技术

## 安装说明

1. 克隆仓库：
   ```
   git clone https://github.com/tankxiaodi/OllamaTutor.git
   ```

2. 创建并激活 Python 虚拟环境（可选，推荐）：
   ```
   python3 -m venv --system-site-packages ./venv
   source venv/bin/activate
   ```

3. 安装依赖项：
   ```
   pip install -r requirements.txt
   ```
   
   如果是macOS的话，还需要安装：
   ```
   brew install portaudio
   brew install mpv
   ```

   如果是Debian/Ubuntu：
   ```
   apt install portaudio19-dev
   ```

4. 获取并配置API 密钥：
   - AssemblyAI 的 API 密钥（必需，100小时免费额度）
   https://www.assemblyai.com/dashboard/signup

   - Google Cloud Text-to-Speech 的凭证（可选，强烈推荐，TTS语音效果好）
   https://cloud.google.com/speech-to-text
   
   - Azure Text-to-Speech 的订阅密钥（可选）


5. 在项目根目录下创建 `.env` 文件，安装如下格式，填写上述 API 密钥和凭证信息。

   ```
    # 使用的tts, 填 Google 或 Edge , Azure
    # Google 语音最自然, 但需要配置CREDENTIAL
    TTS_API=Edge

    ASSEMBLYAI_API_KEY=your_ASSEMBLYAI_API_KEY  (必填)

    GOOGLE_APPLICATION_CREDENTIALS=your_CREDENTIALS_json_file_path (可选)

    AZURE_SUBSCRIPTION_KEY=your_AZURE_SUBSCRIPTION_KEY (可选)
    AZURE_REGION=your_AZURE_REGION (可选)

    CONTEXT_FILE=context/Have_Friends_at_Work.txt

    # AI模型参数
    MODEL_NAME=gemma2
    MODEL_NUM_CTX=8192
    ```

6. 安装 Ollama 并下载所需的模型：
    https://ollama.com/
   ```
   ollama run gemma2
   ```

## 使用方法

先运行Ollama。

然后再运行 `python3 main.py` 。如果一切配置正确，程序会初始化， LLM 并开始说第一句话。
用户在听到提示音后可通过麦克风与 LLM 进行交流。用户一轮对话结束时，请明确说出结束语 "That's it"。

说出"That's it"非常重要，否则LLM会一直等待...

在对话中，LLM 将根据用户提供的教材内容进行教学，帮助用户练习语言。

如果发现LLM的对话不够专业，或是不够准确，请考虑使用更加清晰，明确的教材，或使用更高性能的LLM。

## 自定义教材

推荐使用 Engoo Daily News 或 BBC Learning English 等资源作为教材。

例如:
https://www.bbc.co.uk/learningenglish/english/features/6-minute-english

https://engoo.com/app/materials/en

用户需拷贝文章的文字内容保存至 `context` 目录下的文本文件中，并在 `constants.py` 文件中更新 `CONTEXT_FILE` 变量指向该文件。
LLM即可使用该文件为教材。

## 配置

编辑.env环境变量可以调整常用的参数， 而编辑 `constants.py` 文件可以定义高级参数。例如：
```
 # AI使用的语言
AI_LANGUAGE = "English"
AI_NAME = "Sarah" # AI名字

```

如果需要，也可以使用OpenAI的模型代替Ollama。在环境变量中加入OPENAI=True，并且设定OPENAI_API_KEY即可。

## 运行环境

代码已在 macOS 环境下测试通过。

我的开发环境是: Macbook Pro 2019 M1 Max 64GB和gemma2:27b模型。

理论上也支持 Windows和Debian/Ubuntu。

## 如何贡献

欢迎任何形式的贡献！请遵循标准的 GitHub 流程来提交您的贡献。

## 许可证

本项目遵循 MIT 许可证发布。有关更多信息，请查看 LICENSE 文件。

## 联系方式

有问题或建议，请通过以下方式联系我们：
- 项目问题跟踪：GitHub Issues