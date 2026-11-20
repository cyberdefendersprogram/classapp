# Scapy

Scapy is a Python library and interactive shell for building, sending, capturing and reading packets. In this course you use it for one job: **testing a detection**. You craft the traffic your rule should catch (and the variants it might miss), save it to a pcap, replay it through Suricata or Zeek, and tune the rule. A detection you never tested is a guess.

## Overview

Scapy is useful for:
- **Testing rules**: build the same attack seven ways and see which variants a rule misses (Class 5, Demo 16)
- **Understanding protocols**: every field of a packet is an attribute you can read and change
- **Making test captures**: write a pcap with no real attack and no real victim
- **Reading pcaps**: filter and summarize a capture in a few lines of Python

**Safety note:** only send packets to machines in the lab environments we provide (NetLab, or your own VM). Do not scan or send crafted traffic to any other network. When you only need a test pcap, write it to a file with `wrpcap` and never touch the network.

### Installation

```bash
# Any OS with Python 3
python3 -m venv scapy-env
source scapy-env/bin/activate        # Windows: scapy-env\Scripts\activate
pip install scapy

# Verify
python3 -c "import scapy; print(scapy.__version__)"
```

On NetLab, Scapy is already installed: open a terminal and run `sudo scapy`. Sending packets needs root (or Administrator) rights. Building and writing a pcap does not.

## Basic Syntax

Layers are stacked with `/`. The lower layer goes on the left.

```python
from scapy.all import IP, TCP, UDP, DNS, DNSQR, Raw, wrpcap, rdpcap, sniff, send

pkt = IP(dst="10.0.0.5") / TCP(dport=80, flags="S")     # a SYN to port 80
pkt.show()                                                # every field, with defaults filled in
wrpcap("test.pcap", [pkt])                                # write to a file, no network needed
pkts = rdpcap("test.pcap")                                # read a pcap back
send(pkt)                                                 # put it on the wire (lab only, needs root)
```

| Function | What it does |
|---|---|
| `pkt.show()` / `pkt.summary()` | Print every field / a one-line summary |
| `wrpcap(file, pkts)` / `rdpcap(file)` | Write / read a pcap |
| `send(pkt)` / `sr1(pkt)` | Send at layer 3 / send and wait for one answer |
| `sniff(count=10, filter="tcp port 80")` | Capture packets with a BPF filter |
| `pkts.filter(lambda p: p.haslayer(DNS))` | Select packets from a list |
| `pkt[TCP].flags`, `pkt[IP].src` | Read a field from one layer |

:::command-builder{id="scapy-builder"}
tool_name: python3
target_placeholder: ""
scan_types:
  - name: "Check Scapy Is Installed"
    flag: "-c \"import scapy; print(scapy.__version__)\""
    desc: "Prints the version. If this fails, activate your virtual environment first"
  - name: "Summarize a Pcap"
    flag: "-c \"from scapy.all import *; print(rdpcap('test.pcap').summary())\""
    desc: "One line per packet. Quick check that your crafted file contains what you meant"
  - name: "Write One Crafted Packet to a Pcap"
    flag: "-c \"from scapy.all import *; wrpcap('syn.pcap', [IP(dst='10.0.0.5')/TCP(dport=80,flags='S')])\""
    desc: "Offline: nothing is sent. Replay the file through Suricata with suricata -r syn.pcap"
options: []
:::

---

:::scenario{id="scenario-1" level="beginner"}
title: "Build and Read a Packet"
goal: "Craft a TCP SYN to port 443 and read back its fields, without sending anything."
hint: "Stack IP and TCP with a slash. Use pkt.summary() for one line and pkt.show() for every field. Flags 'S' means SYN."
command: "python3 -c \"from scapy.all import *; p=IP(dst='10.0.0.5')/TCP(dport=443,flags='S'); print(p.summary()); print(p[TCP].flags, p[TCP].dport, p[IP].ttl)\""
expected_output: |
  IP / TCP <your-ip>:ftp_data > 10.0.0.5:https S
  S 443 64
:::

:::scenario{id="scenario-2" level="intermediate"}
title: "Make a Test Pcap for a DNS Rule"
goal: "Write a pcap with one normal DNS query and one with a very long, random-looking name, so you can check that a tunneling rule fires on the second and not on the first."
hint: "DNS(rd=1, qd=DNSQR(qname=...)) goes over UDP port 53. Write both packets to one file, then count them with rdpcap."
command: "python3 -c \"from scapy.all import *; a=IP(dst='10.0.0.2')/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname='www.example.com')); b=IP(dst='10.0.0.2')/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname='a9f3k2x8q1z7m4n5p6w0e8r2t1y3u4i5o6.badzone.example')); wrpcap('dns-test.pcap',[a,b]); print(len(rdpcap('dns-test.pcap')))\""
expected_output: |
  2
:::

