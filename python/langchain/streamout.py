from langchain_community.llms import Ollama
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

llm = Ollama(
    model="qwen3:14b",
    callbacks=[StreamingStdOutCallbackHandler()],  # 启用流式回调
)

llm.invoke("解释牛顿三大定律")