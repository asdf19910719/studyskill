# 通用学习教练

`universal-learning-coach` 是一个同时面向 Codex 和 Claude Code 的学习 Skill。它不是普通总结器，而是把学习资料诊断、资料扩展、老师式讲解、出题批改、Obsidian 笔记沉淀和间隔复习串成一个持续学习流程。

## 支持场景

- 根据已有笔记初始化学习系统。
- 判断资料是否足够支撑系统学习。
- 在工具允许时检索官方文档和高质量资料，扩展薄弱笔记。
- 每次只安排一个 30-60 分钟学习任务。
- 老师式讲解、出题、严格批改和追问。
- 输出 `_学习状态.md`、`错题本.md`、`复习卡片.md` 的更新内容。
- 生成适合 Obsidian 保存的系统学习笔记。

## 安装到 Claude Code

用户级安装：

```bash
mkdir -p ~/.claude/skills/universal-learning-coach
cp -r universal-learning-coach/* ~/.claude/skills/universal-learning-coach/
```

项目级安装：

```text
<ObsidianVault>/.claude/skills/universal-learning-coach/SKILL.md
```

调用示例：

```text
/universal-learning-coach
请读取当前目录的学习资料和 _学习状态.md，继续安排今天的学习任务。
```

## 安装到 Codex

用户级安装：

```bash
mkdir -p ~/.agents/skills/universal-learning-coach
cp -r universal-learning-coach/* ~/.agents/skills/universal-learning-coach/
```

项目级安装：

```text
<ObsidianVault>/.agents/skills/universal-learning-coach/SKILL.md
```

调用示例：

```text
使用 universal-learning-coach skill。请根据 _学习状态.md 给我今天 40 分钟内能完成的学习任务。
```

## Obsidian Vault 推荐结构

```text
ObsidianVault/
├── .agents/
│   └── skills/
│       └── universal-learning-coach/
├── .claude/
│   └── skills/
│       └── universal-learning-coach/
└── 技术学习/
    └── Android远场音频中间件/
        ├── _学习状态.md
        ├── 错题本.md
        ├── 复习卡片.md
        ├── 01_教材笔记/
        ├── 02_扩展笔记/
        ├── 03_错题本/
        └── 04_复习卡片/
```

## 常用调用语句

推荐使用短命令。第一次进入学习项目时：

```text
$universal-learning-coach 初始化
```

以后每次回到同一个学习项目，直接输入：

```text
$universal-learning-coach 继续
```

学完当天任务后：

```text
$universal-learning-coach 学完了
```

完成考试和批改后：

```text
$universal-learning-coach 结束
```

需要单独复习时：

```text
$universal-learning-coach 复习
```

这些短命令会优先读取 `learning_state.json`，再读取 `_学习状态.md`、`错题本.md` 和 `复习卡片.md`，根据上次保存的进度决定下一步，不需要每次重复长提示词。

```text
继续学习。请根据 _学习状态.md 给我今天 40 分钟内能完成的学习任务。
```

```text
我学完了，开始考我。一次只问一个问题，严格批改。
```

```text
结束本次学习。请输出需要更新到 Obsidian 的 _学习状态.md、错题本.md、复习卡片.md 和下次学习计划。
```

```text
当前学习资料中只简单提到了 Android vendor 分区，请判断这部分资料是否足够学习。如果不足，请给出资料缺口诊断，并扩展成系统学习笔记。
```

## 文件结构

```text
universal-learning-coach/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── 学习状态模板.md
│   ├── 错题本模板.md
│   ├── 复习卡片模板.md
│   ├── 知识点笔记模板.md
│   ├── 扩展学习笔记模板.md
│   ├── 资料诊断报告模板.md
│   ├── 外部资料清单模板.md
│   └── learning_state.json
├── references/
│   ├── 六问学习法.md
│   ├── 学习流程说明.md
│   ├── 状态机规则.md
│   ├── 资料缺口诊断规则.md
│   ├── 外部资料检索规则.md
│   ├── 系统学习笔记生成规则.md
│   ├── 出题规则.md
│   ├── 复习策略.md
│   └── 资料来源可信度分级.md
└── scripts/
    ├── init_learning_files.py
    ├── index_materials.py
    ├── build_knowledge_map.py
    ├── append_learning_log.py
    ├── generate_review_plan.py
    ├── scan_learning_gaps.py
    ├── create_expanded_note.py
    ├── studyctl.py
    ├── start_lesson.py
    ├── sync_state.py
    ├── finish_session.py
    ├── doctor.py
    └── test_learning_scripts.py
```

## v1 / v2 差异

