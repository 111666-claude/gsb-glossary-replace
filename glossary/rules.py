"""术语表替换：每个位置取最长匹配，同术语按优先级取优，左到右单次扫描不链式替换。"""


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


class _Node:
    """字典树节点。entry 非空表示有术语在此结束。"""

    __slots__ = ("children", "entry")

    def __init__(self):
        self.children = {}
        self.entry = None


class Glossary:
    """术语台账：字典树索引，处理一行文本的代价不随术语总数增长。"""

    def __init__(self, terms):
        self._root = _Node()
        self._entries = {}
        self.hits = 0
        self.work = 0
        for item in terms:
            self.add(item["term"], item["priority"], item["to"])

    def add(self, term, priority, replacement):
        """登记一条术语。重复登记返回 False：优先级更高则取优，否则保留已有规则。"""
        if not term:
            return False
        existing = self._entries.get(term)
        if existing is not None:
            if priority > existing["priority"]:
                existing["priority"] = priority
                existing["to"] = replacement
            return False
        entry = {"term": term, "priority": priority, "to": replacement}
        self._entries[term] = entry
        node = self._root
        for char in term:
            node = node.children.setdefault(char, _Node())
        node.entry = entry
        return True

    def replace(self, text):
        """左到右扫描一次，每个位置取最长匹配，替换结果不再参与匹配。"""
        out = []
        hits = 0
        index = 0
        length = len(text)
        root = self._root
        while index < length:
            node = root
            best_end = 0
            best_entry = None
            cursor = index
            while cursor < length:
                self.work += 1
                node = node.children.get(text[cursor])
                if node is None:
                    break
                cursor += 1
                if node.entry is not None:
                    best_end = cursor
                    best_entry = node.entry
            if best_entry is None:
                out.append(text[index])
                index += 1
            else:
                out.append(best_entry["to"])
                hits += 1
                index = best_end
        self.hits += hits
        return "".join(out), hits

    def work_count(self):
        return self.work
