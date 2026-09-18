---
title: Cloud-Native Security
---

## Q1 [mcq_single, 2pts]

Why can a kernel-level exploit or runtime misconfiguration let an attacker escape a container in a way that has no direct VM equivalent?

- [ ] Containers always run as root by default
- [x] Containers share the host kernel instead of running under their own hypervisor-isolated guest kernel
- [ ] Containers cannot be scanned for vulnerabilities
- [ ] Containers always have network access to the host

## Q2 [mcq_single, 2pts]

A secret is added via `ENV API_KEY=...` in a Dockerfile, then removed in a later layer. Why is it still a problem?

- [ ] Docker automatically re-adds deleted environment variables
- [x] The secret persists in the image's layer history and is extractable even though a later layer "removed" it
- [ ] Environment variables are never included in image layers
- [ ] It isn't a problem — deleting it in a later layer fully removes it

## Q3 [mcq_multi, 2pts]

Which of these are core Kubernetes security concepts covered in lecture? (Select all that apply)

- [x] RBAC (Role-Based Access Control)
- [x] Network policies
- [x] Pod Security Standards
- [ ] Security groups

## Q4 [mcq_single, 1pt]

By default, are Kubernetes `Secret` objects encrypted?

- [ ] Yes, always encrypted at rest automatically
- [x] No — they're base64-encoded, not encrypted, unless etcd encryption is configured
- [ ] Yes, but only in managed Kubernetes services
- [ ] Secrets objects don't exist in Kubernetes

## Q5 [mcq_single, 1pt]

In the Codecov Bash Uploader compromise, what turned one compromised script into thousands of downstream victims?

- [ ] The attacker directly breached each victim company's cloud account
- [x] Thousands of CI pipelines pulled and ran the same compromised script, each exposing its own CI secrets to the attacker
- [ ] Codecov's own production database was leaked publicly
- [ ] The victims all shared a single cloud account with Codecov

## Q6 [free_response, 2pts]

Which security problems should be caught by build-time scanning (SAST/SCA/IaC scanning), and which can only be caught by runtime protection? Give one example of each.
