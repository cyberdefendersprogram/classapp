"""Build the synthetic Class 5 demo files under content/cis53/demos/files.

    pip install scapy cryptography
    python scripts/make_class5_pcaps.py

Writes class5-wave1.pcap and class5-wave2.pcap (Demo 14, the Pyramid of Pain),
class5-hunt.pcap (Demo 15, hunting for a beacon in noise) and class5-iocs.txt.
All traffic is invented. Addresses are private or documentation ranges (RFC 1918,
RFC 5737, RFC 3330), every domain ends in .test, and the "payload" is a short text
file that starts with the letters MZ. Reuses the packet builders from make_class3_pcaps.py.
"""

import hashlib
import json
import random
from datetime import datetime, timezone

import make_class3_pcaps as m
from make_class3_pcaps import CHROME, PYREQ, Cap, app_records, client_hello, server_hello

# Class 5 is Fri Nov 20, 2026, 9:00 a.m. PT = 17:00 UTC
m.T0 = datetime(2026, 11, 20, 17, 0, 0, tzinfo=timezone.utc).timestamp()

OUT = m.OUT
RESOLVER = "10.0.0.2"
INTRANET = "10.0.0.50"
UA_BROWSER = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0 Safari/537.36"


def req(method, host, uri, ua, body=b""):
    h = f"{method} {uri} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {ua}\r\nAccept: */*\r\n"
    if body:
        h += f"Content-Length: {len(body)}\r\n"
    return (h + "\r\n").encode() + body


def resp(status, body=b"", ctype="application/json"):
    return (
        f"HTTP/1.1 {status}\r\nContent-Type: {ctype}\r\nContent-Length: {len(body)}\r\n\r\n".encode()
        + body
    )


def payload(tag):
    """A harmless stand-in for a dropped file: text that starts with MZ."""
    return (f"MZ this is a harmless demo file, build {tag}\n" * 20).encode()


def office_noise(c, clients, span, seed):
    """Staff browsing the intranet and a few HTTPS sites, so the capture is not only the incident."""
    r = random.Random(seed)
    page = b"<html><title>Merritt Intranet</title><body>Timesheets, parts, news</body></html>"
    sites = [
        ("www.merritt.test", "203.0.113.20"),
        ("docs.corp.test", "10.1.2.10"),
        ("news.example.test", "203.0.113.45"),
    ]
    for client in clients:
        t = r.uniform(2, 30)
        while t < span - 20:
            if r.random() < 0.5:
                c.dns_pair(t - 0.2, client, RESOLVER, "intranet.corp.test", "A", [INTRANET])
                c.tcp(
                    t,
                    client,
                    INTRANET,
                    r.randint(40000, 60000),
                    80,
                    [
                        (
                            "c",
                            req(
                                "GET",
                                "intranet.corp.test",
                                r.choice(["/home", "/news", "/parts"]),
                                UA_BROWSER,
                            ),
                        ),
                        ("s", resp("200 OK", page, "text/html")),
                    ],
                )
            else:
                name, ip = r.choice(sites)
                c.dns_pair(t - 0.2, client, RESOLVER, name, "A", [ip])
                ch = client_hello(name, CHROME["ciphers"], CHROME["exts"], rng=r)
                sflight = (
                    server_hello(True, 0x1301, r)
                    + b"\x14\x03\x03\x00\x01\x01"
                    + app_records(2800, r)
                )
                c.tcp(
                    t,
                    client,
                    ip,
                    r.randint(40000, 60000),
                    443,
                    [
                        ("c", ch),
                        ("s", sflight),
                        ("c", app_records(r.randint(600, 1800), r)),
                        ("s", app_records(r.randint(8000, 60000), r)),
                    ],
                )
            t += r.uniform(25, 90)


def wave(name, victim, c2_ip, c2_name, ua, build, seed, noise_clients):
    """One campaign wave: download a file, then poll for tasks about once a minute."""
    c = Cap(seed)
    r = c.rng
    office_noise(c, noise_clients, 720, seed + 100)
    c.dns_pair(59.7, victim, RESOLVER, c2_name, "A", [c2_ip], ttl=60)
    body = payload(build)
    c.tcp(
        60,
        victim,
        c2_ip,
        r.randint(40000, 60000),
        80,
        [
            ("c", req("GET", c2_name, "/dl/update.bin", ua)),
            ("s", resp("200 OK", body, "application/octet-stream")),
        ],
    )
    bid = "".join(r.choice("0123456789abcdef") for _ in range(8))
    t = 120.0
    n = 0
    while t < 700:
        uri = f"/api/v1/poll?id={bid}"
        answer = b'{"cmd":"sleep"}'
        # One task comes back around minute 8; the host answers with a bigger POST.
        if 470 < t < 540 and n == 0:
            answer = b'{"cmd":"run","args":"' + b"A" * 1800 + b'"}'
            n = 1
        c.tcp(
            t,
            victim,
            c2_ip,
            r.randint(40000, 60000),
            80,
            [("c", req("GET", c2_name, uri, ua)), ("s", resp("200 OK", answer))],
        )
        if n == 1:
            n = 2
            c.tcp(
                t + 6,
                victim,
                c2_ip,
                r.randint(40000, 60000),
                80,
                [
                    ("c", req("POST", c2_name, "/api/v1/result", ua, b"x" * 4200)),
                    ("s", resp("200 OK", b'{"ok":true}')),
                ],
            )
        t += 60 + r.uniform(-4, 4)
    c.save(name)
    return hashlib.sha256(body).hexdigest()


