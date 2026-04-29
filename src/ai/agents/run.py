from src.ai.agents.graph import build_graph
from src.utils.utils import save_file
from src.utils.config import settings


if __name__ == "__main__":

    graph = build_graph()
    img = graph.get_graph(xray= True).draw_mermaid_png()
    save_file(settings.IMG_PATH, img)

    result = graph.invoke({})