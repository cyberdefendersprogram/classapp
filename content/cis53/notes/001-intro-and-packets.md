# CIS 53 — Week 1 Notes
**Why We Monitor, and What a Packet Is**

Friday, October 23, 2026 · 9:00 a.m.–12:00 p.m. PT (online)

---

## Instructor
**Vaibhav Bhandari**
Director of Security @ Lib13
Previous: Shape Security, United Health, Microsoft, YouBase et al.
MS in CS @ UC Santa Cruz
Non-profit: [cyberdefendersprogram.com](https://www.cyberdefendersprogram.com)

---

**Full syllabus:** [Canvas — CIS 53 Syllabus](https://peralta.instructure.com/courses/89432/assignments/syllabus)
**Class Zoom (every Friday):** https://peralta-edu.zoom.us/j/9402327279
**Textbook:** none required. Optional: Bejtlich, *The Practice of Network Security Monitoring*. Readings are assigned in class each week.

## Course Map — Six Fridays

Class Portal dates are authoritative.

| Date | Week | Topic | Assignments |
|------|------|-------|-------------|
| Oct 23 | 1 | Why monitor; packets, Wireshark, tcpdump | Lab 1 and Quiz 1 open |
| Oct 30 | 2 | Reading traffic; scans, beaconing, noise | Lab 1 due; Quiz 2 |
| Nov 6 | 3 | DNS, HTTP, TLS metadata; AI egress | Lab 2 due; case study due |
| Nov 13 | 4 | IDS/IPS, Suricata, Zeek, Sigma; agent logs | Lab 3 due |
| Nov 20 | 5 | Threat intel, hunting, AI-assisted triage | Lab 4 due; **Final released 12:00 pm** |
| Nov 27 | — | No class (Thanksgiving) | |
| Dec 4 | 6 | Student presentations and guest lecture | Final closes Sun Dec 6, 11:59 pm |

## Today's Agenda

- Welcome, grading, tools (TryHackMe, NetLab, Wireshark), the Reading page
- How the Final works — a five-minute preview
- The detection loop and the types of NSM data
- Packets: Ethernet, ARP, IPv4 and IPv6, TCP, UDP
- Hands-on: capture your own machine and build a baseline
- Mitnick case study discussion; Lab 1 preview

---

## Books + Reading

Required — Bejtlich, *The Practice of Network Security Monitoring*, Ch. 1: Network Security Monitoring Rationale. Required — Ch. 2: Collecting Network Traffic: Access, Storage, and Management. (Free through O'Reilly access.)

**Reading questions:**
1. Why is prevention alone not enough to protect a network, and what does monitoring add?
2. Where can you place a sensor to see traffic, and what can you not see from each position?

---

## Part 1 — Our Approach: Threats To, From, and With AI

Every week connects the fundamentals to three questions:

- **To AI:** how do attacks on LLM apps and agents show up in traffic and logs?
- **From AI:** how do AI-enabled attackers change what defenders see?
- **With AI:** where can AI help an analyst, and how do you check its work against evidence?

You cannot spot abnormal AI traffic until you can read normal traffic, so the first two weeks are fundamentals. AI material replaces older content; it is not extra workload.

**No AI tools on quizzes or the Final** unless the instructions say so. On labs, only where the assignment allows, and you stay responsible for verifying anything it produces.

## Part 2 — Why Monitor

**Prevent, detect, respond.** Prevention fails sometimes. Detection shortens the time an intruder is unnoticed; response limits the damage. Network security monitoring (NSM) is the practice of collecting and analyzing network data to find intrusions.

### Types of NSM data

| Type | What it is | Good for | Cost |
|---|---|---|---|
| Full packet capture | Every packet, with payload | Deep investigation, evidence | Storage-heavy |
| Session / flow data | Who talked to whom, how long, how much | Spotting beaconing, scans, large transfers | Light |
| Transaction / log data | DNS, HTTP, TLS and similar records (e.g. Zeek logs) | Fast searching across protocols | Moderate |
| Alert data | IDS/IPS hits | Triage entry point | Light, noisy |
| Statistical data | Counts and baselines | Trends | Light |

### Where sensors sit

- **SPAN/mirror port** on a switch, or a **network tap**, copies traffic to a sensor.
- **Cloud:** VPC flow logs and traffic mirroring replace taps.
- Every position has blind spots: encrypted payloads, traffic that never crosses the sensor, and east-west traffic inside a host or VM.

## Part 3 — What a Packet Is

Data travels in layers; each layer wraps the one above it.

| Layer | Examples | What you read there |
|---|---|---|
| Link | Ethernet, ARP | MAC addresses |
| Network | IPv4, IPv6 | IP addresses, TTL / hop limit |
| Transport | TCP, UDP | Ports, flags, sequence numbers |
| Application | DNS, HTTP, TLS | The actual conversation |

- **TCP handshake:** SYN, SYN/ACK, ACK. Teardown uses FIN or RST. A burst of SYNs with no ACKs is the shape of a scan.
- **UDP:** no handshake; DNS is the common case.
- **IPv6:** longer addresses, no ARP (uses Neighbor Discovery). Many tools and detections still assume IPv4, so attackers can hide there.
- **Hex refresher (10 minutes):** two hex digits make a byte. You will meet it again on the Week 2 quiz.

## Part 4 — Tools

- **Wireshark** — graphical packet analysis. **tcpdump** — command line capture. We use both.
- A capture is evidence: note when and where you captured it, and protect it.
- Capture only on networks you are authorized to monitor.

## Hands-On

Capture your own machine for five minutes while you browse, then write a one-page baseline: top talkers, the protocols you see, and anything that surprised you. Next week we use your baseline to separate normal from suspicious.

## Case Study Discussion — Mitnick

We map one classic intrusion to ATT&CK and ask what a sensor would have seen.

---

## Lab 1 Preview

Full instructions: [Lab 1 on Canvas](https://peralta.instructure.com/courses/89432/assignments/1820968) (due Fri Oct 30, 9:00 a.m.). TryHackMe rooms plus one NetLab lab plus short answers.

## Quiz 1

Opens after class on Canvas. Covers today and the readings.
