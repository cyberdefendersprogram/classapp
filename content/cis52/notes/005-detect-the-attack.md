# CIS 52 — Week 5 Notes
**Detect the Attack**

Friday, September 25, 2026 · 9:00 a.m.–12:00 p.m.

---

## Before We Start

Lab 4 was due today at 9:00 a.m. Late work is accepted through the last class session with a 10% deduction; your lowest lab and lowest quiz score are each dropped. Quiz 5 opens today at 1:00 p.m. and closes Sunday, September 27, at 11:59 p.m.

## Quick Review — Implicit vs. Explicit Deny in AWS IAM/KMS

Before we get into today's material, a quick correction from Lab 3's key-policy denial exercise (Part 2, Step 4) — this is worth reviewing early since it trips people up.

**AWS's authorization model is default deny**: unless something explicitly grants a permission, the request is denied. That default-deny outcome is called an **implicit deny** — nothing said yes, so the answer is no.

An **explicit deny** is different: a policy (identity-based, resource-based, SCP, permissions boundary, etc.) contains an `"Effect": "Deny"` statement that actively blocks the action, even if some other policy would otherwise allow it.

**Why the distinction matters:** an explicit Deny always wins, no matter what else grants access. Implicit deny only "wins" because nothing granted access in the first place — add a grant anywhere, and the request succeeds. This is the mechanism behind patterns like the lab's "Eve" exercise: you don't just avoid granting Eve access, you actively write a Deny statement on the key policy so that even if Eve is later added to an admin group with broad KMS permissions, she's still blocked from this specific key.

### How to Tell Them Apart from the Error Message

This is exactly what the lab asked you to prove, and it's diagnosable from the `AccessDenied` error text alone:

- **Implicit deny (no grant exists):**
  > ... is not authorized to perform: `kms:Decrypt` because no identity-based policy allows the `kms:Decrypt` action

  This says "nothing gave you permission." It does **not** prove a Deny statement was added to the key policy — it only proves the second principal was never granted `kms:Decrypt` in the first place. Functionally the decrypt still fails, so at a glance it looks like the exercise worked, but it doesn't demonstrate the mechanism the lab is teaching.

- **Explicit deny (a Deny statement is present and matched):**
  > ... is not authorized to perform: `kms:Decrypt` on resource: ... with an explicit deny in a resource-based policy

  The phrase **"explicit deny"** appears directly in the error. This is AWS confirming a Deny statement in the key policy is what blocked the request — proof you actually edited the key policy to add a Deny statement for that principal/action, which is the specific deliverable Part 2 Step 4 asked for.

### The General Lesson

When AWS denies a request, always check **why** in the error text:

1. **Implicit deny** → "no identity-based/resource-based policy allows this action." Fix: add a grant — or, if you're intentionally teaching/testing a deny pattern, recognize that this error alone doesn't demonstrate a deny statement exists.
2. **Explicit deny** → "with an explicit deny in a resource-based/identity-based policy." This is a deliberate block that overrides any other grant — the mechanism used for scenarios like "block this one user even though they're in an admin group."

A few Lab 3 submissions produced a correct-looking `AccessDenied` screenshot, but the error text showed the implicit-deny wording rather than "explicit deny" — meaning the key policy likely never had a Deny statement added; the second principal simply hadn't been granted access. Worth double-checking your own screenshot's exact error text against this before you consider that step done.

## Today's Agenda

**Part 1 — Foundations of Detection**
- Recap Week 4 + Lab 4 debrief (container/image scanning, IaC scanning, Kubernetes manifest review)
- Why detection matters: mean-time-to-detect, and the limits shared responsibility puts on what you can even see
- Vocabulary: logs/events vs. alerts vs. metrics; toxic vs. sanitized logs
- What to watch: threat-model-driven logging, privileged-user monitoring, defensive-tool logs, cloud service logs/metrics, deception techniques

**Break — 10 minutes**

**Part 2 — The Detection Pipeline and MITRE ATT&CK**
- How to watch: aggregation & retention → parsing → search & correlation → alerting → SIEM → threat hunting
- MITRE ATT&CK: using the Cloud Matrix to decide what telemetry to collect, not just to label an attack after the fact
- AWS's detect/investigate stack: GuardDuty and Detective, building on Week 4's preview ("Detect → Investigate → Respond")
- Case study revisited: what logs and alerts would have caught Capital One (Week 3) and the Codecov compromise (Week 4) sooner
- Setup: Final Project reminder

---

## Books + Reading

Required — Practical Cloud Security, 2nd Ed. (Dotson), Ch. 7, Detection sections (through "Threat Hunting"). Required — MITRE ATT&CK, Enterprise Cloud Matrix.

**Reading question:** Choose three MITRE ATT&CK techniques from the Cloud Matrix and identify the telemetry you would use to detect or investigate each one.

---

## Part 1 — Foundations of Detection

### Why Detection Matters

