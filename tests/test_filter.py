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


if __name__ == "__main__":
    unittest.main()
