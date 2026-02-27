# Villager (CyberSpike)

Villager is an **AI-native command-and-control (C2) framework** developed by CyberSpike, positioned as a next-generation successor to Cobalt Strike. Released in July 2025, it integrates large language models (LLMs) directly into the attack lifecycle — accepting natural-language objectives and automatically translating them into multi-step technical attack chains. It is studied here as an example of how AI is reshaping offensive tooling and what defenders must now account for.

> **Note:** Villager is a dual-use research tool. All use must be within authorized pentesting engagements, CTF competitions, or controlled lab environments.

## Overview

Villager is significant for:
- **AI-Driven Attack Automation**: Natural language directives are decomposed into subtasks with dependency tracking and failure recovery — no rigid playbooks
- **C2 Operations**: Task-based architecture manages agents, persistence, and lateral movement
- **Containerized Evasion**: Kali Linux attack environments in self-destructing containers that wipe evidence after 24 hours
- **LLM-Assisted Exploitation**: Uses DeepSeek v3 with a database of 4,201 AI system prompts to dynamically select and chain tools

### Architecture

Villager runs as a distributed set of services:

| Service | Port | Role |
|---------|------|------|
| MCP Client | 25989 | Message coordination between components |
| Kali Driver | 1611 | Containerized attack execution environment |
| Browser Automation | 8080 | Client-side and web application attacks |
| FastAPI C2 Interface | 37695 | Task submission and agent management |

### Installation

```bash
# Install from PyPI (10,000+ downloads since July 2025)
pip install villager-ai

# Requires: Docker (for Kali containers), Python 3.10+
# Requires: DeepSeek API key or compatible OpenAI API endpoint

# Start services
villager start
```

:::command-builder{id="villager-builder"}
tool_name: villager
target_placeholder: "192.168.1.100"
scan_types:
  - name: "Submit Recon Task"
    flag: "task submit --goal"
    desc: "Submit a high-level recon objective; AI decomposes into subtasks"
  - name: "List Active Tasks"
    flag: "task list"
    desc: "Show all running and queued attack tasks with status"
  - name: "Execute Tool Chain"
    flag: "chain run"
    desc: "Run a multi-tool attack chain orchestrated by the AI"
  - name: "Spawn Agent"
    flag: "agent deploy"
    desc: "Deploy a persistent agent on a compromised host"
options:
  - name: "Target Host"
    flag: "--target"
    desc: "Set the target IP or domain"
  - name: "AI Model"
    flag: "--model"
    desc: "Select AI backend (deepseek-v3, gpt-4o, etc.)"
  - name: "Stealth Mode"
    flag: "--stealth"
    desc: "Enable forensic evasion and log wiping"
  - name: "Parallel Tasks"
    flag: "--parallel"
    desc: "Execute subtasks concurrently for speed"
:::

## Core Concepts

### How Villager Differs from Cobalt Strike

| Feature | Cobalt Strike | Villager |
|---------|--------------|---------|
| **Command model** | Manual operator scripting | Natural language → AI-generated attack steps |
| **Playbooks** | Static Aggressor scripts | Dynamic, AI-adjusted tactics based on live recon |
| **Tool selection** | Operator chooses tools | AI selects tools based on target profile (WPScan for WordPress, API fuzzer for REST APIs, etc.) |
| **Evasion** | Manual OPSEC | 24-hour self-destructing containers, automated log wiping |
| **Expertise required** | High — deep knowledge of TTPs | Lower — operators issue goals, not commands |

### AI Attack Decomposition

When given a goal like `"find and exploit a foothold on 192.168.1.0/24"`, the AI engine:

1. **Decomposes** the goal into subtasks (host discovery → port scan → vulnerability ID → exploit selection)
2. **Selects tools** dynamically (nmap → nuclei → metasploit or custom exploit)
3. **Tracks dependencies** — later tasks wait on results from earlier ones
4. **Recovers from failures** — if one exploit fails, the AI tries alternative paths
5. **Executes code** directly via `pyeval()` and `os_execute_cmd()` built-ins

### Key Offensive Capabilities

```
- Automated recon-to-exploit pipeline with no manual steps
- Containerized Kali Linux — isolated, scalable, disposable attack nodes
- Browser automation for phishing simulation and client-side exploitation
- Multi-target parallel attack chains
- Direct code execution within the AI's reasoning loop
- Forensic evasion: 24-hour container self-destruct wipes logs and artifacts
```

---

:::scenario{id="scenario-1" level="beginner"}
title: "Understanding AI-Decomposed Recon"
goal: "See how Villager translates a natural language recon goal into concrete tool commands."
hint: "The AI model maps the goal to a sequence of standard tools. This is what defenders must now detect — not just individual tool signatures but orchestrated multi-tool chains."
command: "villager task submit --goal 'enumerate services on 10.0.0.5' --target 10.0.0.5"
expected_output: |
  [villager] Goal received: enumerate services on 10.0.0.5
  [AI] Decomposing into subtasks...

  Subtask 1: nmap -sV -sC -p- 10.0.0.5
  Subtask 2: banner grab open ports via netcat
  Subtask 3: check discovered services against CVE database
  Subtask 4: summarize findings and suggest next steps

  [villager] Running subtask 1...
  PORT     STATE SERVICE  VERSION
  22/tcp   open  ssh      OpenSSH 8.9p1
  80/tcp   open  http     Apache 2.4.52
  3306/tcp open  mysql    MySQL 8.0.31

  [AI] Analysis: Apache 2.4.52 has known CVEs. Recommend subtask: nuclei scan.
  [villager] Task complete. 3 subtasks executed, 1 finding escalated.
