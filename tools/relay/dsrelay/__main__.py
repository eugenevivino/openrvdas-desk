import argparse
import json
from .common import owned
from .project import prepare, execute, read_report
p=argparse.ArgumentParser(description='DeepSignal adapters for supplied Relay; test-only pilot')
s=p.add_subparsers(dest='command',required=True)
a=s.add_parser('pilot'); a.add_argument('--root',required=True)
a=s.add_parser('run'); a.add_argument('--plan',required=True); a.add_argument('--state',required=True)
a=s.add_parser('report'); a.add_argument('--state',required=True)
a=p.parse_args()
if a.command=='pilot': result=execute(prepare(a.root),owned(a.root)/'state')
elif a.command=='run': result=execute(json.loads(owned(a.plan).read_text()),owned(a.state))
else:
    result=read_report(a.state)
print(json.dumps(result,indent=2))

if a.command!='report' and any(m['state']!='batch_tested' for m in result['modules']):
    raise SystemExit(2)
