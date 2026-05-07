import argparse
import json
import re
from pathlib import Path


DEFAULT_STATE = {
    "schema_version": 1,
    "current_topic": "",
    "current_stage": "",
    "current_goal": "",
    "flow_status": "未初始化",
    "next_action": "初始化",
    "last_learning_date": "",
    "last_action": "",
}

FIELD_MAP = {
    "current_topic": "当前学习主题",
    "current_stage": "当前阶段",
    "current_goal": "当前目标",
    "flow_status": "当前流程状态",
    "next_action": "下一步动作",
    "last_learning_date": "最近一次学习日期",
    "last_action": "最近一次动作",
}


def load_json(path):
    if not path.exists():
        return dict(DEFAULT_STATE)
    data = json.loads(path.read_text(encoding="utf-8"))
    state = dict(DEFAULT_STATE)
    state.update(data)
    return state


def save_json(path, state):
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def extract_section_value(text, heading):
    lines = text.splitlines()
    pattern = r"^##\s+" + re.escape(heading) + r"\s*$"
    for index, line in enumerate(lines):
        if not re.match(pattern, line):
            continue
        values = []
        for candidate in lines[index + 1 :]:
            if candidate.startswith("## "):
                break
            stripped = candidate.strip()
            if not stripped or stripped == "待填写" or stripped == "-":
                continue
            if stripped.startswith("可选值"):
                break
            values.append(stripped)
        return values[0] if values else ""
    return ""


def replace_section_value(text, heading, value):
    lines = text.splitlines()
    pattern = r"^##\s+" + re.escape(heading) + r"\s*$"
    for index, line in enumerate(lines):
        if not re.match(pattern, line):
            continue
        end = index + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        return "\n".join(lines[: index + 1] + [str(value or "待填写"), ""] + lines[end:]).rstrip() + "\n"
    suffix = "" if text.endswith("\n") or not text else "\n"
    return text + suffix + "\n## " + heading + "\n" + str(value or "待填写") + "\n"


def sync_to_json(directory):
    base = Path(directory)
    md_path = base / "_学习状态.md"
    json_path = base / "learning_state.json"
    state = load_json(json_path)

    if not md_path.exists():
        save_json(json_path, state)
        return json_path

    text = md_path.read_text(encoding="utf-8")
    for key, heading in FIELD_MAP.items():
        value = extract_section_value(text, heading)
        if value:
            state[key] = value
    save_json(json_path, state)
    return json_path


def sync_to_markdown(directory):
    base = Path(directory)
    md_path = base / "_学习状态.md"
    json_path = base / "learning_state.json"
    state = load_json(json_path)
    text = md_path.read_text(encoding="utf-8") if md_path.exists() else "# 学习状态\n"

    for key, heading in FIELD_MAP.items():
        text = replace_section_value(text, heading, state.get(key, ""))
    md_path.write_text(text, encoding="utf-8")
    return md_path


def main():
    parser = argparse.ArgumentParser(description="Synchronize learning_state.json and _学习状态.md.")
    parser.add_argument("direction", choices=["to-json", "to-md"], help="Sync direction")
    parser.add_argument("directory", nargs="?", default=".", help="Learning directory")
    args = parser.parse_args()

    if args.direction == "to-json":
        output = sync_to_json(args.directory)
    else:
        output = sync_to_markdown(args.directory)
    print("synced: " + str(output))


if __name__ == "__main__":
    main()