:::scenario{id="scenario-3" level="intermediate"}
title: "Test a Rule With Variants"
goal: "A rule looks for the string 'cmd.exe' in HTTP traffic on port 80. Build three payloads that carry the same command: plain, upper case, and split across two TCP segments. Replay each and note which ones the rule misses."
hint: "This is Demo 16. A rule that matches a plain string misses a case change unless it uses nocase, and misses a split string unless the sensor reassembles the stream (a stream-aware rule, or the content in one segment). Write each variant to its own pcap so you can replay them one at a time."
command: "python3 -c \"from scapy.all import *; b=IP(dst='10.0.0.5')/TCP(dport=80,flags='PA'); wrpcap('v1-plain.pcap',[b/Raw(b'GET /cmd.exe HTTP/1.1\\r\\n\\r\\n')]); wrpcap('v2-upper.pcap',[b/Raw(b'GET /CMD.EXE HTTP/1.1\\r\\n\\r\\n')]); wrpcap('v3-split.pcap',[b/Raw(b'GET /cm'), IP(dst='10.0.0.5')/TCP(dport=80,flags='PA',seq=7)/Raw(b'd.exe HTTP/1.1\\r\\n\\r\\n')]); print('written')\""
expected_output: |
  written

  Then: suricata -r v1-plain.pcap -S your.rules -l out/ and check out/fast.log. The plain variant alerts; the upper-case variant does not unless the rule has nocase.
:::

---

## Testing a Detection: The Loop

1. **Write the rule** for the behavior (not only the one sample you have).
2. **List the variants** an attacker could use: case, encoding, fragmenting, a different port, a different order, a slower rate.
3. **Craft one pcap per variant** with Scapy. Name each file for the variant.
4. **Replay** each through Suricata (`suricata -r file.pcap -S rules -l out/`) or Zeek (`zeek -r file.pcap`).
5. **Record** a table: variant, expected, alert fired or not.
6. **Tune** the rule, then rerun every variant. A fix that breaks a variant you already passed is a regression.

This is the same loop as validating a detection with Atomic Red Team or CALDERA, one level lower: there you run a technique on a host, here you craft the packets.

## Pitfalls

- **Checksums and sequence numbers.** Scapy fills them in when you write or send. If you edit a field after building, delete the checksum (`del pkt[IP].chksum, pkt[TCP].chksum`) so it is recalculated.
- **Offline pcaps have no handshake.** Many IDS engines ignore data on a stream that never opened. Add the three handshake packets, or use a Suricata setting for midstream traffic, when a rule you know is right does not fire.
- **Your OS may reset the connection.** When you send a raw SYN from your own machine, the OS did not open that connection and replies with a RST. Another reason to write pcaps instead of sending live.
- **Root is required to send.** Reading and writing files is not.

## Quick Reference

| Task | Code |
|---|---|
| Ping (ICMP echo) | `IP(dst="10.0.0.5")/ICMP()` |
| TCP handshake SYN | `IP(dst=d)/TCP(dport=p, flags="S")` |
| UDP DNS query | `IP(dst=d)/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname="x.example"))` |
| HTTP request text | `IP(dst=d)/TCP(dport=80,flags="PA")/Raw(b"GET / HTTP/1.1\r\n\r\n")` |
| Fragment a packet | `fragment(pkt, fragsize=8)` |
| Read a field | `pkt[IP].src`, `pkt[TCP].flags` |
| Filter a pcap | `[p for p in rdpcap(f) if p.haslayer(DNS)]` |

## Use in This Course

- **Lab 4, Part 2 (NetLab):** NDG Ethical Hacking v2, Lab 02: Packet Crafting with Scapy. Screenshot a crafted packet and the same packet in Wireshark.
- **Class 5, Demo 16:** [Craft packets to test your rule](/demos/016-craft-packets-to-test-your-rule). Seven variants, one rule that misses one.
- **Reading:** Roddie et al., *Practical Threat Detection Engineering*, Ch. 9 (detection validation).

:::quiz{id="quiz-1"}
Q: You built a packet with IP(dst="10.0.0.5")/TCP(dport=80). Which call saves it to a file without sending anything?
- [ ] send(pkt)
- [ ] sr1(pkt)
- [x] wrpcap("test.pcap", [pkt])
- [ ] sniff(count=1)
:::

:::quiz{id="quiz-2"}
Q: Your rule matches the string cmd.exe. A crafted packet with CMD.EXE does not alert. What is the most likely fix?
- [ ] Send the packet faster
- [x] Add the nocase modifier to the content match
- [ ] Remove the port from the rule
- [ ] Use UDP instead of TCP
:::

:::quiz{id="quiz-3"}
Q: Why test a rule with several crafted variants instead of one sample?
- [ ] To make the pcap larger
- [ ] Because Scapy can only send one packet at a time
- [x] An attacker can change case, encoding or timing, and a rule that only matches your sample ages badly
- [ ] To avoid needing a sensor
:::
