#!/usr/bin/env python3
"""Regenerate src/01-index.html from the specs and the current PDFs."""
import json, pathlib, subprocess, re
D = pathlib.Path(__file__).parent

def pages(p):
    if not p.exists(): return 0
    return subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True).stdout.count("\f")

spec = {json.loads(f.read_text())["id"]: json.loads(f.read_text())
        for f in sorted((D/"spec").glob("*.json"))}

order, wk = [], {}
for i in range(1, 25):
    k = f"q{i:02d}"; order.append(k); wk[k] = i if i <= 13 else i + 1
    for after, t in ((5,"t1"), (10,"t2"), (13,"midterm"), (18,"t3"), (22,"t4"), (24,"final")):
        if i == after: order.append(t)
wk.update({"t1":5, "t2":10, "midterm":14, "t3":19, "t4":23, "final":26})

rows = [("00-syllabus", "&mdash;", "Syllabus &amp; 26-Week Schedule",
         "Course format (3-hour weekly blocks), outcomes, grading, policies, and the full week-by-week plan")]
for k in order:
    s = spec[k]
    rows.append((k, str(wk[k]),
                 re.sub(r'<[^>]+>', '', s["title"]),
                 re.sub(r'<[^>]+>', '', s["sub"]).replace("&nbsp;", "").replace("&middot;", "·")))

out = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Course File Index</title><!--STYLE--></head><body>',
       '<div class="masthead"><p class="course">Physical Geography · Grades 9–12 · 3-Hour Weekly Blocks</p>'
       '<h1>Course File Index</h1><p class="sub">Every document in this course, in the order you will use it. '
       'Each week is one three-hour class meeting. Each assessment has a matching <strong>-key</strong> file — '
       'print the plain file for the student and keep the key.</p></div>',
       '<h2>Documents</h2><table><thead><tr><th class="num" style="width:6%">Wk</th><th style="width:15%">File</th>'
       '<th style="width:30%">Document</th><th>Details</th><th class="num" style="width:7%">Pages</th></tr></thead><tbody>']
tot = 0
for k, w, t, d in rows:
    p, kp = pages(D/"pdf"/f"{k}.pdf"), pages(D/"pdf"/f"{k}-key.pdf")
    tot += p + kp
    cls = ' class="exam"' if k in ("midterm", "final") else ''
    fname = f"{k}.pdf" + (f" + {k}-key.pdf" if kp else "")
    out.append(f'<tr{cls}><td class="num">{w}</td><td style="font-family:monospace;font-size:8.4pt">{fname}</td>'
               f'<td><strong>{t}</strong></td><td class="assess">{d}</td>'
               f'<td class="num">{p}{"+"+str(kp) if kp else ""}</td></tr>')
out += ['</tbody></table>',
        f'<p class="small">31 documents · 62 PDF files · {tot} pages total.</p>',
        '''<h2>How to Use These Files</h2>
<ul>
<li><strong>Student copies</strong> are the plain files (<code>q07.pdf</code>, <code>t3.pdf</code>). They carry a name/date/score line and end with an "— END —" marker.</li>
<li><strong>Answer keys</strong> are the <code>-key</code> files. Every key gives the correct answer, a page citation into the textbook, and a point-by-point grading rubric for written responses.</li>
<li><strong>Timing.</strong> A standard block runs quiz (15 min) → instruction (55) → activity (50) → discussion (20). Test blocks trade the activity and discussion time for a 30-minute review and the 50-minute test. Exam blocks are 75 minutes of review and a 90-minute exam.</li>
<li><strong>Page references</strong> throughout use the textbook's printed page numbers. If you are reading the PDF on screen, add 2.</li>
<li><strong>To edit anything</strong>, change the matching file in <code>spec/</code>, then run <code>python3 gen.py &amp;&amp; ./build.sh</code>. Run <code>python3 mkindex.py &amp;&amp; ./build.sh 01-index.html</code> to refresh this page.</li>
</ul>''',
        '<div class="footer-note">Physical Geography · 26-Week Course · Textbook by Jeremy Patrich, College of the Canyons, CC BY 4.0</div>',
        '</body></html>']
(D/"src"/"01-index.html").write_text("\n".join(out), encoding="utf-8")
print("wrote src/01-index.html")
