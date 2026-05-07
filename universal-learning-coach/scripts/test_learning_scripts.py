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


if __name__ == "__main__":
    unittest.main()
