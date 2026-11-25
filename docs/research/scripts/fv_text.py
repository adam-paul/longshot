#!/usr/bin/env python3
"""fv_text.py FILE [--grep REGEX] [--ctx N] [--max N]: strip HTML to text; optionally show regex matches with context."""
import sys, re, html
from html.parser import HTMLParser

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"): self.skip += 1
        if tag in ("p", "br", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "td", "th", "section", "article", "dt", "dd"): self.out.append("\n")
        if tag == "a":
            d = dict(attrs)
            if d.get("href") and not self.skip: self.out.append(" [")
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.skip: self.skip -= 1
        if tag == "a" and not self.skip: self.out.append("] ")
        if tag in ("p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "table"): self.out.append("\n")
    def handle_data(self, data):
        if not self.skip: self.out.append(data)

def main():
    args = sys.argv[1:]
    f = args[0]
    pat = None; ctx = 200; mx = 0
    i = 1
    while i < len(args):
        if args[i] == "--grep": pat = args[i+1]; i += 2
        elif args[i] == "--ctx": ctx = int(args[i+1]); i += 2
        elif args[i] == "--max": mx = int(args[i+1]); i += 2
        else: i += 1
    raw = open(f, "rb").read().decode("utf-8", "replace")
    if "<" in raw[:2000] and ("<html" in raw.lower() or "<div" in raw.lower() or "<p" in raw.lower()):
        p = P(); p.feed(raw); t = "".join(p.out)
    else:
        t = raw
    t = re.sub(r"[ \t\r\f\v]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    if pat:
        seen = []
        for m in re.finditer(pat, t, flags=re.I):
            a = max(0, m.start() - ctx); b = min(len(t), m.end() + ctx)
            if seen and a < seen[-1][1]:
                seen[-1] = (seen[-1][0], b)
            else:
                seen.append((a, b))
        for a, b in seen:
            print("...", t[a:b].replace("\n", " | "), "...\n")
        print(f"[{len(seen)} match regions; text length {len(t)}]")
    else:
        print(t if not mx else t[:mx])
        print(f"[text length {len(t)}]")
main()
