# CIS 55 – Lecture 6 Notes
**Topics:** Security Careers, Red Team Paths, Certifications, CTF/Labs, Bug Bounties, Resources

---

## Course Logistics

- **Last lecture** of CIS 55 (Hacker Techniques)
- **Last quiz:** Opens today (March 8) at 12pm — due midnight Sunday
- **Bug Bounty Class:** Friday, March 14, 11am–12pm (Frozendo, Davis, Tega, Cynthia, Israel)

### Class Schedule Summary

| Date | Topic | Deliverables |
|------|-------|-------------|
| Jan 26 | 1 - Introduction | CIA Triad |
| Feb 2 | 2 - Cryptography & Incident Response | Lab 1, Quiz 1 |
| Feb 9 | 3 - Pentesting Tools (Nmap, Nessus, Metasploit, SQLMap) | Lab 2, Quiz 2 |
| Feb 16 | Holiday (President's Day) | — |
| Feb 23 | 4 - Threat Modeling, OSINT, OWASP, Recon Tools | Lab 3, Quiz 3 |
| Mar 1 | 5 - Cloud Security, LLM Security | Lab 4, Quiz 4 |
| Mar 8 | 6 - Security Careers and Presentations | Lab 5, Quiz 5 |

---

## Security News

- **Flight Radar 24 under DDoS:** https://www.paddleyourownkanoo.com/2025/03/05/the-worlds-most-popular-flight-tracker-is-fighting-an-ongoing-ddos-cyber-attack
- **Satellite hack (polyglot malware targeting aviation satellite comms):** https://www.bleepingcomputer.com/news/security/new-polyglot-malware-hits-aviation-satellite-communication-firms

---

## Guest: Cynthia Dueltgen

Senior Software Engineer, Berkeley CA. SANS Immersion Academy graduate (GSEC, GCIH).
Background in sysadmin, customer success, web dev, 3D graphics — all converging to cybersecurity.
Specialties: offensive security, purple team coordination, adversary simulations, technical reports.

---

## Reading

**A Hacker's Mind** by Bruce Schneier — *"We have Paleolithic emotions, medieval institutions, and godlike technology."* — Edward O. Wilson

---

## Cybersecurity Careers

### Jobs are Plentiful

- ~1 million cybersecurity workers in the US; ~715,000 jobs unfilled as of Nov 2021 (Lightcast)
- Post-COVID remote work expanded demand globally
- Every company needs experts to build and protect systems

### Career Pathway Resource

- **CyberSeek.org:** Interactive career pathway map showing entry → mid → advanced roles, required certs, and salaries
  - https://www.cyberseek.org/pathway.html
  - Feeder roles: Networking, Software Development, Systems Engineering, Financial/Risk Analysis, IT Support
  - Entry: Cybersecurity Specialist, Cyber Crime Analyst, Incident & Intrusion Analyst, IT Auditor
  - Mid: Cybersecurity Analyst, Cybersecurity Consultant, Penetration & Vulnerability Tester
  - Advanced: Cybersecurity Manager, Cybersecurity Engineer, Cybersecurity Architect

### Types of Cybersecurity Jobs

- Compliance Specialists
- Project Management
- Detection & Response
- Threat Analytics
- DevOps
- Security Architecture
- Incident Response / Threat Hunting
- Malware Analysis / Reverse Engineering
- SOC Analyst
- Penetration Tester / Red Team

---

## 10 Coolest Jobs in Cybersecurity

### Entry-Level (Initial Jobs with Advancement)

1. **Digital Forensic Analyst / Investigator** — "CSI for cyber geeks." Investigating computers and networks for evidence after incidents.
2. **Penetration Tester (Systems & Networks)** — "Be a hacker, but do it legally and get paid a lot of money." Find vulnerabilities in target systems.
3. **Application Penetration Tester** — Testing applications pre-deployment so they don't present opportunities for intruders.
4. **SOC Analyst** — "Fire ranger. Better catch the initial blaze, or there goes the forest." Anomaly detection, active monitoring, active response.
5. **Cyber Defender / Security Engineer (Enterprise)** — Implement/tune firewalls, IPS/IDS, patching, admin rights, monitoring, application whitelisting.

### Advanced (After a Few Years + Specialized Training)

6. **Hunter / Incident Responder** — "The secret agent of geekdom." Rational investigation when others are panicking.
7. **Security Architect** — Design and build defensible systems; part of an adopt team.
8. **Secure Software Development Manager** — Programmer with special powers; prevents hackers from exploiting your org.
9. **Malware Analyst / Reverse Engineer** — "The technical elite." Look deep inside malicious software to understand behavior.
10. **Technical Director / CISO** — Strategic thinker, hands-on design and deployment. Holds the keys to tech infrastructure.

---

## Red Team Career Path

### Hacker Categories (Hats)

- **White Hat:** Exploit vulnerabilities to help organizations strengthen security (authorized, ethical)
- **Black Hat:** Cybercriminals — infiltrate networks for personal/malicious purposes
- **Gray Hat:** Violate ethical standards without explicitly malicious intent

### Cybersecurity Domains Mind Map

Key red team / offensive security domains:
- **Physical Security** → Blueteam, Social Engineering, Redteam (Application, Infrastructure)
- **Risk Assessment** → Penetration test, Vulnerability scan, Blackbox/Whitebox, Source Code Scan
- **Security Architecture** → Security Engineering, Cryptography, Secure Application Development

---

## Many Paths into Cybersecurity

> "There is no real path to cybersecurity as a career; teenage hackers who target Navy intelligence officers, cyberwar backgrounds, political operatives who focus on privacy issues, or even political activists who go on to succeed in cybersecurity careers."

---

## Mindset

### Eternal Student

Cybersec is vast and constantly changing. Building a resume requires:
- Hackathons & cyber competitions
- Cyber conferences
- Technical projects
- Certifications
- Formal/higher education
- Work experience

### Practice Over Perfection

> "We are all impostors. We all 'fake it till you make it'. It's more like 'practice till you make it'. No one is born being good at what they do — it takes thousands of hours of practice. Pentesting is no different."

### Technical Fundamentals

Must-know basics for any cybersecurity professional:
- **Python** (programming fundamentals)
- **Computer Networks** — OSI/TCP-IP models, IPv4/IPv6, MAC, ports, Router/Switch/Hub/Bridge
- **Linux** — Kali Linux for pentesting; Linux commands in switches, firewalls, stack balancers

---

## Labs / CTF Platforms

Purposefully vulnerable VMs to sharpen hacking skills:

| Platform | URL | Notes |
|----------|-----|-------|
| Hack The Box | https://www.hackthebox.com/ | Web exploits, Windows, Linux boxes |
| Try Hack Me | https://tryhackme.com/ | Beginner-friendly guided paths |
| Proving Grounds | https://www.offsec.com/labs/ | OffSec's practice environment |

---

## Bug Bounties

- Average HackerOne hacker earns ~**$20,000/year** (largely part-time)
- Reality: top 1% earn big money; 99% see little monetary reward
- Still valuable: builds resume, applies skills to real-world systems

| Platform | URL |
|----------|-----|
| BugCrowd | https://www.bugcrowd.com/ |
| HackerOne | https://www.hackerone.com/ |

---

## Certifications

### Vendor-Agnostic (Recommended for Red Team)

| Cert | Description | Link |
|------|-------------|------|
| **OSCP** | Offensive Security Certified Professional — 24hr hands-on exam, Kali Linux pentesting | https://www.offsec.com/courses/pen-200/ |
| **CISSP** | Certified Information Systems Security Professional — for security analysts | https://www.isc2.org/certifications/cissp |
| **CISA** | Certified Information Systems Auditor — globally recognized IS audit cert | https://www.isaca.org/credentialing/cisa |
| **CompTIA Security+** | Baseline security skills validation | https://www.comptia.org/certifications/security |
| **ISC2 CC** | Entry-level ISC2 certification (free) | https://www.isc2.org/certifications/cc |

### OSCP Study Group

- https://www.cyberdefendersprogram.com/oscpstudygroup

### AWS Certifications (Cloud Security Path)

Starting point: **AWS Cloud Practitioner (CLF-C01)**
Study resource: https://acloudguru.com/

| Level | Cert | Exam |
|-------|------|------|
| Foundational | Cloud Practitioner | CLF-C01 |
| Associate | Solutions Architect, Developer, SysOps | SAA-C02, DVA-C01, SOA-C02 |
| Professional | Solutions Architect Pro, DevOps Engineer | SAP-C01, DOP-C01 |
| Specialty | Security (SCS-C01), Advanced Networking, ML | Various |

### CompTIA IT Certification Roadmap

Full roadmap at: https://www.comptia.org/content/it-careers-path-roadmap

---

## The Future

Key technologies shaping cybersecurity:
- **Blockchain** — decentralized trust, supply chain integrity
- **Artificial Intelligence** — both offensive (AI-driven attacks) and defensive (anomaly detection, SOAR)

Knowledge of both will likely be required for cybersecurity positions in the near future.

---

## Resources to Stay Updated

### Blogs

| Blog | URL |
|------|-----|
| AWS Security Blog | https://aws.amazon.com/blogs/security/ |
| Krebs on Security | https://krebsonsecurity.com/ |
| Schneier on Security | https://www.schneier.com/ |
| Daniel Miessler | https://danielmiessler.com/ |
| Troy Hunt | https://www.troyhunt.com/ |
| Dark Reading | http://www.darkreading.com/ |

### Books

- *Cryptonomicon* — Neal Stephenson (fiction, crypto themes)
- *A Hacker's Mind* — Bruce Schneier

### More Resources

- **Cyber Defenders Program:** https://www.cyberdefendersprogram.com

### Detection & Response Learning (from Sumedh)

1. **Level 100** — End-to-end terminology intro by Jeff Crume, IBM Distinguished Engineer:
   https://www.youtube.com/watch?v=jq_LZ1RFPfU&list=PLOspHqNVtKADkWLFt9OcziQF7EatuANSY
2. **Level 300** — Detection and response with Microsoft Sentinel hands-on exercises:
   https://www.udemy.com/course/microsoft-sentinel-from-zero-to-hero/
3. **Level 300** — Detection and response video series:
   - Intro: https://youtu.be/8Oa_IT3IOpo?si=wGGz_xLUhE2HkVn0
   - Full playlist: https://youtube.com/playlist?list=PLeaA8CQiZrWyodUEdNL2yBA4dM5TTBkrI&si=r56rtt5FPCtSVRd3

---

## Keep in Touch

- LinkedIn: https://www.linkedin.com/in/vaibhavb
- Rate My Professors: https://www.ratemyprofessors.com/add/professor-rating?tid=2886941