- No set of preventive controls (Weeks 1–4) is ever complete. The question isn't *if* something will eventually get past them, it's *how fast you notice* when it does.
- Industry research cited in this week's reading: breaches that took organizations **under 200 days to identify** saved over **$1 million** compared to slower detection — speed of detection is a direct cost lever, not just a security nicety.
- **Shared responsibility limits what you can see.** You generally cannot see a cloud provider's own internal logs. What *is* newly visible in the cloud, and often underused, is the log of **your own team's actions** taken through the provider's console, API, and CLI — that's the layer this week focuses on watching closely.

### Vocabulary: Logs, Events, Alerts, Metrics

| Term | Definition |
|---|---|
| **Log / Event** | A record of a specific thing that happened (an authentication attempt, a web request, a config change) |
| **Alert** | An event where a rule decided it's worth notifying a human — not every event is an alert |
| **Metric** | A time-based number about system behavior (requests/minute, free disk space) — storage cost stays flat regardless of activity volume, unlike logs |

Every log entry needs at minimum: **when, what, and who** (who may be an automated system, not a person).

**Toxic vs. sanitized logs** — a distinction worth remembering:
- **Toxic logs** may contain secrets outright (raw SSH session recordings, exact commands run via a shell) — access to these should be tightly restricted to a small team, and accessing them should itself generate a notification.
- **Sanitized logs** are designed not to contain secrets (console/API admin actions, auth success/failure) — this is the majority of what you log and search routinely.

**Never put passwords, API keys, or PII directly in a log.** Use a unique identifier with a separate correlation table instead — more copies of a secret is more risk, not more visibility.

### What to Watch

- **You can't log everything usefully** — what you watch has to come from your threat model (Week 1) and your asset inventory (which systems, which data). Watching network *volume* helps catch bulk data theft; it does nothing to catch a single corrupted software update.
- **Privileged-user activity is the highest-value thing to watch.** Stolen or misused admin credentials are among the most common root causes of a breach — monitoring admins isn't about distrust, it's about catching an attacker *wearing an admin's credentials*. Cloud providers log this via services like **AWS CloudTrail** (and Azure Activity Log, Google Cloud's operations suite) — but it usually has to be explicitly enabled and paid for.
- **Defensive tools produce logs too, and those logs need watching just as much as the tools need deploying.** A WAF, firewall, IDS, or antivirus that silently blocks an attack still generates a signal worth investigating — in the 2013 Target breach, one root failure was ignoring antivirus alerts that had already fired.
- **EDR/NDR/XDR** extend antivirus's signature-matching into full behavioral telemetry, historical replay once new threat intel arrives, and the ability to quarantine an entire compromised host, not just a file.
- **Cloud service logs and metrics** — think about what would "go haywire" during an attack on each service you run: a CPU spike may mean cryptomining or ransomware; denied VPC flow traffic *from your own component* means either misconfiguration or an attacker; a spike in database read volume may mean data theft in progress.
- **Deception techniques** (advanced — only after the basics work): **honeypots** (fake systems that exist only to attract and slow attackers), **honey tokens** (fake-but-tempting files or unused API keys that alert on use), **honey IDs** (unused accounts named like `superadmin` that alert immediately if used). Unlike most "security through obscurity," secrecy is essential here — a documented honeypot is a useless honeypot.

---

## Part 2 — The Detection Pipeline and MITRE ATT&CK

### How to Watch: the Detection Pipeline

Whether it's one product (a SIEM) or several stitched together, every detection program needs the same chain:

1. **Aggregation & retention** — centralize logs so an attacker with access to one compromised system can't erase the evidence. Put the log aggregator in a **separate account with separate administrative credentials**, the same principle as Week 2's least privilege and Week 3's KMS key policies. Retain most logs for **at least a year**, balanced against privacy/regulatory limits.
2. **Parsing** — extracting structured fields (timestamp, source IP, outcome) from many different log formats (syslog, CLF/ELF from web servers, CEF, CADF) so they can be searched and correlated together.
3. **Search & correlation** — querying across systems: logins without VPN, malware detection followed by a login, 150 failed logins then one success (brute force), one failed login across 300 accounts then a success on account #301 (password spraying).
4. **Alerting & automated response** — too sensitive, and real signals drown in noise (alert fatigue); too loose, and you miss the real thing. **Logs stopping entirely is itself a signal worth alerting on.** Automated response is powerful but risky — an attacker can deliberately trigger your own lockdown logic as a cheap denial-of-service.
5. **SIEM** — a Security Information and Event Manager can do some or all of the above in one product, applying correlation rules and historical baselines across every log source at once.
6. **Threat hunting** — the one legitimate case of *proactively* looking for trouble instead of reacting to an alert: form a hypothesis ("maybe this specific threat actor is targeting us"), then query your existing data to prove or disprove it. Only attempt this once the basics above are solid.

### MITRE ATT&CK — Using It to Decide What to Log

MITRE ATT&CK documents attacker **tactics, techniques, and procedures (TTPs)** in far more operational detail than a kill chain — and the **Cloud Matrix** exists specifically for cloud-native attack paths. The point for detection: for every technique an attacker could use against your environment, ask **what telemetry would let you catch it**.

