---
title: Identity Is the Perimeter
---

## Q1 [mcq_single, 2pts]

Which pair correctly matches the two IAM concepts to their definitions?

- [ ] Authentication = what you're allowed to do; Authorization = proving who you are
- [x] Authentication = proving who you are; Authorization = what you're allowed to do
- [ ] Authentication and Authorization both mean proving who you are
- [ ] Authentication is only used for machines; Authorization is only used for humans

## Q2 [mcq_single, 2pts]

Why does the reading (Practical Cloud Security, Ch. 4) say credentials are attackers' most-used tool?

- [ ] Firewalls cannot detect stolen credentials being used
- [x] A valid login blends in with normal activity, so patches and firewalls don't stop an attacker who simply logs in
- [ ] Passwords are the only authentication factor AWS supports
- [ ] Credential theft is illegal, so attackers rarely attempt it

## Q3 [mcq_multi, 3pts]

Which of these are steps in the IAM life cycle covered in lecture? (Select all that apply)

- [x] Request
- [x] Authorize
- [x] Revalidate
- [ ] Deprecate

## Q4 [mcq_single, 2pts]

An IAM policy has one statement that Allows `s3:GetObject` for every user in the account, and a second statement that explicitly Denies `s3:GetObject` for user Eve. What happens when Eve tries to `GetObject`?

- [ ] She is allowed, because Allow statements are evaluated first
- [ ] She is allowed, because the more specific principal (everyone) wins
- [x] She is denied, because an explicit Deny always overrides an Allow
- [ ] The request fails with an error, since the two statements conflict

## Q5 [mcq_single, 2pts]

According to BeyondCorp, what should determine whether a request gets access to a resource?

- [ ] Whether the request came from inside the corporate network
- [x] Evidence about the device and user's trust level, evaluated on every request
- [ ] Whether the user has ever logged in successfully before
- [ ] The strength of the Wi-Fi signal at the user's location

## Q6 [mcq_single, 2pts]

In the NIST SP 800-207 Zero Trust model, which component actually sits in front of the resource and enforces the access decision on every request?

- [ ] Policy Engine (PE)
- [ ] Policy Administrator (PA)
- [x] Policy Enforcement Point (PEP)
- [ ] Policy Information Point (PIP)

## Q7 [mcq_single, 2pts]

Why are temporary role credentials generally safer than a long-lived IAM access key?

- [ ] Temporary credentials are encrypted and access keys are not
- [ ] Temporary credentials work across every AWS account automatically
- [x] Temporary credentials expire automatically, which limits how long a leaked credential stays useful
- [ ] Temporary credentials don't require any permissions policy

## Q8 [mcq_single, 1pt]

Which MITRE ATT&CK technique describes an attacker using a legitimate, stolen cloud login instead of exploiting a software vulnerability?

- [x] T1078.004 — Valid Accounts: Cloud Accounts
- [ ] T1190 — Exploit Public-Facing Application
- [ ] T1566 — Phishing
- [ ] T1499 — Endpoint Denial of Service

## Q9 [free_response, 2pts]

If being inside the corporate network no longer establishes trust, what evidence should a Zero Trust policy engine evaluate before granting access to a cloud resource?
