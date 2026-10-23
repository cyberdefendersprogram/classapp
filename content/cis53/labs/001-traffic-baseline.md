# Lab 1: Packets, Wireshark, and a Normal Baseline

**CIS 53 — Intrusion Detection In-Depth**

**Open now. Due:** Friday, November 6, 2026, 9:00 a.m. It covers Weeks 1 and 2, and it is open early so you can work on it while you set up TryHackMe and NetLab.
**Canvas:** [Lab 1 assignment](https://peralta.instructure.com/courses/89432/assignments/1820968)

Covers Weeks 1 and 2. Submit everything as a single PDF.

**Before you take any screenshots:** crop or black out any passwords, tokens, or personal data. Never submit credentials. Use only the lab environments we provide — do not capture or scan any other network.

## Part 1 — TryHackMe rooms (45 points)

Complete these rooms from your **TryHackMe assignments** (Business group `2026-Fall-CIS53`). Each room is assigned to the class group and due Fri Nov 6, 9:00 a.m. Screenshot each room showing it as completed.

- [Network Traffic Basics](https://tryhackme.com/room/networktrafficbasics)
- [Wireshark: The Basics](https://tryhackme.com/room/wiresharkthebasics)
- [Wireshark: Packet Operations](https://tryhackme.com/room/wiresharkpacketoperations)

If you don't see these in your TryHackMe assignments, email me at vbhandari@peralta.edu with the email address you want your TryHackMe account tied to.

## Part 2 — NetLab (30 points)

Log in at [openlab.baccc.net](https://openlab.baccc.net/) and complete **NDG Security+ v4 → Lab 22: Capturing Network Traffic**.

- Screenshot a capture you made, with the filter bar visible.
- Screenshot one TCP conversation and point out the handshake.
- If the lab will not start or the steps do not match the screen, tell us **before the deadline** with a screenshot of the problem. You will not be penalized for a lab that is broken.

## Part 3 — Short answers (25 points)

About 100–150 words each:

1. What does a normal baseline look like for the traffic you captured in Part 2 (hosts, protocols, ports, volume)? Name one pattern that would make you investigate.
2. Write one capture filter and one display filter. For each, say what it shows and why you would use it.
3. Suppose a chatbot app on a laptop talks to a cloud AI service over HTTPS. What could you learn from a packet capture of that traffic, and what would stay hidden because it is encrypted?

## What your screenshots must show

| Item | A good screenshot shows |
|---|---|
| Part 1 — each room | The room page marked 100% / completed, with your TryHackMe username visible |
| Part 2 — capture | The Wireshark window with your capture file, the filter bar, and packet list |
| Part 2 — TCP stream | The three-way handshake (SYN, SYN/ACK, ACK) highlighted or in a flow graph |

## Submission

- One PDF with all screenshots and your short answers.
- Short answers: keep each to the length stated; write in your own words and be ready to explain them.
- Late submissions follow the syllabus's 10% deduction policy.
- You may use AI tools to *study*, but anything an AI tells you about a tool or a command is unverified until you have tried it. Do not paste AI output as your answer.
