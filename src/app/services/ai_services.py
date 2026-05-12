import asyncio
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import AsyncGenerator

from langchain_groq.chat_models import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from ddgs import DDGS # Đảm bảo bạn đã cài duckduckgo-search
from src.utils.config import settings

class AIService:
    def __init__(self):
        # 1. Khởi tạo LLM
        self.llm = ChatGroq(
            model=settings.MODEL_NAME,
            api_key=settings.GROQ_API_KEY,
            max_tokens=1000,
            temperature=0,
        )

        # 2. Chains - Tách biệt logic Prompt
        self.rewrite_query_chain = (
            ChatPromptTemplate.from_messages([
                ("system", "Rewrite the user's question into a short, effective web search query in English or Vietnamese. Return ONLY the query text."),
                ("human", "{prompt}")
            ]) | self.llm | StrOutputParser()
        )

        self.web_chain = (
            ChatPromptTemplate.from_messages([
                ("system", """Bạn là trợ lý AI có quyền truy cập internet. 
Hãy trả lời câu hỏi dựa TRỰC TIẾP vào kết quả tìm kiếm dưới đây.
- Nếu không thấy câu trả lời, hãy nói: "Tôi không tìm thấy thông tin cụ thể cho vấn đề này."
- Trích dẫn nguồn dạng [Source 1], [Source 2].
- Ngôn ngữ: Tiếng Việt.

Kết quả tìm kiếm:
{web_results}"""),
                ("human", "{prompt}")
            ]) | self.llm | StrOutputParser()
        )

    def _get_current_time_vn(self) -> str:
        now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
        return now.strftime("Hôm nay là ngày %d/%m/%Y. Bây giờ là %H:%M.")

    async def search_web(self, query: str) -> str:
        """Thực hiện search an toàn hơn"""
        def _sync_search():
            try:
                with DDGS() as ddgs:
                    # Thêm region='vi-vnm' nếu muốn ưu tiên kết quả VN
                    results = list(ddgs.text(query, max_results=5))
                    if not results: return ""
                    
                    return "\n\n".join([
                        f"[Source {i+1}]\nTitle: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}"
                        for i, r in enumerate(results)
                    ])
            except Exception as e:
                return f"ERROR: {e}"

        return await asyncio.to_thread(_sync_search)

    async def generate_response(self, prompt: str) -> AsyncGenerator[str, None]:
        # Phân loại logic đơn giản
        prompt_lower = prompt.lower()
        
        # 1. Trả lời thời gian (Hardcoded cho nhanh và chính xác)
        if any(x in prompt_lower for x in ["mấy giờ", "ngày bao nhiêu", "hôm nay là ngày"]):
            yield f"data: {self._get_current_time_vn()}\n\n"
            return

        # 2. Xử lý Search nếu cần thông tin thực tế
        # (Tạm thời giữ logic cũ của bạn, nhưng nên nâng cấp lên AI Router sau này)
        if self.must_search(prompt):
            query = await self.rewrite_query_chain.ainvoke({"prompt": prompt})
            web_results = await self.search_web(query.strip())

            if not web_results or "ERROR" in web_results:
                yield "data: Xin lỗi, mình gặp lỗi khi tìm kiếm thông tin mới nhất.\n\n"
                return

            async for chunk in self.web_chain.astream({"prompt": prompt, "web_results": web_results}):
                yield f"data: {chunk}\n\n"
        
        # 3. Trả lời bình thường
        else:
            normal_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant. Answer in Vietnamese."),
                ("human", "{prompt}")
            ])
            chain = normal_prompt | self.llm | StrOutputParser()
            
            async for chunk in chain.astream({"prompt": prompt}):
                await asyncio.sleep(0.1)  # Giả lập delay để có trải nghiệm streaming tốt hơn
                yield f"data: {chunk}\n\n"

    def must_search(self, prompt: str) -> bool:
        # Giữ nguyên list keywords của bạn nhưng có thể bổ sung thêm
        keywords = ["giá", "thời tiết", "tin tức", "mới nhất", "ai là", "tổng thống", "thắng", "vừa mới"]
        return any(k in prompt.lower() for k in keywords)