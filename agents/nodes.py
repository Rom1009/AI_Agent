from langchain_ollama import ChatOllama
from .state import AgentState

model = ChatOllama(model="qwen2.5:7b", base_url="http://ollama:11434")

def fetch_news_node(state: AgentState):
    print("Fetching news...: ", state["topic"])
    fake_news = [
        f"Tin AI 1: OpenAI ra mắt model mới cho {state['topic']}",
        f"Tin Kinh tế 2: Thị trường {state['topic']} đang biến động mạnh"
    ]

    return fake_news

def summarize_node(state: AgentState):
    print("--- AI đang tóm tắt dữ liệu ---")
    combined_news = "\n".join(state['news_list'])
    prompt = f"Hãy tóm tắt các tin sau về {state['topic']} ngắn gọn, súc tích:\n{combined_news}"
    
    response = model.invoke(prompt)
    return {"final_summary": response.content}