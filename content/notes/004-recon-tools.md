# CIS 55 – Lecture 4 Notes
**Topics:** Uber Hack 2022, OSINT, Reconnaissance Tools (Maltego, Recon-NG, Shodan, Censys, theHarvester)

---

## Course Logistics

- **Lab 4 due:** February 28 (Friday)
- **Lab 5 due:** March 6
- **Quiz 4:** Open from 1pm today until Sunday midnight

---

## 1. Hacker News – Weekly Roundup

- **AISLE, Windows Internals, AI Magic Strings:** https://www.vitraag.com/security-news
- **Cline Supply Chain Attack:** https://thehackernews.com/2026/02/cline-cli-230-supply-chain-attack.html

---

## 2. Case Study: The Uber Hack (2022)

### What Happened

On September 15, 2022, Uber was compromised through a two-stage attack:

1. **Social Engineering / MFA Fatigue** — The attacker phished an Uber employee's credentials, then repeatedly sent MFA push notifications until the employee approved one out of frustration. This gave the attacker access to Uber's VPN.

2. **Privilege Escalation** — Once inside the network, the attacker found a PowerShell script in a shared network folder. The script contained hardcoded administrative credentials for **Thycotic**, Uber's Privileged Access Management (PAM) system.

### Key Concepts from this Breach

**Social Engineering:** Using psychological manipulation to trick a person into revealing sensitive information or granting access. MFA fatigue is a social engineering technique where attackers spam push notifications hoping the victim approves one.

**Privilege Escalation:** A hacker with limited access increases their permissions. The attacker moved from VPN access → admin access to Thycotic → full credential access for all of Uber's services.

**Thycotic (PAM):** A privileged access management system used to store and manage passwords and secrets. The admin account gave the attacker secrets for **all** Uber services.

### What Was Compromised

| System | Purpose |
|--------|---------|
| **OneLogin** | Identity and Access Management (IAM) / Single Sign-On for all Uber employees |
| **AWS (IAM)** | Controls who has access to every Amazon cloud service Uber runs |
| **DUO** | Multi-factor authentication platform |
| **GSuite** | Google Workspace — email, documents, Drive |
| **Avengers** | Uber's internal financial revenue metrics service |
| **Slack** | Internal communications — attacker posted "I am a hacker and Uber has suffered a data breach" |

**Impact:** With AWS IAM access, the attacker had control over all of Uber's cloud infrastructure — including the databases holding user and payment data. The company was valued at **$65.5 billion** at the time.

### Key Lessons

- Hardcoded credentials in scripts are a critical risk — use secrets management properly
- PAM systems are high-value targets; protect them accordingly
- MFA push notifications can be abused — number matching and phishing-resistant MFA (e.g., hardware keys) are more secure
- Network segmentation limits the blast radius of compromised credentials
- SSO/IAM systems are skeleton keys — their compromise is total compromise

---

## 3. CVE Reminder

A **CVE (Common Vulnerabilities and Exposures)** is a weakness in computational logic that, when exploited, negatively impacts Confidentiality, Integrity, or Availability (CIA).

- **National Vulnerability Database (NVD):** nvd.nist.gov — maintained by NIST
- **CVSS (Common Vulnerability Scoring System):** standardized 0–10 score for severity

---

## 4. Elements of Penetration Testing

| Phase | Description |
|-------|-------------|
| **Planning and Scoping** | Define goals, rules of engagement, and target boundaries |
| **Information Gathering & Vulnerability ID** | Recon, scanning, enumeration |
| **Attacks and Exploits** | Attempt to compromise identified vulnerabilities |
| **Penetration Testing Tools** | Use specialized tooling (Nmap, Nessus, Metasploit, etc.) |
| **Reporting and Communication** | Document findings, risk ratings, and remediation |

---

## 5. Bug Bounty Programs

Bug bounty programs allow ethical hackers to report vulnerabilities to organizations in exchange for rewards. Good starting points:

- **Bugcrowd:** https://bugcrowd.com/domain-vdp-pro
- **HackerOne:** https://hackerone.com/daimler_truck
- **National Cyber League (NCL):** https://nationalcyberleague.org/
  - Practice at: https://trove.cyberskyline.com/

---

## 6. Reconnaissance

**Goal:** Find the most efficient way to attack the target to accomplish the goals of the assessment — without directly engaging the target.

Reconnaissance is the phase where the most time is spent. The information gathered here guides every subsequent phase of a pentest.

Two types:
- **Passive Recon:** Gather information without touching the target (OSINT, search engines, public records)
- **Active Recon:** Interact directly with the target (DNS queries, port scanning, banner grabbing)

---

## 7. OSINT (Open Source Intelligence)

OSINT is the collection and analysis of information from publicly available sources. It is the foundation of passive reconnaissance.

### Categories of OSINT

**Google Hacking (Google Dorking)**

Use advanced search operators to find sensitive information indexed by Google.

| Operator | What It Searches | Example |
|----------|-----------------|---------|
| `site:` | Pages on a specific domain (cannot search port) | `site:example.com` |
| `inurl:` | The full URL, including port and file path | `inurl:admin login` |
| `filetype:` | Specific file extensions | `filetype:pdf confidential` |

