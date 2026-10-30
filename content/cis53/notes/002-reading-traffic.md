# CIS 53 — Week 2 Notes
**Reading Traffic and Spotting Anomalies**

Friday, October 30, 2026 · 9:00 a.m.–12:00 p.m. PT (online)

---

**Class Zoom:** https://peralta-edu.zoom.us/j/9402327279
**Syllabus:** [Canvas — CIS 53 Syllabus](https://peralta.instructure.com/courses/89432/assignments/syllabus)

## Today's Agenda

- Case study review: Mitnick in packets (Case Study 1); Target is assigned today (Case Study 2)
- Capture filters vs. display filters
- TCP in trouble: resets, retransmissions, scans, beaconing
- Noisy-capture drill: find the signal
- AI thread: what an LLM API call looks like on the wire
- Class 2 in-class check (portal quiz); Lab 1 check-in (due next class); Quiz 1 opens after class (due Sun Nov 1, 11:59 p.m.)

---

## Books + Reading

Required — Bejtlich, *The Practice of Network Security Monitoring*, Ch. 6: Command Line Packet Analysis Tools and Ch. 7: Graphical Packet Analysis Tools. Required — Wireshark User's Guide, Filtering Packets (Display Filters).

**Reading questions:**
1. What does each tool (command line vs. graphical) let you do faster, and when would you reach for each?
2. When do you use a capture filter and when a display filter, and what does each one change?

---

## Class 1 and Class 2 Reading: Discussion Questions

**Class 1 (Bejtlich Ch. 1: NSM Rationale; Ch. 2: Collecting Network Traffic):** prevention eventually fails, so monitoring and response matter; where the sensor sits (tap, SPAN, inline) decides what you can see and how much storage you need.

1. Why is prevention alone not enough, and what does monitoring add?
2. Where can you place a sensor, and what can you not see from each position?
3. For your own network, which position would you choose, and what stays invisible (encrypted, east-west, cloud)?

**Class 2 (Bejtlich Ch. 6: Command Line Packet Analysis Tools; Ch. 7: Graphical Packet Analysis Tools):**

1. What does each tool (command line vs. graphical) let you do faster, and when do you reach for each?
2. When do you use a capture filter and when a display filter, and what does each one change?
3. Why does the book recommend capturing with dumpcap and analyzing the saved file afterwards?
4. Which of these tools would you let an AI assistant drive, and which not?

What the book gives you for today: tcpdump switches (`-n -i -s -c -w -r`, `-tttt -e -XX`), BPF primitives (`host`, `src`, `dst`, `net`, `port`, `tcp`, `udp`, `icmp`, and `and/or/not`), dumpcap with the same BPF via `-f`, tshark with display filters (`-r`, `-t ad`, `-Y`, `-V`, `-x`), and Wireshark's three everyday features: display filters, Follow TCP Stream, and Export Objects.

---

## Part 0 — Mitnick in Packets (Case Study 1 Review)

Case Study 1 (Mitnick) is due today at 9:00 a.m. Template and instructions: [Case Studies](/case-studies/001-mitnick).

In December 1994 an attacker used a SYN flood and TCP sequence number prediction to forge a session into Tsutomu Shimomura's X terminal and plant a trust entry. Walk through it:

1. **Recon:** finger, showmount and RPC probes. Visible to a sensor, but nobody was watching.
2. **Silence the trusted server:** a SYN flood to its rsh port (T1498).
3. **Measure:** about 20 SYNs to the target, each SYN-ACK revealing the next initial sequence number (a fixed step of 128,000 in the reported case).
4. **Forge:** spoofed SYN as the server, then a blind ACK with the predicted number.
5. **Plant:** an rsh command that writes `+ +` into `.rhosts`; then reset.

Discuss: Which weakness mattered most (address-based trust, predictable ISNs, or unmonitored probing)? What would a sensor see? What stops it today (random ISNs per RFC 6528, SYN cookies, no address-based trust, SSH, egress filtering)? How would an AI-driven attacker change the probing?

**Hands-on:** [Demo 004: Mitnick in packets](/demos/004-mitnick-in-packets) (a synthetic reconstruction; not the original evidence).

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

Real networks are noisy. In class we work through [Demo 005: Scan, beacon and noise](/demos/005-scan-beacon-noise), a 20-minute capture with a port scan, a 60-second beacon and a legitimate AI streaming call hidden in ordinary traffic. (For more practice, malware-traffic-analysis.net has pre-checked exercises.)

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

## Class 2 Demos

- [Demo 003: Capture vs display filters](/demos/003-capture-vs-display-filters): ten questions on one capture.
- [Demo 004: Mitnick in packets](/demos/004-mitnick-in-packets)
- [Demo 005: Scan, beacon and noise](/demos/005-scan-beacon-noise): find a port scan, a 60-second beacon and a legitimate AI streaming call.

## More on the AI Thread

- **To AI:** attacks on LLM apps and agents hide inside TLS; what you see is a new destination, an unexpected upload, or a burst of tool calls.
- **From AI:** AI-written tooling can add jitter and blend into AI or cloud traffic, so perfectly regular beacons are the easy case.
- **With AI:** an assistant can explain a tshark line or draft a filter. Verify every claim against a packet number, and never paste real captures into a public tool.

## Case Study 2: Target (2013)

Due Fri Nov 6, 9:00 a.m. See [Case Studies](/case-studies/002-target) for the template and starting sources. This is the "alerts fired, nobody acted" case. It connects to Bejtlich Ch. 1 (monitoring needs response).

## Class 2 In-Class Check

A short portal quiz at the end of class covering filters, TCP flags, beaconing and the Mitnick case.

## Lab 1 (Week 2): Due Next Class

[Lab 1 on Canvas](https://peralta.instructure.com/courses/89432/assignments/1820968) is **due Fri Nov 6, 9:00 a.m.** It is comprehensive for Classes 1 and 2: the TryHackMe rooms and the NetLab lab cover packets and baselines (Class 1) as well as filters, scans, resets and beaconing (Class 2). Use today's demos to practice before you write it up.

## Quiz 1

Covers hex and TCP/IP fundamentals. Opens on Canvas after this class (Fri Oct 30). **Due Sunday, Nov 1, 11:59 p.m.**
