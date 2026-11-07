"""Build a PEP 503 simple index (for GitHub Pages) from a folder of wheels."""
import argparse
import hashlib
import html
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path


def page(body):
    return f"<!DOCTYPE html>\n<html><body>\n{body}</body></html>\n"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("wheels_dir", type=Path)
    parser.add_argument("site_dir", type=Path)
    args = parser.parse_args(argv)

    wheels = sorted(args.wheels_dir.glob("*.whl"))
    if not wheels:
        sys.exit(f"no .whl files in {args.wheels_dir}; refusing to publish an empty index")

    projects = defaultdict(list)
    for wheel in wheels:
        name = re.sub(r"[-_.]+", "-", wheel.name.split("-")[0]).lower()
        projects[name].append(wheel)

    simple, files = args.site_dir / "simple", args.site_dir / "files"
    files.mkdir(parents=True, exist_ok=True)
    for name, project_wheels in projects.items():
        links = ""
        for wheel in project_wheels:
            shutil.copy2(wheel, files / wheel.name)
            digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
            fname = html.escape(wheel.name)
            links += f'<a href="../../files/{fname}#sha256={digest}">{fname}</a><br>\n'
        (simple / name).mkdir(parents=True, exist_ok=True)
        (simple / name / "index.html").write_text(page(links))
    (simple / "index.html").write_text(page("".join(f'<a href="{n}/">{n}</a><br>\n' for n in projects)))


if __name__ == "__main__":
    main()
