import argparse
import shutil
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

FILES = {
    "_学习状态.md": "学习状态模板.md",
    "错题本.md": "错题本模板.md",
    "复习卡片.md": "复习卡片模板.md",
    "learning_state.json": "learning_state.json",
}


def init_learning_files(target_dir):
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    results = []

    for output_name, template_name in FILES.items():
        output = target / output_name
        template = ASSETS / template_name
        if output.exists():
            results.append("exists: " + str(output))
            continue
        shutil.copyfile(str(template), str(output))
        if output.suffix == ".json":
            data = json.loads(output.read_text(encoding="utf-8"))
            output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        results.append("created: " + str(output))

    return results


def main():
    parser = argparse.ArgumentParser(description="Create default learning files from skill templates.")
    parser.add_argument("target_dir", nargs="?", default=".", help="Learning directory")
    args = parser.parse_args()

    for line in init_learning_files(args.target_dir):
        print(line)


if __name__ == "__main__":
    main()
