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
}

ACTION_COMMANDS = {
    "初始化": "$universal-learning-coach 初始化",
    "诊断资料": "$universal-learning-coach 继续",
    "概念预热": "$universal-learning-coach 继续",
    "扩展笔记": "$universal-learning-coach 继续",
    "继续学习": "$universal-learning-coach 继续",
    "开始考试": "$universal-learning-coach 学完了",
    "结束更新": "$universal-learning-coach 结束",
    "生成复习计划": "$universal-learning-coach 复习",
}


def read_json_state(directory):
    path = Path(directory) / "learning_state.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "source": str(path),
        "flow_status": data.get("flow_status") or "未初始化",
        "next_action": data.get("next_action") or "初始化",
        "current_topic": data.get("current_topic") or "",
    }


def read_markdown_state(directory):
    path = Path(directory) / "_学习状态.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    return {
        "source": str(path),
        "flow_status": extract_section_value(text, "当前流程状态") or "未初始化",
        "next_action": extract_section_value(text, "下一步动作") or "初始化",
        "current_topic": extract_section_value(text, "当前学习主题") or "",
    }


def extract_section_value(text, heading):
    pattern = r"^##\s+" + re.escape(heading) + r"\s*$"
    lines = text.splitlines()
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


def load_state(directory):
    return read_json_state(directory) or read_markdown_state(directory) or {
        "source": "default",
        **DEFAULT_STATE,
    }


def create_json_state(directory):
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "learning_state.json"
    if path.exists():
        return "exists: " + str(path)
    path.write_text(json.dumps(DEFAULT_STATE, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return "created: " + str(path)


def render_status(state):
    return "\n".join(
        [
            "当前状态来源：" + state["source"],
            "当前学习主题：" + (state.get("current_topic") or "未填写"),
            "当前流程状态：" + state["flow_status"],
            "下一步动作：" + state["next_action"],
        ]
    )


def render_next(state):
    command = ACTION_COMMANDS.get(state["next_action"], "$universal-learning-coach 继续")
    reason = build_reason(state)
    return "\n".join(
        [
            render_status(state),
            "建议调用：" + command,
            "原因：" + reason,
        ]
    )


def build_reason(state):
    action = state["next_action"]
    if action == "扩展笔记":
        return "当前资料不足或状态要求先补齐系统学习笔记。"
    if action == "概念预热":
        return "知识地图显示当前概念是陌生先修概念，应先用六问法做短讲解和最小自测。"
    if action == "开始考试":
        return "当前学习任务已完成，下一步应通过单题考试检验掌握情况。"
    if action == "结束更新":
        return "当前会话需要沉淀到学习状态、错题本和复习卡片。"
    if action == "生成复习计划":
        return "当前应优先处理到期复习项目。"
    if action == "初始化":
        return "当前目录尚未建立学习系统。"
    return "当前状态适合继续一个 30-60 分钟的小学习任务。"


def main():
    parser = argparse.ArgumentParser(description="Inspect structured learning state and recommend the next skill command.")
    parser.add_argument("command", choices=["init", "status", "next"], help="Action to perform")
    parser.add_argument("directory", nargs="?", default=".", help="Learning directory")
    args = parser.parse_args()

    if args.command == "init":
        print(create_json_state(args.directory))
        return

    state = load_state(args.directory)
    if args.command == "status":
        print(render_status(state))
    elif args.command == "next":
        print(render_next(state))


if __name__ == "__main__":
    main()
