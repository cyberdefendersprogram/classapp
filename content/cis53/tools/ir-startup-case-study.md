# Incident Response Startup Case Study

**CIS 53 — Intrusion Detection In-Depth**

Instead of re-reading an old breach, you will research a **new company** working on detection and incident response. These companies are being built right now around the same problems this course covers: too many alerts, too little analyst time, cloud and SaaS visibility, and attacks on and by AI.

## The assignment

Choose **one** company from the list below (or get another approved by the instructor). Write 600+ words (about 1–2 pages) covering:

1. **The problem:** what pain point does the company say it solves, and for whom?
2. **How it works:** what data does it collect or read (network, cloud logs, endpoint, identity, email, AI/LLM logs)? What does it detect, investigate, or automate?
3. **Where AI is used:** be specific. What is the model doing, what do the company's materials *claim*, and what evidence do they show?
4. **Compare to this class:** which parts could you build with Zeek, Suricata, Sigma, and a SIEM? What would you still have to do by hand?
5. **Map to frameworks:** pick two attacker behaviors the product says it catches and map them to MITRE ATT&CK (and ATLAS for AI-related ones).
6. **Business and stage:** funding, customers, and competitors as stated in primary sources.
7. **Critique:** three questions you would ask in a demo, and one risk (false positives, blind spots, data privacy, over-trusting AI).

**Present** the highlights in 3 minutes at the last class (Dec 4), alongside the guest lecture.

## How to research

- Start with the company's own site, documentation, blog, and demo videos. Add press releases, customer stories, conference talks, and independent coverage.
- Funding numbers below come from roundups and articles, and **sources disagree**. Confirm every figure in a primary source (the company's announcement or filing) before you use it, and cite where you got it.
- Do not sign up for trials or share school or personal data with any company without checking with me. Do not contact the company on the course's behalf.
- Treat marketing as claims, not facts. Say what the company *says* and what it *shows*.

## Companies to research

All names and figures are as reported in secondary sources in October 2026 — verify before relying on them.

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

### Securing AI systems and agents (the "threats to AI" side of this course)

| Company | What it does (as reported) | Stage / funding (as reported) |
|---|---|---|
| Noma Security | Security posture for AI agents | $100M Series B (Jul 2025) |
| WitnessAI | AI security and governance | $58M Series B (Jan 2026) |
| Runlayer | MCP security gateway | $11M seed (Nov 2025) |
| Helmet Security | MCP infrastructure security | $9M seed (Dec 2025) |
| Operant AI | MCP and AI runtime security | $13.5M Series A (Sep 2024) |
| Zenity | AI agent security | Named in reports; find the details yourself |

**Already acquired (good for "what happened to the startup" angles):** Protect AI (Palo Alto Networks), Lakera (Check Point), Pangea (CrowdStrike), Aim Security (Cato Networks), CalypsoAI (F5).

### Offensive AI (for contrast)

XBOW (autonomous offensive security) and RunSybil (AI-native offensive security). Pick one of these only if your case study explains how a defender should expect their attacks to look.

## Grading

Graded with the same case-study rubric as other case studies (structure, spelling, grammar, technical research and analysis, and conclusions), with extra weight on **evidence for claims** and **a clear distinction between what the company says and what it shows**.
