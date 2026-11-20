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

Required — Brown & Roberts, *Intelligence-Driven Incident Response*, 2nd Ed., Ch. 2: Basics of Intelligence (data versus intelligence, sources and methods, the intelligence cycle and OODA, qualities of good intelligence, levels of intelligence, confidence levels). Required — Roddie et al., *Practical Threat Detection Engineering*, Ch. 7: Developing Detections Using Behavioral Indicators (detecting adversary tools, using PsExec as the example, and detecting TTPs). Also useful — Ch. 6 (detections from indicators of compromise) and Ch. 10 (leveraging threat intelligence: requirements, triage, and using blog posts, VirusTotal and threat assessments). Required — MITRE ATLAS matrix overview. Optional — NIST AI 100-2; Roddie Ch. 9: Detection Validation (Atomic Red Team and CALDERA).

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

## Demos for today

- [Demo 14: Same attacker, twice (Pyramid of Pain)](/demos/014-pyramid-of-pain-same-attacker-twice): indicator rules from wave 1 go silent in wave 2; the behavior rule still fires.
- [Demo 15: Hunt the beacon in conn.log](/demos/015-hunt-the-beacon-in-conn-log): no alert fired; a regularity query finds three suspects, context removes two.
- [Demo 16: Craft packets to test your rule](/demos/016-craft-packets-to-test-your-rule): Scapy builds seven variants offline; one rule misses one, and the fix is one word.
- [Demo 17: AI-assisted triage](/demos/017-ai-assisted-triage-check-the-model): check a confident model answer claim by claim against the logs.

## Recent AI events we will use (verify before you rely on any detail)

- **AI against AI tools:** EchoLeak (CVE-2025-32711), a no-click prompt injection in Microsoft 365 Copilot; the malicious prompt in the Amazon Q Developer extension 1.84.0 (AWS-2025-015); "Clinejection" (Feb 2026), prompt injection through an AI issue-triage bot.
- **AI-enabled attackers:** Anthropic's report on the AI-orchestrated GTG-1002 campaign (Nov 2025), which published no indicators; Google's threat intelligence group on the "exploit_agent" framework (Nov 16, 2026). Both are good exercises in confidence levels (Brown and Roberts Ch. 2): compare each headline with the primary report.
- **Third-party AI tools as the way in:** Vercel and Context.ai (April 2026).

These feed Case Study 5, where you choose an incident from a catalogue.

## Assignments

- **Lab 4:** [Lab 4 on Canvas](https://peralta.instructure.com/courses/89432/assignments/1820969), due **Friday, December 4, 9:00 a.m.** Includes the TryHackMe Pyramid of Pain and Intro to Cyber Threat Intel rooms, the SOC Simulator scenario "Phishing unfolding", Scapy on NetLab, the Unit 42 RedLine quiz, and an AI-triage exercise built on Demo 17.
- **Case Study 5:** [Case Study 5 on Canvas](https://peralta.instructure.com/courses/89432/assignments/1820975), due **Friday, December 4, 9:00 a.m.** Pick one incident from the catalogue (breach detection, hunting, or attacks on AI systems). No presentation. Propose your own incident by Wed Nov 25.
- **Week 5 quiz:** covers Class 4, due Sunday, Nov 22.
- **Class 5 in-class quiz** on the portal.
- **Company Research:** the Case Study 3 highlights page is on the portal; read it before your 3-minute presentation.

## Presentations

Dec 4 is the Case Study 3 startup highlights (3 minutes each) plus a guest lecture. Sign-up slots are assigned in class today.
