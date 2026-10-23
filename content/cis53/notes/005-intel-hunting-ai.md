# CIS 53 — Week 5 Notes
**Threat Intelligence, Hunting, and AI-Assisted Analysis**

Friday, November 20, 2026 · 9:00 a.m.–12:00 p.m. PT (online)

---

**Class Zoom:** https://peralta-edu.zoom.us/j/9402327279
**Syllabus:** [Canvas — CIS 53 Syllabus](https://peralta.instructure.com/courses/89432/assignments/syllabus)

## Today's Agenda

- Indicators, behaviors and the Pyramid of Pain
- ATT&CK and ATLAS as a shared language
- Enrichment and confidence
- Hunting: hypothesis, data, query, validate
- Testing detections with packet crafting
- AI thread: AI-enabled attackers and **AI-assisted triage**
- **Final-format demo:** an AI-agent exfiltration scenario
- Final briefing; Final is **released at 12:00 p.m.**
- Presentation slots for Dec 4

---

## Books + Reading

Required — Brown & Roberts, *Intelligence-Driven Incident Response*, 2nd Ed., Ch. 2: Basics of Intelligence. Required — Roddie et al., *Practical Threat Detection Engineering*, Ch. 7: Developing Detections Using Behavioral Indicators. Required — MITRE ATLAS matrix overview. Optional — NIST AI 100-2; Practical Threat Detection Engineering Ch. 9: Detection Validation.

**Reading questions:**
1. What turns raw indicators into intelligence an analyst can act on?
2. Why do behavioral detections age better than indicator-based ones, and how would you test one?
3. Pick one ATLAS technique. What evidence of it could a defender collect from network traffic or application logs?

---

## Part 1 — Indicators and Behavior

- **Indicators of compromise (IoCs):** hashes, IPs, domains. Easy to use, easy for an attacker to change.
- **Pyramid of Pain:** the higher you detect (tools, then tactics, techniques and procedures), the more it costs the attacker to adapt.
- **IoA (indicators of attack):** the behavior itself, such as a process spawning an unexpected shell or a host contacting rare destinations at regular intervals.

## Part 2 — Intelligence Is Analysis, Not a Feed

A list of bad IPs is data. Intelligence is data with **context** (who, why, how reliable) that supports a decision. Always record the source and your confidence. Check indicator age: an IP from last year may belong to someone else now.

## Part 3 — A Shared Language

**MITRE ATT&CK** describes adversary tactics and techniques. **MITRE ATLAS** does the same for attacks on AI systems. Mapping a finding to a technique makes it comparable, searchable and easy to explain.

## Part 4 — Hunting

1. **Hypothesis** ("a host is beaconing to a rare destination").
2. **Data** (flow records, DNS logs, Zeek `conn.log`).
3. **Query** (group by destination, look for regular intervals).
4. **Validate** (is it a known service? what does the endpoint say?).
5. **Record and automate:** turn a good hunt into a detection.

## Part 5 — Test Your Detections

A detection you never tested is a guess. **Scapy** lets you craft packets to trigger or evade a rule in a safe lab, then tune. Only use it in the lab environments we provide.

## Part 6 — The AI Thread

**From AI:** attackers use models for faster reconnaissance, convincing phishing and quicker tooling. The traffic still has to cross a network and touch hosts, so behavior-based detection remains useful, but volume and speed rise.

**With AI: AI-assisted triage.** In class we give an LLM a sanitized alert bundle and compare its answer to the ground truth:

- Where was it right? Where did it invent evidence or miss it?
- Could you check each claim against a log line or packet?
- What must never be pasted into a tool (credentials, personal data, production secrets)?

Treat the model as a fast junior analyst whose work you always check. You will document one of its mistakes in Lab 4.

## Final-Format Demo and Briefing

We solve an AI-agent exfiltration level live. Then the rules for the Final:

- **Released:** today, 12:00 p.m. PT. **Closes:** Sunday, Dec 6, 11:59 p.m. PT.
- Multi-level, evidence-based; hints are available for each level.
- **No AI tools** on the Final unless the instructions say so.
- Show your evidence: packet numbers, log lines, hashes.

---

## Lab 4

[Lab 4 on Canvas](https://peralta.instructure.com/courses/89432/assignments/1820969) — due this morning at 9:00 a.m. It includes the TryHackMe SOC Simulator scenario "Phishing Unfolding".

## Presentations

Dec 4 is student presentations plus a guest lecture. Sign-up slots are assigned in class today.
