"""
Bokeh 기반 네트워크 시각화
- NetworkX from_networkx() 통합
- 호버 툴팁, 인터랙티브 선택 지원
- st.bokeh_chart()로 렌더링
"""
import networkx as nx
import streamlit as st
from bokeh.models import (
    Circle,
    ColumnDataSource,
    HoverTool,
    MultiLine,
    NodesAndLinkedEdges,
    Plot,
    Range1d,
    TapTool,
)
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx


_LAYOUTS = {
    "spring": lambda G: nx.spring_layout(G, seed=42),
    "kamada_kawai": nx.kamada_kawai_layout,
    "circular": nx.circular_layout,
    "shell": nx.shell_layout,
}


def _build_graph(data: dict) -> nx.DiGraph:
    G = nx.DiGraph()
    for node in data.get("nodes", []):
        props = node.get("properties", {})
        G.add_node(
            node["id"],
            label=props.get("label", node["id"]),
            size=props.get("size", 20),
        )
    for edge in data.get("edges", []):
        props = edge.get("properties", {})
        G.add_edge(
            edge["start"],
            edge["end"],
            edge_label=props.get("label", ""),
            color=props.get("color", "#95a5a6"),
            thickness=props.get("thickness", 1.0),
        )
    return G


def render(data: dict) -> None:
    layout_name = st.selectbox("레이아웃", list(_LAYOUTS.keys()), key="bokeh_layout")

    G = _build_graph(data)
    layout_fn = _LAYOUTS[layout_name]

    plot = Plot(
        width=800, height=600,
        x_range=Range1d(-1.5, 1.5),
        y_range=Range1d(-1.5, 1.5),
        background_fill_color="#1a1a2e",
        border_fill_color="#1a1a2e",
    )

    graph_renderer = from_networkx(G, layout_fn, scale=1, center=(0, 0))

    # 노드 스타일
    node_sizes = [G.nodes[n].get("size", 20) for n in G.nodes()]
    graph_renderer.node_renderer.data_source.data["size"] = node_sizes
    graph_renderer.node_renderer.data_source.data["label"] = [
        G.nodes[n].get("label", n) for n in G.nodes()
    ]
    graph_renderer.node_renderer.glyph = Circle(
        size="size",
        fill_color="#3498db",
        line_color="#1a252f",
        line_width=2,
    )
    graph_renderer.node_renderer.selection_glyph = Circle(
        size="size", fill_color=Spectral4[2]
    )
    graph_renderer.node_renderer.hover_glyph = Circle(
        size="size", fill_color=Spectral4[1]
    )

    # 엣지 스타일
    edge_colors = [G.edges[e].get("color", "#95a5a6") for e in G.edges()]
    edge_widths = [max(G.edges[e].get("thickness", 1.0), 0.5) for e in G.edges()]
    graph_renderer.edge_renderer.data_source.data["color"] = edge_colors
    graph_renderer.edge_renderer.data_source.data["line_width"] = edge_widths
    graph_renderer.edge_renderer.glyph = MultiLine(
        line_color="color", line_width="line_width", line_alpha=0.8
    )
    graph_renderer.edge_renderer.selection_glyph = MultiLine(
        line_color=Spectral4[2], line_width=3
    )

    graph_renderer.inspection_policy = NodesAndLinkedEdges()
    graph_renderer.selection_policy = NodesAndLinkedEdges()

    plot.renderers.append(graph_renderer)
    plot.add_tools(
        HoverTool(tooltips=[("노드", "@label"), ("크기", "@size")]),
        TapTool(),
    )

    st.bokeh_chart(plot, use_container_width=True)
