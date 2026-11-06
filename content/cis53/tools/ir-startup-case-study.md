# Incident Response Startup Case Study

**CIS 53 — Intrusion Detection In-Depth**

Instead of re-reading an old breach, you will research a **new company** working on incident response: finding, investigating and containing attacks faster. These companies are being built right now around problems this course covers: too many alerts, too little analyst time, cloud and SaaS visibility, and the question of what an AI model can safely do in a SOC.

## The assignment

Choose **one** company from the list below (or get another incident-response company approved by the instructor by Tuesday, Nov 10). The Word template and the exact headings are on the Canvas assignment (Case Study 3, due Fri Nov 13, 9:00 a.m.). Write 600+ words (2–3 pages) covering:

1. **Summary:** what the company sells, who buys it, and your judgment.
2. **The problem and the data it reads:** the pain point, and which data it collects or reads (packets, flow, logs, alerts, cloud, identity, endpoint, email, AI/LLM logs). How does it handle encrypted traffic?
3. **How it works and where AI is used:** a table of claims, the evidence the company shows, and the source. What is the model doing, and what does a human still decide?
4. **Build it yourself:** which parts you could build with Zeek, Suricata, Sigma and a SIEM, what you would still do by hand, and one concrete detection sketch.
5. **Map to frameworks:** two attacker behaviors the product says it catches, mapped to MITRE ATT&CK (and ATLAS for attacks on AI).
6. **Business and stage:** funding, customers and competitors from primary sources.
7. **Critique:** three demo questions, one risk, and one sentence tying it to Class 3 (DNS, HTTP, TLS metadata, server-side evidence).
8. **Sources:** four or more, with at least two primary.

**Present** the highlights in 3 minutes at the last class (Dec 4), alongside the guest lecture.

## How to research

- Start with the company's own site, documentation, blog, and demo videos. Add press releases, customer stories, conference talks, and independent coverage.
- Funding numbers below come from roundups and articles, and **sources disagree**. Confirm every figure in a primary source (the company's announcement or filing) before you use it, and cite where you got it.
- Do not sign up for trials or share school or personal data with any company without checking with me. Do not contact the company on the course's behalf.
- Treat marketing as claims, not facts. Say what the company *says* and what it *shows*.

## Companies to research

All names and figures are as reported in secondary sources in October 2026 — verify before relying on them. Only incident-response companies are eligible; AI-security and offensive-AI startups are not part of this assignment.

### AI SOC and autonomous investigation

| Company | What it does (as reported) | Stage / funding (as reported) |
|---|---|---|
| 7AI | Autonomous security agents for the SOC | $130M Series A (Dec 2025); launched from stealth Feb 2025 with a $36M seed |
| Dropzone AI | AI SOC analyst that investigates alerts | About $57M total; $37M Series B (Jul 2025) |
| Prophet Security | AI SOC analyst | Reported about $41M total, including a $30M Series A |
| Qevlar AI | Autonomous SOC investigation (Paris) | $30M Series A (Mar 2026) |
| Surf AI | Agentic operations for security teams | Launched with $57M (Mar 2026) |
| Torq | Agentic SOC hyperautomation | $140M Series D (Jan 2026), reported $1.2B valuation (a larger, later-stage company, good for comparison) |
| Artemis Security | AI-native SOC automation | Reported $70M seed and Series A (Apr 2026); thinly sourced, check carefully |

### Cloud and SaaS incident response and forensics

| Company | What it does (as reported) | Notes |
|---|---|---|
| Mitiga | Incident readiness and response for cloud, SaaS, and hybrid environments | Funding figures conflict across sources |
| Cado Security | Cloud-native forensics and investigation across AWS, Azure, and Google Cloud | Reported as acquired by Darktrace in 2025; confirm |
| Ciroos | Multi-agent "AI SRE teammate" for incident diagnosis (DevOps/SRE angle) | Early stage |

## Grading

Graded with the same case-study rubric as other case studies (structure, spelling, grammar, technical research and analysis, and conclusions), with extra weight on **evidence for claims** and **a clear distinction between what the company says and what it shows**.
