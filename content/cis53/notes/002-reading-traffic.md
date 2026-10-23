# CIS 53 — Week 2 Notes
**Reading Traffic and Spotting Anomalies**

Friday, October 30, 2026 · 9:00 a.m.–12:00 p.m. PT (online)

---

**Class Zoom:** https://peralta-edu.zoom.us/j/9402327279
**Syllabus:** [Canvas — CIS 53 Syllabus](https://peralta.instructure.com/courses/89432/assignments/syllabus)

## Today's Agenda

- Case study review: Mitnick, then Target (ATT&CK mapped)
- Capture filters vs. display filters
- TCP in trouble: resets, retransmissions, scans, beaconing
- Noisy-capture drill: find the signal
- AI thread: what an LLM API call looks like on the wire
- Quiz 1 opens after class; Lab 2 preview

---

## Books + Reading

Required — Bejtlich, *The Practice of Network Security Monitoring*, Ch. 6: Command Line Packet Analysis Tools and Ch. 7: Graphical Packet Analysis Tools. Required — Wireshark User's Guide, Filtering Packets (Display Filters).

**Reading questions:**
1. What does each tool (command line vs. graphical) let you do faster, and when would you reach for each?
2. When do you use a capture filter and when a display filter, and what does each one change?

---

## Part 1 — Filters

| | Capture filter | Display filter |
|---|---|---|
| When it applies | Before packets are saved | After capture, on what you already have |
| Syntax | BPF (`host 10.0.0.5 and port 53`) | Wireshark (`ip.addr == 10.0.0.5 && dns`) |
| Risk | Packets you filter out are gone forever | None; you can change it any time |

Rule of thumb: capture broadly when you can afford the storage, filter when you analyze. Learn a small set well: `ip.addr`, `tcp.port`, `dns`, `http`, `tls.handshake`, `tcp.flags`, `frame contains "..."`.

## Part 2 — TCP in Trouble

What the abnormal looks like:

- **Scans:** many SYNs to many ports (or hosts) with RSTs coming back. An ACK scan or a slow scan looks different; check the flags.
- **Resets and retransmissions:** can mean a closed port, a firewall, or a broken connection. Context decides.
- **Beaconing:** a host contacts the same destination at regular intervals, with similar sizes. Use **Statistics → Conversations** and **I/O Graphs** to see regularity.
- **Large or long transfers:** check bytes per direction. Uploads much larger than downloads deserve a second look.

Always ask: *is this unusual for this host, at this time?* That is why Week 1 had you build a baseline.

## Part 3 — Noisy-Capture Drill

Real networks are noisy. In class we work through a pre-checked capture from malware-traffic-analysis.net:

1. Start with Conversations and Protocol Hierarchy. What is normal here?
2. Find the host that does not fit.
3. Follow a stream; export objects; hash anything you extract.
4. Write down the evidence chain: what you saw, in which packet, and what it means.

Hashing and noting packet numbers is what makes your finding checkable by someone else.

## Part 4 — The AI Thread: What an LLM Call Looks Like

An app calling a hosted LLM usually shows:

- A DNS lookup for the provider's API name, then a TLS connection (the **SNI** shows the name even when the payload is encrypted).
- A small request followed by a **long streaming response**.
- Bytes up and bytes down that depend on prompt and answer length.

**False-positive lesson:** a long-lived streaming connection to a single host can look like command-and-control. Before calling it malicious, check the destination, the process, and whether it matches an approved service. Next week we ask the reverse question: how would a data leak through an AI service look?

---

## Lab 2 Preview

Full instructions: [Lab 2 on Canvas](https://peralta.instructure.com/courses/89432/assignments/1820970) (due Fri Nov 6, 9:00 a.m.). Wireshark rooms, the NetLab ARP poisoning lab, and an AI-egress question.

## Quiz 1

Covers hex and TCP/IP fundamentals. Opens on Canvas after this class (Fri Oct 30).