:::

:::scenario{id="scenario-2" level="intermediate"}
title: "Containerized Attack Execution"
goal: "Understand how Villager uses disposable Kali containers to isolate and erase attack artifacts."
hint: "Each attack session runs inside a Docker container managed by the Kali Driver service (port 1611). The container auto-destructs after 24 hours, deleting all logs, tool outputs, and network traces from the attack node — a key forensic evasion technique defenders must account for."
command: "villager agent deploy --target 10.0.0.5 --stealth --ttl 24h"
expected_output: |
  [villager] Spawning Kali container...
  [villager] Container ID: kali_7f3a2b9c
  [villager] Agent deployed on 10.0.0.5
  [villager] Stealth mode: ON
  [villager] Self-destruct scheduled: 24h from now

  # All attack artifacts (logs, tool outputs, shell history)
  # are stored only inside this container.
  # After 24h: container wiped, no forensic trace on attack node.

  # Defender note: Detect via network behavior, not endpoint artifacts.
  # Look for: unusual outbound connections, container registry pulls,
  # anomalous process trees from containerized environments.
:::

:::scenario{id="scenario-3" level="intermediate"}
title: "Dynamic Tool Selection for Web Targets"
goal: "See how the AI selects the right tool based on the target's technology stack."
hint: "This is the key AI capability: instead of the operator knowing to use WPScan for WordPress or sqlmap for SQL injection, the AI fingerprints the stack and picks the appropriate tool automatically. Defenders should watch for rapid sequential tool signatures from the same source IP."
command: "villager task submit --goal 'test web app for vulnerabilities' --target https://example.com"
expected_output: |
  [AI] Fingerprinting target: https://example.com
  [AI] Detected: WordPress 6.4.2, PHP 8.1, MySQL

  [AI] Tool selection:
    - WPScan → enumerate plugins and users
    - nuclei wordpress-* templates → known CVEs
    - sqlmap → test login form for SQLi

  [villager] Running WPScan...
  [+] WordPress version 6.4.2 identified
  [+] Plugin: contact-form-7 v5.8 (vulnerable: CVE-2024-XXXX)
  [+] User enumeration: admin, editor

  [AI] Escalating: plugin CVE found. Recommend exploit attempt.
:::

## Defensive Implications

Understanding Villager is critical for defenders because it changes the threat model:

| Old Assumption | New Reality with AI-Native C2 |
|----------------|-------------------------------|
| Attacks follow predictable TTPs | AI dynamically adapts — no fixed playbook to signature |
| Tools leave known artifacts | Self-destructing containers erase endpoint evidence |
| High attacker expertise required | Low-barrier — natural language lowers skill floor |
| Sequential manual steps | Parallel automated chains compress attack timelines |

### Detection Strategies

```
1. Network-based detection (not endpoint):
   - Watch for rapid sequential scans from single IPs
   - Alert on multi-tool signatures in short time windows (nmap → nuclei → sqlmap < 5 min)
   - Monitor for unusual container registry pulls (kalilinux/kali-rolling)
   - Detect MCP/FastAPI C2 traffic patterns on unusual ports (25989, 37695)

2. Behavioral detection:
   - Anomalous process trees (docker → kali tools chain)
   - Outbound connections to LLM API endpoints during active sessions
   - Bulk DNS lookups followed by rapid port scans

3. Threat Intelligence:
   - Track PyPI packages: villager-ai and dependencies
   - Monitor CyberSpike IOCs and C2 infrastructure
```

---

:::quiz{id="quiz-1"}
Q: What is the primary way Villager differs from traditional C2 frameworks like Cobalt Strike?
- [ ] It uses more exploits than Cobalt Strike
- [x] It accepts natural language goals and uses AI to dynamically generate and execute attack steps
- [ ] It only targets Windows systems
- [ ] It requires less network access than Cobalt Strike
:::

:::quiz{id="quiz-2"}
Q: Why do Villager's self-destructing containers complicate forensic investigation?
- [ ] They encrypt all files on the target
- [ ] They disable antivirus on the target host
- [x] They wipe attack logs and artifacts from the attack node after 24 hours, leaving no trace of the tooling used
- [ ] They delete files on the victim machine
:::

:::quiz{id="quiz-3"}
Q: What is the best detection strategy against AI-native C2 frameworks that erase endpoint artifacts?
- [ ] Scan endpoints for known malware signatures
- [ ] Check for Cobalt Strike beacon patterns
- [x] Focus on network-based behavioral detection — rapid multi-tool sequences and unusual outbound connections
- [ ] Require stronger passwords on all accounts
:::

## Quick Reference

| Component | Default Port | Purpose |
|-----------|-------------|---------|
| MCP Client | 25989 | Inter-service message coordination |
| Kali Driver | 1611 | Container orchestration for attacks |
| Browser Automation | 8080 | Web and client-side exploitation |
| FastAPI C2 | 37695 | Task submission and agent control |

| Concept | Description |
|---------|-------------|
| AI decomposition | Goal → subtasks with dependency graph |
| Kali Driver | Docker-based disposable attack containers |
| Self-destruct TTL | 24h container auto-wipe for forensic evasion |
| pyeval() | Direct Python execution within AI reasoning loop |
| 4,201 prompts | Built-in library of exploit-generation system prompts |
