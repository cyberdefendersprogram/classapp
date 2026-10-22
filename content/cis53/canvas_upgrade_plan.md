# CIS 53 Canvas Upgrade Plan (course 89432, Fall 2026)

Status: DRAFT. Nothing here has been pushed to Canvas. Push as unpublished drafts only after approval.

## 1. Calendar (class meetings, Fridays 9am-12pm PT)

| Wk | Date | Topic | Canvas module |
|---|---|---|---|
| 1 | Oct 23 | Network Traffic Analysis 1 | Week 1 |
| 2 | Oct 30 | Network Traffic Analysis 2 | Week 2 |
| 3 | Nov 6 | Application Protocols + guest speaker | Week 3 |
| 4 | Nov 13 | IDS/IPS, HIDS, SIEM, monitoring architecture | Week 4 |
| 5 | Nov 20 | Threat intel, IoCs, advanced topics | Week 5 |
| - | Nov 27 | No class (Thanksgiving) | - |
| 6 | Dec 4 | Intrusion Detection Challenge (Final) | Week 6 |

DECISION NEEDED: Final Levels 1-5 currently unlock Nov 20 and are due Nov 22 (Canvas).
Proposed: unlock Nov 20 (head start), class Dec 4 is the capstone presentation and
Level 6, all levels due Sun Dec 6 11:59pm PT.

## 2. Theme: detect threats to, from, and with AI

Keep the existing structure and grade weights. Add AI inside existing assignments
rather than adding new graded items.

| Week | Existing item | Upgrade |
|---|---|---|
| 1 | Mitnick case study | Add a 10-point "AI-era Mitnick" reflection: how would LLM-assisted social engineering change the attack? |
| 2 | Lab (Wireshark/ARP) + Target case study | Add Part D: capture a local LLM chat (Ollama or stub API) and identify the HTTP stream, JSON body and streaming response. |
| 3 | Lab 2 (DNS/protocols) + APT1 case study | Add Part D: AI egress lab (below). Replace APT1 with the AI incident case-study menu (below). |
| 4 | IDS/IPS Lab + OPM case study | Add Part D: Suricata and Sigma rules against LLM-app logs (below). |
| 5 | Lab + IDS Hands-on Quiz + YourChoice case study | Add AI-assisted triage task. Rewrite quiz (below). YourChoice must map to ATT&CK and, if AI-related, ATLAS. |
| 6 | Final Levels 1-5 | Keep. Add Level 6: compromised AI agent (below). |

## 3. Draft content

### 3a. Week 3 Lab Part D - AI Egress Detection (25 pts, carved from Lab 2's 100)

Scenario: a company wants to know which employees send data to AI services.
You get `ai_egress.pcap` (instructor-built, synthetic).

1. List all DNS queries to AI-service domains (Wireshark: `dns.qry.name` filters).
2. For TLS sessions, extract SNI, certificate subject and JA3/JA4 fingerprint. Which hosts talk to which AI service?
3. Identify the session with the largest upload. What does metadata tell you? What can you NOT know without decryption?
4. Write one detection (Zeek `notice` idea, Suricata rule on SNI, or Sigma over proxy logs) that flags large uploads to AI endpoints from non-approved hosts.
5. Deliverable (max 1 page): findings table (host, service, bytes out, time) + your detection + one false-positive risk.

### 3b. Week 4 Lab Part D - Detecting Attacks on an LLM App (25 pts)

Given `llm_app_logs.jsonl` (synthetic: user prompt, tool called, tool args, response size, user id, timestamp):

1. Find prompts containing instruction-override or data-exfiltration patterns (prompt injection indicators).
2. Find tool calls that are rare for that user or app (e.g. a chatbot suddenly calling a file-read or HTTP-fetch tool).
3. Write a Sigma rule for one of the above.
4. Write a Suricata rule for one network indicator from the companion `agent_egress.pcap`.
5. Validate: run your rule against the logs, report true/false positives, and tune once.
6. Map each finding to MITRE ATT&CK and MITRE ATLAS technique names (look them up; do not guess IDs).

### 3c. Week 3 Case Study (replaces APT1): AI Security Incident

