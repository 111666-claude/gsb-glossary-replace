"""术语表替换：按最长匹配优先替换，同长度按优先级降序。

缺陷：按登记顺序替换（不做最长匹配）、替换结果会被后面的术语再次匹配、重复登记不查优先级、
每次替换全扫术语表。
"""


def load_terms(path):
    """读术语表，每行是 term、priority、replacement，用制表符分隔。"""
    terms = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            term, priority, replacement = line.split("\t")
            terms.append({"term": term, "priority": int(priority), "to": replacement})
    return terms


class Glossary:
    """术语台账。"""

    def __init__(self, terms):
        self.terms = terms
        self.hits = 0
        self.work = 0

    def add(self, term, priority, replacement):
        """登记一条术语，返回是否成功。缺陷：重复 term 不查优先级，直接追加。"""
        self.terms.append({"term": term, "priority": priority, "to": replacement})
        return True

    def replace(self, text):
        """替换一段文本，返回 (结果, 命中次数)。缺陷：不做最长匹配、链式再替换、全扫术语表。"""
        out = text
        hits = 0
        for item in self.terms:
            self.work += 1
            if item["term"] and item["term"] in out:
                hits += out.count(item["term"])
                out = out.replace(item["term"], item["to"])
        self.hits += hits
        return out, hits

    def work_count(self):
        return self.work
