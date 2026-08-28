# CIS 52 — Week 1 Notes
**Cloud Security Foundations**

Friday, August 28, 2026 · 9:00 a.m.–12:00 p.m.

---

## Instructor
**Vaibhav Bhandari**
Director of Security @ Lib13
Previous: Shape Security, United Health, Microsoft, YouBase et al.
MS in CS @ UC Santa Cruz
Non-profit: [cyberdefendersprogram.com](https://www.cyberdefendersprogram.com)

---

**Full syllabus:** [Canvas — CIS 52 Syllabus](https://peralta.instructure.com/courses/92216/assignments/syllabus)
**Required textbook (free):** [Practical Cloud Security, 2nd Ed. — Chris Dotson](https://www.repository.gctu.edu.gh/files/original/58109f0c11ade205dc3deb567a9d1525.pdf)

## Course Map — Six Fridays, One Defensive Workflow

Class Portal dates are authoritative.

| Date | Week | Topic | Assignments |
|------|------|-------|-------------|
| Aug 28 | 1 | Cloud Security Foundations | Classwork |
| Sep 4 | 2 | Identity Is the Perimeter | Lab 1 + Quiz 1 |
| Sep 11 | 3 | Secure the Cloud Stack | Lab 2 + Quiz 2 |
| Sep 18 | 4 | Cloud-Native Security | Lab 3 + Quiz 3 |
| Sep 25 | 5 | Detect the Attack | Lab 4 + Quiz 4 |
| Oct 2 | 6 | Respond, Recover, Improve | Lab 5 + Quiz 5 |

---

## Course Logistics

- Fridays, 9:00 a.m.–12:00 p.m.; office hours 12:00–1:00 p.m.
- Five labs and five quizzes; the lowest score in each category is dropped
- Readings, links, assignments, and updates live in the Class Portal
- Use only instructor-authorized cloud and lab environments

**Deadlines:**
- Quizzes — 50% of grade; open Friday 1:00 p.m., close Sunday 11:59 p.m., 90 minutes after starting
- Labs — 50% of grade; normally due Friday at 9:00 a.m.
- Late work normally receives a 10% deduction

**Treat AI output like untrusted code:**
- Understand and test every command or configuration you submit
- Never paste passwords, keys, tokens, cookies, or protected data into AI tools
- Never expose credentials in screenshots, logs, code, or repositories
- Stop or delete cloud resources when they're no longer needed

---

## Books + Reading

Required book: **Practical Cloud Security**, Chris Dotson, 2nd Edition, O'Reilly Media, 2023. Selected chapters — not the entire book — support the six-week course. Free online access is linked from the Class Portal. Plan for 60–90 minutes of required reading each week.

Read before the next checkpoint:
- Required — Practical Cloud Security, Chapter 1
- Required — NIST SP 800-145
- Required — AWS Shared Responsibility Model
- Optional — Amazon Builder Rewards and Berkeley's *Above the Clouds*

**Reading question:** As an organization moves from IaaS to PaaS to SaaS, what changes about technical control and security responsibility? Control decreases — responsibility changes, but it doesn't disappear.

---

## Part 1 — The Cloud Operating Model

Cloud is an operating model, not a location: on-demand access to shared computing resources over a network. Resources can be provisioned and released rapidly; usage is measured, elastic, and delivered as a service. Security decisions move into identities, APIs, configuration, and automation.

**Five NIST characteristics create cloud speed — and risk:**
- On-demand self-service
- Broad network access
- Resource pooling
- Rapid elasticity
- Measured service

### Service Models — Who Controls the Stack

- **IaaS** — customer operates virtual machines, storage, and networks
- **PaaS** — provider operates the runtime; customer ships applications and data
- **SaaS** — provider operates the application; customer governs users and data
- **Serverless** removes server management — not security responsibility

### Shared Responsibility — Managed Does Not Mean Automatically Secure

- **IaaS** — secure the OS, workload, identities, data, and configuration
- **PaaS** — secure the application, data, identities, and service settings
- **SaaS** — secure users, data, sharing, endpoints, and tenant settings
- The provider secures the underlying service and physical infrastructure

### Deployment Models — Trust Boundaries

- **Public cloud** — shared provider infrastructure
- **Private cloud** — dedicated cloud environment
- **Hybrid cloud** — connected cloud and on-premises environments
- **Multi-cloud** — services from more than one provider

### Resource Hierarchy

Regions define geographic service locations; zones isolate failure domains.

| Provider | Hierarchy |
|---|---|
| AWS | Organizations → Accounts |
| Azure | Tenants → Subscriptions → Resource Groups |
| Google Cloud | Organizations → Folders → Projects |

### Management, Control, and Data Planes

- **Management plane** — administration and governance
- **Control plane** — create, configure, and authorize resources
- **Data plane** — use services and access data

Ask who can act in each plane — and where the evidence appears.

---

## Part 2 — Following the Attack Path

*Fictional teaching scenario — not a real organization or incident.*

**CampusCart incident:** a suspicious admin login and customer files visible from the internet. A privileged account authenticated from a new location, had no phishing-resistant MFA, and its permissions could change storage access. Is the login the breach, or the first link in a longer chain?

**An attack path is a chain of ordinary weaknesses:**
1. Stolen or abused credential
2. Privileged identity or workload role
3. Excessive permission
4. Public storage or exposed service
5. Sensitive data access or control-plane action

**Cloud failures repeat in recognizable patterns:**
- Public storage or exposed services
- Excessive permissions and weak trust policies
- Stolen or long-lived credentials
- Insecure APIs and application paths
- Missing logging, inventory, ownership, or cleanup

**Breaking the path — and preserving the evidence:**
- Reduce exposure and use secure defaults
- Require strong MFA and prefer temporary credentials
- Grant only the permissions required for the task
- Segment workloads and sensitive data
- Log identity, administrative, network, and data access

---

## Cross-Cloud Map — Functions Stay Stable, Names Change

Use the function, not the brand name, as your mental anchor.

| Function | AWS | Azure | Google Cloud |
|---|---|---|---|
| Identity | IAM | Entra ID + RBAC | Cloud IAM |
| Compute | EC2 | Virtual Machines | Compute Engine |
| Object storage | S3 | Blob Storage | Cloud Storage |
| Audit | CloudTrail | Activity Log | Cloud Audit Logs |
| Posture | Security Hub + Config | Defender + Policy | Security Command Center |

---

## Lab 1 Preview — Building an IAM Evidence Quest

Full instructions: [Lab 1 — AWS Account Setup and IAM Fundamentals](../labs/001-aws-iam-fundamentals.md) ([Canvas](https://peralta.instructure.com/courses/92216/assignments/1757696))

You will:
- Protect the assigned account with strong authentication
- Identify privileged, standard-user, and workload identities
- Test one allowed operation and one denied operation
- Locate the audit evidence and clean up safely

**Win condition — six clean pieces of evidence:** authentication control, identity design, least-privilege role or policy, allowed test result, denied test result + audit event, cleanup confirmation (no secrets in screenshots).

**Due:** Friday, September 4, 2026, 9:00 a.m.

---

## Quiz 1

- Opens Friday, September 4, at 1:00 p.m.
- Closes Sunday, September 6, at 11:59 p.m.
- 90 minutes after starting
- Covers Week 1 lecture and required readings

---

## Next Week — Identity Is the Perimeter

- Complete Lab 1 by Friday, September 4, at 9:00 a.m.
- Read Practical Cloud Security, Chapter 4
- Read Google BeyondCorp and selected sections of NIST SP 800-207
- Be ready to reason about human and workload access
