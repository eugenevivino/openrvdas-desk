"""Separate reservation wait from dispatcher delay using recorded intervals."""
import statistics

def samples(rows, capacities, max_parallel):
    by_id={r['id']:r for r in rows}; output=[]
    for row in rows:
        result=row.get('result') or {}; start=result.get('started_at')
        deps=row['spec'].get('deps',[])
        finishes=[(by_id[d].get('result') or {}).get('finished_at') for d in deps]
        if not deps or start is None or any(t is None for t in finishes): continue
        ready=max(finishes); opportunity=ready
        others=[r for r in rows if r['id']!=row['id'] and r.get('started_at') is not None and r.get('finished_at') is not None and r['started_at']<start and r['finished_at']>ready]
        events=sorted({ready,start}|{max(ready,r['started_at']) for r in others}|{min(start,r['finished_at']) for r in others})
        for left,right in zip(events,events[1:]):
            active=[r for r in others if r['started_at']<=left<r['finished_at']]
            used={k:sum(r['spec'].get('resources',{}).get(k,0) for r in active) for k in capacities}
            blocked=len(active)>=max_parallel or any(used[k]+n>capacities[k] for k,n in row['spec'].get('resources',{}).items())
            if blocked: opportunity=right
        output.append({'job':row['id'],'dependency_finish_to_start_s':max(0,start-ready),'reservation_wait_s':max(0,opportunity-ready),'capacity_available_to_start_s':max(0,start-opportunity)})
    return output

def summarize(values):
    return {'samples':len(values),'median':statistics.median(values) if values else None,'maximum':max(values) if values else None}
