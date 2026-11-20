"""Project-owned swap observations only. No jobs, leases or allocation state."""
import math
import os
from pathlib import Path
import sqlite3
from .common import owned


def record_swap(path,*,boot_id,wall_s,monotonic_s,used_mib):
    """Atomically record a verified observation and find a fresh five-minute one.

    Baselines require the same boot, ages of 300..600 seconds on BOTH clocks,
    and elapsed-clock agreement within two seconds. Missing evidence returns
    None; corrupt storage is an error, never permission to start work.
    """
    if (not isinstance(boot_id,str) or not boot_id
            or any(type(v) not in (int,float) or not math.isfinite(v) or v<0
                   for v in (wall_s,monotonic_s))
            or type(used_mib) is not int or used_mib<0):
        raise ValueError('invalid verified swap observation')
    path=Path(path)
    if path.is_symlink(): raise ValueError('measurement database must not be a symlink')
    parent=owned(path.parent); parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    if parent.stat().st_uid!=os.getuid() or parent.stat().st_mode&0o077:
        raise ValueError('measurement cache directory must be private')
    path=parent/path.name
    try:
        fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError: pass
    else: os.close(fd)
    if path.is_symlink() or not path.is_file() or path.stat().st_mode&0o077 or path.stat().st_uid!=os.getuid():
        raise ValueError('measurement database ownership or permissions changed')
    try:
        conn=sqlite3.connect(path,timeout=5,isolation_level=None)
        try:
            conn.execute('PRAGMA synchronous=FULL')
            conn.execute('BEGIN IMMEDIATE')
            conn.execute('CREATE TABLE IF NOT EXISTS samples (id INTEGER PRIMARY KEY,boot_id TEXT NOT NULL,wall_s REAL NOT NULL,monotonic_s REAL NOT NULL,used_mib INTEGER NOT NULL)')
            rows=conn.execute('SELECT wall_s,monotonic_s,used_mib FROM samples WHERE boot_id=?',(boot_id,)).fetchall()
            valid=[]
            for wall,mono,used in rows:
                if (type(wall) not in (int,float) or type(mono) not in (int,float)
                        or not math.isfinite(wall) or not math.isfinite(mono)
                        or wall<0 or mono<0 or type(used) is not int or used<0):
                    raise ValueError('corrupt measurement row')
                wall_age=wall_s-wall; mono_age=monotonic_s-mono
                if 300<=wall_age<=600 and 300<=mono_age<=600 and abs(wall_age-mono_age)<=2:
                    valid.append({'wall_s':wall,'monotonic_s':mono,'used_mib':used})
            conn.execute('INSERT INTO samples(boot_id,wall_s,monotonic_s,used_mib) VALUES(?,?,?,?)',
                         (boot_id,wall_s,monotonic_s,used_mib))
            conn.execute('DELETE FROM samples WHERE boot_id<>? OR wall_s<? OR monotonic_s<?',
                         (boot_id,wall_s-1200,monotonic_s-1200))
            conn.commit()
            return max(valid,key=lambda row:(row['wall_s'],-row['used_mib'])) if valid else None
        finally: conn.close()
    except sqlite3.Error:
        raise ValueError('measurement database unavailable or corrupt') from None
