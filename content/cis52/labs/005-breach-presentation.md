# Final Project: Cloud Breach Case Study — Timeline, MITRE ATT&CK Mapping, and Defense

**CIS 52 — Cloud Security Fundamentals**

**Due:** Friday, October 2, 2026, 9:00 a.m. (written report) — **presentations in class the same day, Class 6**
**Canvas:** Final Project assignment (link posted on Canvas)
**Student templates:**
- Write-up: [`templates/005-lab-template.docx`](templates/005-lab-template.docx)
- Slides: [`templates/005-presentation-template.pptx`](templates/005-presentation-template.pptx)

This is the capstone for the course: pick a real-world cloud breach, dig into what actually happened, map it to the MITRE ATT&CK framework, and connect it back to the controls from Weeks 1–4 (IAM and least privilege, encryption and network segmentation, CSPM and API security, container/IaC/supply-chain security). You'll deliver a written report and a short in-class presentation.

**No billed cloud resources or lab environment are required** — this is a research and analysis project based on public breach reporting.

---

## Part 1 — Pick Your Breach

Choose **one** of the following, or pitch your own breach to the instructor for approval before you start writing.

| Breach | Year | Category |
|---|---|---|
| Snowflake Customer Breaches | 2024 | Identity |
| Tesla Kubernetes Dashboard Cryptojacking | 2018 | Containers/K8s |
| SolarWinds Orion | 2020 | Supply Chain |
| Uber — GitHub-Leaked AWS Keys | 2016 | Secrets/Data |
| LastPass | 2022 | Encryption/Key Management |
| MOVEit / Clop | 2023 | Vendor/Supply Chain |
| Microsoft Storm-0558 | 2023 | Key Management |
| Uber — MFA Fatigue Attack | 2022 | Identity |

**Already covered in lecture, open if you want to go deeper than we did in class:**
- Capital One (Week 3)
- Codecov Bash Uploader (Week 4)

**Looking for more ideas or want to see how professionals present breach research?** Browse recent talks at [fwd:cloudsec North America](https://fwdcloudsec.org/conference/north-america/) — a community conference dedicated to cloud security research and incident case studies. Many talks there dissect a single breach or attack technique in the same format you're being asked to produce.

**Submit your pick through the course portal's Final Project topic form as soon as you decide** — one breach per student; first claim holds it, so pick early.

## Part 2 — Written Report

Using the [Word template](templates/005-lab-template.docx), write a report with the following sections. Use real, cited sources — vendor post-incident reports, CISA/CSA advisories, journalist reporting (e.g., Krebs on Security, The Record), and conference talks are all fair game. **Do not fabricate details** — if a fact isn't publicly confirmed, say so.

1. **Executive Summary** (short — 3–5 sentences): what happened, who was affected, and the overall impact.
2. **Background**: the organization, the systems/services involved, and why this environment was an attractive target.
3. **Timeline**: a dated (or relative-time, if exact dates aren't public) sequence of events from initial access through detection and disclosure. A table works well here.
4. **Technical Attack Path**: step-by-step account of how the attacker actually moved through the environment — initial access, how they escalated or pivoted, and how they ultimately accessed or exfiltrated data.
5. **MITRE ATT&CK Mapping**: a table mapping each major step in your technical attack path to a [MITRE ATT&CK](https://attack.mitre.org/) tactic and technique (use the [Enterprise](https://attack.mitre.org/matrices/enterprise/) or [Cloud](https://attack.mitre.org/matrices/enterprise/cloud/) matrix as appropriate) — columns: **Tactic**, **Technique ID & Name**, **How it applied in this breach**.
6. **Defense — What Could Have Stopped It**: for at least three points in the attack path, identify a specific control that could have interrupted it. Tie these back to concepts from this course where they apply (least-privilege IAM, MFA, KMS key policies, network segmentation/Zero Trust, CSPM, secrets management, SBOM/supply-chain controls, etc.) — say which one control you'd prioritize and why.
7. **References**: a list of every source you cited, with links.

## Part 3 — Presentation

Using the [PowerPoint template](templates/005-presentation-template.pptx), prepare a **5-minute presentation (~6–8 slides)** summarizing your report for the class. Suggested slide flow:

1. Title — breach name, organization, year
2. What happened (one or two sentences — the "so what")
3. Timeline
4. Technical attack path (a simple diagram or step list)
5. MITRE ATT&CK mapping (highlight 3–5 key techniques, not the whole table)
6. What could have stopped it
7. Takeaways / lessons for your own cloud environment
8. References

You will present live in class on October 2 (Class 6). Keep it tight — 5 minutes goes fast. Practice out loud at least once before class.

---

## Grading

| Component | Weight |
|---|---|
| Written report — timeline, technical accuracy, and MITRE ATT&CK mapping | 40% |
| Written report — defensive recommendations, tied to course concepts | 25% |
| Presentation — clarity, timing, and command of the material | 25% |
| Sourcing — cited, credible references throughout | 10% |

---

## Submission

- **Written report** as a Word doc or exported PDF, submitted on Canvas by Friday, October 2, 2026, 9:00 a.m.
- **Slides** submitted on Canvas before class the same day, and presented live in class.
- Late work follows the syllabus's 10% deduction policy; your lowest lab score is still dropped, but plan to submit this one on time since presentations happen in class.
