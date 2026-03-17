import json
from pathlib import Path


DEFAULT_PATH = Path("statics/inputs/sample.json")


def load_graph_data(path: str | Path = DEFAULT_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_nodes(data: dict) -> list[dict]:
    return data.get("nodes", [])


def get_edges(data: dict) -> list[dict]:
    return data.get("edges", [])
