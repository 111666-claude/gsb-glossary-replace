"""入口：无参数时从标准输入读 JSONL；--sample 跑内置样例。"""

import argparse
import io
import json
import os
import sys

from .filter import run
from .rules import Glossary, load_terms

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMS = os.path.join(HERE, "sample", "terms.txt")


def build_parser():
    parser = argparse.ArgumentParser(prog="glossary-replace", description="术语表替换过滤器")
    parser.add_argument("--terms", default=TERMS, help="术语表路径")
    parser.add_argument("--sample", default=None, help="longest / chain / dup / work")
    return parser


def feed(glossary, payload):
    out = io.StringIO()
    run(io.StringIO(payload), out, glossary)
    return out.getvalue().strip()


def main(argv=None):
    args = build_parser().parse_args(argv)
    glossary = Glossary(load_terms(args.terms))
    if args.sample == "longest":
        print(feed(glossary, json.dumps({"id": "t1", "text": "ab"}) + "\n"))
    elif args.sample == "chain":
        glossary = Glossary([{"term": "a", "priority": 1, "to": "b"}, {"term": "b", "priority": 1, "to": "c"}])
        print(feed(glossary, json.dumps({"id": "t1", "text": "a"}) + "\n"))
    elif args.sample == "dup":
        glossary = Glossary([])
        glossary.add("x", 1, "low")
        second = glossary.add("x", 5, "high")
        text, _ = glossary.replace("x")
        print("second=%s text=%s" % (str(second).lower(), text))
    elif args.sample == "work":
        glossary = Glossary([{"term": "a", "priority": 1, "to": "b"} for _ in range(3000)])
        payload = "".join(json.dumps({"id": "t-%d" % index, "text": "a"}) + "\n" for index in range(3000))
        feed(glossary, payload)
        print("work=%d" % glossary.work_count())
    elif args.sample is None:
        return run(sys.stdin, sys.stdout, glossary)
    else:
        raise SystemExit("需要 --sample longest|chain|dup|work")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
