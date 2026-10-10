r"""check_reply_colon.py — 构建前哨兵：推特回复行的「@句柄」分隔符必须是半角冒号。

背景（2026-10-11 卡死事故）：
  游戏用 `ThisIsThePresident.TwitterReply.Initialized()` 解析回复行：
      line.LocalizedText.Split(new[]{':'}, 2)   // 只认 ASCII 冒号
  再取 array[1] 作为正文；若译文把 `@handle:` 写成 `@handle：`（全角），
  Split 只得到一个元素 ⇒ IndexOutOfRangeException ⇒ SendTweet() 中断
  ⇒ 第一条推文选满后 Send 按钮永远没反应（事件卡死、游戏不崩）。

用法：
  python check_reply_colon.py            # 扫描 zh\*.json，有全角冒号则 exit 1
  python check_reply_colon.py --list     # 额外打印前 20 条命中
"""
import io
import json
import os
import re
import sys

def project_root():
    """项目根目录：默认 = 本脚本所在目录的上一级（tools/ 的父目录），可用 --root <dir> 覆盖。"""
    for i, a in enumerate(sys.argv):
        if a == "--root" and i + 1 < len(sys.argv):
            return os.path.abspath(sys.argv[i + 1])
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SRC_RE = re.compile(r"^\s*@[^\s:：]+\s*:\s*\S")
HANDLE_RE = re.compile(r"^\s*(@[^\s:：]+)\s*[:：]")


def main():
    show = "--list" in sys.argv
    zh = os.path.join(project_root(), "zh")
    if not os.path.isdir(zh):
        print("zh/ not found at %s -- nothing to check (RESULT=OK)" % zh)
        return 0
    bad = []
    total = 0
    for path in sorted(os.listdir(zh)):
        if not path.endswith(".json"):
            continue
        full = os.path.join(zh, path)
        with io.open(full, encoding="utf-8") as fh:
            try:
                data = json.load(fh)
            except Exception as exc:  # noqa: BLE001
                print("PARSE-FAIL %s: %s" % (path, exc))
                bad.append((path, "<parse>", str(exc)))
                continue
        if not isinstance(data, dict):
            continue
        for key, val in data.items():
            if not isinstance(key, str) or not isinstance(val, str):
                continue
            if not SRC_RE.match(key):
                continue
            total += 1
            m = HANDLE_RE.match(val)
            if not m:
                continue
            if "：" in val[: m.end()]:
                bad.append((path, key[:60], val[:60]))
    print("reply lines (source @handle:): %d" % total)
    print("full-width colon in handle separator: %d" % len(bad))
    if bad:
        for row in bad[:20] if show else bad[:5]:
            print("  BAD %s | %s || %s" % row)
        print("RESULT=FAIL")
        return 1
    print("RESULT=OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
