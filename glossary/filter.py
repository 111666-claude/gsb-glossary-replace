"""流式过滤器：从输入流读 JSONL，逐行替换后写到输出流。"""

import json

from .rules import Glossary


def run(instream, outstream, glossary):
    """逐行处理 JSONL。缺陷：同一条 id 重复出现也照处理一遍。"""
    for line in instream:
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        text, hits = glossary.replace(record.get("text", ""))
        outstream.write(json.dumps({"id": record.get("id"), "text": text, "hits": hits}) + "\n")
    return 0
