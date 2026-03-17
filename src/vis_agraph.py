"""
streamlit-agraph 기반 네트워크 시각화
- Streamlit 전용 React 컴포넌트
- 드래그/줌/클릭 인터랙션 지원
"""
import json
import re

import streamlit as st
from streamlit_agraph import Config, Edge, Node
from streamlit_agraph import _agraph

_COLOR_THEMES = {
    "파란색": "#3498db",
    "초록색": "#2ecc71",
    "주황색": "#e67e22",
    "보라색": "#9b59b6",
    "빨간색": "#e74c3c",
    "청록색": "#1abc9c",
    "회색": "#7f8c8d",
}

_NODE_SHAPES = ["dot", "star", "triangle", "triangleDown", "diamond", "hexagon", "square"]

_LAYOUT_OPTIONS = {
    "자동 (barnesHut)": ("barnesHut", False, None),
    "자동 (forceAtlas2)": ("forceAtlas2Based", False, None),
    "자동 (반발력)": ("repulsion", False, None),
    "계층형 ↓ (위→아래)": ("barnesHut", True, "UD"),
    "계층형 ↑ (아래→위)": ("barnesHut", True, "DU"),
    "계층형 → (왼→오)": ("barnesHut", True, "LR"),
    "계층형 ← (오→왼)": ("barnesHut", True, "RL"),
}

_HIGHLIGHT_COLORS = {
    "노란색": "#f1c40f",
    "빨간색": "#e74c3c",
    "주황색": "#e67e22",
    "초록색": "#2ecc71",
    "파란색": "#3498db",
    "보라색": "#9b59b6",
}


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _parse_utterance_count(label: str) -> int:
    """엣지 라벨에서 발언수 숫자를 추출. 예: '발언수: 3' → 3, '' → 1 (연결 존재 자체를 1로)"""
    if not label:
        return 1
    m = re.search(r"(\d+)", label)
    return int(m.group(1)) if m else 1


def _compute_node_stats(nodes_raw: list, edges_raw: list) -> dict[str, dict]:
    """각 노드에 대한 네트워크 통계를 계산."""
    stats: dict[str, dict] = {}
    for n in nodes_raw:
        nid = n["id"]
        stats[nid] = {
            "out_edges": 0,           # 발언한 엣지 수 (start == nid)
            "in_edges": 0,            # 발언 대상이 된 엣지 수 (end == nid)
            "out_utterances": 0,      # 총 발언 수 (라벨에서 파싱)
            "in_utterances": 0,       # 총 수신 발언 수
            "out_targets": [],        # 발언 대상 목록
            "in_sources": [],         # 발언자 목록
            "out_details": [],        # (대상, 발언수) 상세
            "in_details": [],         # (발언자, 발언수) 상세
        }

    for e in edges_raw:
        s, t = e["start"], e["end"]
        label = e.get("properties", {}).get("label", "")
        utt = _parse_utterance_count(label)

        if s in stats:
            stats[s]["out_edges"] += 1
            stats[s]["out_utterances"] += utt
            stats[s]["out_targets"].append(t)
            stats[s]["out_details"].append((t, utt, label))
        if t in stats:
            stats[t]["in_edges"] += 1
            stats[t]["in_utterances"] += utt
            stats[t]["in_sources"].append(s)
            stats[t]["in_details"].append((s, utt, label))

    return stats


def _build_hover_title(nid: str, node_stats: dict) -> str:
    """vis.js 노드 hover 시 표시할 HTML 툴팁 생성."""
    s = node_stats
    degree = s["out_edges"] + s["in_edges"]
    lines = [
        f"📌 {nid}",
        f"──────────────────",
        f"🔗 연결 수: {degree} (발신 {s['out_edges']} / 수신 {s['in_edges']})",
    ]
    if s["out_utterances"]:
        lines.append(f"🗣️ 발언 수: {s['out_utterances']} ({s['out_edges']}명에게)")
    if s["in_utterances"]:
        lines.append(f"👂 수신 발언 수: {s['in_utterances']} ({s['in_edges']}명으로부터)")

    if s["out_targets"]:
        targets = ", ".join(dict.fromkeys(s["out_targets"]))  # 중복 제거, 순서 유지
        lines.append(f"➡️ 발언 대상: {targets}")
    if s["in_sources"]:
        sources = ", ".join(dict.fromkeys(s["in_sources"]))
        lines.append(f"⬅️ 발언자: {sources}")

    return "\n".join(lines)


