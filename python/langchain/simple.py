from langchain_community.llms import Ollama

# 初始化 Ollama 模型
llm = Ollama(
    model="qwen3:14b",  # 模型名称（与 ollama pull 下载的名称一致）
    base_url="http://localhost:11434",  # Ollama 服务地址
    temperature=0.7,  # 控制生成随机性（0-1）
)

# 调用模型生成文本
response = llm.invoke("北京在哪个国家")
print(response)