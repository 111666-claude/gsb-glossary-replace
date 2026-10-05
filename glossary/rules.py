"""术语表替换：每个位置取能匹配到的最长术语，同长度按优先级降序、再按术语字典序升序。

实现：字典树单趟扫描，左到右每个位置沿树走到不能走为止，取途中最后一条术语（即最长匹配）；
替换结果不再参与匹配，不链式替换；同一术语重复登记返回 False 且不覆盖已有规则；
代价只随文本长度增长，不随术语数乘文本长度增长。
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
        self._root = {}
        self._size = 0
        self.hits = 0
        self.work = 0
        for item in terms:
            self.add(item["term"], item["priority"], item["to"])

    def add(self, term, priority, replacement):
        """登记一条术语，返回是否成功；重复登记返回 False 且不覆盖已有规则。"""
        if not term:
            return False
        node = self._root
        for char in term:
            node = node.setdefault(char, {})
        if None in node:
            return False
        node[None] = replacement
        self._size += 1
        return True

    def replace(self, text):
        """替换一段文本，返回 (结果, 命中次数)。左到右单趟扫描，替换结果不再匹配。"""
        out = []
        hits = 0
        index = 0
        length = len(text)
        while index < length:
            node = self._root
            best_to = None
            best_end = index
            cursor = index
            while cursor < length:
                self.work += 1
                nxt = node.get(text[cursor])
                if nxt is None:
                    break
                node = nxt
                cursor += 1
                if None in node:
                    best_to = node[None]
                    best_end = cursor
            if best_to is not None:
                out.append(best_to)
                hits += 1
                index = best_end
            else:
                out.append(text[index])
                index += 1
        self.hits += hits
        return "".join(out), hits

    def work_count(self):
        return self.work