Pick one: (a) EchoLeak, the zero-click prompt-injection data-exfiltration flaw in Microsoft 365 Copilot; (b) the 2023 Samsung ChatGPT source-code leak (shadow AI); (c) a publicly reported AI-orchestrated intrusion campaign (find a vendor report, 2025 or later); (d) another instructor-approved case.
600+ words: what happened, attack chain, which telemetry would have detected it, ATT&CK and ATLAS mapping, one prevent and one detect control.
Verify every claim against a primary source and cite it.

### 3d. Week 5 Lab addition - AI-Assisted Triage (25 pts)

Take 10 alerts from the provided SIEM export. Ask an LLM to triage each (severity, true/false positive, next step). Then triage them yourself using evidence. Report: agreement rate, two cases where the LLM was wrong or overconfident, and what evidence you checked. Disclose the tool and prompts used. (This is the course's permitted-AI exercise; AI remains prohibited on quizzes and the Final.)

### 3e. Week 5 IDS Hands-on Quiz rewrite (120 pts)

Keep Q1 (signature) and Q3 (false positive). Replace the rest:
- Q2 (20): Given a short pcap excerpt, is this alert a true positive, false positive or inconclusive? Justify with packet evidence.
- Q4 (20): Read this Snort rule line by line and explain each option.
- Q5 (20): Write a Suricata rule that detects <behavior given in class>. Explain what it would miss.
- Q6 (20): Given Zeek conn.log and dns.log rows, correlate by uid and describe what happened.
- Add (20): Name two signals that would indicate LLM-API data exfiltration at the network layer and one thing encryption hides. (Re-weight so total stays 120.)
- Remove the Google Scholar paper-counting question. Keep "how would you protect your IDS" as an optional 10-point bonus.

### 3f. Final Level 6 - Compromised Agent (10 pts)

New synthetic evidence set (`level6.zip`, password = an answer from Level 5):
`agent_egress.pcap`, `llm_app_logs.jsonl`, `zeek_logs/`. Questions in the Level 1-5 style: signal or noise; which tool call is anomalous; which prompt carried the injection; what data left and where; did the attacker succeed; which control would have stopped it; ATT&CK and ATLAS mapping. Evidence must be built and verified before release.

## 4. Canvas housekeeping

- Fill the empty Syllabus tab (use the corrected syllabus; matches this plan).
- Delete or unpublish about 30 template pages ("Module 1 - [Enter Module 1 topic here]" and its -2 / -3 copies) and the duplicate "Instructor Resources" pages.
- Fix the "Intrustion" typo in the two file names.
- Add a Week 6 date label so students see Dec 4.
- Add a Week 1 ungraded orientation item (tools check: Wireshark, NetLab, TryHackMe account).
- Align case-study wording ("1-2 page, 600 words" vs "template guidelines") into one rubric.

## 4b. Canvas file audit (nothing deleted yet)

Provenance: the Canvas course is the 2015 course (outline xlsx: Oct 23 - Dec 4, 2015, Room P218, prior instructor) re-dated. The Oct 23 - Dec 4 Fridays match 2026, so Dec 4 is real.
2025 decks (Drive: 2026-Fall-CIS-53 / 2025-Fall-CIS-53 / slides, labs) are newer than the Canvas decks and are NOT in Canvas.

| File(s) in Canvas | Verdict | Why |
|---|---|---|
| Week 1-5 decks (2015) | REPLACE with 2025 decks 01-06, then update | 2015 content (Bro, Cabrillo Netlab, Moodle, Tuesday office hours, Authentic8 plugs). 2025 decks already add Sigma/YARA, EDR, ATT&CK/CTI prompt, SOC-analyst lab. Still carry Target/APT1/OPM and Snort-only IDS. |
| Guest Speakers - Craig Le Clair and Mukul Kumar.pptx | REMOVE | Dated 11/20/15, Altera. |
| Incident Response Guest Lecture (Vincent Meneau).pptx | REMOVE or replace | Dated 10.22.15; use NIST SP 800-61r3 style content or a new guest. |
| Craig Le Clair IDS Lecture.ppt | REMOVE | Legacy 2015 .ppt. |
| CIS 53 Course Outline and Content Breakdown.xlsx | REMOVE | 2015 dates, prior instructor, room. Instructor-only. |
| Intrusion Detection Hands-on Resources.boxnote | REPLACE | Packetrix, bro.org links; rewrite with Zeek, Suricata, Security Onion, Sigma, malware-traffic-analysis.net. |
| CyberQuest_Oct2015.zip, "U.S. CyberQuests" references | REMOVE | 2015 contest data. Verify site still exists before keeping any reference. |
| hexquiz.pdf (x2), hexquiz_answers.pdf | KEEP one hexquiz.pdf; HIDE answers | Duplicate; confirm answer key is not student-visible. |
| Mandiant_APT1_Report.pdf | MOVE to optional reading | 2013 report. Fine as history, not core. |
| SharkFest2015PacketChallenge.pdf, ncl info.docx | REMOVE (verify first) | 2015 / unclear. |
| netcat_cheat_sheet_v1.pdf | KEEP optional | Timeless. |
| Practice pcaps (dns, http, ftp, nmap_*, email-file-carving, application-layer-analysis.zip) | KEEP, add a README | Fundamentals are timeless, used by Weeks 2-3. |
| Odd 2004-era pcaps (can-2003-0003, MS04-011 exploit, SIP spoof, rtp raw, tnef patch, httpd.conf, file.php) | REMOVE unless a lab references them | Check module/page usage first. |
| level1-5.zip, level1.pcap (Final) | KEEP, FIX | See student feedback below. |
| Duplicate images (banners x3, orientation x3, 2020 screenshots x many) | REMOVE | Duplicates and 2020 screenshots. Check page references first. |

## 4c. Fixes from 2025 student feedback (Feedback.docx)

- Final: later levels required answers from earlier/later levels; Level 5 Q1 only solvable via a known-plaintext zip attack (bkcrack); Level 4 pcap is missing packets. Fix the dependency chain and the pcap, and add hint tiers.
- Add encrypted-traffic coverage (TLS metadata, JA3/JA4), more IPv6, and a noisier "realistic" pcap where signal must be found among normal traffic.
- Show a worked demo of a Final-style level before the Final.
- Workload: students called the homework 2-3 classes worth (labs + reflection essays + case studies). So SWAP content; do not stack AI work on top. Cut reflection essays to short answers.
- Recommend (not require) a networking fundamentals primer before Week 1; six weeks is short.

## 4d. TryHackMe class (org: The Peralta Colleges)

Created group `2026-Fall-CIS53` (Manage teams > Groups) on 2026-10-21. No admins or users added yet. Org has 134 tokens, 62 used, 72 remaining. Existing: `2026-Fall-AI-Village` (11 users, module "AI Village @ Merritt: Hack the AI"), old `2025-Fall-CIS53` (empty).
Room names below were read from the live TryHackMe path outlines (SOC Level 1, SOC Level 2 "NEW 2026", AI Security) on 2026-10-21. Room durations and org-level availability are NOT verified; check each before assigning.

| Wk | Class focus | Suggested rooms (replace reflection essays with completion + short answers) |
|---|---|---|
| 1 | Traffic fundamentals | Network Traffic Basics; Wireshark: The Basics |
| 2 | Traffic analysis 2 | Wireshark: Packet Operations; Wireshark: Traffic Analysis; NetworkMiner; Network Discovery Detection |
| 3 | App protocols + AI egress | Data Exfiltration Detection; Man-in-the-Middle Detection; Traffic Analysis Pitfalls; AI: AI Security Threats, LLM Security |
| 4 | IDS/SIEM + attacks on LLM apps | IDS Fundamentals; Snort; Detection Engineering With Snort; Network Monitoring with Zeek; Threat Hunting with Zui; Intro to Detection Engineering; Sigma Language; AI: Prompt Injection, Jailbreaking, Prompt Defence, LLMborghini (challenge) |
| 5 | Threat intel + hunting + AI triage | Pyramid of Pain; MITRE; Intro to Cyber Threat Intel; Threat Hunting: Introduction / Foothold; AI & Automation in Detection Engineering; AI: RAG Security Fundamentals, Data Poisoning in RAG Systems, UnIndexed (challenge) |
| Final prep | Capstone practice | Advanced Packet Analysis; The Silent Transfer (challenge); SOC Simulator: Phishing Unfolding; optional Boogeyman 1-3 |
| Optional | Extra credit | AI Supply Chain Security (Payload, Checkpoint); Threat Hunting With YARA; Wazuh |

## 4e. Weekly reading list DRAFT (CIS 52 style: 60-90 min, one reading question)

Syllabus keeps two optional books (Bejtlich, Wilson); everything else is "assigned in class". Chapter titles below were read from the O'Reilly tables of contents on 2026-10-21; I have NOT read the chapters, so check relevance before assigning. Wilson's chapter titles were not retrievable (the audiobook page lists "Chapter 1-15" only); pick Wilson chapters from the print edition.

| Wk | Required reading | Reading question |
|---|---|---|
| 1 | Bejtlich Ch. 1 "Network Security Monitoring Rationale"; Ch. 2 "Collecting Network Traffic: Access, Storage, and Management" (taps/SPAN sections) | Why is prevention alone not enough, and what does monitoring add? |
| 2 | Bejtlich Ch. 6 "Command Line Packet Analysis Tools" and Ch. 7 "Graphical Packet Analysis Tools" (concepts; tool UIs are dated); Wireshark User's Guide, display filters | When do you use a capture filter and when a display filter? |
| 3 | Bejtlich Ch. 10 "Server-side Compromise" and Ch. 11 "Client-side Compromise" (the investigation walk-throughs); OWASP Top 10 for LLM Applications (prompt injection, sensitive information disclosure) | What network or log evidence would show data leaving through an AI service? |
| 4 | Bejtlich Ch. 4 "Distributed Deployment" and Ch. 9 "NSM Operations"; Roddie Ch. 1 "Fundamentals of Detection Engineering" and Ch. 6 "Developing Detections Using Indicators of Compromise"; Suricata/Snort rule docs; Wilson (prompt-injection material) | When does a signature beat a behavioral detection, and when does it fail? |
| 5 | Brown and Roberts Ch. 2 "Basics of Intelligence"; Roddie Ch. 7 "Developing Detections Using Behavioral Indicators" and Ch. 9 "Detection Validation"; MITRE ATLAS overview; NIST AI 100-2 introduction | Why do behavioral detections age better than IoCs, and how would you test one? |
| 6 | Presentation prep only; optional Brown and Roberts Ch. 10 "Strategic Intelligence" | n/a |

## 4f. NetLab (openlab.baccc.net) - pessimistic review, PARTIAL

I could not sign in (login is the user's to do), so this is from NDG's public pages plus the lab titles in Canvas. Courses are NDG Security+ v4 (aligned to SY0-601, 2021) and NDG Ethical Hacking v2 (2020-21): assume dated tooling until a lab guide is opened.
Verified titles: EH v2 Lab 01 DNS Footprinting, Lab 02 Packet Crafting with Scapy; Security+ v4 Lab 08 Identifying and Analyzing NIDS/HIDS Alerts. From Canvas only (unverified): EH Lab 06 Network Analysis, Lab 07 Evading IDS; Security+ Lab 04 ARP Poisoning, Lab 15 Common Protocols, Lab 22 Capturing Network Traffic.

| Lab | Verdict (pessimistic) |
|---|---|
| Sec+ Lab 22 Capturing Network Traffic | Keep only if Wireshark UI still matches; otherwise TryHackMe Wireshark rooms cover it. |
| Sec+ Lab 04 ARP Poisoning | Keep: concept is timeless and TryHackMe has no direct equivalent that I found. |
| EH Lab 01 DNS Footprinting | Keep as optional; overlaps TryHackMe DNS Manipulation. |
| EH Lab 02 Packet Crafting with Scapy | Add (Week 5 packet crafting topic); Scapy is timeless. |
| Sec+ Lab 08 NIDS/HIDS Alerts | Risky: likely older Snort/Security Onion. Verify, else drop for TryHackMe Snort rooms. |
| EH Lab 07 Evading IDS | Verify. Evasion theory still valid; tooling likely old. Optional only. |
| EH Lab 06 Network Analysis | Unknown; verify or drop. |
| Sec+ Lab 15 Common Protocols | Drop: generic Security+ content, off-topic for an IDS course. |

## 5. Open questions

1. Final window: confirm the proposal in section 1.
2. Textbook: optional Bejtlich, or none?
3. Synthetic evidence (3a, 3b, 3f): I can generate the logs and a pcap with Scapy; you validate before release.
4. Slide decks (Weeks 1-5 .pptx) were not reviewed and would need matching AI slides.
