import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "扩展学习笔记模板.md"


def is_ascii_word(text):
    return bool(re.fullmatch(r"[A-Za-z0-9_+-]+", text))


def safe_filename(topic):
    parts = topic.strip().split()
    if not parts:
        return "扩展学习笔记"

    result = parts[0]
    previous = parts[0]
    for part in parts[1:]:
        separator = "_" if is_ascii_word(previous) and is_ascii_word(part) else ""
        result += separator + part
        previous = part

    result = re.sub(r'[<>:"/\\|?*]', "_", result)
    return result


def create_note(topic, output_dir):
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = safe_filename(topic) + "_扩展学习笔记.md"
    output = target_dir / filename

    template = TEMPLATE.read_text(encoding="utf-8")
    content = template.replace("# 知识点标题", "# " + topic, 1)
    if "当前环境无法联网检索" not in content:
        content += "\n\n> 当前环境无法联网检索时，请在资料来源中标注哪些内容来自用户资料、哪些内容来自模型归纳。\n"

    output.write_text(content, encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(description="Create an expanded learning-note Markdown file from template.")
    parser.add_argument("topic", help="Knowledge point title")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    args = parser.parse_args()

    output = create_note(args.topic, args.output_dir)
    print("created: " + str(output))


if __name__ == "__main__":
    main()
