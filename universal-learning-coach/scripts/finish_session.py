import argparse
import json
from pathlib import Path


DEFAULT_STATE = {
    "schema_version": 1,
    "flow_status": "学习中",
    "next_action": "继续学习",
    "last_learning_date": "",
    "last_action": "",
    "mastered": [],
    "unmastered": [],
}


def load_state(path):
    if not path.exists():
        return dict(DEFAULT_STATE)
    data = json.loads(path.read_text(encoding="utf-8"))
    state = dict(DEFAULT_STATE)
    state.update(data)
    return state


def save_state(path, state):
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_section(path, heading, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    current = path.read_text(encoding="utf-8") if path.exists() else "# " + path.stem + "\n"
    separator = "" if current.endswith("\n") else "\n"
    path.write_text(current + separator + "\n## " + heading + "\n\n" + body.strip() + "\n", encoding="utf-8")


def finish_session(directory, args):
    base = Path(directory)
    base.mkdir(parents=True, exist_ok=True)
    day = args.date

    learned_lines = ["- " + item for item in args.learned]
    if not learned_lines:
        learned_lines = ["- " + args.summary]

    state_body = "\n".join(
        [
            "### 本次总结",
            args.summary,
            "",
            "### 本次掌握",
            "\n".join(learned_lines),
            "",
            "### 当前流程状态",
            args.flow_status,
            "",
            "### 下一步动作",
            args.next_action,
        ]
    )
    append_section(base / "_学习状态.md", day + " 学习结束", state_body)

    if args.wrong:
        wrong_body = "\n".join(
            [
                "### 日期",
                day,
                "",
                "### 错因分析",
                "\n".join("- " + item for item in args.wrong),
                "",
                "### 下次复习时间",
                args.next_review or "待安排",
            ]
        )
        append_section(base / "错题本.md", day + " 错题追加", wrong_body)

    if args.flashcard_q or args.flashcard_a:
        flashcard_body = "\n".join(
            [
                "### Q：",
                args.flashcard_q or "待填写",
                "",
                "### A：",
                args.flashcard_a or "待填写",
                "",
                "### 易错点：",
                "; ".join(args.wrong) if args.wrong else "待填写",
                "",
                "### 复习记录",
                "- 第 1 次：",
            ]
        )
        append_section(base / "复习卡片.md", day + " 复习卡片追加", flashcard_body)

    state_path = base / "learning_state.json"
    state = load_state(state_path)
    state["flow_status"] = args.flow_status
    state["next_action"] = args.next_action
    state["last_learning_date"] = day
    state["last_action"] = "结束更新"
    state["mastered"] = merge_unique(state.get("mastered", []), args.learned)
    state["unmastered"] = merge_unique(state.get("unmastered", []), args.wrong)
    save_state(state_path, state)
    return base


def merge_unique(existing, additions):
    result = list(existing or [])
    for item in additions:
        if item and item not in result:
            result.append(item)
    return result


def main():
    parser = argparse.ArgumentParser(description="Append end-of-session updates and update learning_state.json.")
    parser.add_argument("directory", nargs="?", default=".", help="Learning directory")
    parser.add_argument("--date", required=True, help="Session date as YYYY-MM-DD")
    parser.add_argument("--summary", required=True, help="Session summary")
    parser.add_argument("--learned", action="append", default=[], help="Learned item; can be repeated")
    parser.add_argument("--wrong", action="append", default=[], help="Wrong or weak point; can be repeated")
    parser.add_argument("--flashcard-q", default="", help="Flashcard question")
    parser.add_argument("--flashcard-a", default="", help="Flashcard answer")
    parser.add_argument("--flow-status", default="学习中", help="Next flow status")
    parser.add_argument("--next-action", default="继续学习", help="Next action")
    parser.add_argument("--next-review", default="", help="Next review date")
    args = parser.parse_args()

    output = finish_session(args.directory, args)
    print("updated: " + str(output))


if __name__ == "__main__":
    main()
