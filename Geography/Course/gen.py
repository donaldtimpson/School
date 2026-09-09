#!/usr/bin/env python3
"""Generate assessment HTML from compact JSON specs.
Emits two files per spec: <id>.html (student copy) and <id>-key.html (answer key).
Stems and rubrics may contain inline HTML."""
import json, sys, pathlib

DIR = pathlib.Path(__file__).parent
LETTERS = "abcdefgh"

def fmt(x):
    return str(int(x)) if float(x) == int(x) else str(x)

def head(title):
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            f'<title>{title}</title><!--STYLE--></head>\n<body>\n')

def total_points(spec):
    return sum(len(p["questions"]) * p["ptsEach"] for p in spec["parts"])

def render_student(spec):
    o = []; A = o.append
    A(head(spec["title"]))
    A('<div class="masthead">')
    A(f'  <p class="course">{spec["eyebrow"]}</p>')
    A(f'  <h1>{spec["title"]}</h1>')
    A(f'  <p class="sub">{spec["sub"]}</p>')
    A('</div>\n')
    A('<div class="idline">')
    A('  <span class="nm">Name &nbsp;</span>')
    A('  <span class="dt">Date &nbsp;</span>')
    A(f'  <span class="sc">Score &nbsp; &nbsp; / {total_points(spec)}</span>')
    A('</div>\n')
    if spec.get("instructions"):
        A(f'<div class="instr">{spec["instructions"]}</div>\n')

    n = 0
    for p in spec["parts"]:
        cnt, pe, t = len(p["questions"]), p["ptsEach"], p["type"]
        unit = "point" if pe == 1 else "points"
        A(f'<p class="part">{p["name"]} <span class="pts">{cnt} question'
          f'{"" if cnt==1 else "s"} &times; {fmt(pe)} {unit} = {fmt(cnt*pe)} points</span></p>')
        A(f'<ol class="q" style="counter-reset: qn {n};">')
        for q in p["questions"]:
            n += 1
            A('  <li>')
            A(f'    <p class="stem">{q["stem"]}</p>')
            if t == "mc":
                A('    <ul class="ch">')
                for i, c in enumerate(q["choices"]):
                    A(f'      <li data-l="{LETTERS[i]}">{c}</li>')
                A('    </ul>')
            elif t == "tf":
                A('    <p class="tf">TRUE &nbsp;&nbsp;/&nbsp;&nbsp; FALSE</p>')
            elif t == "match":
                A('    <table class="matchtbl"><tbody>')
                for i, (l, r) in enumerate(zip(q["left"], q["right"])):
                    A(f'      <tr><td class="mline">____</td><td class="ml">{i+1}. {l}</td>'
                      f'<td class="mr">{LETTERS[i]}) {r}</td></tr>')
                A('    </tbody></table>')
            else:
                ln = q.get("lines", p.get("lines", 4))
                A('    <div class="lines">' + "<div></div>" * ln + '</div>')
            A('  </li>')
        A('</ol>\n')
    A('<div class="endmark">&mdash; END &mdash;</div>\n')
    A('</body></html>')
    return "\n".join(o)

def render_key(spec):
    o = []; A = o.append
    A(head(spec["title"] + " — Answer Key"))
    A(f'<div class="keyhead">ANSWER KEY &nbsp;&middot;&nbsp; {spec["keyhead"]}'
      f'<span class="kpts">{total_points(spec)} points total</span></div>\n')
    A('<div class="key">')
    n = 0
    for p in spec["parts"]:
        pe, t = p["ptsEach"], p["type"]
        unit = "point" if pe == 1 else "points"
        A(f'<p class="part">{p["name"]} <span class="pts">{fmt(pe)} {unit} each</span></p>')
        A(f'<ol class="q" style="counter-reset: qn {n};">')
        for q in p["questions"]:
            n += 1
            A('  <li>')
            if t == "mc":
                i = q["answer"]
                A(f'    <span class="ans">{LETTERS[i]}) {q["choices"][i]}</span>')
            elif t == "tf":
                A(f'    <span class="ans">{"TRUE" if q["answer"] else "FALSE"}</span>')
            elif t == "match":
                pairs = " &nbsp;&middot;&nbsp; ".join(
                    f'{i+1}&ndash;{LETTERS[a]}' for i, a in enumerate(q["answer"]))
                A(f'    <span class="ans">{pairs}</span>')
            else:
                A(f'    <span class="ans">{q["answer"]}</span>')
            if q.get("why"):
                A(f'    <br><span class="why">{q["why"]}</span>')
            if q.get("rubric"):
                A(f'    <div class="rubric"><strong>Rubric:</strong> {q["rubric"]}</div>')
            A('  </li>')
        A('</ol>\n')
    A('</div>\n')
    A('</body></html>')
    return "\n".join(o)

if __name__ == "__main__":
    args = sys.argv[1:] or [str(p) for p in sorted((DIR / "spec").glob("*.json"))]
    for a in args:
        path = pathlib.Path(a)
        if not path.exists():
            path = DIR / "spec" / a
        spec = json.loads(path.read_text(encoding="utf-8"))
        (DIR / "src" / (spec["id"] + ".html")).write_text(render_student(spec), encoding="utf-8")
        (DIR / "src" / (spec["id"] + "-key.html")).write_text(render_key(spec), encoding="utf-8")
        print(f"  spec -> src/{spec['id']}.html + {spec['id']}-key.html")
