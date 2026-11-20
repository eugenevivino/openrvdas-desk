"""Measure Relay reservations using durable claim and completion events."""
import math
import statistics


def _timestamp(stamp):
    return type(stamp) in (int, float) and math.isfinite(stamp)


def _reservations(rows, events):
    if events is None:
        return None
    by_id = {row['id']: row for row in rows}
    attempts = dict.fromkeys(by_id, 0)
    tokens = dict.fromkeys(by_id, 0)
    pending = {}
    intervals = []
    for event in events:
        job, stamp, data = event['job_id'], event['created_at'], event['data']
        if job not in by_id or not _timestamp(stamp) or not isinstance(data, dict):
            return None
        token = data.get('token')
        if type(token) is not int:
            return None
        if event['kind'] == 'claimed':
            if job in pending or data.get('attempt') != attempts[job] + 1 or token <= tokens[job]:
                return None
            attempts[job] += 1
            tokens[job] = token
            pending[job] = (token, stamp)
        elif event['kind'] == 'finished':
            claim = pending.pop(job, None)
            if claim is None or claim[0] != token or stamp < claim[1]:
                return None
            intervals.append((job, token, claim[1], stamp, by_id[job]['spec'].get('resources', {})))

    for job, row in by_id.items():
        active = row['state'] in {'running', 'uncertain'}
        if (attempts[job] != row['attempt'] or tokens[job] != row['token']
                or active != (job in pending)):
            return None
        if active:
            token, claim = pending[job]
            intervals.append((job, token, claim, math.inf, row['spec'].get('resources', {})))
    return intervals


def samples(rows, capacities, max_parallel, *, attempt_events=None, reservation_rows=None):
    by_id = {row['id']: row for row in rows}
    reservations = _reservations(rows if reservation_rows is None else reservation_rows, attempt_events)
    output = []
    for row in rows:
        start = (row.get('result') or {}).get('started_at')
        deps = row['spec'].get('deps', [])
        finishes = [(by_id.get(dep, {}).get('result') or {}).get('finished_at') for dep in deps]
        if not deps or not _timestamp(start) or not all(map(_timestamp, finishes)):
            continue
        ready = max(finishes)
        raw = max(0, start - ready)
        wait = None
        if reservations is not None:
            wait = 0
            overlapping = [
                interval for interval in reservations
                if interval[:2] != (row['id'], row['token'])
                and interval[2] < start and interval[3] > ready
            ] if ready < start else []
            boundaries = sorted({ready, start}
                                | {max(ready, interval[2]) for interval in overlapping}
                                | {min(start, interval[3]) for interval in overlapping})
            for left, right in zip(boundaries, boundaries[1:]):
                active = [interval for interval in overlapping if interval[2] <= left < interval[3]]
                used = {name: sum(interval[4].get(name, 0) for interval in active) for name in capacities}
                same_job = any(interval[0] == row['id'] for interval in active)
                if same_job or len(active) >= max_parallel or any(
                    used[name] + count > capacities[name] for name, count in row['spec'].get('resources', {}).items()
                ):
                    wait += right - left
        output.append({
            'job': row['id'], 'dependency_finish_to_start_s': raw, 'reservation_wait_s': wait,
            'capacity_available_to_start_s': max(0, raw - wait) if wait is not None else None,
        })
    return output


def summarize(values):
    return {'samples': len(values), 'median': statistics.median(values) if values else None,
            'maximum': max(values) if values else None}
