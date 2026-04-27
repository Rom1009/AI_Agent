from agents.graph import build_graph
from utils.utils import save_file



if __name__ == "__main__":

    graph = build_graph()
    img = graph.get_graph(xray= True).draw_mermaid_png()
    save_file("public/graph.png", img)

    result = graph.invoke({})