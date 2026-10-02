"""Compare the prose revision with its frozen predecessor."""
from collections import Counter
from pathlib import Path
import difflib
import hashlib
import json
import re

RUN = Path(__file__).resolve().parents[1]
SRC = Path('/home/data3/txy/docs/paper/latex')
OLD = RUN / 'before'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clean(s):
    return re.sub(r'(?m)(?<!\\)%.*$', '', s)


def closure(root):
    found = set()
    def visit(rel):
        if rel in found:
            return
        found.add(rel)
        for name in re.findall(r'\\input\{([^}]+)\}', clean((root / rel).read_text())):
            visit(name if name.endswith('.tex') else name + '.tex')
    visit('main.tex')
    return found


def main():
    current, previous = closure(SRC), closure(OLD)
    errors = []
    if current != previous:
        errors.append('Changed TeX dependency set')
    rows, all_diffs = [], []
    for rel in sorted(current | previous):
        before, after = (OLD / rel).read_text(), (SRC / rel).read_text()
        a, b = clean(before), clean(after)
        nums = lambda s: Counter(re.findall(r'(?<![A-Za-z])\d+(?:[.,]\d+)*', s.replace('{,}', ',')))
        removed, added = nums(a) - nums(b), nums(b) - nums(a)
        approved = rel == 'sections/appendix_components.tex' and removed == {'288': 1} and not added
        if (removed or added) and not approved:
            errors.append({'unexpected_numeric_change': rel, 'removed': dict(removed), 'added': dict(added)})
        commands = r'\\(?:cite\w*|ref|eqref|label|input|includegraphics)(?:\[[^]]*\])?\{[^}]+\}'
        same_refs = Counter(re.findall(commands, a)) == Counter(re.findall(commands, b))
        equations = r'\\begin\{equation\}.*?\\end\{equation\}'
        same_equations = re.findall(equations, a, re.S) == re.findall(equations, b, re.S)
        if not same_refs or not same_equations:
            errors.append({'changed_references_or_equations': rel})
        changed = before != after
        if changed:
            all_diffs.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                                fromfile='before/' + rel, tofile='after/' + rel, n=0))
        rows.append({'path': rel, 'changed': changed, 'before_sha256': digest(OLD / rel),
                     'after_sha256': digest(SRC / rel), 'removed_numbers': dict(removed),
                     'added_numbers': dict(added), 'approved_repetition_removal': approved,
                     'references_preserved': same_refs, 'equations_preserved': same_equations})
    protected = [p for p in OLD.rglob('*') if p.is_file() and
                 (p.relative_to(OLD).parts[0] in ['figures', 'tables', 'inputs', 'scripts'] or
                  p.name in ['references.bib', 'build.sh'])]
    protected_checks = []
    for p in protected:
        rel = p.relative_to(OLD)
        same = (SRC / rel).is_file() and digest(p) == digest(SRC / rel)
        protected_checks.append({'path': str(rel), 'unchanged': same, 'sha256': digest(p)})
        if not same:
            errors.append({'changed_data_or_asset': str(rel)})
    report = {'status': 'PASS' if not errors else 'FAIL',
              'source': str(SRC), 'before': str(OLD), 'files': rows,
              'changed_tex_files': sum(x['changed'] for x in rows),
              'protected_files': protected_checks, 'errors': errors,
              'numeric_exception': 'One redundant 288 in the contrast with independent patients was removed; 288 queries and 24 virtual profiles remain stated.',
              'scope': 'Numeric tokens, equations, citation/ref keys and asset hashes; meaning is assessed separately by independent review.'}
    (RUN / 'review/revision_diff.patch').write_text(''.join(all_diffs))
    (RUN / 'review/revision_preservation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'changed_tex_files': report['changed_tex_files'],
                      'protected_files': len(protected_checks), 'errors': errors}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
