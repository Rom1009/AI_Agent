from src.module.model import DigestRequest, DigestResponse
from fastapi import FastAPI
import uvicorn



app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "FastAPI is running for n8n & MCP"}

@app.post("/process-data")
def process_data(data: dict):
    # Logic xử lý dữ liệu của bạn ở đây (ví dụ: lấy kết quả model)
    result = {"message": "Data processed", "content": "Dữ liệu đã sẵn sàng để gửi mail"}
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)