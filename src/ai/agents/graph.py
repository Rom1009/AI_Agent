from langgraph.graph import StateGraph, END, START
from src.ai.agents.state import DigestState
from src.ai.agents.nodes import load_config, load_profile, generate_queries, web_search, filter_docs, summarize_with_llm, format_email, send_email

def build_graph():
    builder = StateGraph(DigestState)

    builder.add_node("load_config", load_config)
    builder.add_node("load_profile", load_profile)
    builder.add_node("generate_queries", generate_queries)
    builder.add_node("web_search", web_search)
    builder.add_node("filter_docs", filter_docs)
    builder.add_node("summarize_with_llm", summarize_with_llm)
    builder.add_node("format_email", format_email)
    builder.add_node("send_email", send_email)


    builder.add_edge(START, "load_config")
    builder.add_edge("load_config", "load_profile")
    builder.add_edge("load_profile", "generate_queries")
    builder.add_edge("generate_queries", "web_search")
    builder.add_edge("web_search", "filter_docs")
    builder.add_edge("filter_docs", "summarize_with_llm")


    builder.add_edge("summarize_with_llm", "format_email")
    builder.add_edge("format_email", "send_email")
    builder.add_edge("send_email", END)

    return builder.compile()