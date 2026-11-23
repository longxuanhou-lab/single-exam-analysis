"""Add an approved illustrated cover and print an A4 exam report."""
import argparse
import base64
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from html import escape

TEMPLATES = Path(__file__).resolve().parents[1] / "templates"
COVERS = {
    "语文": "chinese", "数学": "math", "英语": "english", "物理": "physics",
    "历史": "history", "化学": "chemistry", "生物": "biology", "地理": "geography",
    "政治": "politics", "思想政治": "politics",
}


def browser_path(explicit):
    if explicit:
        return explicit
    for name in ("msedge", "google-chrome", "chromium", "chromium-browser", "chrome"):
        if path := shutil.which(name):
            return path
    for variable in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"):
        if location := os.environ.get(variable):
            for relative in ("Microsoft/Edge/Application/msedge.exe", "Google/Chrome/Application/chrome.exe"):
                path = Path(location, relative)
                if path.is_file():
                    return str(path)
    for executable in ("Google Chrome", "Microsoft Edge", "Chromium"):
        path = Path(f"/Applications/{executable}.app/Contents/MacOS/{executable}")
        if path.is_file():
            return str(path)
    raise SystemExit("Chromium browser unavailable. Use --browser or export .html and print it with a PDF tool.")


def illustration(key, class_name):
    data = base64.b64encode((TEMPLATES / f"{key}.jpg").read_bytes()).decode("ascii")
    return f'<img class="{class_name}" src="data:image/jpeg;base64,{data}" alt="手绘小书人">'


def create_cover(args):
    exam = escape(args.exam)
    class_name = escape(args.class_name)
    banner = f'<div class="banner"><span>{escape(args.brand)}</span><span>{escape(args.series)}</span></div>'
    if args.kind == "student":
        subject = "思想政治" if args.subject == "政治" else args.subject
        title = f"{subject or ''}个人学情报告"
        return title, f"""
        <section class="cover student-cover">
          {banner}
          <h1>{escape(title)}</h1>
          <p class="exam">{exam}</p>
          <div class="student-front">
            <div class="identity"><small>姓名</small><strong>{escape(args.student_name)}</strong>
              <small>班级</small><strong>{class_name}</strong></div>
            {illustration("student", "student-art")}
          </div>
        </section>"""
    if args.kind == "subject":
        subject = "思想政治" if args.subject == "政治" else args.subject
        return f"{subject}学科成绩分析", f"""
        <section class="cover subject-cover">
          {banner}
          <div class="cover-titles"><div><h1>{escape(subject)}</h1><h2>学科成绩分析</h2></div>
            <div class="cover-meta"><strong>{class_name}</strong><span>{exam}</span></div></div>
          <div class="illustration">{illustration(COVERS[subject], "subject-art")}</div>
        </section>"""
    title = escape(args.title)
    return args.title, f"""
    <section class="cover overview-cover">
      {banner}
      <h1>{title}</h1>
      <p class="exam">{exam}</p><strong>{class_name}</strong>
      <div class="illustration">{illustration("student", "overview-art")}</div>
    </section>"""


def document(args):
    title, cover = create_cover(args)
    css = (TEMPLATES / "report.css").read_text(encoding="utf-8")
    body = args.body.read_text(encoding="utf-8-sig")
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>{escape(title)}</title>
<style>{css}</style></head><body class="{args.kind}-report">{cover}{body}</body></html>"""


def print_pdf(html, output, browser):
    with tempfile.TemporaryDirectory(prefix="single-exam-print-") as directory:
        work = Path(directory)
        source = work / "report.html"
        dest = work / "report.pdf"
        source.write_text(html, encoding="utf-8")
        result = subprocess.run([
            browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
            f"--user-data-dir={work / 'profile'}", f"--print-to-pdf={dest}", source.as_uri(),
        ], capture_output=True, timeout=90)
        if result.returncode != 0 or not dest.is_file() or dest.stat().st_size < 100:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            raise SystemExit(f"Browser did not produce the PDF. {detail}")
        shutil.copyfile(dest, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("body", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--kind", required=True, choices=("subject", "student", "overview"))
    parser.add_argument("--subject", choices=COVERS)
    parser.add_argument("--student-name", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--class-name", default="")
    parser.add_argument("--exam", required=True)
    parser.add_argument("--brand", default="")
    parser.add_argument("--series", default="")
    parser.add_argument("--browser")
    args = parser.parse_args()
    if args.kind == "subject" and not args.subject:
        parser.error("subject reports require --subject")
    if args.kind == "student" and not (args.student_name and args.class_name):
        parser.error("student reports require --student-name and --class-name")
    if args.kind == "overview" and not args.title:
        parser.error("overview reports require --title")
    suffix = args.output.suffix.lower()
    if suffix not in (".html", ".pdf"):
        parser.error("output must end in .html or .pdf")
    if args.body.resolve() == args.output.resolve():
        parser.error("body and output must use different paths")
    html = document(args)
    if suffix == ".html":
        args.output.write_text(html, encoding="utf-8")
    else:
        print_pdf(html, args.output.resolve(), browser_path(args.browser))


if __name__ == "__main__":
    main()
