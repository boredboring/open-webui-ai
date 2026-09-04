"""
数据结构课程练习题工具 —— 本地离线测试脚本。

用途：不依赖 Open WebUI，直接对 ds_quiz_tool.py 的抽题与判分逻辑做单元测试。
运行：python test_ds_quiz_tool.py
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ds_quiz_tool as m  # noqa: E402


def run(func, **kwargs):
    return json.loads(func(**kwargs))


class TestResolveChapter(unittest.TestCase):
    def test_numeric(self):
        self.assertEqual(m.resolve_chapter("第3章")[0], "ch03")
        self.assertEqual(m.resolve_chapter("3")[0], "ch03")
        self.assertEqual(m.resolve_chapter("ch05")[0], "ch05")
        self.assertEqual(m.resolve_chapter("chapter 7")[0], "ch07")

    def test_keyword(self):
        self.assertEqual(m.resolve_chapter("栈和队列")[0], "ch03")
        self.assertEqual(m.resolve_chapter("二叉树")[0], "ch05")
        self.assertEqual(m.resolve_chapter("排序算法")[0], "ch08")

    def test_invalid(self):
        self.assertEqual(m.resolve_chapter("操作系统"), (None, None))
        self.assertEqual(m.resolve_chapter(""), (None, None))


class TestRandomQuiz(unittest.TestCase):
    def setUp(self):
        self.t = m.Tools()

    def test_basic(self):
        r = run(self.t.ds_random_quiz, chapter="第3章", question_count=3, question_type="all")
        self.assertTrue(r["ok"])
        self.assertEqual(r["data"]["question_count"], 3)
        self.assertEqual(len(r["data"]["questions"]), 3)
        # 自测模式默认不含答案
        self.assertNotIn("answer", r["data"]["questions"][0])

    def test_include_answer(self):
        r = run(self.t.ds_random_quiz, chapter="ch02", question_count=4, question_type="all", include_answer=True)
        self.assertTrue(r["ok"])
        for q in r["data"]["questions"]:
            self.assertIn("answer", q)
            self.assertIn("explanation", q)

    def test_type_filter(self):
        r = run(self.t.ds_random_quiz, chapter="第5章", question_count=99, question_type="choice")
        self.assertTrue(r["ok"])
        for q in r["data"]["questions"]:
            self.assertEqual(q["type"], "choice")

    def test_difficulty_filter(self):
        r = run(self.t.ds_random_quiz, chapter="第8章", question_count=99, question_type="all", difficulty="easy")
        self.assertTrue(r["ok"])
        for q in r["data"]["questions"]:
            self.assertEqual(q["difficulty"], "easy")

    def test_invalid_chapter(self):
        r = run(self.t.ds_random_quiz, chapter="机器学习")
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "INVALID_CHAPTER")

    def test_question_count_clamped(self):
        # 每章只有 4 题，请求 100 题应被限制为实际题数
        r = run(self.t.ds_random_quiz, chapter="第1章", question_count=100, question_type="all")
        self.assertTrue(r["ok"])
        self.assertEqual(r["data"]["question_count"], 4)


class TestGradeQuiz(unittest.TestCase):
    def setUp(self):
        self.t = m.Tools()
        self.r = run(self.t.ds_random_quiz, chapter="第2章", question_count=4, question_type="all", include_answer=True)
        self.qs = self.r["data"]["questions"]

    def _grade(self, answers):
        return run(
            self.t.ds_grade_quiz,
            questions=json.dumps(self.qs, ensure_ascii=False),
            answers=json.dumps(answers, ensure_ascii=False),
        )

    def test_all_correct(self):
        g = self._grade([q["answer"] for q in self.qs])
        self.assertTrue(g["ok"])
        self.assertEqual(g["data"]["correct_count"], 4)
        self.assertEqual(g["data"]["score"], 100.0)

    @staticmethod
    def _wrong_answer(q):
        if q["type"] == "choice":
            for letter in ("A", "B", "C", "D"):
                if letter != q["answer"]:
                    return letter
        if q["type"] == "judge":
            return "错" if q["answer"] == "对" else "对"
        return "与正确答案无关的文本zz"

    def test_all_wrong(self):
        wrong = [self._wrong_answer(q) for q in self.qs]
        g = self._grade(wrong)
        self.assertTrue(g["ok"])
        self.assertEqual(g["data"]["correct_count"], 0)
        for it in g["data"]["results"]:
            self.assertFalse(it["correct"])
            self.assertTrue(it["graded"])
            self.assertIn("explanation", it)

    def test_mixed(self):
        correct = [q["answer"] for q in self.qs]
        wrong = [self._wrong_answer(q) for q in self.qs]
        g = self._grade([correct[0], wrong[1], wrong[2], wrong[3]])
        self.assertEqual(g["data"]["correct_count"], 1)

    def test_length_mismatch(self):
        g = self._grade(["B"])
        self.assertFalse(g["ok"])
        self.assertEqual(g["error"]["code"], "LENGTH_MISMATCH")

    def test_invalid_questions_json(self):
        g = run(self.t.ds_grade_quiz, questions="not-json", answers='["B"]')
        self.assertFalse(g["ok"])
        self.assertEqual(g["error"]["code"], "INVALID_QUESTIONS")

    def test_grade_by_stem_without_id(self):
        # 去掉 id，仅凭 stem 也应能判分
        qs_no_id = [{k: v for k, v in q.items() if k != "id"} for q in self.qs]
        g = run(
            self.t.ds_grade_quiz,
            questions=json.dumps(qs_no_id, ensure_ascii=False),
            answers=json.dumps([q["answer"] for q in self.qs], ensure_ascii=False),
        )
        self.assertTrue(g["ok"])
        self.assertEqual(g["data"]["correct_count"], 4)

    def test_normalization_choice_case_insensitive(self):
        # 选择题答案大小写不敏感：正确答案 B，提交 b
        choice = [q for q in self.qs if q["type"] == "choice"]
        self.assertTrue(choice)
        g = run(
            self.t.ds_grade_quiz,
            questions=json.dumps(choice, ensure_ascii=False),
            answers=json.dumps([q["answer"].lower() for q in choice], ensure_ascii=False),
        )
        self.assertEqual(g["data"]["correct_count"], len(choice))


class TestAnswerNormalization(unittest.TestCase):
    def test_judge(self):
        self.assertTrue(m._answers_match("对", "对", "judge"))
        self.assertTrue(m._answers_match("正确", "对", "judge"))
        self.assertTrue(m._answers_match("T", "对", "judge"))
        self.assertTrue(m._answers_match("错", "错", "judge"))
        self.assertFalse(m._answers_match("对", "错", "judge"))

    def test_fill(self):
        self.assertTrue(m._answers_match("栈", "栈", "fill"))
        self.assertTrue(m._answers_match("平均查找长度", "平均", "fill"))
        self.assertFalse(m._answers_match("队列", "栈", "fill"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
