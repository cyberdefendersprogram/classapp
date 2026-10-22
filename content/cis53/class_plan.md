# CIS 53 Fall 2026 — What to Cover in Class (instructor plan, DRAFT)

Fridays 9:00 a.m.–12:00 p.m. PT, online. Built from the Canvas modules, the 2025 decks, and the 2025 student feedback. Nothing here is student-facing yet.

## Design principles (from 2025 feedback)

1. **Demo the Final's format before the Final.** Students asked for it twice. Do a live 15-minute "solve a level" in Week 4 and again in Week 5 (one network-only, one with an AI agent).
2. **Teach signal versus noise.** Use at least one noisy capture, not only clean exercises.
3. **Cover encrypted traffic and IPv6** (both were called out as missing). TLS metadata (SNI, certificates, JA3/JA4) in Week 3; IPv6 in Week 1.
4. **Cut, don't stack.** AI replaces older content; students said the workload was already 2–3 classes' worth.
5. **Detect, don't just define.** Every week ends with a student doing a detection or investigation step, not a vocabulary check.
6. **Security Onion is out as a required setup** (too tedious). Use TryHackMe rooms and NetLab; show Security Onion output on screen only.

## What to cut or shrink from the 2015/2025 decks

- Bits, bytes, binary and hex: 40 minutes down to a 10-minute refresher (the Week 2 quiz still covers hex and TCP/IP).
- Case-study retellings of HBGary, Target, APT1, OPM: replace with 10-minute ATT&CK-mapped recaps and the startup case study.
- Product pitches, Authentic8, Bromium, Cuckoo, dated OTX IP lookups, Moodle and Cabrillo Netlab references.
- Snort 2 config walkthroughs (preprocessors): show rule anatomy; use Suricata syntax (Snort 3 and Suricata rules are close).
- Capture-filter syntax slide-by-slide (12 slides): one demo plus a cheat sheet.

## Week 1 (Oct 23) — Why monitor, and what a packet is

- 0:00 Welcome, course approach (to / from / with AI), grading, TryHackMe and NetLab access, readings and the Reading page. **How the Final works** (show Level 1 from last year as a 5-minute preview).
- 0:25 Detection loop: prevent, detect, respond. NSM data types: full packet, flow, logs, alerts. Where sensors sit (SPAN, tap, cloud).
- 1:00 Packets: Ethernet, ARP, IPv4 *and IPv6*, TCP, UDP; handshake and teardown. Hex refresher (10 min).
- 1:50 Break.
- 2:00 Hands-on: capture your own machine for 5 minutes and build a one-page baseline.
- 2:40 Mitnick case study discussion with an ATT&CK mapping template; assign Week 1 readings; preview Lab 1.

## Week 2 (Oct 30) — Reading traffic and spotting anomalies

- Case study review: Mitnick, then Target (ATT&CK mapped, 10 min each).
- Capture filter versus display filter: live demo, then a cheat sheet.
- TCP in trouble: resets, retransmissions, scans (SYN, ACK), beaconing with I/O graphs and conversations; export objects and hashing.
- **Noisy-capture drill:** find the signal in normal office-like traffic (use a malware-traffic-analysis.net exercise, pre-checked).
- **AI thread:** what an LLM API call looks like (DNS, SNI, bytes up and down, long streaming responses). Streaming traffic can look like C2 beaconing, a false-positive lesson.
- Quiz: Hex and TCP/IP opens. Assign Week 2 readings; preview Lab 2.

## Week 3 (Nov 6) — Application protocols and encrypted traffic

- DNS in depth (resolution, tunneling, DGA, fast flux); HTTP; **TLS metadata** (SNI, certificates, JA3/JA4) and what encryption hides; email and phishing evidence; authentication and SMB at a high level.
- File carving and hashing.
- **AI thread:** shadow AI and data egress; detecting uploads to AI services; what a DLP or proxy would log.
- Hands-on: a DNS tunnel plus a TLS capture.
- Case study due: the IR startup research (companies list in the Tools page). Quick round-the-room "what did you pick, and why."

## Week 4 (Nov 13) — Detection technology and architecture

- IDS and IPS concepts, evasion theory (still sound), signature versus behavioral versus anomaly.
- **Rule anatomy:** write a Suricata/Snort rule live; test it against a capture; tune it. Zeek logs (conn, dns, http, ssl) and correlating by uid. Sigma for logs. SIEM triage in 20 minutes.
- Architecture: taps/SPAN, cloud visibility (VPC Flow Logs, traffic mirroring, GuardDuty), TLS blind spots, retention.
- **AI thread:** attacks on LLM apps and agents (prompt injection, tool abuse) and the telemetry that exposes them; what a normal agent log looks like.
- **Final-format demo:** solve a network level live, thinking aloud, with hints.

## Week 5 (Nov 20) — Intelligence, hunting, and AI-assisted analysis; Final released

- Pyramid of Pain, IoC versus IoA, ATT&CK and ATLAS; enrichment and confidence; NetFlow; hunting loop (hypothesis, data, query, validate); packet crafting with Scapy to test detections.
- **AI thread:** AI-enabled attackers; **AI-assisted triage** exercise (LLM versus ground truth, document its mistakes).
- **Final-format demo:** an AI-agent exfiltration level.
- Final briefing: format, hints policy, rules, no AI on the Final. Released at the end of class (12:00 p.m.).
- Assign presentation slots for Dec 4.

## Week 6 (Dec 4) — Presentations and guest lecture

- Student presentations: 3-minute startup case-study highlights (and Final findings if time allows).
- Guest lecture (open: who? Last year was a Wiz speaker).
- Wrap-up: how the course fits together, next steps (SOC L1/L2 paths, certifications), reminder that the Final closes Sunday, Dec 6, 11:59 p.m.

## Still to decide

- Guest speaker for Dec 4.
- Whether students bring a Wireshark install or use a browser-based option for tight laptops.
- How many presentation slots fit in the time available (class size).
