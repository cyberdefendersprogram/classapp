# CIS 52 — Week 3 Notes
**Secure the Cloud Stack**

Friday, September 11, 2026 · 9:00 a.m.–12:00 p.m.

---

## Before We Start

Lab 2 was due today at 9:00 a.m. Late work is accepted through the last class session with a 10% deduction; your lowest lab and lowest quiz score are each dropped. Quiz 3 opens today at 1:00 p.m. and closes Sunday at 11:59 p.m.

## Today's Agenda

**Part 1 — Data and Network Foundations**
- Recap Week 2 + Lab 2 debrief (policies, conditions, KMS)
- Data classification and protecting data at rest and in transit
- Encryption and key management: KMS, key policies, key lifecycle
- Virtual private clouds, security groups, and segmentation
- Zero Trust networking and administrative access

**Break — 10 minutes**

**Part 2 — Applications, APIs, and Posture**
- Cloud application architecture and API gateways
- OWASP API Security Top 10: BOLA, broken authentication, SSRF, misconfiguration
- Cloud security posture management (CSPM) and security benchmarks
- Case study: the Capital One breach — SSRF, a misconfigured WAF, and an over-privileged role
- Setup: Lab 3 preview

---

## Books + Reading

Required — Practical Cloud Security, 2nd Ed. (Dotson), selected sections: Ch. 2 (Data Asset Management and Protection), Ch. 5 (Vulnerability Management), Ch. 6 (Network Security). Required — OWASP API Security Top 10 (2023): API1 Broken Object Level Authorization, API2 Broken Authentication, API7 Server-Side Request Forgery, API8 Security Misconfiguration. Required — Cloud Security Alliance, *A Technical Analysis of the Capital One Cloud Misconfiguration Breach*.

**Reading question:** Identify at least three points where the Capital One attack path could have been interrupted. Which control would you prioritize and why?

---

## Part 1 — Data and Network Foundations

### Data Classification and Protection

- **Classify before you protect** — know what data you hold (public, internal, confidential, regulated) before deciding controls. You can't protect what you haven't inventoried.
- **Protect data at rest** — encryption is necessary but not sufficient; access control and logging matter just as much as the cipher.
- **Protect data in transit** — TLS everywhere, including service-to-service traffic inside a VPC. "Internal" is not a trust boundary.

### Encryption and Key Management

- **Envelope encryption** — a data key encrypts the data; a key-encryption key (KEK) in a managed KMS encrypts the data key. This lets you rotate and control access to the KEK without re-encrypting all the data.
- **Customer-managed vs. provider-managed keys** — a provider-managed key is simpler; a customer-managed key (CMK) gives you a key policy, rotation control, and an audit trail of every use.
- **Key policies are IAM for keys** — a KMS key policy controls who can `Encrypt`, `Decrypt`, `GenerateDataKey`, or manage the key itself, independent of the resource's own IAM policy. Both must allow an action for it to succeed.
- **Key lifecycle** — create, rotate (automatically or on a schedule), disable, and schedule deletion with a waiting period so a mistaken deletion is recoverable.

### Virtual Private Clouds and Segmentation

- A **VPC** is a logically isolated network inside a cloud account; subnets divide it into smaller address ranges, often split into public (has a route to the internet) and private (does not).
- **Security groups** are stateful, attached to resources (instance-level firewall); **network ACLs** are stateless, attached to subnets (subnet-level firewall). Security groups only allow; NACLs can allow and deny.
- **Segmentation** limits blast radius: a compromised web tier shouldn't have a direct network path to the database tier's admin port.
- **Administrative access** should never sit on the open internet — use a bastion, session manager, or private endpoint instead of exposing SSH/RDP broadly.

### Zero Trust Networking

Zero Trust networking carries Week 2's "identity is the perimeter" idea into the network layer: being on the VPC or behind the firewall proves nothing about what a request is allowed to do. Every service-to-service call should still authenticate and authorize, even inside a private subnet — this is what prevents a single compromised host from moving laterally unchecked.

---

## Part 2 — Applications, APIs, and Posture

### Cloud Application and API Security

Modern cloud apps are API-first: a web/mobile client, an API gateway, and backend services that call each other over the network using workload identities rather than human logins.

**OWASP API Security Top 10 (2023) — four to know cold:**

