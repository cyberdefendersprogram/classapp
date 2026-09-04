# CIS 52 — Week 2 Notes
**Identity Is the Perimeter**

Friday, September 4, 2026 · 9:00 a.m.–12:00 p.m.

---

## Before We Start

Lab 1 was due today at 9:00 a.m. Late work is accepted through the last class session with a 10% deduction; your lowest lab and lowest quiz score are each dropped. Quiz 1 opens today at 1:00 p.m. and closes Sunday at 11:59 p.m.

## Today's Agenda

**Part 1 — Identity Fundamentals**
- Recap Week 1 + Lab 1 debrief
- Authentication vs. authorization, the IAM life cycle
- Least privilege, MFA, passwords, federation & SSO

**Break — 10 minutes**

**Part 2 — Identity in Practice**
- AWS IAM hands-on: users, groups, roles, policies
- Zero Trust: BeyondCorp + NIST SP 800-207
- The attacker's view: stolen and misused cloud credentials
- Setup: TryHackMe + AWS Academy, Lab 2 & Quiz 2 preview

---

## Books + Reading

Required — Practical Cloud Security, 2nd Ed. (Dotson), Chapter 4: Identity and Access Management. Required — BeyondCorp: A New Approach to Enterprise Security (Ward & Beyer, Google). Required — NIST SP 800-207, Zero Trust Architecture. Optional — MITRE ATT&CK, Valid Accounts: Cloud Accounts (T1078.004).

**Reading question:** Why are temporary roles and workload identities generally safer than distributing long-lived cloud credentials?

---

## Part 1 — Identity Fundamentals

Credentials are attackers' most-used tool: in breaches involving web applications, lost or stolen credentials have been the leading attack vector for years running. Patches and firewalls don't help if the attacker just logs in.

### Two Distinct Jobs

- **Identity** — how a person or a piece of automation is represented in the system. Authentication ("authn") proves the requester really owns that identity.
- **Access management** — allowing an identity to perform only the tasks it needs, nothing more. Authorization ("authz") is the check of what an authenticated identity is allowed to do.

### The Identity Life Cycle

1. **Request** — an authenticated entity asks to create, delete, grant, or revoke
2. **Approve** — explicit approval inside the org; public signups may auto-approve with anti-fraud checks
3. **Create / Grant** — the identity is created or access is granted, ideally by automation
4. **Authenticate** — the identity proves it is who it claims to be
5. **Authorize** — every action is checked against policy
6. **Revalidate** — access is periodically re-checked and pruned

### Least Privilege and Separation of Duties