v1 是纯 Skill 指令、模板和规则文件，适合 Codex 与 Claude Code 直接使用。v2 增加 Python 脚本，用于自动创建学习文件、扫描学习材料、生成知识地图、追加学习日志、生成今日学习任务、生成复习计划、扫描资料缺口和创建扩展笔记模板。

## 自动流程说明

这个 skill 不是后台常驻服务，仍需要通过 `$universal-learning-coach <短命令>` 触发。但触发后不需要重新说明完整流程。它会优先按 `learning_state.json` 中的结构化状态继续；没有 JSON 时，再按 `_学习状态.md` 中的状态字段继续：

```text
初始化
→ 材料索引
→ 知识地图
→ 逐概念诊断
→ 概念预热
→ 必要时扩展笔记
→ 继续学习
→ 学完后考试
→ 结束更新
→ 生成复习计划
→ 下次继续
```

`learning_state.json` 中关键字段：

```json
{
  "flow_status": "学习中",
  "next_action": "继续学习"
}
```

`_学习状态.md` 中对应字段：

```markdown
## 当前流程状态
学习中

## 下一步动作
继续学习
```

`继续` 会优先读取这些字段。如果 `next_action` / `下一步动作` 是 `扩展笔记`，则先诊断和扩展；如果是 `开始考试`，则直接出题；如果是 `生成复习计划`，则先复习；否则生成当天 30-60 分钟学习任务。
如果 `next_action` 是 `概念预热`，则不会直接进入系统笔记，而是先围绕 `current_concept` 解释“概念是什么、解决什么问题、为什么现在要学”，再做一个最小自测。

## v2 脚本

```bash
python scripts/init_learning_files.py .
python scripts/index_materials.py .
python scripts/build_knowledge_map.py .
python scripts/append_learning_log.py --target 错题本.md --input latest_wrong_answers.md
python scripts/generate_review_plan.py .
python scripts/scan_learning_gaps.py ./学习资料.md
python scripts/create_expanded_note.py "Android vendor 分区"
python scripts/studyctl.py next .
python scripts/start_lesson.py . --minutes 40
python scripts/sync_state.py to-json .
python scripts/sync_state.py to-md .
python scripts/finish_session.py . --date 2026-05-07 --summary "完成 vendor 分区学习"
python scripts/doctor.py .
python scripts/test_learning_scripts.py
```

`finish_session.py` 适合在 `$universal-learning-coach 结束` 时由 AI 调用，用于自动追加 `_学习状态.md`、`错题本.md`、`复习卡片.md`，并同步更新 `learning_state.json`。
`index_materials.py` 会扫描当前学习目录中的 `.md` / `.txt` 学习材料，生成 `学习材料索引.md`，并更新 `learning_state.json.materials`；`init_learning_files.py` 会自动调用它。
`build_knowledge_map.py` 会抽取学习材料中的关键概念，生成 `知识地图.md`，并把逐概念的资料深度、熟悉度、先修关系和下一步动作写入 `learning_state.json.concepts`；`init_learning_files.py` 会自动调用它。
`start_lesson.py` 适合在 `$universal-learning-coach 继续` 路由到普通学习时调用，用于根据 `learning_state.json` 或 `_学习状态.md` 自动生成 `今日学习任务.md`，并默认额外生成 `YYYY-MM-DD_今日学习任务.md` 作为当天归档。
`doctor.py` 适合进入学习项目后先运行，用于检查状态文件是否完整、是否有到期复习、下一步应该调用哪个短命令。

## 注意事项

- 有联网能力时优先使用官方资料；没有联网能力时必须输出检索计划，不能假装搜索过。
- 学习任务默认控制在 30-60 分钟。
- 现有 Obsidian 文件默认追加更新，不随意覆盖。
- 技术学习必须包含问题背景、核心机制、工程应用、常见误区、排障和验收标准。

## 验收测试 Prompt

```text
$universal-learning-coach 初始化
```

```text
$universal-learning-coach 继续
```

```text
使用 universal-learning-coach skill。当前学习资料中只简单提到了 Android vendor 分区，请判断这部分资料是否足够学习。如果不足，请给出资料缺口诊断。
```

```text
使用 universal-learning-coach skill。请围绕 Android vendor 分区、Treble、VNDK，查找官方资料和高质量补充资料，并生成一份系统学习笔记。
```

```text
使用 universal-learning-coach skill。当前环境不能联网。请帮我为 Android vendor 分区生成外部资料检索计划。
```

```text
$universal-learning-coach 学完了
```

```text
$universal-learning-coach 结束
```

```text
使用 universal-learning-coach skill。请把刚才扩展出来的 Android vendor 分区学习笔记整理成适合保存到 Obsidian 的 Markdown，并给出文件名、标签、关联笔记。
```
