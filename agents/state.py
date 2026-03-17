from typing import Annotated, TypedDict, List

class AgentState(TypedDict):
    new_list: List[str]
    final_summary: str
    topic: str

