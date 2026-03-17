# 🕸️ Network Graph Visualizer

Streamlit에서 **5가지 라이브러리**로 네트워크 그래프를 시각화하는 도구입니다.
노드/엣지 스타일링(크기, 색상, 두께), 다양한 레이아웃, 인터랙션을 모두 지원합니다.

---

## 📦 설치

### 필수 요구사항
- Python 3.13+
- `uv` 패키지 매니저 (또는 `pip`)

### 의존성 설치

```bash
# uv 사용 (권장)
uv sync

# 또는 pip
pip install -r requirements.txt
```

설치될 패키지:
- `streamlit` - UI 프레임워크
- `pyvis` - vis.js 기반 물리 시뮬레이션
- `streamlit-agraph` - React 기반 Streamlit 전용 컴포넌트
- `plotly` - 대화형 산점도 그래프
- `networkx` - 그래프 알고리즘 & 레이아웃
- `matplotlib` - 정적 렌더링
- `bokeh` - 인터랙티브 시각화

---

## 🚀 실행

```bash
uv run streamlit run app.py
```

브라우저가 자동으로 열리며, `http://localhost:8501`에서 접속 가능합니다.

---

## 📊 5가지 시각화 라이브러리

### 🌐 **PyVis** (vis.js 기반)
- **강점**: 물리 시뮬레이션, 매끄러운 인터랙션
- **기능**:
  - 노드 드래그 가능
  - 동적 레이아웃 (중력/스프링)
  - 엣지 방향 표시 (화살표)
  - 색상/두께 완전 반영
- **사용 시기**: 네트워크 구조를 직관적으로 탐색하고 싶을 때

### ⚛️ **streamlit-agraph** (React)
- **강점**: Streamlit 전용, 깔끔한 UI, 클릭 이벤트
- **기능**:
  - 노드 클릭 시 ID 반환
  - 하이라이트 및 애니메이션
  - 물리 기반 레이아웃
- **사용 시기**: 특정 노드 선택이 필요할 때

### 📊 **Plotly** (NetworkX + Scatter)
- **강점**: 다양한 레이아웃, 출판 품질 그래프
- **기능**:
  - 5가지 레이아웃 선택
    - `spring`: 스프링 레이아웃
    - `kamada_kawai`: 최적 거리 기반
    - `circular`: 원형
    - `shell`: 껍질
    - `spectral`: 스펙트럼
  - 호버 툴팁
  - 줌/패닝
- **사용 시기**: 레이아웃을 비교하거나 프레젠테이션용으로

### 🎨 **Matplotlib** (NetworkX)
- **강점**: 한국어 폰트 지원, 정적 렌더링
- **기능**:
  - 레이아웃 선택 가능
  - 엣지 레이블 토글
  - 선명한 텍스트 렌더링
  - 고해상도 출력
- **사용 시기**: 논문/보고서용 정적 이미지

### 📈 **Bokeh** (NetworkX)
- **강점**: 인터랙티브 선택, 호버 정보
- **기능**:
  - 노드 선택 시 연결된 엣지 하이라이트
  - 호버 툴팁 (노드명, 크기)
  - 레이아웃 선택
  - TapTool 지원
- **사용 시기**: 노드 관계를 자세히 탐색할 때

---

## 📁 JSON 데이터 형식

```json
{
  "nodes": [
    {
      "id": "node_id",
      "properties": {
        "label": "표시될 이름",
        "size": 30
      }
    }
  ],
  "edges": [
    {
      "id": "edge_id",
      "start": "source_node_id",
      "end": "target_node_id",
      "properties": {
        "label": "관계 설명",
        "color": "#3498db",
        "thickness": 2.5,
        "style": "solid"
      }
    }
  ]
}
```

### 확장 가능한 구조
새로운 속성 추가:
```json
{
  "id": "node_id",
  "properties": {
    "label": "...",
    "size": 30,
    "group": "team_a",        // 그룹화
    "icon": "🏢",             // 아이콘 표시
    "description": "..."      // 추가 정보
  }
}
```

각 시각화 모듈은 필요한 속성만 추출하므로, 새 속성 추가 시 모든 라이브러리에 자동 반영됩니다.

---

## 📤 데이터 업로드

### 기본값
기본적으로 `statics/inputs/sample.json` 파일을 로드합니다.

### 커스텀 데이터
앱의 **사이드바**에서 JSON 파일을 드래그&드롭으로 업로드:
1. 파일 업로드 위젯 사용
2. 자동으로 노드/엣지 수 표시
3. 원본 JSON은 사이드바 하단에서 확인 가능

