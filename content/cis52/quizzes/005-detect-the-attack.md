---
title: Detect the Attack
---

## Q1 [mcq_single, 2pts]

Which of these is the best definition of an "alert," as distinct from a log or event?

- [ ] Any record of something that happened, regardless of importance
- [x] An event where a rule decided it's worth notifying a human for review
- [ ] A time-based number like requests-per-minute or free disk space
- [ ] Any entry written to a SIEM

## Q2 [mcq_single, 2pts]

Why should toxic logs (e.g., raw SSH session recordings, exact commands run) be restricted to a small team, with access itself triggering a notification?

- [ ] Toxic logs are always corrupted and unreliable
- [x] They can contain secrets outright, so unrestricted access multiplies the risk of exposing credentials
- [ ] They are the only logs a SIEM can ingest
- [ ] They take up more storage than sanitized logs

## Q3 [mcq_multi, 2pts]

Which of these are steps in the detection pipeline described in lecture? (Select all that apply)

- [x] Aggregation and retention
- [x] Parsing
- [x] Search and correlation
- [ ] Terraform apply

## Q4 [mcq_single, 1pt]

Why should a log aggregator sit in a separate account with separate administrative credentials from the systems it's collecting logs from?

- [ ] It's required by every cloud provider's terms of service
- [x] So an attacker who compromises a monitored system can't also erase the logs of their own activity
- [ ] Separate accounts are the only way to enable CloudTrail
- [ ] It reduces the cloud bill

## Q5 [mcq_single, 1pt]

In the AWS Detect → Investigate framing from lecture, what is GuardDuty's role?

- [ ] It scans for vulnerabilities and exposure before an attack happens
- [x] It continuously analyzes CloudTrail, VPC Flow Logs, and DNS logs to catch malicious activity as it happens
- [ ] It builds a graph of related historical activity after a finding is raised
- [ ] It automatically remediates every finding without human review

## Q6 [free_response, 2pts]

Pick one MITRE ATT&CK Cloud Matrix technique (name or technique ID) and describe what telemetry you would collect to detect it, tying your answer back to the Capital One or Codecov case study if it applies.
