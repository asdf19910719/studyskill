import subprocess
import sys
import tempfile
import unittest
import os
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run_script(name, *args, input_text=None):
    cmd = [sys.executable, str(SCRIPTS / name)]
    cmd.extend(str(arg) for arg in args)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        cmd,
        input=input_text,
        text=True,
        encoding="utf-8",
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(ROOT),
    )


class LearningScriptsTest(unittest.TestCase):
    def test_init_learning_files_creates_missing_files_and_keeps_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            existing = work / "_学习状态.md"
            existing.write_text("keep me", encoding="utf-8")

            result = run_script("init_learning_files.py", work)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(existing.read_text(encoding="utf-8"), "keep me")
            self.assertTrue((work / "错题本.md").exists())
            self.assertTrue((work / "复习卡片.md").exists())
            self.assertIn("created", result.stdout)
            self.assertIn("exists", result.stdout)

    def test_init_learning_files_state_template_contains_flow_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)

            result = run_script("init_learning_files.py", work)

            self.assertEqual(result.returncode, 0, result.stderr)
            content = (work / "_学习状态.md").read_text(encoding="utf-8")
            self.assertIn("## 当前流程状态", content)
            self.assertIn("## 下一步动作", content)

    def test_init_learning_files_creates_structured_state_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)

            result = run_script("init_learning_files.py", work)

            self.assertEqual(result.returncode, 0, result.stderr)
            state_path = work / "learning_state.json"
            self.assertTrue(state_path.exists())
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["flow_status"], "未初始化")
            self.assertEqual(state["next_action"], "初始化")

    def test_init_learning_files_indexes_existing_materials(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "Android_vendor架构.md").write_text("# Android vendor 架构\nTreble 和 VNDK\n", encoding="utf-8")
            (work / "错题本.md").write_text("# existing wrong answers\n", encoding="utf-8")

            result = run_script("init_learning_files.py", work)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((work / "学习材料索引.md").exists())
            state = json.loads((work / "learning_state.json").read_text(encoding="utf-8"))
            self.assertIn("Android_vendor架构.md", state["materials"])
            self.assertNotIn("错题本.md", state["materials"])

    def test_studyctl_next_prefers_learning_state_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "learning_state.json").write_text(
                json.dumps(
                    {
                        "flow_status": "需要扩展资料",
                        "next_action": "扩展笔记",
                        "current_topic": "Android vendor 分区",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = run_script("studyctl.py", "next", work)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("下一步动作：扩展笔记", result.stdout)
            self.assertIn("$universal-learning-coach 继续", result.stdout)

    def test_studyctl_next_falls_back_to_markdown_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "_学习状态.md").write_text(
                "# 学习状态\n\n## 当前流程状态\n待考试\n\n## 下一步动作\n开始考试\n",
                encoding="utf-8",
            )

            result = run_script("studyctl.py", "next", work)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("下一步动作：开始考试", result.stdout)
            self.assertIn("$universal-learning-coach 学完了", result.stdout)

    def test_sync_state_updates_json_from_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "_学习状态.md").write_text(
                "# 学习状态\n\n## 当前学习主题\nAndroid 音频\n\n## 当前流程状态\n学习中\n\n## 下一步动作\n继续学习\n",
                encoding="utf-8",
            )

            result = run_script("sync_state.py", "to-json", work)

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((work / "learning_state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["current_topic"], "Android 音频")
            self.assertEqual(state["flow_status"], "学习中")
            self.assertEqual(state["next_action"], "继续学习")

    def test_sync_state_updates_markdown_from_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "_学习状态.md").write_text(
                "# 学习状态\n\n## 当前学习主题\n旧主题\n\n## 当前流程状态\n未初始化\n\n## 下一步动作\n初始化\n",
                encoding="utf-8",
            )
            (work / "learning_state.json").write_text(
                json.dumps(
                    {
                        "current_topic": "Android 音频",
                        "flow_status": "待复习",
                        "next_action": "生成复习计划",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = run_script("sync_state.py", "to-md", work)

            self.assertEqual(result.returncode, 0, result.stderr)
            content = (work / "_学习状态.md").read_text(encoding="utf-8")
            self.assertIn("Android 音频", content)
            self.assertIn("待复习", content)
            self.assertIn("生成复习计划", content)

    def test_finish_session_appends_logs_and_updates_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            run_script("init_learning_files.py", work)

            result = run_script(
                "finish_session.py",
                work,
                "--date",
                "2026-05-07",
                "--summary",
                "理解了 vendor 分区的工程边界。",
                "--learned",
                "vendor 与 system 的职责边界",
                "--wrong",
                "混淆 vendor 和 product 分区",
                "--flashcard-q",
                "vendor 分区解决什么问题？",
                "--flashcard-a",
                "隔离厂商实现和系统框架，降低系统升级耦合。",
                "--flow-status",
                "待复习",
                "--next-action",
                "生成复习计划",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((work / "learning_state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["flow_status"], "待复习")
            self.assertEqual(state["next_action"], "生成复习计划")
            self.assertIn("理解了 vendor 分区", (work / "_学习状态.md").read_text(encoding="utf-8"))
            self.assertIn("混淆 vendor", (work / "错题本.md").read_text(encoding="utf-8"))
            self.assertIn("vendor 分区解决什么问题", (work / "复习卡片.md").read_text(encoding="utf-8"))

    def test_doctor_reports_missing_learning_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)

            result = run_script("doctor.py", work)

            self.assertEqual(result.returncode, 1)
            self.assertIn("缺失文件", result.stdout)
            self.assertIn("_学习状态.md", result.stdout)
            self.assertIn("init_learning_files.py", result.stdout)

    def test_doctor_passes_initialized_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            run_script("init_learning_files.py", work)

            result = run_script("doctor.py", work)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("健康检查通过", result.stdout)
            self.assertIn("下一步动作：初始化", result.stdout)

    def test_append_learning_log_appends_date_heading_and_input_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            target = work / "错题本.md"
            source = work / "latest.md"
            target.write_text("# 错题本\n", encoding="utf-8")
            source.write_text("### 原题\n为什么要拆分控制面和数据面？\n", encoding="utf-8")

            result = run_script(
                "append_learning_log.py",
                "--target",
                target,
                "--input",
                source,
                "--date",
                "2026-05-07",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            content = target.read_text(encoding="utf-8")
            self.assertIn("## 2026-05-07", content)
            self.assertIn("为什么要拆分控制面和数据面", content)

    def test_generate_review_plan_outputs_due_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "错题本.md").write_text(
                "# 错题本\n### 知识点\nvendor 分区\n### 下次复习时间\n2026-05-07\n",
                encoding="utf-8",
            )
            (work / "复习卡片.md").write_text(
                "# 复习卡片\n### Q：\nTreble 解决什么问题？\n### 下次复习时间\n2026-05-08\n",
                encoding="utf-8",
            )

            result = run_script("generate_review_plan.py", work, "--date", "2026-05-07")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("vendor 分区", result.stdout)
            self.assertNotIn("Treble 解决什么问题", result.stdout)
            self.assertTrue((work / "今日复习计划.md").exists())

    def test_scan_learning_gaps_scores_sparse_material_low(self):
        with tempfile.TemporaryDirectory() as tmp:
            material = Path(tmp) / "学习资料.md"
            material.write_text("- vendor 分区\n- Treble\n", encoding="utf-8")

            result = run_script("scan_learning_gaps.py", material)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# 资料完整度诊断", result.stdout)
            self.assertIn("建议扩展", result.stdout)
            self.assertIn("/10", result.stdout)

    def test_create_expanded_note_creates_named_markdown_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)

            result = run_script(
                "create_expanded_note.py",
                "Android vendor 分区",
                "--output-dir",
                work,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            expected = work / "Android_vendor分区_扩展学习笔记.md"
            self.assertTrue(expected.exists())
            content = expected.read_text(encoding="utf-8")
            self.assertIn("# Android vendor 分区", content)
            self.assertIn("## 十、资料来源", content)

    def test_start_lesson_generates_today_task_from_json_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "learning_state.json").write_text(
                json.dumps(
                    {
                        "current_topic": "Android vendor 分区",
                        "current_stage": "系统分区基础",
                        "current_goal": "理解 vendor/system 边界",
                        "flow_status": "学习中",
                        "next_action": "继续学习",
                        "materials": ["Android系统分层_vendor架构_Treble.md"],
                        "unmastered": ["VNDK 作用", "vendor/product 区别"],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = run_script("start_lesson.py", work, "--minutes", "40", "--date", "2026-05-07")

            self.assertEqual(result.returncode, 0, result.stderr)
            task_path = work / "今日学习任务.md"
            archive_path = work / "2026-05-07_今日学习任务.md"
            self.assertTrue(task_path.exists())
            self.assertTrue(archive_path.exists())
            content = task_path.read_text(encoding="utf-8")
            archive_content = archive_path.read_text(encoding="utf-8")
            self.assertIn("# 今日学习任务", content)
            self.assertIn("Android vendor 分区", content)
            self.assertIn("40 分钟", content)
            self.assertIn("VNDK 作用", content)
            self.assertIn("vendor/product 区别", content)
            self.assertIn("## 通过标准", content)
            self.assertEqual(content, archive_content)

    def test_index_materials_writes_index_and_updates_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "notes").mkdir()
            (work / "notes" / "Android_vendor架构.md").write_text("# Android vendor 架构\nTreble 和 VNDK\n", encoding="utf-8")
            (work / "学习材料.txt").write_text("binder 音频链路\n", encoding="utf-8")
            (work / "今日学习任务.md").write_text("# generated\n", encoding="utf-8")
            (work / "2026-05-07_今日学习任务.md").write_text("# generated archive\n", encoding="utf-8")
            (work / "learning_state.json").write_text(
                json.dumps({"materials": [], "current_topic": ""}, ensure_ascii=False),
                encoding="utf-8",
            )

            result = run_script("index_materials.py", work)

            self.assertEqual(result.returncode, 0, result.stderr)
            index_path = work / "学习材料索引.md"
            self.assertTrue(index_path.exists())
            index_content = index_path.read_text(encoding="utf-8")
            self.assertIn("notes/Android_vendor架构.md", index_content)
            self.assertIn("学习材料.txt", index_content)
            self.assertNotIn("今日学习任务.md", index_content)
            self.assertNotIn("2026-05-07_今日学习任务.md", index_content)
            state = json.loads((work / "learning_state.json").read_text(encoding="utf-8"))
            self.assertIn("notes/Android_vendor架构.md", state["materials"])
            self.assertIn("学习材料.txt", state["materials"])
            self.assertEqual(state["current_topic"], "Android vendor架构")


if __name__ == "__main__":
    unittest.main()
