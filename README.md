# glossary-replace

术语表替换过滤器：从标准输入读 JSONL，逐行按术语表替换后写 JSONL 到标准输出，只用 Python 标准库。

```
python3 -m glossary --sample longest
python3 -m glossary --sample chain
python3 -m glossary --sample dup
python3 -m glossary --sample work
printf '%s\n' '{"id":"t1","text":"ab"}' | python3 -m glossary
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **最长匹配**：一段文本要在每个位置都取能匹配到的最长术语；长度相同时取优先级最高的一条，
  再相同按术语字典序升序。
- **不链式替换**：替换产生的新文本不再被其它术语匹配，一次扫描左到右只替换一次。
- **登记幂等**：同一个术语重复登记返回 false，且不覆盖已有规则的优先级与替换词。
- **输出契约**：每行输出 `{"id": 原样, "text": 替换后文本, "hits": 命中次数}`。
- **代价**：处理一行文本不许全扫术语表，`work_count()` 不随术语数乘文本长度增长；
  10 万条术语、每秒 10 万行。

## 输出契约（不改格式）

```
{"id": .., "text": .., "hits": ..}
second=.. text=..
work=..
```

## 目录

```
glossary/__main__.py  标准输入入口与样例
glossary/filter.py    JSONL 流式处理
glossary/rules.py     最长匹配替换
sample/terms.txt      术语表
tests/test_filter.py  unittest 用例
```