@st.fragment
def _graph_view(nodes_raw: list, edges_raw: list) -> None:
    """선택 상태 표시 + agraph 렌더링 — 노드 클릭 시 이 fragment만 rerun."""
    # ── session_state에서 옵션값 읽기 ─────────────────────────────────────
    node_color = _COLOR_THEMES[st.session_state.get("agraph_node_color", "파란색")]
    highlight_color = _HIGHLIGHT_COLORS[st.session_state.get("agraph_highlight_color", "노란색")]
    size_scale = st.session_state.get("agraph_size_scale", 1.0)
    node_shape = st.session_state.get("agraph_node_shape", "dot")
    show_hover_title = st.session_state.get("agraph_hover_title", True)
    node_shadow = st.session_state.get("agraph_shadow", True)
    show_edge_labels = st.session_state.get("agraph_edge_labels", True)
    edge_width_scale = st.session_state.get("agraph_edge_width", 1.0)
    smooth_edges = st.session_state.get("agraph_smooth_edges", False)
    show_arrows = st.session_state.get("agraph_arrows", True)
    physics_enabled = st.session_state.get("agraph_physics", True)
    graph_width = st.session_state.get("agraph_width", 750)
    graph_height = st.session_state.get("agraph_height", 600)
    spring_length = st.session_state.get("agraph_spring_length", 200)
    layout_key = st.session_state.get("agraph_layout", "자동 (barnesHut)")
    layout_solver, layout_hierarchical, layout_direction = _LAYOUT_OPTIONS[layout_key]
    dim_opacity = st.session_state.get("agraph_dim_opacity", 0.15)

    # ── 노드 통계 계산 ─────────────────────────────────────────────────────
    node_stats = _compute_node_stats(nodes_raw, edges_raw)

    # ── 선택 상태 표시 (상세 정보 포함) ──────────────────────────────────────
    selected_node = st.session_state.get("agraph_selected_node")
    if selected_node:
        col_info, col_btn = st.columns([5, 1])
        with col_info:
            st.markdown(f"#### 🔍 {selected_node}")
        with col_btn:
            if st.button("✕", key="agraph_deselect", help="선택 해제"):
                st.session_state["agraph_selected_node"] = None
                selected_node = None
                st.rerun(scope="fragment")

    if selected_node and selected_node in node_stats:
        s = node_stats[selected_node]
        degree = s["out_edges"] + s["in_edges"]

        c1, c2, c3 = st.columns(3)
        c1.metric("전체 연결", degree)
        c2.metric("발신 →", s["out_edges"])
        c3.metric("← 수신", s["in_edges"])

        with st.expander("📋 상세 연결 정보", expanded=True):
            detail_col1, detail_col2 = st.columns(2)
            with detail_col1:
                st.markdown("**➡️ 발언 대상 (발신)**")
                if s["out_details"]:
                    for target, utt, label in s["out_details"]:
                        display_label = label if label else "(라벨 없음)"
                        st.markdown(f"- **{target}** — {display_label}")
                else:
                    st.caption("발신 엣지 없음")
            with detail_col2:
                st.markdown("**⬅️ 발언자 (수신)**")
                if s["in_details"]:
                    for source, utt, label in s["in_details"]:
                        display_label = label if label else "(라벨 없음)"
                        st.markdown(f"- **{source}** — {display_label}")
                else:
                    st.caption("수신 엣지 없음")

    # ── 선택 노드 기반 연결 관계 계산 ─────────────────────────────────────
    connected_nodes: set[str] = set()
    connected_edge_indices: set[int] = set()  # 하이라이트용: 선택 노드 직접 연결 엣지
    label_edge_indices: set[int] = set()      # 라벨 표시용: 연결 노드 포함 모든 인접 엣지
    if selected_node:
        for i, e in enumerate(edges_raw):
            if e["start"] == selected_node or e["end"] == selected_node:
                connected_nodes.add(e["start"])
                connected_nodes.add(e["end"])
                connected_edge_indices.add(i)
        connected_nodes.discard(selected_node)

        # 선택 노드 + 연결된 노드 전체를 포함하는 엣지 → 라벨 표시 대상
        relevant_nodes = connected_nodes | {selected_node}
        for i, e in enumerate(edges_raw):
            if e["start"] in relevant_nodes or e["end"] in relevant_nodes:
                label_edge_indices.add(i)

    # ── 노드 구성 ─────────────────────────────────────────────────────────
    def _node_color(n_id: str) -> str:
        if selected_node is None:
            return node_color
        if n_id == selected_node:
            return highlight_color
        if n_id in connected_nodes:
            return node_color
        return _hex_to_rgba(node_color, 0.25)

    nodes = [
        Node(
            id=n["id"],
            label=n.get("properties", {}).get("label", n["id"]),
            size=(node_size := n.get("properties", {}).get("size", 20) * size_scale),
            color=_node_color(n["id"]),
            shape=node_shape,
            title=_build_hover_title(n["id"], node_stats[n["id"]]) if show_hover_title and n["id"] in node_stats else n["id"],
            borderWidth=4 if n["id"] == selected_node else 2,
            shadow=node_shadow,
            font={"size": max(8, int(node_size * 0.45)), "color": "#222222"},
        )
        for n in nodes_raw
    ]

    # ── 양방향 엣지 감지 (분리 표시용) ────────────────────────────────────
    edge_pairs: dict[tuple[str, str], list[int]] = {}
    for i, e in enumerate(edges_raw):
        pair = (e["start"], e["end"])
        edge_pairs.setdefault(pair, []).append(i)

    has_reverse: set[int] = set()  # 반대 방향 엣지가 존재하는 인덱스
    for (s, t), indices in edge_pairs.items():
        if (t, s) in edge_pairs:
            has_reverse.update(indices)

    def _edge_smooth(e: dict) -> dict:
        pair = (e["start"], e["end"])
        reverse_pair = (e["end"], e["start"])
        if reverse_pair in edge_pairs:
            # 양방향 → 방향에 따라 다른 곡선
            if pair < reverse_pair:
                return {"enabled": True, "type": "curvedCW", "roundness": 0.2}
            else:
                return {"enabled": True, "type": "curvedCCW", "roundness": 0.2}
        if smooth_edges:
            return {"enabled": True, "type": "curvedCW", "roundness": 0.2}
        return {"enabled": False}

    # ── 엣지 구성 ─────────────────────────────────────────────────────────
    def _edge_props(idx: int, e: dict) -> tuple[str, float]:
        base_color = e.get("properties", {}).get("color", "#95a5a6")
        base_width = e.get("properties", {}).get("thickness", 1.0) * edge_width_scale
        if selected_node is None:
            return base_color, base_width
        if idx in connected_edge_indices:
            return base_color, max(base_width, 2.0)
        return _hex_to_rgba("#95a5a6", dim_opacity), 0.5

    def _edge_label(idx: int, e: dict) -> str:
        if not show_edge_labels:
            return ""
        if selected_node is not None and idx not in label_edge_indices:
            return ""
        return e.get("properties", {}).get("label", "")

    edges = [
        Edge(
            source=e["start"],
            target=e["end"],
            label=_edge_label(i, e),
            color=_edge_props(i, e)[0],
            width=_edge_props(i, e)[1],
            dashes=e.get("properties", {}).get("style", "solid") == "dashed",
            smooth=_edge_smooth(e),
            arrows={"to": {"enabled": show_arrows, "scaleFactor": 0.8}},
            font={"size": 12, "align": "middle", "background": "rgba(255,255,255,0.85)"},
        )
        for i, e in enumerate(edges_raw)
    ]

    config = Config(
        width=graph_width,
        height=graph_height,
        directed=True,
        physics=physics_enabled and not layout_hierarchical,
        hierarchical=layout_hierarchical,
        direction=layout_direction or "UD",
        sortMethod="directed",
        levelSeparation=spring_length,
    )
    config.physics["solver"] = layout_solver
    config.physics["barnesHut"] = {"springLength": spring_length}
    config.physics["forceAtlas2Based"] = {"springLength": spring_length}
    config.physics["repulsion"] = {"nodeDistance": spring_length}

    nodes_data = [n.to_dict() for n in nodes]
    edges_data = [e.to_dict() for e in edges]
    data_json = json.dumps({"nodes": nodes_data, "edges": edges_data})
    config_json = json.dumps(config.__dict__)
    return_value = _agraph(
        data=data_json,
        config=config_json,
        key=f"agraph_graph_{selected_node}_{spring_length}_{layout_key}",
    )
    if return_value:
        if return_value == st.session_state.get("agraph_selected_node"):
            # 같은 노드 재클릭 → 선택 해제
            st.session_state["agraph_selected_node"] = None
        else:
            st.session_state["agraph_selected_node"] = return_value
        st.rerun(scope="fragment")


