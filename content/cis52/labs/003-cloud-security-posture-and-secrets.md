# Lab 3: Network Segmentation, Encryption, and Cloud Security Posture

**CIS 52 — Cloud Security Fundamentals**

**Due:** Friday, September 18, 2026, 9:00 a.m.
**Canvas:** Lab 3 assignment (link posted on Canvas)

This lab puts this week's lecture directly into practice: locking down network exposure (Part 1), encrypting data with a customer-managed key (Part 2), running a CSPM benchmark scan (Part 3), and probing an API for the exact class of flaw behind the Capital One breach (Part 4). Complete all four parts, plus the optional bonus, and submit everything as **one PDF**.

**Before you take any screenshots:** black out or crop your AWS Access Key ID, Secret Access Key, and any passwords if they ever appear on screen. Never submit a screenshot containing real credentials.

**⚠️ Cost control — delete/disable everything as soon as you have your screenshots.** Security Hub bills while enabled; unused EC2/NAT resources cost money even when idle. Don't leave anything running after you've captured what you need — see Cleanup at the end of each part.

---

## Part 1 — VPC Segmentation and Security Groups

This week's lecture argued that administrative access should never sit on the open internet, and that segmentation limits blast radius. Prove both.

1. In a VPC of your choice (default VPC is fine), create a security group with an ingress rule that allows SSH (port 22) or RDP (port 3389) from `0.0.0.0/0`. Screenshot it — this is the "before," the mistake this exercise fixes.
2. Edit the rule so it only allows that port from **your own IP address** (`/32`), not the whole internet. Screenshot the corrected rule.
3. Attach the security group to an instance (or explain in 1–2 sentences which instance you'd attach it to, if you don't want to launch one).
4. In 2–3 sentences: security groups are stateful and only allow — walk through what a network ACL would add on top of this security group that the security group can't do by itself.
5. **Cleanup:** delete the security group (and any instance you launched) once you have your screenshots.

## Part 2 — KMS Customer-Managed Key and Envelope Encryption in Practice

Lab 2 covered how a key policy is IAM for keys. This part proves envelope encryption end-to-end: create a key, use it to encrypt real data, then prove that revoking access actually blocks decryption.

1. Create a new KMS customer-managed key (symmetric, encrypt/decrypt), alias it something like `alias/lab3-data-key`.
2. Create an S3 bucket (Block Public Access fully enabled) and upload a test object using **this key** for server-side encryption (SSE-KMS, not the default AWS-managed key).
3. Screenshot the object's properties showing it's encrypted with your customer-managed key.
4. Edit the key's key policy to **deny** `kms:Decrypt` for a second IAM user or role you create (similar to the Eve pattern from Lab 2, but on the key policy instead of the bucket policy).
5. Attempt to download/decrypt the object as that denied principal. Screenshot the failure. Then attempt it as your normal admin principal and screenshot the success.
6. In 2–3 sentences: what's the practical difference between denying access on the **bucket policy** (Lab 2) versus denying it on the **KMS key policy** (this lab) — when would you use one over the other?
7. **Cleanup:** delete the test object, bucket, extra IAM principal, and schedule deletion of the KMS key.

## Part 3 — CSPM Benchmark Scan

Run a benchmark scan against your own account — the same category of check that, run regularly, would have surfaced the over-permissive role and public data behind the Capital One breach before an attacker did.

1. Either install and run **Prowler** (see the Prowler tool page in this course's Tools section) against your account, **or** enable **Security Hub** with the CIS AWS Foundations Benchmark standard if you prefer a console-only option.
2. Let it generate findings, then screenshot the overall dashboard/summary (pass/fail counts, severity breakdown).
3. Pick one **failed** finding and screenshot its detail view (the specific check, the resource, and the remediation guidance).
4. In 2–3 sentences, using this week's risk-based prioritization framework: is your chosen finding a real risk in a production account, or a low-risk lab artifact? How did you decide?
5. **Cleanup:** if you used Security Hub, disable it once you have your screenshots (it's a billed service). Prowler has no cleanup — it only reads your account.

## Part 4 — API Security Probe (OWASP API Top 10)

This is the API1/API8-class problem from lecture, hands-on: a passive scan for misconfiguration, and a manual replay test for broken authorization.

1. Using **OWASP ZAP** (see the ZAP tool page in this course's Tools section), run a **baseline scan** against an instructor-approved lab target (do not scan any system you don't own or haven't been explicitly authorized to test). Screenshot the alert summary.
2. Pick one WARN or FAIL-level finding and screenshot its detail, then explain in 1–2 sentences which OWASP API Security Top 10 category it falls under (API1, API2, API7, or API8) and why.
3. In 2–3 sentences, tying back to the Capital One case study: which single control from Parts 1–4 of this lab (network segmentation, KMS key policy denial, CSPM scanning, or API scanning) do you think would have been most effective at breaking that attack path, and why?

---

## Bonus — TryHackMe: Cloud Security Fundamentals (20 points)

Complete the TryHackMe room [Cloud Security Fundamentals](https://tryhackme.com/room/cloudsecurityfundamentals) and include one screenshot showing your completion. This is optional and worth 20 points on top of the lab's normal scoring — it reinforces this week's material from a hands-on, attacker-facing angle.

---

## Submission

- **One PDF** combining all screenshots and written answers from Parts 1–4 (and the bonus, if attempted).
- Due Friday, September 18, 2026, 9:00 a.m. — late submissions follow the syllabus's 10% deduction policy.
- Remember: delete the security group/instance, KMS key, S3 bucket, and disable Security Hub if you used it — don't leave billed resources running.
