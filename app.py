import json
from pathlib import Path

import streamlit as st

from src.data_loader import load_graph_data

st.set_page_config(
    page_title="Graph Visualizer",
    page_icon="🕸️",
    layout="wide",
)

st.title("🕸️ Network Graph Visualizer")
st.markdown("네트워크 데이터를 다양한 라이브러리로 시각화합니다.")

# ── 사이드바: 데이터 로드 ──────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 데이터")
    uploaded = st.file_uploader("JSON 파일 업로드", type=["json"])

    if uploaded:
        data = json.loads(uploaded.read().decode("utf-8"))
        st.success(f"업로드 완료: {uploaded.name}")
    else:
        data = load_graph_data()
        st.info("기본 샘플 데이터 사용 중")

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    st.metric("노드 수", len(nodes))
    st.metric("엣지 수", len(edges))

    with st.expander("원본 JSON 보기"):
        st.json(data)

# ── 탭 구성 ───────────────────────────────────────────────────────────────
tab_pyvis, tab_agraph, tab_plotly, tab_matplotlib, tab_bokeh = st.tabs([
    "🌐 PyVis",
    "⚛️ streamlit-agraph",
    "📊 Plotly",
    "🎨 Matplotlib",
    "📈 Bokeh",
])

with tab_pyvis:
    st.subheader("PyVis — vis.js 기반 물리 시뮬레이션")
    st.caption("노드 드래그, 줌, 호버 지원 | 방향 엣지 및 두께/색상 완전 반영")
    try:
        from src import vis_pyvis
        vis_pyvis.render(data)
    except ImportError as e:
        st.error(f"pyvis 패키지가 필요합니다: `pip install pyvis`\n\n{e}")

with tab_agraph:
    st.subheader("streamlit-agraph — React 기반 Streamlit 전용 컴포넌트")
    st.caption("노드 클릭 시 선택 정보 반환 | 물리 기반 레이아웃")
    try:
        from src import vis_agraph
        vis_agraph.render(data)
    except ImportError as e:
        st.error(f"streamlit-agraph 패키지가 필요합니다: `pip install streamlit-agraph`\n\n{e}")

with tab_plotly:
    st.subheader("Plotly — NetworkX 레이아웃 + Plotly Scatter")
    st.caption("다양한 레이아웃 선택 가능 | 호버 툴팁, 줌/패닝 지원")
    try:
        from src import vis_plotly
        vis_plotly.render(data)
    except ImportError as e:
        st.error(f"plotly, networkx 패키지가 필요합니다: `pip install plotly networkx`\n\n{e}")

with tab_matplotlib:
    st.subheader("NetworkX + Matplotlib — 정적 렌더링")
    st.caption("레이아웃 선택, 엣지 레이블 표시 옵션 | 한국어 폰트 지원")
    try:
        from src import vis_matplotlib
        vis_matplotlib.render(data)
    except ImportError as e:
        st.error(f"matplotlib, networkx 패키지가 필요합니다: `pip install matplotlib networkx`\n\n{e}")

with tab_bokeh:
    st.subheader("Bokeh — 인터랙티브 그래프 (NetworkX 통합)")
    st.caption("호버 툴팁, 노드 선택, 연결된 엣지 하이라이트")
    try:
        from src import vis_bokeh
        vis_bokeh.render(data)
    except ImportError as e:
        st.error(f"bokeh, networkx 패키지가 필요합니다: `pip install bokeh networkx`\n\n{e}")
