# CIS 52 — Week 6 Notes
**Respond, Recover, Improve**

Friday, October 2, 2026 · 9:00 a.m.–12:00 p.m.

---

## Before We Start

The Final Project (written report + slides) was due today at 9:00 a.m. on Canvas. **Today is the last class session, which is also the cutoff for late work** on every earlier lab (10% deduction); your lowest lab and lowest quiz score are each dropped. Quiz 5 opens today at 1:00 p.m. and closes Sunday, October 4, at 11:59 p.m.

## Today's Agenda

Most of today belongs to you: every student presents their Final Project. We also have a guest speaker, and a short opener that closes the loop on the detection pipeline from Week 5.

| Time | Segment |
|---|---|
| 9:00 | Welcome, logistics, and **Respond & Recover in 10 minutes** |
| 9:10 | Final Project presentations, block 1 |
| 10:10 | Break (10 minutes) |
| 10:20 | **Guest speaker: Keith Hodo (Senior Partner Solutions Architect, AWS)** — *Cyber Security in the Era of Agentic Coding* |
| 11:00 | Final Project presentations, block 2 |
| 12:00 | Course wrap-up |

Your presentation slot is shown on the course portal's **Final Projects** page. Presentations are a **hard 5 minutes** — with every student presenting, there is no slack in the schedule. Have your slides open and ready before the person ahead of you finishes.

---

## Books + Reading

Required — Practical Cloud Security, 2nd Ed. (Dotson), Ch. 7, Response and Recovery sections ("Preparing for an Incident" through "Example Metrics"). Required — NIST SP 800-61 Rev. 3, *Incident Response Recommendations and Considerations for Cybersecurity Risk Management*. Required — Cloud Security Alliance, Cloud Controls Matrix (CCM) and introductory guidance. Optional — AWS Security Incident Response Guide.

**Reading questions:**
- Which cloud characteristics make incident response easier than in traditional infrastructure, and which make it harder?
- Why should a security incident lead to changes in architecture and controls, rather than ending when normal service is restored?
- Choose one technical security control used during this course. What evidence would demonstrate that the control is operating effectively?

---

## Part 1 — Respond & Recover in 10 Minutes

Week 5 ended with an alert firing. This week is what happens next — and the chapter's blunt point is that **most of incident response is decided before the incident starts.**

### Prepare Before the Alert: Team, Plans, Tools

**Team**
- Name a **primary and a backup** technical incident-response lead and a **primary and a backup** business lead — someone who can sign off on taking a system down or authorizing a payment. Response cannot wait for someone to come back from vacation.
- Line up specialists for the components your threat model says are most likely to be attacked, plus **legal, communications, and HR** contacts (HR matters if the attacker turns out to be an insider).
- Attackers know nobody wants to be on call on a holiday weekend — incidents tend to start at inconvenient times. Rotate people to avoid burnout, write down roles ahead of time, and meet at least quarterly.