Full database of Google dorks: https://www.exploit-db.com/google-hacking-database

**Data Recon**

- How to use breach data: https://www.youtube.com/watch?v=UeI7wEdLPn8
- Corporate structure info: https://opencorporates.com/
- Government/military example (Army recon doctrine): https://fas.org/irp/doddir/army/atp2-22-9.pdf

**Social Recon**

- OSINT Framework (interactive tool map): https://osintframework.com/
- OSINT CTF challenge: https://resources.infosecinstitute.com/topic/trend-micro-osint-challenge/#gref
- OSINT Curious (YouTube): https://www.youtube.com/watch?v=zo_geMvcOg8
- Photo EXIF data extractor: https://exif.tools/

**Communities**

- r/OSINT: https://www.reddit.com/r/OSINT/

---

## 8. Recon Tools

### Maltego

Maltego is a comprehensive tool for **graphical link analysis** — it offers real-time data mining and information gathering, representing relationships on a **node-based graph**. It uses an entity-relationship model to make patterns and multi-hop connections visually identifiable.

- Used for OSINT and digital forensics
- **Maltego CE** (Community Edition) ships with Kali Linux — free with result limits
- Entities: Domain, IP, Person, Email, Organization, URL, Netblock, etc.
- **Transforms** query external data sources and expand entities on the graph

**Typical use:** Start with a domain → run transforms → discover IPs, MX records, emails, related domains, and person profiles automatically.

---

### Recon-NG

Recon-NG is a powerful **web reconnaissance framework** written in Python, similar to theHarvester but more modular (similar in structure to Metasploit). It is included in Kali Linux.

- Created by Tim Tomes (@LaNMaSteR53)
- Module categories: Recon (77), Reporting (8), Import (2), Exploitation (2), Discovery (2)
- Results are stored in a per-workspace database

**Basic workflow:**
```
workspaces create [name]
marketplace install [module]
modules load [module]
options set SOURCE [target]
run
show hosts / show contacts
```

---

### Shodan

Shodan is often called **"the scariest search engine on the planet."** Instead of indexing web pages, Shodan scans the internet and indexes **banners** returned by servers and devices — revealing open ports, services, and software versions.

- Indexes: webcams, routers, power plants, VoIP phones, industrial control systems, IoT devices
- Allows advanced passive recon on a target without touching it directly
- A malicious actor can use Shodan to find a foothold before ever contacting the target

**Example search:**
```
telnet port:23 country:"US"
```

This reveals internet-facing Telnet services in the US — a major misconfiguration and security risk.

---

### Censys

Censys (https://search.censys.io/) is a search engine similar to Shodan, with a stronger focus on **TLS certificates** and structured data. Data is grouped into three views:

| View | Contents |
|------|---------|
| **IPv4 Hosts** | Open ports, banners, and services per IP |
| **Top Million Websites** | Web-facing services for popular domains |
| **Certificates** | TLS certificate data — useful for subdomain enumeration |

The certificate view makes Censys especially powerful for discovering subdomains through **certificate transparency logs**.

---

### theHarvester

theHarvester is a CLI-based tool for gathering emails, subdomains, hosts, employee names, and open ports from multiple public sources.

- Data sources: Google, Bing, LinkedIn, Twitter, Shodan, VirusTotal, and more
- Highly effective during **black box assessments** where you start with only a domain name

**Common options:**

| Flag | Purpose |
|------|---------|
| `-d` | Target domain or company name |
| `-b` | Data source (google, bing, shodan, linkedin, etc.) |
| `-l` | Limit number of results |
| `-f` | Save results to HTML and XML |
| `-n` | DNS reverse query on discovered ranges |
| `-c` | DNS brute force for domain |
| `-h` | Use Shodan database to enrich discovered hosts |

**Example commands:**
```bash
theharvester -d microsoft.com -l 500 -b google -h myresults.html
theharvester -d microsoft.com -b pgp
theharvester -d microsoft.com -l 200 -b linkedin
theharvester -d apple.com -b googleCSE -l 500 -s 300
```

---

## 9. Additional Tools (Lab 5 Preview)

### OWASP Top 10

The OWASP Top 10 lists the most critical web application security risks.

- **CSRF (Cross-Site Request Forgery):** Tricks a browser into making unauthorized requests — can be used to steal session cookies
- **XSS (Cross-Site Scripting):** Injects JavaScript into a website. XSS can be chained into CSRF — run script on victim's browser → forge requests as the victim

### Hacker Tools

| Tool | Platform | Purpose |
|------|----------|---------|
| **Ncat** | Linux | Network utility for reading/writing data across networks (like netcat) |
| **Mimikatz** | Windows | Post-exploitation tool for extracting plaintext passwords and hashes from Windows memory |

---

## Reminders

- **Quiz 4:** Open 1pm today until Sunday midnight
- **Lab 4 due:** Friday, February 28
- **Lab 5 due:** March 6
