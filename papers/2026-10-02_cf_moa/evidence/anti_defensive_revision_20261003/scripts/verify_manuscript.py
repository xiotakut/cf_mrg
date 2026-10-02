#!/usr/bin/env python3
"""Check a compiled manuscript without changing its sources or invoking TeX.

Usage: python3 scripts/verify_manuscript.py [--source-dir draft] [--review-dir review]
Requires PyMuPDF (``python3 -m pip install pymupdf``), installed normally or made
available through PYTHONPATH. No workstation-specific dependency path is used.
This is a static integrity check, not a scientific or visual-layout review.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys


PACKAGE = Path(__file__).resolve().parents[1]
INPUT = re.compile(r"\\(?:input|include)(?![A-Za-z@])\s*(?:\{([^{}]+)\}|([^\s{}%]+))")
CITE = re.compile(
    r"\\(?:[Cc]ite(?:p|t|alp|alt|author|year(?:par)?)?|autocite|parencite|textcite|nocite)"
    r"\*?(?:\s*\[[^\]]*\])*\s*\{([^{}]+)\}"
)
REF = re.compile(r"\\(?:ref|eqref|autoref|pageref|[Cc]ref)\*?\s*\{([^{}]+)\}")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_tex(text):
    """Mask comments and verbatim bodies for structural inspection only."""
    text = re.sub(
        r"\\begin\{(verbatim\*?|Verbatim|lstlisting)\}[\s\S]*?\\end\{\1\}",
        lambda m: "\n" * m.group(0).count("\n"), text,
    )
    text = re.sub(r"\\verb\*?(.).*?\1", "", text)
    lines = []
    for line in text.splitlines(keepends=True):
        for i, char in enumerate(line):
            if char == "%":
                slashes = len(line[:i]) - len(line[:i].rstrip("\\"))
                if slashes % 2 == 0:
                    line = line[:i] + ("\n" if line.endswith("\n") else "")
                    break
        lines.append(line)
    return "".join(lines)


def brace_issues(text):
    stack, issues = [], []
    line, i = 1, 0
    while i < len(text):
        char = text[i]
        if char == "\\":
            # Escaped braces and backslashes are not grouping delimiters.
            if i + 1 < len(text) and not text[i + 1].isalpha():
                i += 2
                continue
        elif char == "\n":
            line += 1
        elif char == "{":
            stack.append(line)
        elif char == "}":
            if stack:
                stack.pop()
            else:
                issues.append({"line": line, "issue": "unmatched closing brace"})
        i += 1
    issues.extend({"line": n, "issue": "unmatched opening brace"} for n in stack)
    return issues


def word_count(text):
    """Approximate English tokens, including headings/captions/table cells."""
    text = re.sub(r"\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|\$[^$]*\$", " ", text)
    text = re.sub(r"\\begin\{(?:equation|align|gather)\*?\}[\s\S]*?"
                  r"\\end\{(?:equation|align|gather)\*?\}", " ", text)
    text = CITE.sub(" ", text)
    text = REF.sub(" ", text)
    text = re.sub(r"\\(?:label|bibliography|bibliographystyle|includegraphics|"
                  r"begin|end|vspace|hspace|setlength)\*?(?:\[[^\]]*\])?"
                  r"\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?", " ", text)
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", text))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=PACKAGE / "draft")
    parser.add_argument("--review-dir", type=Path, default=PACKAGE / "review")
    args = parser.parse_args()
    source = args.source_dir.expanduser().resolve()
    review = args.review_dir.expanduser().resolve()
    review.mkdir(parents=True, exist_ok=True)
    errors, warnings, tex_files, dependencies, edges = [], [], {}, {}, []

    def relative(path):
        try:
            return str(path.relative_to(source))
        except ValueError:
            return str(path)

    def remember(path, kind):
        key = relative(path)
        if key not in dependencies:
            dependencies[key] = {
                "kind": kind, "bytes": path.stat().st_size, "sha256": digest(path),
                "mtime_ns": path.stat().st_mtime_ns,
            }
        return key

    def resolve(name, parent, suffixes=("",), extra=()):
        candidate = Path(name)
        bases = [source, parent.parent, *extra] if not candidate.is_absolute() else [Path("/")]
        for base in bases:
            for suffix in suffixes:
                path = (base / (name + suffix)).resolve()
                if path.is_file():
                    return path
        return None

    def expand(path, active=()):
        if path in active:
            errors.append({"check": "input_cycle", "path": relative(path)})
            return ""
        if not path.is_file():
            errors.append({"check": "missing_tex", "path": relative(path)})
            return ""
        remember(path, "tex")
        text = clean_tex(path.read_text(encoding="utf-8"))
        tex_files[path] = text
        for issue in brace_issues(text):
            errors.append({"check": "tex_braces", "path": relative(path), **issue})

        def replace(match):
            name = match.group(1) or match.group(2)
            child = resolve(name, path, ("", ".tex"))
            edges.append({"from": relative(path), "input": name,
                          "resolved": relative(child) if child else None})
            if child is None:
                errors.append({"check": "missing_input", "path": relative(path), "input": name})
                return ""
            return expand(child, (*active, path))

        return INPUT.sub(replace, text)

    expanded = expand(source / "main.tex")
    graphic_dirs = []
    for match in re.finditer(r"\\graphicspath\s*\{((?:\s*\{[^{}]*\})+\s*)\}", expanded):
        graphic_dirs.extend((source / p).resolve() for p in re.findall(r"\{([^{}]*)\}", match[1]))

    graphics = []
    for match in re.finditer(r"\\includegraphics\*?(?:\s*\[[^\]]*\])?\s*\{([^{}]+)\}", expanded):
        path = resolve(match[1], source / "main.tex", ("", ".pdf", ".png", ".jpg", ".jpeg"), graphic_dirs)
        graphics.append({"reference": match[1], "path": relative(path) if path else None})
        if path:
            remember(path, "figure")
        else:
            errors.append({"check": "missing_figure", "reference": match[1]})

    bib_keys, bib_files = [], []
    for match in re.finditer(r"\\(?:bibliography|addbibresource)(?:\[[^\]]*\])?\s*\{([^{}]+)\}", expanded):
        for name in match[1].split(","):
            path = resolve(name.strip(), source / "main.tex", ("", ".bib"))
            if path is None:
                errors.append({"check": "missing_bibliography", "reference": name})
                continue
            remember(path, "bibliography")
            bib_files.append(relative(path))
            bib_keys.extend(re.findall(r"(?im)^\s*@(?!comment\b|string\b|preamble\b)\w+\s*[{(]\s*([^,\s]+)\s*,",
                                       path.read_text(encoding="utf-8")))
    cited_keys = {key.strip() for m in CITE.finditer(expanded) for key in m[1].split(",")}
    wildcard = "*" in cited_keys
    cited_keys.discard("*")
    labels = re.findall(r"\\label\s*\{([^{}]+)\}", expanded)
    ref_keys = {key.strip() for m in REF.finditer(expanded) for key in m[1].split(",")}
    for check, keys in (
        ("undefined_citation", sorted(cited_keys - set(bib_keys))),
        ("undefined_reference", sorted(ref_keys - set(labels))),
        ("duplicate_bib_key", sorted(k for k, n in Counter(bib_keys).items() if n > 1)),
        ("duplicate_label", sorted(k for k, n in Counter(labels).items() if n > 1)),
    ):
        if keys:
            errors.append({"check": check, "keys": keys})

    if r"\begin{document}" not in expanded or r"\end{document}" not in expanded:
        errors.append({"check": "missing_document_environment"})
    body = expanded.partition(r"\begin{document}")[2]
    main_text, marker, appendix = body.partition(r"\appendix")
    pdf_path = next((p for p in (source / "build/main.pdf", source / "main.pdf") if p.is_file()), None)
    log_path = next((p for p in (source / "build/main.log", source / "main.log") if p.is_file()), None)
    pdf_report, log_report, compiled_bib = {}, {}, {}
    bbl_path = next((p for p in (source / "build/main.bbl", source / "main.bbl") if p.is_file()), None)
    if bbl_path:
        rendered_keys = set(re.findall(r"\\bibitem(?:\[[\s\S]*?\])?\s*\{([^{}]+)\}",
                                       bbl_path.read_text(encoding="utf-8")))
        compiled_bib = {"path": relative(bbl_path), "sha256": digest(bbl_path),
                        "entries": len(rendered_keys), "keys": sorted(rendered_keys)}
        if cited_keys - rendered_keys:
            errors.append({"check": "cited_keys_missing_from_bbl", "keys": sorted(cited_keys - rendered_keys)})
    elif cited_keys:
        warnings.append({"check": "compiled_bibliography_unavailable", "message": "Source citation keys checked; compiled .bbl could not be inspected."})
    try:
        import pymupdf
    except ImportError:
        pymupdf = None
        errors.append({"check": "pdf_dependency", "message": "PyMuPDF unavailable; install pymupdf or set PYTHONPATH."})
    if pdf_path is None:
        errors.append({"check": "missing_compiled_pdf"})
    elif pymupdf is not None:
        try:
            with pymupdf.open(pdf_path) as doc:
                page_stats = []
                for number, page in enumerate(doc, 1):
                    text = page.get_text()
                    page_stats.append({"page": number, "text_characters": len(text),
                                       "width_pt": page.rect.width, "height_pt": page.rect.height})
                    for token, check in (("??", "pdf_unresolved_marker"), ("\ufffd", "pdf_replacement_character"),
                                         ("\x00", "pdf_nul_character")):
                        if token in text:
                            index = text.index(token)
                            errors.append({"check": check, "page": number,
                                           "context": text[max(0, index - 60):index + 60]})
                    if not text.strip():
                        warnings.append({"check": "page_without_extractable_text", "page": number})
                if not len(doc):
                    errors.append({"check": "empty_pdf"})
                pdf_report = {"path": relative(pdf_path), "sha256": digest(pdf_path),
                              "bytes": pdf_path.stat().st_size, "pages": len(doc),
                              "text_characters": sum(p["text_characters"] for p in page_stats),
                              "metadata": doc.metadata, "page_statistics": page_stats,
                              "pymupdf_version": pymupdf.VersionBind}
            for item in graphics:
                if item["path"] and item["path"].lower().endswith(".pdf"):
                    with pymupdf.open(source / item["path"]) as figure:
                        item["pdf_pages"] = len(figure)
                        if not len(figure):
                            errors.append({"check": "empty_figure_pdf", "path": item["path"]})
        except Exception as exc:
            errors.append({"check": "pdf_read_error", "message": str(exc)})

    if log_path is None:
        errors.append({"check": "missing_compile_log"})
    else:
        log = log_path.read_text(encoding="utf-8", errors="replace")
        bad = []
        pattern = re.compile(r"Overfull\s+\\[hv]box|Missing character:|Undefined control sequence|"
                             r"(?:Citation|Reference).*undefined|There were undefined (?:references|citations)|^!", re.I)
        for number, line in enumerate(log.splitlines(), 1):
            if pattern.search(line):
                bad.append({"line": number, "message": line.strip()})
        if bad:
            errors.append({"check": "compile_log", "messages": bad})
        log_report = {"path": relative(log_path), "sha256": digest(log_path),
                      "blocking_messages": bad,
                      "underfull_boxes": len(re.findall(r"Underfull\s+\\[hv]box", log)),
                      "warning_lines": [line.strip() for line in log.splitlines() if "Warning:" in line]}
    if pdf_path and dependencies:
        newest = max(v["mtime_ns"] for v in dependencies.values())
        pdf_report["mtime_at_least_source_mtimes"] = pdf_path.stat().st_mtime_ns >= newest
        if pdf_path.stat().st_mtime_ns < newest:
            warnings.append({"check": "source_newer_than_pdf", "message": "Rebuild before final acceptance; timestamps alone do not bind PDF to source content."})

    # Detect edits during this read-only check rather than silently mixing versions.
    for name, info in dependencies.items():
        path = source / name
        if not path.is_file() or digest(path) != info["sha256"]:
            errors.append({"check": "source_changed_during_check", "path": name})
    manifest = {name: info["sha256"] for name, info in sorted(dependencies.items())}
    source_hash = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    report = {
        "schema_version": 1, "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not errors else "FAIL", "source_dir": str(source),
        "entrypoint": "main.tex", "source_closure_sha256": source_hash,
        "checker": {"name": Path(__file__).name, "sha256": digest(Path(__file__))},
        "source_hash_definition": "SHA-256 of compact sorted JSON mapping closure-relative filenames to file SHA-256 hashes",
        "files": dict(sorted(dependencies.items())), "input_edges": edges,
        "counts": {"tex_files": len(tex_files), "source_closure_files": len(dependencies),
                   "figure_environments": len(re.findall(r"\\begin\{figure\*?\}", expanded)),
                   "graphics_inclusions": len(graphics), "unique_figure_files": len({x["path"] for x in graphics if x["path"]}),
                   "table_environments": len(re.findall(r"\\begin\{(?:table\*?|longtable)\}", expanded)),
                   "bib_entries": len(bib_keys), "unique_cited_keys": len(cited_keys),
                   "labels": len(labels), "unique_referenced_labels": len(ref_keys),
                   "main_approximate_english_words": word_count(main_text),
                   "appendix_approximate_english_words": word_count(appendix) if marker else 0},
        "word_count_scope": "Expanded TeX body split at appendix; approximate English tokens including headings, captions, and table cells, excluding preamble, bibliography text, math, citation/ref keys, and control sequences. Not a venue-certified word count.",
        "bibliography": {"files": bib_files, "cited_keys": sorted(cited_keys), "all_keys": sorted(set(bib_keys)),
                         "unused_keys": sorted(set(bib_keys) - cited_keys), "nocite_wildcard": wildcard,
                         "compiled": compiled_bib},
        "graphics": graphics, "pdf": pdf_report, "compile_log": log_report,
        "errors": errors, "warnings": warnings,
        "limits": ["Static literal input/figure/bibliography closure; does not implement TeX macro execution.",
                   "No missing-character log messages or replacement markers is not proof of perfect glyph rendering.",
                   "No automated overlap or visual-layout claim; manual page inspection remains separate.",
                   "Does not validate scientific claims, numerical result provenance, author identities, or citation metadata.",
                   "Hashes bind this check to read files; source/PDF correspondence also requires the build receipt."],
    }
    target = review / "manuscript_integrity.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(target), "counts": report["counts"],
                      "pdf_pages": pdf_report.get("pages"), "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