---

## 🏗️ 프로젝트 구조

```
graph_visualize/
├── app.py                     # Streamlit 메인 앱 (5개 탭)
├── pyproject.toml             # 의존성 정의
├── README.md                  # 이 파일
├── src/
│   ├── __init__.py
│   ├── data_loader.py         # JSON 로드 공통 유틸
│   ├── vis_pyvis.py           # PyVis 시각화
│   ├── vis_agraph.py          # streamlit-agraph 시각화
│   ├── vis_plotly.py          # Plotly 시각화
│   ├── vis_matplotlib.py      # Matplotlib 시각화
│   └── vis_bokeh.py           # Bokeh 시각화
└── statics/
    └── inputs/
        └── sample.json        # 샘플 데이터
```

### 모듈별 역할

| 파일 | 역할 |
|---|---|
| `app.py` | Streamlit UI, 탭 관리, 에러 처리 |
| `data_loader.py` | JSON 로드, 노드/엣지 추출 |
| `vis_*.py` | 각 라이브러리별 렌더링 로직 |

---

## 💡 사용 예시

### 1. 기본 실행
```bash
uv run streamlit run app.py
```
기본 샘플 데이터가 모두 탭에서 시각화됩니다.

### 2. 커스텀 데이터 사용
1. 자신의 JSON 파일 준비
2. 사이드바 "📂 데이터" → "JSON 파일 업로드"
3. 선택한 탭에서 즉시 렌더링

### 3. 레이아웃 비교
**Plotly** 또는 **Matplotlib** 탭에서 드롭다운으로 레이아웃 변경하며 비교:
- Spring layout: 전체 구조 파악
- Kamada-Kawai: 대칭적 배치
- Circular: 간단한 배열
- Shell: 그룹별 배치

### 4. 인터랙티브 탐색
**PyVis** 또는 **Bokeh** 탭에서:
- 노드를 드래그해서 구조 재정렬
- 엣지 관계 직관적으로 파악
- 호버로 엣지 라벨 확인

---

## ⚙️ 커스터마이징

### 색상 스키마 변경
각 `vis_*.py` 파일에서:
```python
# 배경색
bgcolor="#1a1a2e"  → 원하는 색상으로 변경

# 노드 색상
node_color="#3498db"  → 커스텀 색

# 텍스트 색상
font_color="#ffffff"  → 커스텀 색
```

### 물리 시뮬레이션 파라미터 (PyVis)
`vis_pyvis.py`의 `physics` 설정:
```python
"barnesHut": {
  "gravitationalConstant": -8000,  # 더 크면 노드 분산
  "springConstant": 0.04,          # 더 크면 경직됨
  "springLength": 150              # 노드 간 거리
}
```

### 레이아웃 추가 (Plotly/Matplotlib/Bokeh)
```python
# vis_plotly.py의 _LAYOUTS 딕셔너리에 추가
_LAYOUTS = {
    "spring": nx.spring_layout,
    "your_layout": nx.your_layout_function,
    ...
}
```

---

## 🐛 트러블슈팅

### 한국어가 깨진다
**Matplotlib** 탭 문제시:
```python
# vis_matplotlib.py 상단에서 폰트 확인
matplotlib.rcParams["font.family"] = ["Malgun Gothic", "AppleGothic"]
```
시스템에 설치된 폰트로 변경하세요.

### 특정 라이브러리 오류
앱 실행 시 탭에 에러 메시지 표시됩니다.
```
plotly 패키지가 필요합니다: `pip install plotly networkx`
```
메시지의 지시대로 설치하면 됩니다.

### 대용량 데이터 성능
- PyVis: 수백 개 노드까지 괜찮음
- Plotly: ~1000 노드 권장
- Bokeh: ~500 노드 권장
- Matplotlib: 수백 개 노드

---

## 📝 라이선스 및 기여

이 프로젝트는 개인/교육용입니다.
자유롭게 수정하고 배포할 수 있습니다.

---

## 🔗 참고자료

- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [PyVis](https://pyvis.readthedocs.io/)
- [streamlit-agraph](https://github.com/ChrisDelChr/streamlit-agraph)
- [Plotly Python](https://plotly.com/python/)
- [NetworkX](https://networkx.org/)
- [Matplotlib](https://matplotlib.org/)
- [Bokeh](https://docs.bokeh.org/)
