import sys
import json
from agents.graph import create_graph

def run_agent(user_topic):
    app = create_graph()
    
    # Chạy Agent
    initial_state = {"topic": user_topic, "news_list": []}
    result = app.invoke(initial_state)
    
    # Trả về kết quả dạng JSON để n8n đọc
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    # Lấy chủ đề từ tham số dòng lệnh (n8n truyền vào)
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    else:
        topic = "AI News"
    run_agent(topic)