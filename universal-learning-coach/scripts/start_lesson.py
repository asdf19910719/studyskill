import argparse
import json
import re
from datetime import date
from pathlib import Path


DEFAULT_STATE = {
    "source": "default",
    "current_topic": "待确定主题",
    "current_stage": "",
    "current_goal": "",
    "flow_status": "学习中",
    "next_action": "继续学习",
    "materials": [],
    "unmastered": [],
}


def read_json_state(directory):
    path = Path(directory) / "learning_state.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    state = dict(DEFAULT_STATE)
    state.update(data)
    state["source"] = str(path)
    state["materials"] = normalize_list(data.get("materials"))
    state["unmastered"] = normalize_list(data.get("unmastered"))
    return state


def read_markdown_state(directory):
    path = Path(directory) / "_学习状态.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    state = dict(DEFAULT_STATE)
    state["source"] = str(path)
    state["current_topic"] = extract_section_value(text, "当前学习主题") or state["current_topic"]
    state["current_stage"] = extract_section_value(text, "当前阶段") or ""
    state["current_goal"] = extract_section_value(text, "当前目标") or ""
    state["flow_status"] = extract_section_value(text, "当前流程状态") or state["flow_status"]
    state["next_action"] = extract_section_value(text, "下一步动作") or state["next_action"]
    state["unmastered"] = extract_list_section(text, "未掌握点")
    return state


def extract_section_value(text, heading):
    pattern = r"^##\s+" + re.escape(heading) + r"\s*$"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not re.match(pattern, line):
            continue
        for candidate in lines[index + 1 :]:
            if candidate.startswith("## "):
                break
            stripped = candidate.strip()
            if stripped and stripped not in ["待填写", "-"]:
                return stripped.lstrip("- ").strip()
    return ""


def extract_list_section(text, heading):
    pattern = r"^##\s+" + re.escape(heading) + r"\s*$"
    lines = text.splitlines()
    values = []
    in_section = False
    for line in lines:
        if re.match(pattern, line):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            stripped = line.strip()
            if stripped.startswith("- "):
                values.append(stripped[2:].strip())
    return values


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def load_state(directory):
    return read_json_state(directory) or read_markdown_state(directory) or dict(DEFAULT_STATE)


def render_lesson(state, minutes, lesson_date):
    topic = state.get("current_topic") or "待确定主题"
    stage = state.get("current_stage") or "当前阶段未填写"
    goal = state.get("current_goal") or "完成一个可验证的小学习任务"
    materials = state.get("materials") or ["请先根据当前目录资料或官方资料补齐阅读材料"]
    weak_points = state.get("unmastered") or ["本次学习后再记录未掌握点"]

    return "\n".join(
        [
            "# 今日学习任务",
            "",
            "## 日期",
            lesson_date,
            "",
            "## 预计时长",
            str(minutes) + " 分钟",
            "",
            "## 今日主题",
            topic,
            "",
            "## 当前阶段",
            stage,
            "",
            "## 为什么今天学这个",
            "根据学习状态，当前下一步动作是 `" + (state.get("next_action") or "继续学习") + "`。本任务聚焦一个小主题，避免重新开始整套课程。",
            "",
            "## 学习目标",
            "学完后你应该能：",
            "1. 用自己的话说明 `" + topic + "` 解决的问题。",
            "2. 解释 `" + goal + "`。",
            "3. 针对未掌握点给出可验证回答。",
            "",
            "## 需要阅读的材料",
            render_bullets(materials),
            "",
            "## 当前未掌握点",
            render_bullets(weak_points),
            "",
            "## 10 分钟核心讲解提示",
            "请使用 `$universal-learning-coach 继续` 围绕今日主题进行老师式讲解：先讲问题背景，再讲核心机制、边界、工程场景和常见误区。",
            "",
            "## 自测题",
            "1. `" + topic + "` 主要解决什么问题？",
            "2. `" + goal + "` 中最容易混淆的边界是什么？",
            "3. 结合一个真实场景，说明你会如何判断自己已经理解。",
            "",
            "## 通过标准",
            "- 能在 3 分钟内讲清楚今日主题的问题背景和核心机制。",
            "- 能准确回答未掌握点：" + "；".join(weak_points) + "。",
            "- 能指出至少一个常见误区或排障思路。",
            "",
            "## 学完后下一步",
            "`$universal-learning-coach 学完了`",
            "",
        ]
    )


def render_bullets(items):
    return "\n".join("- " + item for item in items)


def main():
    parser = argparse.ArgumentParser(description="Generate a concrete daily learning task from learning_state.json or _学习状态.md.")
    parser.add_argument("directory", nargs="?", default=".", help="Learning directory")
    parser.add_argument("--minutes", type=int, default=40, help="Expected lesson duration")
    parser.add_argument("--date", default=date.today().isoformat(), help="Lesson date as YYYY-MM-DD")
    parser.add_argument("--output", default="今日学习任务.md", help="Output Markdown filename")
    args = parser.parse_args()

    base = Path(args.directory)
    base.mkdir(parents=True, exist_ok=True)
    state = load_state(base)
    output_path = base / args.output
    output_path.write_text(render_lesson(state, args.minutes, args.date), encoding="utf-8")
    print("created: " + str(output_path))


if __name__ == "__main__":
    main()
