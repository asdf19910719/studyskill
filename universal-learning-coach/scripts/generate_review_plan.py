import argparse
import re
from datetime import date, datetime
from pathlib import Path


DATE_PATTERN = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def collect_due_blocks(path, today):
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    due_blocks = []

    for index, line in enumerate(lines):
        match = DATE_PATTERN.search(line)
        if not match:
            continue
        due_date = parse_date(match.group(1))
        if due_date > today:
            continue

        start = max(0, index - 6)
        block_lines = [item for item in lines[start : index + 1] if item.strip()]
        block = "\n".join(block_lines).strip()
        if block:
            due_blocks.append(block)

    return due_blocks


def build_review_plan(directory, today):
    base = Path(directory)
    wrong_answers = collect_due_blocks(base / "错题本.md", today)
    flashcards = collect_due_blocks(base / "复习卡片.md", today)

    lines = [
        "# 今日复习计划",
        "",
        "## 优先复习",
    ]

    if not wrong_answers and not flashcards:
        lines.append("- 今天没有扫描到到期复习条目。")
    else:
        count = 1
        for block in wrong_answers + flashcards:
            summary = " / ".join(
                part.strip("# ：:") for part in block.splitlines() if part.strip() and not part.startswith("# ")
            )
            lines.append(str(count) + ". " + summary)
            count += 1

    lines.extend(
        [
            "",
            "## 复习问题",
            "- 先闭卷复述核心问题、核心思想、边界、应用和排障。",
            "- 对错题条目重新回答原题。",
            "- 对复习卡片遮住答案后自测。",
            "",
            "## 需要重新学习的知识点",
            "- 根据复习得分低于 7/10 的条目决定。",
            "",
            "## 下次复习日期",
            "- 按 D+1、D+3、D+7、D+14、D+30 更新。",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate today's spaced review plan.")
    parser.add_argument("directory", nargs="?", default=".", help="Learning directory")
    parser.add_argument("--date", help="Override today as YYYY-MM-DD")
    args = parser.parse_args()

    today = parse_date(args.date) if args.date else date.today()
    plan = build_review_plan(args.directory, today)
    output = Path(args.directory) / "今日复习计划.md"
    output.write_text(plan, encoding="utf-8")
    print(plan)


if __name__ == "__main__":
    main()