| # | Risk | What it means |
|---|---|---|
| API1 | Broken Object Level Authorization | The API checks *who you are* but not *whether you're allowed to touch this specific object* — swap an ID in the URL and read someone else's record |
| API2 | Broken Authentication | Weak, missing, or misconfigured auth on API endpoints — the same credential problems as Week 2, now facing machine-to-machine traffic |
| API7 | Server-Side Request Forgery (SSRF) | The server is tricked into making a request on the attacker's behalf, often reaching internal-only resources the attacker could never hit directly |
| API8 | Security Misconfiguration | Default configs, verbose errors, missing hardening, overly permissive CORS — the "everything else" bucket that's still one of the most common findings |

### Cloud Security Posture Management (CSPM)

- **Security benchmarks** (e.g., CIS Benchmarks) give a checklist of secure baseline settings for a cloud service or OS.
- **CSPM tooling** continuously scans an account against these benchmarks and flags drift — a bucket that became public, a security group that got a `0.0.0.0/0` rule added, a key that lost its rotation policy.
- **Vulnerability vs. misconfiguration** — a vulnerability is a flaw in software; a misconfiguration is a flaw in how you set something up. Cloud breaches are dominated by the second category.
- **Risk-based prioritization** — not every finding is worth fixing today. Weigh exploitability, exposure (public vs. private), and data sensitivity before triaging a backlog.
- **Validate, don't blindly trust the scanner** — as in Lab 2, a scanner's output is a lead, not a verdict; confirm exploitability before calling something a false positive or a critical finding.

### Case Study — Capital One (2019)

A former AWS employee exploited a **misconfigured web application firewall** in front of a Capital One-hosted application to perform an **SSRF** attack. The SSRF request reached the **EC2 instance metadata service**, which returned temporary credentials for an IAM role attached to that instance. Because the role was **over-privileged** — it could list and read far more S3 buckets than the application actually needed — the attacker used those credentials to exfiltrate data from more than 100 million customer records.

**Where the attack path could have been broken:**
- A correctly configured WAF that didn't forward the SSRF payload
- Blocking or requiring a token for instance metadata service requests (IMDSv2)
- Least-privilege IAM role scoped to only the buckets the app needed (Week 2)
- Network egress controls limiting what the compromised host could reach
- CSPM/benchmark scanning that would have flagged the over-permissive role and the public buckets
- Data-access logging and alerting on unusual S3 `GetObject` volume, which would have shortened detection time

This is the same lesson as CampusCart in Week 1 and the credential misuse in Week 2, one layer further into the stack: a single missing control rarely causes a breach — an *uninterrupted chain* of missing controls does.

---

## Lab 3 Preview — Network Segmentation, Encryption, and Cloud Security Posture

Full instructions: Lab 3 assignment on Canvas (link posted on Canvas).

You will:
- Lock down a security group from open ingress (`0.0.0.0/0`) to your own IP only — administrative access, hands-on
- Create a KMS customer-managed key, encrypt an S3 object with it, then deny `kms:Decrypt` on the key policy for a second principal and prove the denial works
- Run a CSPM benchmark scan (Prowler or Security Hub's CIS benchmark) and triage one finding
- Run an OWASP ZAP baseline scan against a lab API target and map one finding to the OWASP API Top 10
- **Bonus (20 pts):** complete the TryHackMe room [Cloud Security Fundamentals](https://tryhackme.com/room/cloudsecurityfundamentals)

**Cost control:** Security Hub bills while enabled — disable it and delete lab resources as soon as you have your screenshots.

**Due:** Friday, September 18, 2026, 9:00 a.m.

---

## Quiz 3

- Opens today, September 11, at 1:00 p.m.
- Closes Sunday, September 13, at 11:59 p.m.
- 90 minutes after starting, 2 attempts
- 6 questions, 10 points — covers today's lecture plus the Week 3 reading (Ch. 2, 5 & 6; OWASP API Top 10; Capital One breach analysis)

---

## Next Week — Cloud-Native Security

- Complete Lab 3 by Friday, September 18, at 9:00 a.m.
- Read Practical Cloud Security, selected Ch. 5 (container scanners, SAST, SCA, cloud workload protection); NIST SP 800-190; NIST SP 800-204C
- Be ready to reason about containers, image and registry risk, Kubernetes security concepts, and DevSecOps/CI/CD pipeline security
