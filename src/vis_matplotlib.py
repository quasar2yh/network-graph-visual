"""
NetworkX + Matplotlib 기반 네트워크 시각화
- 정적 렌더링, 다양한 레이아웃/스타일 지원
- st.pyplot()으로 렌더링
"""
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

matplotlib.rcParams["font.family"] = ["Malgun Gothic", "AppleGothic", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False


_LAYOUTS = {
    "spring": lambda G: nx.spring_layout(G, seed=42),
    "kamada_kawai": nx.kamada_kawai_layout,
    "circular": nx.circular_layout,
    "shell": nx.shell_layout,
    "planar": nx.planar_layout,
}


def _build_graph(data: dict) -> nx.DiGraph:
    G = nx.DiGraph()
    for node in data.get("nodes", []):
        G.add_node(node["id"], **node.get("properties", {}))
    for edge in data.get("edges", []):
        G.add_edge(edge["start"], edge["end"], **edge.get("properties", {}))
    return G


def render(data: dict) -> None:
    col1, col2 = st.columns(2)
    with col1:
        layout_name = st.selectbox("레이아웃", list(_LAYOUTS.keys()), key="mpl_layout")
    with col2:
        show_edge_labels = st.checkbox("엣지 레이블 표시", value=True, key="mpl_edge_labels")

    G = _build_graph(data)
    pos = _LAYOUTS[layout_name](G)

    # 노드 속성 추출
    node_sizes = [G.nodes[n].get("size", 20) * 30 for n in G.nodes()]
    node_labels = {n: G.nodes[n].get("label", n) for n in G.nodes()}

    # 엣지 속성 추출
    edge_colors = [G.edges[e].get("color", "#95a5a6") for e in G.edges()]
    edge_widths = [max(G.edges[e].get("thickness", 1.0), 0.5) for e in G.edges()]
    edge_labels = {
        (e[0], e[1]): G.edges[e].get("label", "")
        for e in G.edges()
        if G.edges[e].get("label")
    } if show_edge_labels else {}

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_facecolor("#1a1a2e")
    fig.patch.set_facecolor("#1a1a2e")

    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color="#3498db", ax=ax)
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_color="#ffffff", font_size=10, ax=ax)
    nx.draw_networkx_edges(
        G, pos,
        edge_color=edge_colors,
        width=edge_widths,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=15,
        connectionstyle="arc3,rad=0.1",
        ax=ax,
    )
    if edge_labels:
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels,
            font_color="#ecf0f1", font_size=8, ax=ax,
        )

    ax.axis("off")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
