import asyncio
from typing import AsyncGenerator
from src.utils.config import settings
from langchain_groq.chat_models import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from ddgs import DDGS

class AIService:

    def __init__(self):
        self.llm = ChatGroq(model = settings.MODEL_NAME, api_key = settings.GROQ_API_KEY, max_tokens=1000)
        self.search_tool = DDGS()

        self.chain = self.llm | StrOutputParser()

    # async def generate_chat_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        
    #     # response = self.llm.invoke(prompt)

    #     # full_response = f"Answer: {response}"
    #     # tokens = full_response.split()

    #     # for token in tokens:
    #     #     await asyncio.sleep(0.2)
    #     #     yield f"data: {token} \n \n"

    #     async for chunk in self.chain.astream(prompt):
    #         await asyncio.sleep(0.1)  # Giả lập độ trễ để thấy hiệu ứng streaming
    #         yield f"data: {chunk}"

    async def generate_chat_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        
        # response = self.llm.invoke(prompt)

        search_results = self.search_tool.search(prompt, max_results=3)
        

        # full_response = f"Answer: {response}"
        # tokens = full_response.split()

        # for token in tokens:
        #     await asyncio.sleep(0.2)
        #     yield f"data: {token} \n \n"

        async for chunk in self.chain.astream(prompt):
            await asyncio.sleep(0.1)  # Giả lập độ trễ để thấy hiệu ứng streaming
            yield f"data: {chunk}"