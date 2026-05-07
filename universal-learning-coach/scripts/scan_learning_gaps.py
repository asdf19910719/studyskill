import argparse
from pathlib import Path


DIMENSIONS = [
    ("解决什么问题", ["解决", "问题", "痛点", "why"]),
    ("背景 / 出现原因", ["背景", "原因", "为什么", "历史"]),
    ("官方定义", ["官方", "定义", "spec", "documentation"]),
    ("大白话解释", ["大白话", "类比", "一句话"]),
    ("核心机制拆解", ["机制", "流程", "原理", "架构"]),
    ("关键概念关系", ["关系", "区别", "对比", "边界"]),
    ("真实项目作用", ["项目", "工程", "场景", "实践"]),
    ("局限性和边界", ["局限", "边界", "限制"]),
    ("常见误区", ["误区", "错误理解", "坑"]),
    ("典型问题和排障", ["排障", "排查", "故障", "debug"]),
    ("官方资源和推荐资料", ["资料", "链接", "参考", "source"]),
    ("学习顺序", ["学习顺序", "路线", "阶段"]),
    ("验收标准", ["验收", "自测", "掌握", "标准"]),
]


def score_material(text):
    hits = []
    lowered = text.lower()
    for name, keywords in DIMENSIONS:
        if any(keyword.lower() in lowered for keyword in keywords):
            hits.append(name)

    score = min(10, round(len(hits) / len(DIMENSIONS) * 10))
    missing = [name for name, _ in DIMENSIONS if name not in hits]
    return score, hits, missing


def build_report(path):
    material = Path(path)
    text = material.read_text(encoding="utf-8")
    score, hits, missing = score_material(text)
    suggestion = "建议扩展" if score < 7 else "暂不需要扩展"

    lines = [
        "# 资料完整度诊断",
        "",
        "## 当前知识点",
        material.stem,
        "",
        "## 资料完整度评分",
        str(score) + "/10",
        "",
        "## 已具备内容",
    ]
    lines.extend("- " + item for item in hits) if hits else lines.append("- 暂未识别到系统学习必备内容。")
    lines.extend(["", "## 缺失内容"])
    lines.extend("- " + item for item in missing) if missing else lines.append("- 暂未发现明显缺失。")
    lines.extend(
        [
            "",
            "## 是否建议扩展成独立学习笔记",
            suggestion,
            "",
            "## 建议扩展方向",
            "1. 补官方定义和背景问题。",
            "2. 补核心机制、工程边界和常见误区。",
            "3. 补排障、自测题和验收标准。",
            "",
            "## 下一步建议",
            "如果需要继续学习，请先把低分知识点扩展成系统学习笔记。",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scan Markdown material and output a learning-gap report.")
    parser.add_argument("material", help="Markdown learning material")
    args = parser.parse_args()

    print(build_report(args.material))


if __name__ == "__main__":
    main()