**Plans**
- Plans are where IR gets **cloud-specific**. Know what your provider will and won't do during an incident *before* you need it (extra logs? forensic images? a security contact?). For most incidents that only involve your application, the response is yours — the shared responsibility model from Week 1 applies here too.
- Have a small, **pre-approved budget** for the first few hours (an IR firm's initial charges, emergency travel) so nobody is waiting on procurement mid-incident.
- Define **severity levels** — e.g., *confirmed unsuccessful attack*, *successful attack without data loss*, *successful attack with data loss* — so you don't wake 30 people for a contained malware alert.
- Rehearse with a **tabletop exercise**. Typical cloud lockdown plans: cut portal/API access to a handful of responders, cut network access to some or all of the environment, or shut everything down, lock the secrets server, and rebuild.
- **Backups belong in a separate cloud account with separate administrative credentials.** Attackers have wiped production *and* every backup the production account could reach. Know how long a restore actually takes.

**Tools**
- A separate, normally-empty **incident response cloud account** (accounts cost nothing until you provision resources) plus virtual images with forensic tools.
- Tested, step-by-step procedures for common tasks — e.g., capture memory, hash it, verify it, hard power-off, snapshot the disks.
- Current network/data/logging diagrams, contact lists, a (virtual) war room, a backup communications channel in case email or chat is what got compromised, checklists, and forms for documenting what you did.

### Respond: Triage, Then the OODA Loop

1. **Triage first.** Mobilize part of the team, decide the severity, and only then escalate. It's easy to overreact *and* underreact.
2. **Use the attack chain to predict the next move.** The Lockheed Martin Cyber Kill Chain (reconnaissance → weaponization → delivery → exploitation → installation → command and control → actions on objective) or the MITRE ATT&CK tactics from Week 5 tell you what the attacker has probably already done and what comes next.
3. **Run the OODA loop — Observe, Orient, Decide, Act — and repeat it quickly until the incident is resolved.**

| Phase | What it means in the cloud |
|---|---|
| **Observe** | Pull provider logs (CloudTrail), firewall and flow logs, OS logs, and metrics — the pipeline you built in Week 5 |
| **Orient** | Work out what's happening and what's next, using knowledge of your crown-jewel assets plus external threat intel (free sources like CISA alerts count) |
| **Decide** | Pick the next tactic: take systems offline, revoke access, quarantine, or build a new environment |
| **Act** | Execute — this is where the cloud helps most: scripted security-group/NACL lockdowns instead of unplugging cables, and rebuilding compute from images while keeping the data stores |

Jot down 15-second "lessons learned" notes *while* you respond; you won't remember them afterward. And don't be afraid to call an IR firm — attackers have far more practice attacking than most defenders have defending.

### Contain Without Destroying Evidence

- **Cloud forensics** is mostly disciplined copying: take a forensic copy (disk snapshot, memory capture, database snapshot, flow logs), then generate a **cryptographic hash (e.g., SHA-256)** so anyone can later prove the copy wasn't altered.
- **Blocking unauthorized access** is harder than it sounds once an attacker has admin rights. The common move — rotating every password and API key, including automation credentials, and blocking network access — is disruptive, so build the scripts *ahead* of time. Week 3's segmentation is what keeps the blast radius small enough to contain.
- **Stopping exfiltration and command-and-control** often means cutting **outbound** traffic, not just inbound — the Codecov lesson from Week 4 again.
- See the new **[AWS IR Containment Playbook](../tools/aws-ir-containment.md)** tool page for the exact CLI commands: find what a leaked key did, deactivate it, deny-all the principal, revoke role sessions, and isolate and snapshot an instance.

### Recover: Redeploy, Notify, Learn

- **Redeploy, don't clean.** Once someone has had administrative access, you can't prove you found every backdoor — one altered permission or registry entry is enough to let them back in. Rebuild from known-good images and switch production traffic over; the cloud makes this far easier than buying new hardware. If you *can't* redeploy, get explicit executive sign-off that the business is accepting that risk.
- **Notify.** You may have regulatory or contractual obligations to tell customers or law enforcement — and failed cover-ups (the chapter names **Yahoo!, Cathay Pacific, and Uber**) are worse than the disclosure would have been. Listen for this in today's Uber 2016 presentation.
- **Lessons learned** — after everyone has slept — update the team, plans, procedures, tools, and checklists.
- **Measure it.** Example metrics from the reading: % of alerts that are confirmed incidents vs. false positives (detection), time from alert to review and from confirmed incident to closure (response), time to redeploy affected systems (recovery), and estimated cost per incident (overall).

### NIST SP 800-61 Rev. 3 — Incident Response Is a Loop, Not an Ending

Rev. 3 (April 2025) replaces Rev. 2's four-phase lifecycle (Preparation → Detection & Analysis → Containment, Eradication & Recovery → Post-Incident Activity) with the **six NIST Cybersecurity Framework (CSF) 2.0 functions**:

- **Govern, Identify, Protect** — the preparation work: policies, roles, asset inventory, and the preventive controls from Weeks 1–4. Improvements from past incidents feed back into these.
- **Detect** — Week 5's pipeline.
- **Respond, Recover** — today's material.

The key shift for this week's reading question: lessons learned aren't a final phase you reach after service is restored — **improvement runs across all six functions**. An incident that ends with "service restored" and no change to architecture or controls is an incident you've scheduled to happen again.

### CSA Cloud Controls Matrix — Proving a Control Actually Works

The **CCM** is the Cloud Security Alliance's cloud-specific control framework: control objectives organized into domains (identity and access management, cryptography and key management, logging and monitoring, security incident management, supply chain, and more), mapped to other standards such as ISO 27001 and NIST, with the **CAIQ** (Consensus Assessments Initiative Questionnaire) as its companion questionnaire for assessing a provider.

The useful habit from this reading: a control isn't "done" because it's configured; it's done when you can show **evidence it's operating**. Using controls from this course:

| Control (Week) | Evidence it's operating |
|---|---|
| MFA on all human IAM users (Week 2) | IAM credential report showing `mfa_active=true` for every console user; CloudTrail `ConsoleLogin` events with `MFAUsed: Yes` |
| KMS key-policy explicit deny (Week 3) | The `AccessDenied ... with an explicit deny in a resource-based policy` error from Lab 3 — not the implicit-deny wording |
| IaC scanning in CI (Week 4) | Pipeline logs showing Checkov ran on every merge and failed builds that violated policy |
| CloudTrail logging (Week 5) | An alert that fires when `StopLogging` or `DeleteTrail` is called — and a test showing it did |

---

## Part 2 — Final Project Presentations

Every presentation follows the same arc you used in your report: what happened, the timeline, the attack path, the ATT&CK mapping, and the control that would have broken the chain.

**While you listen, take notes like an incident responder.** For each breach, jot down:
1. **Initial access** — how did the attacker get in?
2. **Dwell time and detection** — how long were they inside, and who noticed (the victim, a third party, or the attacker announcing it)?
3. **The one control** — the single control that would have most changed the outcome.

You'll use these notes on Quiz 5's free-response question. Patterns to listen for across the room: stolen or leaked credentials (keys in code, MFA fatigue, missing MFA), third-party and supply-chain access, and breaches discovered by someone *other* than the victim.

---

## Guest Speaker — Keith Hodo, Amazon Web Services

**Cyber Security in the Era of Agentic Coding.** Keith is a Senior Partner Solutions Architect at AWS. His talk follows a new security hire at a fictional pharmaceutical company building a clinical-trial platform with AI agents in the development loop.

Ideas to listen for, and how they connect to this course:
- **"Security is job zero"** — and agents raise the stakes, because the same team can now ship far more software that touches sensitive data.
- **Least agency** extends Week 2's least privilege to autonomy: the minimum tools, context, network reach, and decision authority an agent needs, with destructive actions held for explicit human approval.
- **A prompt is not a control.** A document that tells an agent to ignore its instructions is *data, not authority* — boundaries are enforced by identity and infrastructure, then verified. (OWASP Top 10 for LLM Applications: LLM01 Prompt Injection, LLM03 Supply Chain, LLM06 Excessive Agency.)
- **Every actor needs its own identity** — people, workloads, and agents — so the log can trace *person → agent session → model request → tool call → changed record*. That's this week's IR lesson applied to agents: if your logs can't tell the story, you can't respond.
- **Rehearse containment for agents too:** disable a tool, revoke an agent's credentials, freeze memory, roll back, go manual — ideally within ten minutes.

---

## Course Wrap-Up — Six Weeks, One Chain

| Week | Theme | The control layer |
|---|---|---|
| 1 | Cloud Security Foundations | Shared responsibility, threat modeling, asset inventory |
| 2 | Identity Is the Perimeter | IAM, least privilege, MFA, Zero Trust |
| 3 | Secure the Cloud Stack | Encryption & KMS, network segmentation, CSPM, API security |
| 4 | Cloud-Native Security | Containers, IaC scanning, supply chain |
| 5 | Detect the Attack | Logging pipeline, MITRE ATT&CK, GuardDuty & Detective |
| 6 | Respond, Recover, Improve | IR team/plans/tools, OODA, redeploy, lessons learned |

Every breach presented today is a chain where several of these layers failed at once — and every one of them ended in this week's material: someone had to respond, recover, and decide what to change.

---

## Quiz 5

- Opens today, October 2, at 1:00 p.m.
- Closes Sunday, October 4, at 11:59 p.m.
- 90 minutes after starting, 2 attempts
- 6 questions, 10 points — covers today's opener, the guest talk, the Week 6 reading (Ch. 7 Response & Recovery; NIST SP 800-61 Rev. 3; CSA CCM), and one free-response question drawn from a classmate's presentation
