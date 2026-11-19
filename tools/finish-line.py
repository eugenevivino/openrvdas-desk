#!/usr/bin/env python3
"""Finish-line counts for DeepSignal units (D-PIPE1 rule 2). Stdlib only.

Reads docs/units.json: {"units": [{"unit", "branch", "head", "critical", "stamps": {stamp: {"ok", "evidence",
"at"}}}], "superseded": [...]}. A stamp counts only when ok is true, evidence is non-empty and "at" equals the
unit head (a stamp proven on an older head is stale and does not count).

  LANDED    = moved
  QUALIFIED = tested and fixed
  FINISHED  = moved, tested, fixed, in_app and tested_in_app

Usage: python3 tools/finish-line.py [--manifest docs/units.json] [--all] [--unit NAME]
Never compute these numbers from PR or branch counts.
"""
import argparse
import json
import sys
from pathlib import Path

STAMPS = ('moved', 'tested', 'fixed', 'in_app', 'tested_in_app')


def counts(stamp, head):
    return bool(stamp.get('ok')) and bool(stamp.get('evidence')) and stamp.get('at') == head


def check(unit):
    head = unit.get('head', '')
    marks, notes = {}, []
    for name in STAMPS:
        stamp = unit.get('stamps', {}).get(name, {})
        marks[name] = counts(stamp, head)
        if stamp.get('ok') and not marks[name]:
            notes.append('%s claimed but not counted (evidence %s, at %s, head %s)'
                         % (name, 'present' if stamp.get('evidence') else 'missing', stamp.get('at') or '?', head))
    landed = marks['moved']
    qualified = marks['tested'] and marks['fixed']
    finished = all(marks.values())
    return marks, landed, qualified, finished, notes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--manifest', default=str(Path(__file__).resolve().parents[1] / 'docs' / 'units.json'))
    parser.add_argument('--all', action='store_true', help='list every unit, not only those with a stamp')
    parser.add_argument('--unit', help='show one unit with its evidence')
    args = parser.parse_args(argv)
    try:
        data = json.loads(Path(args.manifest).read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        print('finish-line: cannot read %s: %s' % (args.manifest, error), file=sys.stderr)
        return 2
    units = data.get('units', [])
    totals = {'LANDED': 0, 'QUALIFIED': 0, 'FINISHED': 0}
    rows = []
    for unit in units:
        marks, landed, qualified, finished, notes = check(unit)
        totals['LANDED'] += landed
        totals['QUALIFIED'] += qualified
        totals['FINISHED'] += finished
        rows.append((unit, marks, notes))
    active = sum(1 for u in units if str(u.get('status', '')).startswith('ACTIVE'))
    print('LANDED %d  QUALIFIED %d  FINISHED %d  (of %d units: %d active, %d paused; %d superseded branches)'
          % (totals['LANDED'], totals['QUALIFIED'], totals['FINISHED'], len(units), active,
             len(units) - active, len(data.get('superseded', []))))
    print('stamps: M moved, T tested, F fixed, A in app, P tested in app; X counted, . not')
    for unit, marks, notes in rows:
        if args.unit and unit.get('unit') != args.unit:
            continue
        if not (args.all or args.unit or any(marks.values()) or notes):
            continue
        grid = ''.join('X' if marks[name] else '.' for name in STAMPS)
        crit = ' CRITICAL' if unit.get('critical') else ''
        print('  %s  %-28s %-8s %s%s' % (grid, unit.get('unit'), unit.get('head'), unit.get('branch'), crit))
        for note in notes:
            print('        stale: ' + note)
        if args.unit:
            for name in STAMPS:
                stamp = unit.get('stamps', {}).get(name, {})
                print('        %-14s %s' % (name, stamp.get('evidence') or '(no evidence)'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
