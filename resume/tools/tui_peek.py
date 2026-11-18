import os, pty, time, select, fcntl, termios, struct, signal, re
pid, fd = pty.fork()
if pid == 0:
    os.chdir('/private/tmp/deepsignal')
    os.environ['TERM'] = 'xterm-256color'
    os.environ['CODEX_HOME'] = os.path.expanduser('~/.codex-deepsignal'); os.execvp('codex', ['codex', 'cloud'])
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack('HHHH', 50, 160, 0, 0))
buf = b''; start = time.time(); sent = 0; mark = 0
while time.time() < start + 16:
    r, _, _ = select.select([fd], [], [], 0.2)
    if r:
        try: d = os.read(fd, 65536)
        except OSError: break
        if not d: break
        buf += d
        for _ in range(d.count(b'\x1b[6n')): os.write(fd, b'\x1b[1;1R')
    if sent == 0 and time.time() - start > 7: mark = len(buf); os.write(fd, b'o'); sent = 1
    if sent == 1 and time.time() - start > 14: os.write(fd, b'\x1b'); time.sleep(0.3); os.write(fd, b'q'); sent = 2
time.sleep(0.5)
for sig in (signal.SIGTERM, signal.SIGKILL):
    try: os.kill(pid, sig); time.sleep(0.3)
    except OSError: pass
s = buf[mark:].decode('utf-8', 'replace')
s = re.sub(r'\x1b\[[0-9;?<>=]*[A-Za-z]|\x1b\][^\x07\x1b]*(\x07|\x1b\\)|\x1b[()][A-Z0-9]|\x1b[=>78]', '\n', s)
out = []
for l in (x.strip() for x in s.split('\n')):
    if l and l not in out: out.append(l)
print('\n'.join(out))
