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
    def test_longest_term_wins_at_each_position(self):
        glossary = Glossary([
            {"term": "a", "priority": 1, "to": "X"},
            {"term": "ab", "priority": 1, "to": "Y"},
            {"term": "b", "priority": 1, "to": "Z"},
        ])
        self.assertEqual(glossary.replace("ab"), ("Y", 1))

    def test_falls_back_to_shorter_match(self):
        glossary = Glossary([
            {"term": "a", "priority": 1, "to": "X"},
            {"term": "ab", "priority": 1, "to": "Y"},
        ])
        self.assertEqual(glossary.replace("ac"), ("Xc", 1))

    def test_scans_left_to_right_without_overlap(self):
        glossary = Glossary([
            {"term": "aa", "priority": 1, "to": "X"},
            {"term": "a", "priority": 1, "to": "Y"},
        ])
        self.assertEqual(glossary.replace("aaa"), ("XY", 2))


class NoChainTest(unittest.TestCase):
    def test_replacement_text_is_not_replaced_again(self):
        glossary = Glossary([
            {"term": "a", "priority": 1, "to": "b"},
            {"term": "b", "priority": 1, "to": "c"},
        ])
        self.assertEqual(glossary.replace("a"), ("b", 1))


class AddTest(unittest.TestCase):
    def test_duplicate_registration_returns_false_and_keeps_first(self):
        glossary = Glossary([])
        self.assertTrue(glossary.add("x", 1, "low"))
        self.assertFalse(glossary.add("x", 5, "high"))
        self.assertEqual(glossary.replace("x"), ("low", 1))

    def test_empty_term_is_rejected(self):
        self.assertFalse(Glossary([]).add("", 1, "x"))


class WorkTest(unittest.TestCase):
    def test_work_does_not_scale_with_term_count_times_text(self):
        glossary = Glossary([{"term": "a", "priority": 1, "to": "b"} for _ in range(3000)])
        for _ in range(3000):
            glossary.replace("a")
        self.assertLessEqual(glossary.work_count(), 6000)

    def test_work_scales_with_text_length_only(self):
        glossary = Glossary([{"term": "t%d" % index, "priority": 1, "to": "x"} for index in range(1000)])
        glossary.replace("zzzz")
        self.assertLessEqual(glossary.work_count(), 4)


if __name__ == "__main__":
    unittest.main()
