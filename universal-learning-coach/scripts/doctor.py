import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path


REQUIRED_FILES = [
    "learning_state.json",
    "_学习状态.md",
    "错题本.md",
    "复习卡片.md",
]

ACTION_COMMANDS = {
    "初始化": "$universal-learning-coach 初始化",
    "诊断资料": "$universal-learning-coach 继续",
    "扩展笔记": "$universal-learning-coach 继续",
    "继续学习": "$universal-learning-coach 继续",
    "开始考试": "$universal-learning-coach 学完了",
    "结束更新": "$universal-learning-coach 结束",
    "生成复习计划": "$universal-learning-coach 复习",
}

DATE_PATTERN = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def load_state(directory):
    path = Path(directory) / "learning_state.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def count_due_reviews(directory, today):
    base = Path(directory)
    count = 0
    for name in ["错题本.md", "复习卡片.md"]:
        path = base / name
        if not path.exists():
            continue
        for match in DATE_PATTERN.finditer(path.read_text(encoding="utf-8")):
            try:
                if datetime.strptime(match.group(1), "%Y-%m-%d").date() <= today:
                    count += 1
            except ValueError:
                continue
    return count


def run_doctor(directory):
    base = Path(directory)
    missing = [name for name in REQUIRED_FILES if not (base / name).exists()]
    state = load_state(base)
    next_action = state.get("next_action") or "初始化"
    flow_status = state.get("flow_status") or "未初始化"
    command = ACTION_COMMANDS.get(next_action, "$universal-learning-coach 继续")
    due_count = count_due_reviews(base, date.today())

    lines = ["# 学习项目健康检查", ""]

    if missing:
        lines.extend(["## 缺失文件"])
        lines.extend("- " + name for name in missing)
        lines.extend(
            [
                "",
                "## 修复建议",
                "运行：python universal-learning-coach/scripts/init_learning_files.py <学习目录>",
                "",
                "## 当前路由",
                "当前流程状态：" + flow_status,
                "下一步动作：" + next_action,
                "建议调用：" + command,
                "",
            ]
        )
        return 1, "\n".join(lines)

    lines.extend(
        [
            "健康检查通过：基础学习文件齐全。",
            "",
            "## 当前路由",
            "当前流程状态：" + flow_status,
            "下一步动作：" + next_action,
            "建议调用：" + command,
            "",
            "## 复习检查",
            "到期复习条目：" + str(due_count),
            "",
        ]
    )

    if due_count > 0 and next_action != "生成复习计划":
        lines.extend(
            [
                "## 提醒",
                "存在到期复习条目，建议优先执行 `$universal-learning-coach 复习`。",
                "",
            ]
        )

    return 0, "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check whether a learning project has the required files and a valid next action.")
    parser.add_argument("directory", nargs="?", default=".", help="Learning directory")
    args = parser.parse_args()

    code, output = run_doctor(args.directory)
    print(output)
    sys.exit(code)


if __name__ == "__main__":
    main()