- **Least privilege** — every user, system, or tool gets the absolute minimum access to do its job; deny by default. Watch for "permission creep" as roles change and old access is never removed.
- **Separation of duties** — no single person can undermine the entire environment (e.g., the admin who changes systems shouldn't also control the logs that would catch it).

### Multi-Factor Authentication

- Something you know — password, passphrase, PIN
- Something you have — access badge, authenticator app, hardware security key
- Something you are — fingerprint, face, retina

MFA is one of the strongest, cheapest defenses against stolen or weak credentials — enable it for every privileged user.

### Passwords, Passphrases, and API Keys

Never reuse a password. Use a reputable password wallet. Prefer long, randomly generated passwords (~20 characters) wherever you don't need to memorize them. API keys authenticate automation, not people — they can't use MFA, so treat them as sensitive secrets, not config. Prefer federated identity or a managed IAM service over rolling your own password verification.

### Federated Identity and SSO

Federated identity means two systems agree to trust the same identity, so you don't create a separate account on each one. SSO redirects you to a central identity provider (IdP); the app never sees your password. SAML (2005) uses XML "assertions," common in large enterprise apps. OIDC (2014) uses JSON Web Tokens on top of OAuth 2.0, common in modern web/mobile apps.

### Cross-Cloud IAM Map

| Function | AWS | Azure | Google Cloud |
|---|---|---|---|
| Workforce identity | IAM | Entra ID (Azure AD) | Cloud IAM |
| Customer identity (CIAM) | Amazon Cognito | Azure AD B2C | Identity Platform |
| Temporary credentials | STS / IAM roles | Managed identities | Workload identity federation |
| Access logs | CloudTrail | Activity Log | Cloud Audit Logs |

---

## Part 2 — Identity in Practice

### AWS IAM Hands-On

- **Direct interaction** — e.g., user Bob is allowed to launch new EC2 instances
- **Delegation** — e.g., EC2 instance i-123456 is allowed to read from an S3 bucket, no human involved
- **IAM characteristics** — centralized, account-scoped, deny by default; spans Regions/Zones; new identities start with zero privileges

**Root user, IAM users, and groups:**
- Root user — created the account, has complete access; lock it behind hardware MFA, don't use it day to day
- IAM users — an identity with assigned permissions; rotate credentials, require MFA
- Groups — attach policies to the group, not individual users, to manage permissions at scale

**IAM policies** are JSON documents that allow or deny. Effects are explicit ("Allow" or "Deny") and an explicit deny always wins. Policies can scope by service, resource, Region, account, or principal, and add conditions by date, source IP, or MFA presence. Resource-based policies (e.g., an S3 bucket policy) can grant access too.

**Roles** are temporary credentials, not standing access — a cloud role isn't a full identity, it's a status another identity assumes, backed by temporary credentials. You put the role "hat" on for a privileged task and take it off when you're done; every assumption is logged. Non-human entities assume roles too: an EC2 instance can assume a role at launch and never need a stored secret.

**IAM best practices checklist:**
- Create individual identities — never share credentials
- Grant least privilege by default; add access as justified
- Manage permissions through groups and roles, not individual users
- Add conditions to further restrict privileged access
- Enable audit logging (e.g., AWS CloudTrail) for every API call
- Enforce a strong password policy and MFA for privileged users
- Rotate credentials on a schedule
- Reduce or eliminate day-to-day use of the root account

### Zero Trust

**Identity is the perimeter.** There is no network firewall around a cloud API. Every request must prove who it is and what it's allowed to do — every time.

**BeyondCorp** — Google's internal model, published after realizing VPN + corporate network access no longer reflected real risk. Core shift: access decisions are based on device and user trust, not on which network you're connecting from. Connecting from the office earns you nothing by default; an unmanaged or unpatched device is denied even on-network.

**NIST SP 800-207** describes the components of a Zero Trust decision:
- **Policy Engine (PE)** — decides whether to grant access, using identity, device posture, behavior, and threat intelligence
- **Policy Administrator (PA)** — establishes or shuts down the communication path based on the PE's decision
- **Policy Enforcement Point (PEP)** — sits in front of the resource and enforces the decision on every request

This mirrors the textbook's PDP / PAP / PEP model for centralized cloud authorization.

### The Attacker's View

**MITRE ATT&CK T1078.004 — Valid Accounts: Cloud Accounts.** Adversaries obtain and use legitimate cloud credentials — console, API keys, or federated tokens — instead of exploiting a vulnerability. A valid login blends in with normal activity, which is exactly why it's so hard to detect. Common sources: phishing, credential stuffing, leaked keys in code repos, compromised third-party apps. Detection signals: logins from new locations/devices, unusual API call patterns, MFA absence on a privileged action.

This is precisely the CampusCart clue from Week 1 — a privileged account, authenticated from a new location, with no phishing-resistant MFA.

**What would have broken the attack path:** phishing-resistant MFA on every privileged account, least-privilege roles instead of standing admin access, temporary scoped credentials instead of long-lived keys, continuous context-aware authorization (Zero Trust), and CloudTrail-style audit logging on every privileged action.

---

## Lab 2 Preview — IAM Policies, Conditions & KMS

Full instructions: [Lab 2 — IAM Policies, Conditions, and KMS on Canvas](https://peralta.instructure.com/courses/92216/assignments/1757697)

You will:
- Create user Eve, an S3 bucket, and a policy: allow `GetObject` for your account, deny it for Eve — then prove it with screenshots of both the denied and successful calls
- Create an IAM role for Security Hub, Inspector, and Secrets Manager, gated on source IP **and** MFA present, not IP alone
- Create a customer managed KMS key and screenshot its key policy

**Due:** Friday, September 11, 2026, 9:00 a.m.

---

## Quiz 2

- Opens today, September 4, at 1:00 p.m.
- Closes Sunday, September 6, at 11:59 p.m.
- 90 minutes after starting, 2 attempts
- 9 questions, 18 points — covers today's lecture plus the Week 2 reading (Ch. 4, BeyondCorp, NIST SP 800-207, MITRE T1078.004)

---

## Next Week — Secure the Cloud Stack

- Complete Lab 2 by Friday, September 11, at 9:00 a.m.
- Read Practical Cloud Security, selected Ch. 2, 5 & 6 (data protection, vulnerability management, network security)
- Be ready to reason about encryption, key management, and network trust boundaries beyond identity
