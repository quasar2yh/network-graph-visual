"""
TDD tests for vis_bokeh module.
Tests run without Streamlit context by mocking st calls.
"""
import pytest
import networkx as nx
from unittest.mock import patch, MagicMock

from bokeh.models import Circle, MultiLine, GraphRenderer
from bokeh.plotting import from_networkx

SAMPLE_DATA = {
    "nodes": [
        {"id": "A", "properties": {"label": "Node A", "size": 30}},
        {"id": "B", "properties": {"label": "Node B", "size": 20}},
        {"id": "C", "properties": {"label": "Node C", "size": 25}},
    ],
    "edges": [
        {"id": "1", "start": "A", "end": "B", "properties": {"label": "AB", "color": "#ff0000", "thickness": 2.0}},
        {"id": "2", "start": "B", "end": "C", "properties": {"label": "", "color": "#95a5a6", "thickness": 1.0}},
    ],
}


class TestBuildGraph:
    def test_returns_digraph(self):
        from src.vis_bokeh import _build_graph
        G = _build_graph(SAMPLE_DATA)
        assert isinstance(G, nx.DiGraph)

    def test_node_count(self):
        from src.vis_bokeh import _build_graph
        G = _build_graph(SAMPLE_DATA)
        assert len(G.nodes) == 3

    def test_edge_count(self):
        from src.vis_bokeh import _build_graph
        G = _build_graph(SAMPLE_DATA)
        assert len(G.edges) == 2

    def test_node_has_label(self):
        from src.vis_bokeh import _build_graph
        G = _build_graph(SAMPLE_DATA)
        assert G.nodes["A"]["label"] == "Node A"

    def test_node_has_size(self):
        from src.vis_bokeh import _build_graph
        G = _build_graph(SAMPLE_DATA)
        assert G.nodes["A"]["size"] == 30

    def test_edge_has_color(self):
        from src.vis_bokeh import _build_graph
        G = _build_graph(SAMPLE_DATA)
        assert G.edges["A", "B"]["color"] == "#ff0000"

    def test_empty_data(self):
        from src.vis_bokeh import _build_graph
        G = _build_graph({"nodes": [], "edges": []})
        assert len(G.nodes) == 0
        assert len(G.edges) == 0


class TestBokehObjects:
    """Test that Bokeh objects can be constructed with correct API."""

    def test_circle_glyph_uses_radius_not_size(self):
        """Bokeh 3.x Circle uses radius, not size."""
        c = Circle(radius="node_radius", radius_units="screen", fill_color="#3498db")
        assert c is not None

    def test_circle_selection_glyph(self):
        c = Circle(radius="node_radius", radius_units="screen", fill_color="#f1c40f")
        assert c is not None

    def test_multiline_glyph(self):
        m = MultiLine(line_color="color", line_width="line_width", line_alpha=0.8)
        assert m is not None

    def test_from_networkx_with_precomputed_layout(self):
        """from_networkx must receive pre-computed layout to avoid kwarg conflicts."""
        G = nx.DiGraph()
        G.add_nodes_from(["A", "B"])
        G.add_edge("A", "B")
        pos = nx.spring_layout(G, seed=42)
        renderer = from_networkx(G, lambda g: pos)
        assert isinstance(renderer, GraphRenderer)


class TestRenderFunction:
    """Test render() doesn't raise exceptions (streamlit mocked)."""

    @patch("src.vis_bokeh.st")
    def test_render_no_exception(self, mock_st):
        mock_st.selectbox.return_value = "spring"
        mock_st.bokeh_chart = MagicMock()
        from src.vis_bokeh import render
        render(SAMPLE_DATA)
        mock_st.bokeh_chart.assert_called_once()

    @patch("src.vis_bokeh.st")
    def test_render_all_layouts(self, mock_st):
        mock_st.bokeh_chart = MagicMock()
        from src.vis_bokeh import render, _LAYOUTS
        for layout_name in _LAYOUTS:
            mock_st.selectbox.return_value = layout_name
            render(SAMPLE_DATA)
