import argparse
import sys
from datetime import date
from pathlib import Path


def read_input(input_path):
    if input_path:
        return Path(input_path).read_text(encoding="utf-8").strip()
    return sys.stdin.read().strip()


def append_learning_log(target_path, content, log_date=None):
    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    current = target.read_text(encoding="utf-8") if target.exists() else ""
    day = log_date or date.today().isoformat()

    separator = "" if current.endswith("\n") or not current else "\n"
    appended = separator + "\n## " + day + "\n\n" + content.strip() + "\n"
    target.write_text(current + appended, encoding="utf-8")
    return target


def main():
    parser = argparse.ArgumentParser(description="Append a dated Markdown section to a learning file.")
    parser.add_argument("--target", required=True, help="Target Markdown file")
    parser.add_argument("--input", help="Input Markdown file. Reads stdin when omitted.")
    parser.add_argument("--date", help="Override date as YYYY-MM-DD")
    args = parser.parse_args()

    content = read_input(args.input)
    if not content:
        raise SystemExit("No input content provided.")

    target = append_learning_log(args.target, content, args.date)
    print("appended: " + str(target))


if __name__ == "__main__":
    main()
