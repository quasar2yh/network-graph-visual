"""
PyVis 기반 네트워크 시각화
- vis.js 래퍼, 물리 시뮬레이션 기반 인터랙티브 레이아웃
- st.components.v1.html()로 렌더링
"""
import streamlit.components.v1 as components
from pyvis.network import Network


def render(data: dict) -> None:
    net = Network(
        height="620px",
        width="100%",
        bgcolor="#1a1a2e",
        font_color="#ffffff",
        directed=True,
    )

    for node in data.get("nodes", []):
        props = node.get("properties", {})
        net.add_node(
            node["id"],
            label=props.get("label", node["id"]),
            size=props.get("size", 20),
            title=f"ID: {node['id']}<br>Size: {props.get('size', 20)}",
        )

    for edge in data.get("edges", []):
        props = edge.get("properties", {})
        thickness = props.get("thickness", 1.0)
        color = props.get("color", "#95a5a6")
        label = props.get("label", "")
        net.add_edge(
            edge["start"],
            edge["end"],
            label=label,
            color=color,
            width=thickness,
            title=label if label else f"{edge['start']} → {edge['end']}",
            arrows="to",
        )

    net.set_options("""
    {
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -8000,
          "springConstant": 0.04,
          "springLength": 150
        }
      },
      "edges": {
        "smooth": {
          "type": "curvedCW",
          "roundness": 0.2
        }
      },
      "nodes": {
        "font": { "size": 14 }
      }
    }
    """)

    html = net.generate_html()
    components.html(html, height=640)
