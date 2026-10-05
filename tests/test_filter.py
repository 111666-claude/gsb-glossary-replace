import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glossary.filter import run  # noqa: E402
from glossary.rules import Glossary, load_terms  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TermsTest(unittest.TestCase):
    def test_load_terms_from_sample(self):
        terms = load_terms(os.path.join(HERE, "sample", "terms.txt"))
        self.assertEqual(len(terms), 3)


class FilterTest(unittest.TestCase):
    def test_replaces_single_term(self):
        glossary = Glossary([{"term": "a", "priority": 1, "to": "X"}])
        out = io.StringIO()
        run(io.StringIO('{"id": "t1", "text": "aaa"}\n'), out, glossary)
        self.assertIn('"text": "XXX"', out.getvalue())

    def test_empty_input_produces_nothing(self):
        out = io.StringIO()
        run(io.StringIO(""), out, Glossary([]))
        self.assertEqual(out.getvalue(), "")

    def test_work_starts_at_zero(self):
        self.assertEqual(Glossary([]).work_count(), 0)


class LongestMatchTest(unittest.TestCase):
    """最长匹配：每个位置取能匹配到的最长术语。"""

    def test_longest_term_wins(self):
        glossary = Glossary([
            {"term": "a", "priority": 1, "to": "X"},
            {"term": "ab", "priority": 1, "to": "Y"},
            {"term": "b", "priority": 1, "to": "c"},
        ])
        text, hits = glossary.replace("ab")
        self.assertEqual((text, hits), ("Y", 1))

    def test_shorter_term_used_when_longer_does_not_match(self):
        glossary = Glossary([
            {"term": "a", "priority": 1, "to": "X"},
            {"term": "ab", "priority": 1, "to": "Y"},
        ])
        text, hits = glossary.replace("ac")
        self.assertEqual((text, hits), ("Xc", 1))

    def test_same_term_higher_priority_wins(self):
        glossary = Glossary([
            {"term": "x", "priority": 1, "to": "low"},
            {"term": "x", "priority": 9, "to": "high"},
        ])
        text, _ = glossary.replace("x")
        self.assertEqual(text, "high")


class NoChainTest(unittest.TestCase):
    """不链式替换：替换产生的新文本不再被其它术语匹配。"""

    def test_replacement_text_is_not_rescanned(self):
        glossary = Glossary([
            {"term": "a", "priority": 1, "to": "b"},
            {"term": "b", "priority": 1, "to": "c"},
        ])
        text, hits = glossary.replace("a")
        self.assertEqual((text, hits), ("b", 1))

    def test_replacement_spanning_terms_is_not_rescanned(self):
        glossary = Glossary([
            {"term": "a", "priority": 1, "to": "bb"},
            {"term": "bb", "priority": 1, "to": "c"},
        ])
        text, hits = glossary.replace("a")
        self.assertEqual((text, hits), ("bb", 1))


class AddTest(unittest.TestCase):
    """登记幂等：重复登记返回 False，按优先级取优。"""

    def test_first_registration_returns_true(self):
        self.assertTrue(Glossary([]).add("x", 1, "low"))

    def test_duplicate_registration_returns_false(self):
        glossary = Glossary([])
        glossary.add("x", 1, "low")
        self.assertFalse(glossary.add("x", 5, "high"))

    def test_higher_priority_duplicate_replaces_rule(self):
        glossary = Glossary([])
        glossary.add("x", 1, "low")
        glossary.add("x", 5, "high")
        text, _ = glossary.replace("x")
        self.assertEqual(text, "high")

    def test_lower_priority_duplicate_keeps_existing_rule(self):
        glossary = Glossary([])
        glossary.add("x", 5, "high")
        glossary.add("x", 1, "low")
        text, _ = glossary.replace("x")
        self.assertEqual(text, "high")


class WorkTest(unittest.TestCase):
    """处理代价：work_count 不随术语数乘文本长度增长。"""

    def test_duplicate_terms_do_not_multiply_work(self):
        glossary = Glossary([{"term": "a", "priority": 1, "to": "b"} for _ in range(3000)])
        for _ in range(3000):
            glossary.replace("a")
        self.assertLessEqual(glossary.work_count(), 6000)

    def test_work_depends_on_text_not_term_count(self):
        glossary = Glossary([{"term": "t%d" % index, "priority": 1, "to": "x"} for index in range(10000)])
        glossary.replace("zzz")
        self.assertLessEqual(glossary.work_count(), len("zzz") * 2)


class SampleTest(unittest.TestCase):
    """内置样例口径。"""

    def run_sample(self, name):
        from glossary.__main__ import main
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            main(["--sample", name])
        return buffer.getvalue().strip()

    def test_sample_longest(self):
        self.assertEqual(self.run_sample("longest"), '{"id": "t1", "text": "Y", "hits": 1}')

    def test_sample_chain(self):
        self.assertEqual(self.run_sample("chain"), '{"id": "t1", "text": "b", "hits": 1}')

    def test_sample_dup(self):
        self.assertEqual(self.run_sample("dup"), "second=false text=high")

    def test_sample_work(self):
        output = self.run_sample("work")
        self.assertTrue(output.startswith("work="))
        self.assertLessEqual(int(output.split("=", 1)[1]), 6000)


if __name__ == "__main__":
    unittest.main()
