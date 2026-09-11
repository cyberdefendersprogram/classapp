---
title: Secure the Cloud Stack
---

## Q1 [mcq_single, 2pts]

In KMS envelope encryption, what is the purpose of the key-encryption key (KEK)?

- [ ] It replaces the need for a data key entirely
- [x] It encrypts the data key, so the data key (and therefore the data) can be re-keyed without re-encrypting all the underlying data
- [ ] It is used once and then automatically deleted
- [ ] It encrypts data directly, and the data key is only a backup

## Q2 [mcq_single, 2pts]

What is the key difference between a security group and a network ACL in a VPC?

- [ ] Security groups are stateless and NACLs are stateful
- [x] Security groups are stateful and attached to resources; NACLs are stateless and attached to subnets
- [ ] NACLs can only allow traffic, never deny it
- [ ] Security groups operate at the subnet level and NACLs operate at the instance level

## Q3 [mcq_multi, 2pts]

Which of these are OWASP API Security Top 10 (2023) risks covered in lecture? (Select all that apply)

- [x] Broken Object Level Authorization
- [x] Server-Side Request Forgery
- [x] Security Misconfiguration
- [ ] Endpoint Denial of Service

## Q4 [mcq_single, 1pt]

An API endpoint correctly checks that a request has a valid login, but lets any logged-in user fetch `/orders/{id}` for any order ID, not just their own. Which risk is this?

- [x] API1 — Broken Object Level Authorization
- [ ] API2 — Broken Authentication
- [ ] API7 — Server-Side Request Forgery
- [ ] API8 — Security Misconfiguration

## Q5 [mcq_single, 1pt]

In the Capital One breach, what allowed the SSRF request to turn into stolen data?

- [ ] The attacker guessed the root account password
- [x] The SSRF reached the instance metadata service, which handed back credentials for an over-privileged IAM role
- [ ] The S3 buckets had no encryption enabled
- [ ] The attacker phished an employee's MFA code

## Q6 [free_response, 2pts]

Identify at least three points where the Capital One attack path could have been interrupted, and say which control you would prioritize and why.
