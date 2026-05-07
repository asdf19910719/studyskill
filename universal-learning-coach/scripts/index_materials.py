import argparse
import json
import re
from pathlib import Path


MATERIAL_SUFFIXES = {".md", ".txt"}
EXCLUDED_NAMES = {
    "_学习状态.md",
    "错题本.md",
    "复习卡片.md",
    "今日复习计划.md",
    "今日学习任务.md",
    "学习材料索引.md",
    "learning_state.json",
}
EXCLUDED_DIRS = {".git", ".agents", ".claude", ".codex", "__pycache__"}


def is_material(path):
    if path.name in EXCLUDED_NAMES:
        return False
    if path.suffix.lower() not in MATERIAL_SUFFIXES:
        return False
    return not any(part in EXCLUDED_DIRS for part in path.parts)


def scan_materials(directory):
    base = Path(directory)
    materials = []
    for path in base.rglob("*"):
        if not path.is_file() or not is_material(path.relative_to(base)):
            continue
        materials.append(path.relative_to(base).as_posix())
    return sorted(materials)


def read_excerpt(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if stripped:
            return stripped[:120]
    return "无摘要"


def infer_topic(materials):
    if not materials:
        return ""
    first = Path(materials[0]).stem
    cleaned = re.sub(r"^\d+[_\-\s]*", "", first)
    cleaned = cleaned.replace("_", " ").replace("-", " ").strip()
    return cleaned


def load_state(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path, state):
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_state(directory, materials):
    state_path = Path(directory) / "learning_state.json"
    state = load_state(state_path)
    state["materials"] = materials
    if materials and not state.get("current_topic"):
        state["current_topic"] = infer_topic(materials)
    if materials and state.get("flow_status") == "未初始化":
        state["flow_status"] = "待诊断资料"
        state["next_action"] = "诊断资料"
    save_state(state_path, state)


def render_index(directory, materials):
    base = Path(directory)
    lines = ["# 学习材料索引", ""]
    if not materials:
        lines.extend(["当前目录未发现 `.md` 或 `.txt` 学习材料。", ""])
        return "\n".join(lines)

    lines.extend(["## 材料列表", ""])
    for item in materials:
        excerpt = read_excerpt(base / item)
        lines.append("- `" + item + "`：" + excerpt)
    lines.extend(["", "## 下一步", "$universal-learning-coach 继续", ""])
    return "\n".join(lines)


def index_materials(directory):
    base = Path(directory)
    base.mkdir(parents=True, exist_ok=True)
    materials = scan_materials(base)
    (base / "学习材料索引.md").write_text(render_index(base, materials), encoding="utf-8")
    update_state(base, materials)
    return materials


def main():
    parser = argparse.ArgumentParser(description="Index local learning materials and update learning_state.json.")
    parser.add_argument("directory", nargs="?", default=".", help="Learning directory")
    args = parser.parse_args()

    materials = index_materials(args.directory)
    print("indexed: " + str(len(materials)))


if __name__ == "__main__":
    main()
