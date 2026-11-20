"""Atomically publish a complete local claim, never replacing another claim.

Darwin signature/flag verified in installed SDK usr/include/sys/stdio.h:
renamex_np(const char *, const char *, unsigned int), RENAME_EXCL=0x00000004.
Linux uses libc renameat2(AT_FDCWD,...,RENAME_NOREPLACE). Unsupported kernels,
symbols, filesystems and cross-device moves fail closed. No rename fallback.
This does not implement shared capacity or forced-termination retirement.
"""
import ctypes
import errno
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
from .common import owned


def rename_exclusive(source,destination):
    library=ctypes.CDLL(None,use_errno=True)
    source=os.fsencode(source); destination=os.fsencode(destination)
    try:
        if sys.platform=='darwin':
            call=library.renamex_np
            call.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_uint]
            call.restype=ctypes.c_int
            result=call(source,destination,0x00000004)
        elif sys.platform=='linux':
            call=library.renameat2
            call.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
            call.restype=ctypes.c_int
            result=call(-100,source,-100,destination,1)
        else: raise OSError(errno.ENOTSUP,'exclusive directory rename unsupported')
    except AttributeError:
        raise OSError(errno.ENOTSUP,'exclusive directory rename unavailable') from None
    if result:
        number=ctypes.get_errno()
        if number in (errno.EEXIST,errno.ENOTEMPTY):
            raise FileExistsError(number,'claim destination exists',os.fsdecode(destination))
        raise OSError(number,'exclusive directory rename refused',os.fsdecode(destination))


def sync_directory(path):
    fd=os.open(path,os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)


class LocalClaim:
    def __init__(self,attempt,destination):
        self.attempt=owned(attempt); destination=Path(destination)
        # Do not resolve the final component: existing symlinks are collisions.
        self.destination=owned(destination.parent)/destination.name
        self.private=Path(tempfile.mkdtemp(prefix='.execution-claim-',dir=self.attempt))
        info=self.private.lstat(); self.identity=(info.st_dev,info.st_ino)
        self.published=False
        self.records={'pid':str(os.getpid()),'relay-owner':str(self.attempt)}
        try:
            for name,value in self.records.items(): self._write_file(name,value)
            sync_directory(self.private); sync_directory(self.attempt)
        except BaseException:
            self.close()
            raise

    def _write_file(self,name,value):
        fd=os.open(self.private/name,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(fd,'w') as stream:
            stream.write(value); stream.flush(); os.fsync(stream.fileno())

    def _ours(self,path):
        try:
            info=path.lstat()
            return stat.S_ISDIR(info.st_mode) and (info.st_dev,info.st_ino)==self.identity
        except FileNotFoundError: return False

    def _complete(self,path):
        return set(p.name for p in path.iterdir())==set(self.records) and all(
            not (path/name).is_symlink() and (path/name).is_file()
            and (path/name).read_text()==value for name,value in self.records.items())

    def publish(self):
        if self.published or not self._ours(self.private):
            raise RuntimeError('local claim already published or ownership lost')
        if not self._complete(self.private):
            raise RuntimeError('private claim metadata changed')
        rename_exclusive(self.private,self.destination)
        self.published=True
        sync_directory(self.destination.parent); sync_directory(self.attempt)

    def close(self):
        if self.published:
            if not self._ours(self.destination) or not self._complete(self.destination):
                raise RuntimeError('claim ownership changed; cleanup quarantined')
            # Withdraw the complete live-PID claim before deleting metadata;
            # the legacy launcher cannot observe our half-removed claim.
            rename_exclusive(self.destination,self.private)
            self.published=False
            if not self._ours(self.private):
                raise RuntimeError('claim changed during withdrawal; cleanup quarantined')
            sync_directory(self.destination.parent); sync_directory(self.attempt)
        if self._ours(self.private):
            shutil.rmtree(self.private); sync_directory(self.attempt)

    def __enter__(self): return self
    def __exit__(self,*args): self.close()
