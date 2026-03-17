"""
streamlit-agraph 기반 네트워크 시각화
- Streamlit 전용 React 컴포넌트
- 드래그/줌/클릭 인터랙션 지원
"""
import streamlit as st
from streamlit_agraph import agraph, Config, Edge, Node


def render(data: dict) -> None:
    nodes_raw = data.get("nodes", [])
    edges_raw = data.get("edges", [])

    nodes = [
        Node(
            id=n["id"],
            label=n.get("properties", {}).get("label", n["id"]),
            size=n.get("properties", {}).get("size", 20),
            color="#3498db",
        )
        for n in nodes_raw
    ]

    edges = [
        Edge(
            source=e["start"],
            target=e["end"],
            label=e.get("properties", {}).get("label", ""),
            color=e.get("properties", {}).get("color", "#95a5a6"),
        )
        for e in edges_raw
    ]

    config = Config(
        width=750,
        height=600,
        directed=True,
        physics=True,
        hierarchical=False,
    )

    return_value = agraph(nodes=nodes, edges=edges, config=config)
    if return_value:
        st.info(f"선택된 노드: **{return_value}**")