def hunt():
    """Thirty noisy minutes: one slow beacon among regular but harmless traffic."""
    c = Cap(55)
    r = c.rng
    span = 1800
    office_noise(c, ["10.0.0.15", "10.0.0.23", "10.0.0.41"], span, 77)

    # The incident: 10.0.0.52 fetches a 1x1 gif every ~90 seconds from a name nobody here uses.
    bad, bad_name, bad_ip = "10.0.0.52", "cdn.assets-front.test", "203.0.113.99"
    c.dns_pair(29.7, bad, RESOLVER, bad_name, "A", [bad_ip], ttl=60)
    gif = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    t = 30.0
    while t < span - 20:
        cid = "".join(r.choice("0123456789abcdef") for _ in range(6))
        c.tcp(
            t,
            bad,
            bad_ip,
            r.randint(40000, 60000),
            80,
            [
                ("c", req("GET", bad_name, f"/static/px.gif?c={cid}", UA_BROWSER)),
                ("s", resp("200 OK", gif, "image/gif")),
            ],
        )
        t += 90 * r.uniform(0.9, 1.1)

    # Decoy 1: the build server polls an internal API every 30 seconds. Regular, harmless.
    t = 10.0
    while t < span - 10:
        c.tcp(
            t,
            "10.0.0.60",
            "10.0.0.51",
            r.randint(40000, 60000),
            80,
            [
                ("c", req("GET", "api.corp.test", "/api/health", "python-requests/2.31.0")),
                ("s", resp("200 OK", b'{"ok":true}')),
            ],
        )
        t += 30
    # Decoy 2: clock sync to the internal time server every 64 seconds. Regular, harmless.
    t = 5.0
    while t < span:
        c.udp(t, "10.0.0.15", 123, RESOLVER, 123, b"\x1b" + bytes(47))
        c.udp(t + 0.02, RESOLVER, 123, "10.0.0.15", 123, b"\x1c" + bytes(47))
        t += 64
    # Decoy 3: an AI agent streams long answers from an LLM API. Irregular, big, long. Not a beacon.
    llm, llm_ip = "api.llm-vendor.test", "198.51.100.30"
    for t in (140, 410, 520, 890, 1260, 1555):
        c.dns_pair(t - 0.3, "10.0.0.77", RESOLVER, llm, "A", [llm_ip])
        ch = client_hello(llm, PYREQ["ciphers"], PYREQ["exts"], rng=r)
        sflight = server_hello(True, 0x1301, r) + b"\x14\x03\x03\x00\x01\x01" + app_records(2800, r)
        c.tcp(
            t,
            "10.0.0.77",
            llm_ip,
            r.randint(40000, 60000),
            443,
            [
                ("c", ch),
                ("s", sflight),
                ("c", app_records(r.randint(2500, 9000), r)),
                ("s", app_records(r.randint(60000, 220000), r)),
            ],
            rtt=0.08,
        )
    c.save("class5-hunt.pcap")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    h1 = wave(
        "class5-wave1.pcap",
        "10.0.0.31",
        "198.51.100.77",
        "sync.cdn-sync.test",
        "python-requests/2.31.0",
        "wave1",
        21,
        ["10.0.0.15", "10.0.0.23"],
    )
    h2 = wave(
        "class5-wave2.pcap",
        "10.0.0.38",
        "198.51.100.140",
        "static.edge-update.test",
        "python-requests/2.32.3",
        "wave2",
        22,
        ["10.0.0.15", "10.0.0.41"],
    )
    hunt()
    (OUT / "class5-iocs.txt").write_text(
        "# CIS 53 Demo 14: the indicator list an analyst wrote after wave 1.\n"
        "# One IP, one domain, one hash. Lowest rungs of the Pyramid of Pain.\n"
        "ip      198.51.100.77\n"
        "domain  sync.cdn-sync.test\n"
        f"sha256  {h1}   (update.bin)\n"
    )
    print("wave2 update.bin sha256:", h2)
    json.dumps({"wave1": h1, "wave2": h2})
