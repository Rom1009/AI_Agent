from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import fetch_news_node, summarize_node

def create_graph():
    # 1. Khởi tạo Graph với trạng thái đã định nghĩa
    workflow = StateGraph(AgentState)

    # 2. Thêm các bước (Nodes)
    workflow.add_node("fetcher", fetch_news_node)
    workflow.add_node("summarizer", summarize_node)

    # 3. Thiết lập đường đi (Edges)
    workflow.set_entry_point("fetcher") # Bắt đầu ở node fetcher
    workflow.add_edge("fetcher", "summarizer") # Xong fetcher thì sang summarizer
    workflow.add_edge("summarizer", END) # Xong summarizer thì kết thúc

    return workflow.compile()