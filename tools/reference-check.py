#!/usr/bin/env python3
"""Check that docs/REFERENCE.md covers every IDEAS number and every brief.

Usage:
  python3 tools/reference-check.py            # exit 1 and list gaps
  python3 tools/reference-check.py --backlog  # rewrite the generated backlog
                                              # index in REFERENCE.md, then check

An IDEAS row counts as covered when "#<n>" appears in REFERENCE.md. A brief
counts as covered when its path (briefs/...) or the IDEAS number in its file
name (briefs/p2/104-erddap.md -> #104) appears there. Standard library only.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / 'docs' / 'REFERENCE.md'
IDEAS = ROOT / 'docs' / 'IDEAS.md'
START = '<!-- backlog-index:'
END = '<!-- /backlog-index -->'
# Brief folders that hold feature work. briefs/cloud and briefs/mac are
# prompt copies of briefs/console and briefs/p2, so they are not checked.
BRIEF_GLOBS = ['briefs/console/*.md', 'briefs/p2/*.md', 'briefs/deepsignal-*.md',
               'briefs/install-clock.md', 'briefs/gate-linux-r3.md']
BRIEF_SKIP = {'INDEX.md', 'INTEGRATION.md'}


def idea_rows():
    """Yield (number, name, status) from IDEAS.md table rows."""
    for line in IDEAS.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 4 or not cells[0].isdigit():
            continue
        status = next((c.split()[0] for c in cells[2:]
                       if c.split() and c.split()[0].rstrip(',.:') in
                       ('PROPOSED', 'DESIGNED', 'BUILDING', 'DONE', 'DROPPED')), '?')
        yield int(cells[0]), cells[1], status.rstrip(',.:')


def covered(text, n):
    return re.search(r'#%d(?!\d)' % n, text) is not None


def write_backlog():
    text = REF.read_text()
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    body_text = head + tail
    lines = ['- #%d %s (%s)' % (n, name, st) for n, name, st in idea_rows()
             if not covered(body_text, n)]
    marker = START + ' generated from docs/IDEAS.md by tools/reference-check.py --backlog; edit IDEAS, not here -->'
    REF.write_text(head + marker + '\n' + '\n'.join(lines) + '\n' + END + tail)


def main():
    if '--backlog' in sys.argv:
        write_backlog()
    text = REF.read_text()
    missing_ideas = [n for n, _, _ in idea_rows() if not covered(text, n)]
    missing_briefs = []
    for pattern in BRIEF_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            if path.name in BRIEF_SKIP:
                continue
            rel = path.relative_to(ROOT).as_posix()
            num = re.match(r'(\d+)-', path.name)
            if rel in text or (num and covered(text, int(num.group(1)))):
                continue
            missing_briefs.append(rel)
    if missing_ideas or missing_briefs:
        print('docs/REFERENCE.md is missing entries. Add them, or run '
              'tools/reference-check.py --backlog for new IDEAS rows.')
        for n in missing_ideas:
            print('  IDEAS #%d' % n)
        for b in missing_briefs:
            print('  brief %s' % b)
        return 1
    print('REFERENCE.md covers all IDEAS rows and briefs.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
