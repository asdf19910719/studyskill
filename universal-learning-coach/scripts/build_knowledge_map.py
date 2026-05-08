import argparse
import json
import re
from pathlib import Path

import index_materials


CONCEPT_RULES = [
    {
        "name": "Android 分区",
        "aliases": ["system 分区", "vendor 分区", "product 分区", "odm", "分区"],
        "type": "基础概念",
        "prerequisite": True,
    },
    {"name": "vendor 分区", "aliases": ["vendor 分区", "vendor"], "type": "核心概念", "prerequisite": True},
    {"name": "Treble", "aliases": ["Treble"], "type": "架构机制", "prerequisite": True},
    {"name": "VNDK", "aliases": ["VNDK"], "type": "约束机制", "prerequisite": True},
    {"name": "SELinux", "aliases": ["SELinux"], "type": "权限/安全", "prerequisite": False},
    {"name": "LocalSocket", "aliases": ["LocalSocket"], "type": "IPC", "prerequisite": False},
    {"name": "共享内存", "aliases": ["共享内存", "shared memory"], "type": "数据通路", "prerequisite": False},
    {"name": "mmap", "aliases": ["mmap"], "type": "内存映射", "prerequisite": False},
    {"name": "futex", "aliases": ["futex"], "type": "同步机制", "prerequisite": False},
    {"name": "Binder", "aliases": ["Binder", "binder"], "type": "IPC", "prerequisite": False},
    {"name": "HAL", "aliases": ["HAL", "Audio HAL"], "type": "硬件抽象", "prerequisite": False},
    {"name": "PCM", "aliases": ["PCM"], "type": "音频数据", "prerequisite": False},
]

DEPTH_DIMENSIONS = [
    ("概念是什么", ["是什么", "定义", "概念", "what"]),
    ("解决什么问题", ["解决", "问题", "痛点", "why"]),
    ("核心思想", ["思想", "核心", "原理", "机制"]),
    ("边界局限", ["边界", "局限", "限制", "区别"]),
    ("真实场景", ["场景", "工程", "项目", "实践"]),
    ("验证掌握", ["验证", "自测", "验收", "掌握"]),
    ("排障", ["排障", "排查", "故障", "debug"]),
    ("相邻概念", ["相邻", "对比", "区别", "关系"]),
]


def load_state(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path, state):
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_materials(directory, state):
    base = Path(directory)
    materials = state.get("materials") or index_materials.scan_materials(base)
    chunks = []
    for item in materials:
        path = base / item
        if path.exists() and path.is_file():
            chunks.append((item, path.read_text(encoding="utf-8", errors="ignore")))
    return chunks


def contains_alias(text, aliases):
    lowered = text.lower()
    return any(alias.lower() in lowered for alias in aliases)


def context_for(text, aliases):
    lines = text.splitlines()
    selected = []
    for index, line in enumerate(lines):
        if contains_alias(line, aliases):
            start = max(0, index - 1)
            end = min(len(lines), index + 2)
            selected.extend(lines[start:end])
    return "\n".join(selected)


def score_depth(context):
    if not context.strip():
        return 0
    lowered = context.lower()
    hits = []
    for name, keywords in DEPTH_DIMENSIONS:
        if any(keyword.lower() in lowered for keyword in keywords):
            hits.append(name)
    return min(10, max(2, round(len(hits) / len(DEPTH_DIMENSIONS) * 10)))


def decide_next_action(score, prerequisite):
    if prerequisite and score < 7:
        return "概念预热"
    if score < 7:
        return "扩展笔记"
    return "继续学习"


def extract_concepts(material_chunks):
    combined = "\n".join(text for _, text in material_chunks)
    concepts = []
    for rule in CONCEPT_RULES:
        if not contains_alias(combined, rule["aliases"]):
            continue
        context = context_for(combined, rule["aliases"])
        score = score_depth(context)
        concepts.append(
            {
                "name": rule["name"],
                "type": rule["type"],
                "material_score": score,
                "familiarity": "陌生",
                "prerequisite": bool(rule["prerequisite"]),
                "next_action": decide_next_action(score, bool(rule["prerequisite"])),
            }
        )
    return concepts


def render_map(state, concepts):
    topic = state.get("current_topic") or "待确定主题"
    lines = [
        "# 知识地图",
        "",
        "## 主题",
        topic,
        "",
        "## 概念诊断表",
        "",
        "| 概念 | 类型 | 资料深度 | 熟悉度 | 是否先修 | 下一步 |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    if concepts:
        for item in concepts:
            lines.append(
                "| {name} | {type} | {score}/10 | {familiarity} | {prerequisite} | {next_action} |".format(
                    name=item["name"],
                    type=item["type"],
                    score=item["material_score"],
                    familiarity=item["familiarity"],
                    prerequisite="是" if item["prerequisite"] else "否",
                    next_action=item["next_action"],
                )
            )
    else:
        lines.append("| 暂未识别 | - | 0/10 | 陌生 | 否 | 补充材料 |")

    lines.extend(
        [
            "",
            "## 推荐学习顺序",
        ]
    )
    ordered = sorted(concepts, key=lambda item: (not item["prerequisite"], -item["material_score"], item["name"]))
    if ordered:
        for index, item in enumerate(ordered, start=1):
            lines.append(str(index) + ". " + item["name"] + "（" + item["next_action"] + "）")
    else:
        lines.append("1. 先补充学习材料，再重新初始化。")

    lines.extend(
        [
            "",
            "## 使用规则",
            "- 初始化阶段只做轻量六问诊断，不一次性展开所有概念。",
            "- `概念预热` 用于先解释陌生先修概念是什么、解决什么问题、和当前主题有什么关系。",
            "- 正式学习阶段一次只选择一个核心概念做完整六问展开。",
            "",
        ]
    )
    return "\n".join(lines)


def build_knowledge_map(directory):
    base = Path(directory)
    base.mkdir(parents=True, exist_ok=True)
    state_path = base / "learning_state.json"
    state = load_state(state_path)
    material_chunks = read_materials(base, state)
    concepts = extract_concepts(material_chunks)
    if not state.get("current_topic") and material_chunks:
        state["current_topic"] = Path(material_chunks[0][0]).stem.replace("_", " ")
    state["concepts"] = concepts
    if concepts:
        first = sorted(concepts, key=lambda item: (not item["prerequisite"], -item["material_score"], item["name"]))[0]
        state["current_concept"] = first["name"]
        state["flow_status"] = "概念盘点完成"
        state["next_action"] = first["next_action"]
    (base / "知识地图.md").write_text(render_map(state, concepts), encoding="utf-8")
    save_state(state_path, state)
    return concepts


def main():
    parser = argparse.ArgumentParser(description="Build a concept-level knowledge map from local learning materials.")
    parser.add_argument("directory", nargs="?", default=".", help="Learning directory")
    args = parser.parse_args()

    concepts = build_knowledge_map(args.directory)
    print("concepts: " + str(len(concepts)))


if __name__ == "__main__":
    main()
