"""
Plotly 기반 네트워크 시각화
- NetworkX 레이아웃 + Plotly Scatter 렌더링
- st.plotly_chart()로 네이티브 통합
"""
import networkx as nx
import plotly.graph_objects as go
import streamlit as st


_LAYOUTS = {
    "spring": nx.spring_layout,
    "kamada_kawai": nx.kamada_kawai_layout,
    "circular": nx.circular_layout,
    "shell": nx.shell_layout,
    "spectral": nx.spectral_layout,
}


def _build_graph(data: dict) -> nx.DiGraph:
    G = nx.DiGraph()
    for node in data.get("nodes", []):
        G.add_node(node["id"], **node.get("properties", {}))
    for edge in data.get("edges", []):
        G.add_edge(edge["start"], edge["end"], **edge.get("properties", {}))
    return G


def render(data: dict) -> None:
    layout_name = st.selectbox(
        "레이아웃 선택",
        list(_LAYOUTS.keys()),
        key="plotly_layout",
    )
    layout_fn = _LAYOUTS[layout_name]

    G = _build_graph(data)
    pos = layout_fn(G, seed=42) if layout_name == "spring" else layout_fn(G)

    fig = go.Figure()

    # 엣지 traces (두께/색상 개별 적용)
    for edge in data.get("edges", []):
        x0, y0 = pos[edge["start"]]
        x1, y1 = pos[edge["end"]]
        props = edge.get("properties", {})
        color = props.get("color", "#95a5a6")
        thickness = props.get("thickness", 1.0)
        label = props.get("label", "")

        fig.add_trace(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode="lines",
            line=dict(width=max(thickness, 0.5), color=color),
            hoverinfo="text",
            text=label or f"{edge['start']} → {edge['end']}",
            showlegend=False,
        ))

    # 노드 trace
    node_x, node_y, node_text, node_hover, node_sizes = [], [], [], [], []
    for node in data.get("nodes", []):
        x, y = pos[node["id"]]
        props = node.get("properties", {})
        node_x.append(x)
        node_y.append(y)
        node_text.append(props.get("label", node["id"]))
        node_hover.append(f"<b>{props.get('label', node['id'])}</b><br>Size: {props.get('size', 20)}")
        node_sizes.append(props.get("size", 20))

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        marker=dict(
            size=node_sizes,
            color="#3498db",
            line=dict(width=2, color="#1a252f"),
        ),
        text=node_text,
        textposition="top center",
        hovertext=node_hover,
        hoverinfo="text",
        showlegend=False,
    ))

    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="#1a1a2e",
        paper_bgcolor="#1a1a2e",
        font=dict(color="#ffffff"),
        margin=dict(l=20, r=20, t=20, b=20),
        height=600,
    )

    st.plotly_chart(fig, use_container_width=True)
