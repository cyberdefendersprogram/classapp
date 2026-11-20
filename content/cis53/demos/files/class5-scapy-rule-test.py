"""CIS 53 Demo 16: craft test traffic for a detection rule, offline.

    pip install scapy
    python class5-scapy-rule-test.py            # writes class5-variants.pcap
    suricata -r class5-variants.pcap -S class5-test.rules -l out -k none
    cat out/fast.log

This script only WRITES a pcap file. It sends nothing on any network. Do not
point Scapy's send() at anything except a lab host you were given.
Each variant is a different way to carry the same request to the same URI.
"""

from scapy.all import IP, TCP, Ether, Raw, wrpcap

SRC, DST = "10.0.0.31", "198.51.100.140"
REQ = (
    b"GET %s HTTP/1.1\r\nHost: static.edge-update.test\r\n"
    b"User-Agent: python-requests/2.32.3\r\n\r\n"
)
t = [1_795_000_000.0]
pkts = []


def emit(pkt):
    t[0] += 0.01
    pkt.time = t[0]
    pkts.append(pkt)


def conversation(sport, segments, uri_bytes=None):
    """A TCP handshake, then the request in one or more segments, then a reply and a close.

    segments: list of (offset_in_request, bytes). Offsets let a variant send pieces out of order.
    """
    seq, sseq = 1000, 5000
    eth = Ether(src="02:00:00:00:00:31", dst="02:00:00:00:00:fe")
    eth_r = Ether(src="02:00:00:00:00:fe", dst="02:00:00:00:00:31")
    emit(eth / IP(src=SRC, dst=DST) / TCP(sport=sport, dport=80, flags="S", seq=seq))
    emit(
        eth_r / IP(src=DST, dst=SRC) / TCP(sport=80, dport=sport, flags="SA", seq=sseq, ack=seq + 1)
    )
    emit(
        eth
        / IP(src=SRC, dst=DST)
        / TCP(sport=sport, dport=80, flags="A", seq=seq + 1, ack=sseq + 1)
    )
    total = 0
    for off, data in segments:
        emit(
            eth
            / IP(src=SRC, dst=DST)
            / TCP(sport=sport, dport=80, flags="PA", seq=seq + 1 + off, ack=sseq + 1)
            / Raw(data)
        )
        total = max(total, off + len(data))
    body = b'{"cmd":"sleep"}'
    reply = b"HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n" % len(body) + body
    emit(
        eth_r
        / IP(src=DST, dst=SRC)
        / TCP(sport=80, dport=sport, flags="PA", seq=sseq + 1, ack=seq + 1 + total)
        / Raw(reply)
    )
    emit(
        eth
        / IP(src=SRC, dst=DST)
        / TCP(sport=sport, dport=80, flags="FA", seq=seq + 1 + total, ack=sseq + 1 + len(reply))
    )
    emit(
        eth_r
        / IP(src=DST, dst=SRC)
        / TCP(sport=80, dport=sport, flags="FA", seq=sseq + 1 + len(reply), ack=seq + 2 + total)
    )


URI = b"/api/v1/poll?id=a1b2c3d4"
whole = REQ % URI

# A: the request in one segment (the rule should fire).
conversation(41001, [(0, whole)])
# B: the same request split mid-URI across two segments.
cut = whole.index(b"poll") + 2
conversation(41002, [(0, whole[:cut]), (cut, whole[cut:])])
# C: segments sent out of order (the second piece first).
conversation(41003, [(cut, whole[cut:]), (0, whole[:cut])])
# D: a percent-encoded letter in the path.
conversation(41004, [(0, REQ % b"/api/v1/p%6fll?id=a1b2c3d4")])
# E: a doubled slash at the start of the path.
conversation(41005, [(0, REQ % b"//api/v1/poll?id=a1b2c3d4")])
# F: upper-case path.
conversation(41006, [(0, REQ % b"/API/V1/POLL?id=a1b2c3d4")])
# G: a benign request to a different path (the rule should stay quiet).
conversation(41007, [(0, REQ % b"/index.html")])

wrpcap("class5-variants.pcap", pkts)
print(f"class5-variants.pcap: {len(pkts)} packets, 7 conversations (ports 41001-41007)")
