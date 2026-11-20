# Lab 4: Threat Intelligence, Hunting, Testing Detections and AI-Assisted Triage

**CIS 53 — Intrusion Detection In-Depth**

**Due:** Friday, December 4, 2026, 9:00 a.m.
**Canvas:** [Lab 4 assignment](https://peralta.instructure.com/courses/89432/assignments/1820969)

Covers Weeks 4 and 5. Submit everything as a single PDF. Part 4 builds on the Class 5 material (Demo 17). The Final opens at the end of Class 5 (Nov 20) and closes Sun Dec 6, so start this lab early.

**Template:** download `CIS53-Lab4-Template.docx` from the Canvas assignment (source: `content/cis53/templates/CIS53-Lab4-Template.docx`), fill it in, and submit one PDF.

**Reading:** Roddie et al., *Practical Threat Detection Engineering*, Ch. 6 (detections from indicators) and Ch. 7 (detections from behavior, including the PsExec example); Ch. 9 (validation) is optional. Brown and Roberts, *Intelligence-Driven Incident Response*, 2nd ed., Ch. 2 (data versus intelligence, source quality, confidence levels).

**Before you take any screenshots:** crop or black out any passwords, tokens, or personal data. Never submit credentials. Use only the lab environments we provide — do not capture or scan any other network.

## Part 1 — TryHackMe (40 points)

Complete these from your **TryHackMe assignments** (Business group `2026-Fall-CIS53`). Screenshot each one showing the **"Room completed!"** screen, or the room page with the green 100% bar.

- [Pyramid Of Pain](https://tryhackme.com/room/pyramidofpainax)
- [Intro to Cyber Threat Intel](https://tryhackme.com/room/cyberthreatintel)
- **SOC Simulator, scenario "Phishing unfolding"** ([scenarios page](https://tryhackme.com/soc-sim/scenarios)): close the alerts correctly, end the scenario, and screenshot your score and the feedback summary. It takes 1–2 hours, so do not leave it to the last day.

If a room or the scenario is not in your assignments (check that you joined the class group first), still do it from the link above and email me at vbhandari@peralta.edu with the email address tied to your TryHackMe account.

## Part 2 — NetLab (25 points)

Complete **NDG Ethical Hacking v2 (Series-1) → Lab 02: Packet Crafting with Scapy**.

- Screenshot a packet you crafted and the same packet in Wireshark.
- In 2–3 sentences, explain how crafted traffic helps you test a detection rule. Use Class 5 Demo 16 ("Craft packets to test your rule") as your example: say what the seven variants showed.
- This lab is older. If a step fails, try again, then tell us **before the deadline** with a screenshot of the problem. You will not be penalized for a lab that is broken.

## Part 3 — Practice for the Final (20 points)

Work the Unit 42 Wireshark quiz ["Crossing the Line: RedLine Stealer"](https://unit42.paloaltonetworks.com/wireshark-quiz-redline-stealer/) (August 2023). The page links the pcap (a ZIP with the password `infected`; open it only in your lab VM, never on your own computer's desktop). The answers are published elsewhere: do not look them up, because the Final will not have them. Submit your answers to the quiz questions and one screenshot of the evidence behind the answer you are most confident in.

## Part 4 — AI-assisted triage (15 points)

In Class 5 we checked a model's triage answer against the logs (Demo 17). Now do it yourself on a new set.

1. Download [`lab4-alert-bundle.json`](/demos/files/lab4-alert-bundle.json) (seven alerts from a Monday morning, plus an asset list). It is synthetic. Read it first and form your own view.
2. Give the bundle to **one AI tool of your choice** and ask it to triage the alerts (true positive, false positive, or needs more data, with a reason and a priority). Keep the prompt and the answer. The bundle contains no real data, but never paste real credentials, personal data or production logs into any tool.
3. Make a **claims table**: one row per factual claim in the answer, with the evidence line from the bundle that supports it, or "no evidence". Check every number, every direction, every ATT&CK ID, and whether the host or destination is on the approved lists.
4. Write up **one mistake** the AI made, in your own words (about 80 words): what it claimed, what the evidence says, and what could have happened if an analyst had acted on it. If it made no mistakes, find the weakest claim and say how you would verify it.
5. Say how you would **group the alerts into incidents** (which alerts belong together), in 2–3 sentences.

Grading: the claims table 6, the mistake write-up 5, the incident grouping 2, prompt and answer attached 2.

## Optional (extra credit)

TryHackMe: [Yara](https://tryhackme.com/room/yara) and [Log Analysis with SIEM](https://tryhackme.com/room/loganalysiswithsiem); or any 2025 exercise from [malware-traffic-analysis.net](https://www.malware-traffic-analysis.net/training-exercises.html).

## What your screenshots and answers must show

| Item | A good screenshot or answer shows |
|---|---|
| Part 1: each room | The "Room completed!" screen, or the room page with the green 100% bar |
| Part 1: SOC Simulator | The score and feedback summary after you ended the scenario |
| Part 2: Scapy | The crafted packet and the same packet in Wireshark |
| Part 3: Redline | Your answers, plus one screenshot of the evidence |
| Part 4 | The prompt, the AI's answer, your claims table and the write-up |

## Submission

- One PDF with all screenshots and your short answers.
- Short answers: keep each to the length stated; write in your own words and be ready to explain them.
- Late submissions follow the syllabus's 10% deduction policy.
- You may use AI tools to *study*, and you must use one in Part 4. Anything an AI tells you about a tool, a command or an ATT&CK ID is unverified until you have tried it or looked it up. Disclose any AI-written text and attach the prompts.
