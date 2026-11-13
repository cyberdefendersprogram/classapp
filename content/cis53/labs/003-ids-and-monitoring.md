# Lab 3: IDS, Zeek, and Alerts

**CIS 53 — Intrusion Detection In-Depth**

**Due:** Friday, November 20, 2026, 9:00 a.m.
**Canvas:** [Lab 3 assignment](https://peralta.instructure.com/courses/89432/assignments/1820972)

Covers Weeks 3 and 4: IDS and IPS, rules, Zeek logs, and detecting attacks on AI apps. Submit everything as a single PDF.

**Reading:** Roddie et al., *Practical Threat Detection Engineering*, Ch. 1 (Fundamentals) and Ch. 2 (the detection life cycle, especially Test); Bejtlich, *The Practice of Network Security Monitoring*, Ch. 9.

**Before you take any screenshots:** crop or black out any passwords, tokens, or personal data. Never submit credentials. Use only the lab environments we provide — do not capture or scan any other network.

## Part 1 — TryHackMe rooms (45 points)

Complete these rooms from your **TryHackMe assignments** (Business group `2026-Fall-CIS53`). Screenshot each room showing the **"Room completed!"** screen, or the room page with the green 100% bar.

- [IDS Fundamentals](https://tryhackme.com/room/idsfundamentals)
- [Snort](https://tryhackme.com/room/snort)
- [Network Monitoring with Zeek](https://tryhackme.com/room/networkmonitoringwithzeek)
- Optional extra practice, no points lost if skipped: [Zeek](https://tryhackme.com/room/zeekbro) (the introduction), [Snort Challenge - The Basics](https://tryhackme.com/room/snortchallenges1) (write rules against real traffic) and [Zeek Exercises](https://tryhackme.com/room/zeekbroexercises)

If a room is not in your assignments (check that you joined the class group first), still do the room from the link above and email me at vbhandari@peralta.edu with the email address tied to your TryHackMe account.

## Part 2 — NetLab (25 points)

Complete **NDG Security+ v4 → Lab 08: Identifying and Analyzing Network/Host Intrusion Detection System (NIDS/HIDS) Alerts**.

- Screenshot two alerts and classify each as true positive, false positive, or inconclusive, with one sentence of evidence.
- This lab is older and may not match the screens exactly. If a step fails, try again, then tell us **before the deadline** with a screenshot of the problem. You will not be penalized for a lab that is broken.

## Part 3 — Detecting attacks on AI apps (30 points)

1. **TryHackMe room** (5 points): complete [Prompt Injection](https://tryhackme.com/room/promptinjectionls) and screenshot it completed.
2. **Find and detect** (15 points): download `agent-tool-calls.jsonl` from this Canvas assignment. It is the tool-call log of a support agent: one JSON object per line, six sessions, one of them carrying a prompt-injection attack. Write down:
   - which session was injected and which two log lines prove it (quote them);
   - **one detection** (a Sigma rule, a `jq` or `grep` query, or a SIEM query) that would flag the injected session without flagging the normal ones; the fields it uses;
   - one false positive it would produce, and how you would tune it.

   Grading: the right session with evidence 4, a rule that matches the injected session and not the normal ones 6, you ran it against the file and show the output 3, false positive 2.
3. **Short answer** (10 points): about 150 words. An LLM-powered app is receiving prompt-injection attempts. Which logs would you collect, which fields in them matter, and what would an alert be built on? Say what the same alert could *not* see if the agent's traffic were encrypted and you only had the network sensor.

## What your screenshots and answers must show

| Item | A good screenshot or answer shows |
|---|---|
| Part 1 — each room | The "Room completed!" screen, or the room page with the green 100% bar |
| Part 2 — alerts | The alert details (rule/message, source, destination, time), not just the alert list |
| Part 3 — detection | The rule or query text, the command you ran, and its output |

Check every cell and every filter or rule you write for consistency with your own screenshots. A rule that does not match what the output shows costs points.

## Submission

- One PDF with all screenshots and your short answers.
- Short answers: keep each to the length stated; write in your own words and be ready to explain them.
- Late submissions follow the syllabus's 10% deduction policy. You may resubmit improved work for a regrade.
- You may use AI tools to *study*, but anything an AI tells you about a tool, a command or an ATT&CK ID is unverified until you have tried it or looked it up. If any text is AI output, disclose it and attach the prompts.
