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
│   └── 外部资料清单模板.md
├── references/
│   ├── 五问学习法.md
│   ├── 学习流程说明.md
│   ├── 资料缺口诊断规则.md
│   ├── 外部资料检索规则.md
│   ├── 系统学习笔记生成规则.md
│   ├── 出题规则.md
│   ├── 复习策略.md
│   └── 资料来源可信度分级.md
└── scripts/
    ├── init_learning_files.py
    ├── append_learning_log.py
    ├── generate_review_plan.py
    ├── scan_learning_gaps.py
    ├── create_expanded_note.py
    └── test_learning_scripts.py
```

## v1 / v2 差异

v1 是纯 Skill 指令、模板和规则文件，适合 Codex 与 Claude Code 直接使用。v2 增加 Python 脚本，用于自动创建学习文件、追加学习日志、生成复习计划、扫描资料缺口和创建扩展笔记模板。

## v2 脚本

```bash
python scripts/init_learning_files.py .
python scripts/append_learning_log.py --target 错题本.md --input latest_wrong_answers.md
python scripts/generate_review_plan.py .
python scripts/scan_learning_gaps.py ./学习资料.md
python scripts/create_expanded_note.py "Android vendor 分区"
python scripts/test_learning_scripts.py
```

## 注意事项

- 有联网能力时优先使用官方资料；没有联网能力时必须输出检索计划，不能假装搜索过。
- 学习任务默认控制在 30-60 分钟。
- 现有 Obsidian 文件默认追加更新，不随意覆盖。
- 技术学习必须包含问题背景、核心机制、工程应用、常见误区、排障和验收标准。

## 验收测试 Prompt

```text
使用 universal-learning-coach skill。当前目录有一份 Android 远场音频中间件学习笔记，请初始化学习系统。
```

```text
使用 universal-learning-coach skill。请根据 _学习状态.md 给我今天 40 分钟内能完成的学习任务。
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
我学完了，开始考我。一次只问一个问题。
```

```text
结束本次学习。请输出 Obsidian 更新内容。
```

```text
使用 universal-learning-coach skill。请把刚才扩展出来的 Android vendor 分区学习笔记整理成适合保存到 Obsidian 的 Markdown，并给出文件名、标签、关联笔记。
```
