import streamlit as st
import httpx
import asyncio

# --- Cấu hình trang ---
st.set_page_config(page_title="AI Agent Chat", page_icon="🤖")
st.title("🤖 AI Agent Streaming Demo")

# --- Khởi tạo lịch sử chat trong session_state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Hiển thị lịch sử chat từ session_state ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Hàm gọi API Streaming từ FastAPI ---
async def get_streaming_response(prompt):
    full_response = ""
    # Cần dùng timeout=None vì các tác vụ AI có thể chạy lâu
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            # URL trỏ tới endpoint FastAPI của bạn
            async with client.stream("GET", "http://localhost:8000/api/ai/generate", params={"prompt": prompt}) as response:
                if response.status_code != 200:
                    st.error(f"Lỗi hệ thống: {response.status_code}")
                    return

                # Đọc từng chunk từ stream
                async for chunk in response.aiter_text():
                    # Xử lý format "data: content\n\n"
                    if chunk.startswith("data: "):
                        # Tách lấy phần nội dung thực sự sau chữ "data: "
                        content = chunk.replace("data: ", "").replace("\n\n", "")
                        full_response += content
                        # Trả về từng đoạn chữ để hiển thị ngay lập tức
                        yield full_response
        except Exception as e:
            st.error(f"Không thể kết nối tới Backend: {e}")

# --- Khu vực nhập liệu của người dùng ---
if prompt := st.chat_input("Bạn muốn hỏi gì?"):
    
    # 1. Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Hiển thị khu vực phản hồi của AI
    with st.chat_message("assistant"):
        placeholder = st.empty()  # Nơi để cập nhật chữ chạy
        
        # Chạy hàm async để lấy dữ liệu
        async def run_chat():
            final_text = ""
            async for current_text in get_streaming_response(prompt):
                final_text = current_text
                # Thêm ký tự ▌ để tạo hiệu ứng con trỏ đang soạn thảo
                placeholder.markdown(current_text + "▌")
            
            # Sau khi xong, hiển thị văn bản cuối cùng không có con trỏ
            placeholder.markdown(final_text)
            return final_text

        # Thực thi xử lý async trong môi trường đồng bộ của Streamlit
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ai_response = loop.run_until_complete(run_chat())

    # 3. Lưu phản hồi của AI vào lịch sử chat
    st.session_state.messages.append({"role": "assistant", "content": ai_response})