| Tactic | Example Cloud Technique | What You'd Watch For |
|---|---|---|
| Initial Access | T1078.004 — Valid Accounts: Cloud Accounts | Login from an unusual location/time, impossible-travel logins |
| Persistence | T1098.001 — Account Manipulation: Additional Cloud Credentials | A new access key or credential issued to an existing identity |
| Privilege Escalation | T1548.005 — Abuse Elevation Control Mechanism: Temporary Elevated Cloud Access | Unusual `AssumeRole` activity, a role gaining broader permissions than its history shows |
| Defense Evasion | T1562.008 — Disable or Modify Cloud Logs | CloudTrail, GuardDuty, or a log sink being disabled or reconfigured — always alert on this one |
| Credential Access | T1552.005 — Unsecured Credentials: Cloud Instance Metadata API | A request pattern to the instance metadata service that doesn't match normal application behavior (this week's Capital One callback) |
| Discovery | T1526 — Cloud Service Discovery | A burst of `List*`/`Describe*` API calls across many services in a short window — reconnaissance after a credential is stolen |
| Exfiltration | T1537 — Transfer Data to Cloud Account | Data replicated or copied to a storage resource in an account you don't control |

This table is a starting point, not the whole matrix — the reading question asks you to build three rows of your own.

### AWS's Detect → Investigate Stack (Building on Week 4)

Week 4 previewed the framing: **Inspector** (before) checks what could go wrong; **GuardDuty** (during) watches live log streams for malicious behavior as it happens; **Detective** (after) graphs related activity so an investigation takes minutes instead of days.

- **GuardDuty** is a managed threat-detection service. It doesn't collect its own new data — it continuously analyzes **CloudTrail events, VPC Flow Logs, and DNS logs** you're likely already generating, correlates them against threat-intelligence feeds (known-bad IPs, domains), and raises **findings** for things like a port scan, a call from an anonymizing proxy, or an EC2 instance querying a bitcoin-mining domain. This is a direct, managed implementation of this week's "aggregation → correlation → alerting" pipeline.
- **Detective** takes over once GuardDuty (or another source) raises a finding — it automatically builds a graph of related entities (an IAM principal, an IP, an EC2 instance) across your log history so an analyst can answer "what else did this credential touch?" without manually cross-referencing CloudTrail by hand.
- Neither tool replaces the controls from Weeks 1–4 — they exist to tell you **when a control was missing or bypassed**.

### In-Class Exercise — GuardDuty Findings (15 minutes)

Work in pairs. Full step-by-step instructions, including the exact CLI commands, are on the [GuardDuty tool page](../tools/guardduty.md#in-class-exercise-15-minutes).

1. Enable GuardDuty on your lab account (if not already on).
2. Generate sample findings — one instance of every finding type, instantly, no real attack required.
3. Pick one **High** severity finding and identify its finding type, the MITRE ATT&CK tactic it maps to, and which log source (CloudTrail, VPC Flow Logs, or DNS) it most likely drew on.
4. Be ready to share your mapping — we'll build a shared tactic-coverage list as a class.

### Case Study Revisited — What Would Have Caught It Sooner

- **Capital One (Week 3):** the SSRF request that reached the instance metadata service is exactly the kind of anomalous request pattern GuardDuty's `UnauthorizedAccess:EC2/MetadataDNSRebind` and related findings are built to catch — a credential-access technique this week's telemetry table calls out directly.
- **Codecov (Week 4):** an uploader script phoning home to an unfamiliar host from inside a CI pipeline is a network anomaly a NIDS/EDR or an outbound-traffic-monitoring rule should have flagged — the chapter's repeated point that no single tool is enough, and that outbound behavior deserves the same scrutiny as inbound.

The throughline from Week 1 onward continues: it's not one missing control, it's an uninterrupted chain — and detection is the layer that catches the chain *while it's still being pulled*, instead of after the fact.

---

## Final Project Reminder

The **Final Project (Cloud Breach Case Study)** is due **Friday, October 2, 2026, 9:00 a.m. — Class 6**, with live in-class presentations that same day. See [`labs/005-breach-presentation.md`](../labs/005-breach-presentation.md) for the full assignment, breach shortlist, and templates. If you haven't picked a breach yet, do it this week — first claim holds it.

---

## Quiz 5

- Opens today, September 25, at 1:00 p.m.
- Closes Sunday, September 27, at 11:59 p.m.
- 90 minutes after starting, 2 attempts
- 6 questions, 10 points — covers today's lecture plus the Week 5 reading (Ch. 7 Detection sections; MITRE ATT&CK Cloud Matrix)

---

## Next Week — Respond to the Attack (Class 6, October 2)

- **Final Project due** at the start of class, with presentations in class
- Read Practical Cloud Security, Ch. 7, Response and Recovery sections; NIST SP 800-61 Rev. 3 (Incident Response); Cloud Security Alliance Cloud Controls Matrix
- Be ready to reason about incident response teams and plans, the OODA loop, cloud forensics, blocking unauthorized access and exfiltration, and recovery/lessons-learned — picking up exactly where this week's detection pipeline hands off