@st.fragment
def render(data: dict) -> None:
    nodes_raw = data.get("nodes", [])
    edges_raw = data.get("edges", [])

    # ── 옵션 패널 (옵션 변경 시에만 이 fragment rerun) ────────────────────
    with st.expander("⚙️ 그래프 옵션", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**노드 설정**")
            st.selectbox("노드 모양", options=_NODE_SHAPES, index=0, key="agraph_node_shape")
            st.selectbox("노드 색상", options=list(_COLOR_THEMES.keys()), index=0, key="agraph_node_color")
            st.slider("노드 크기 배율", min_value=0.5, max_value=3.0, value=1.0, step=0.1, key="agraph_size_scale")
            st.checkbox("호버 툴팁 표시", value=True, key="agraph_hover_title")
            st.checkbox("노드 그림자", value=True, key="agraph_shadow")

        with col2:
            st.markdown("**엣지 설정**")
            st.checkbox("엣지 레이블 표시", value=True, key="agraph_edge_labels")
            st.slider("엣지 두께 배율", min_value=0.5, max_value=5.0, value=1.0, step=0.1, key="agraph_edge_width")
            st.checkbox("곡선 엣지", value=False, key="agraph_smooth_edges")
            st.checkbox("화살표 표시", value=True, key="agraph_arrows")

        with col3:
            st.markdown("**레이아웃 설정**")
            st.selectbox(
                "배치 방식",
                options=list(_LAYOUT_OPTIONS.keys()),
                index=0,
                key="agraph_layout",
            )
            st.checkbox("물리 시뮬레이션", value=True, key="agraph_physics")
            st.slider("그래프 너비", min_value=400, max_value=1400, value=750, step=50, key="agraph_width")
            st.slider("그래프 높이", min_value=300, max_value=1000, value=600, step=50, key="agraph_height")
            st.slider("엣지 길이", min_value=50, max_value=500, value=200, step=10, key="agraph_spring_length")

        st.divider()
        st.markdown("**선택 하이라이트 설정**")
        col4, col5 = st.columns(2)
        with col4:
            st.selectbox(
                "하이라이트 색상",
                options=list(_HIGHLIGHT_COLORS.keys()),
                index=0,
                key="agraph_highlight_color",
            )
        with col5:
            st.slider(
                "비연결 요소 투명도",
                min_value=0.05, max_value=0.5, value=0.15, step=0.05,
                key="agraph_dim_opacity",
            )

    st.caption("노드를 클릭하면 연결된 엣지가 강조됩니다. 같은 노드를 다시 클릭하면 선택이 해제됩니다.")

    # ── 그래프 뷰 (노드 클릭 시 이 부분만 rerun) ─────────────────────────
    _graph_view(nodes_raw, edges_raw)
