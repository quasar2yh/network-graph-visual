import sys
import os
from pathlib import Path
import subprocess


def resolve_file_path(filename: str) -> Path:
    """
    Resolve input file path.

    Supports:
    - Filename only: sample.json → statics/inputs/sample.json
    - Relative path: statics/inputs/sample.json
    - Absolute path: /full/path/to/file.json
    """
    filepath = Path(filename)

    # If filename is just a name (no path separator), look in statics/inputs
    if "/" not in filename and "\\" not in filename:
        filepath = Path("statics/inputs") / filename

    if not filepath.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")

    return filepath


def main():
    if len(sys.argv) < 2:
        print("사용법: uv run main.py <filename>")
        print("\n예시:")
        print("  uv run main.py sample.json")
        print("  uv run main.py statics/inputs/sample.json")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        filepath = resolve_file_path(filename)
        print(f"파일 로드: {filepath}")
    except FileNotFoundError as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)

    # Set environment variable for app.py
    os.environ["GRAPH_VISUALIZE_DATA_FILE"] = str(filepath.resolve())

    # Run streamlit app
    subprocess.run([
        "streamlit", "run", "app.py",
        "--logger.level=warning"
    ])


if __name__ == "__main__":
    main()
