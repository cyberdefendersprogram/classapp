# Prowler

Prowler is an open-source cloud security posture management (CSPM) tool that audits AWS, Azure, and GCP accounts against security benchmarks like the CIS Benchmarks, and frameworks like NIST, PCI DSS, and SOC 2. It runs hundreds of checks and reports findings by severity, giving you a prioritized list of misconfigurations instead of a wall of raw logs.

## Overview

Prowler is essential for:
- **Benchmark Compliance**: Check an account against CIS AWS Foundations Benchmark and similar baselines
- **Misconfiguration Discovery**: Find public buckets, over-permissive IAM roles, disabled logging, and weak encryption settings
- **Risk-Based Prioritization**: Findings are tagged by severity so you can triage instead of guessing
- **Evidence for Remediation**: Each finding maps to the specific resource and setting that failed, so you can validate before fixing

### Installation

```bash
# Install via pip (requires Python 3.9+)
pip install prowler

# Verify setup — requires AWS credentials already configured
# (aws configure, or an assumed role)
prowler aws --version
```

:::command-builder{id="prowler-builder"}
tool_name: prowler
target_placeholder: "aws"
scan_types:
  - name: "Full AWS Scan"
    flag: "aws"
    desc: "Run every check against the current AWS account"
  - name: "Single Service"
    flag: "aws --service s3"
    desc: "Scan only one service, e.g. s3, iam, ec2, kms"
  - name: "CIS Benchmark"
    flag: "aws --compliance cis_2.0_aws"
    desc: "Scan against the CIS AWS Foundations Benchmark v2.0"
  - name: "List Checks"
    flag: "aws --list-checks"
    desc: "List every check Prowler can run, without executing them"
options:
  - name: "Severity Filter"
    flag: "--severity"
    desc: "Only run checks at this severity: critical, high, medium, low"
  - name: "Output Formats"
    flag: "--output-formats"
    desc: "csv, json-asff, html (multiple allowed)"
  - name: "Output Directory"
    flag: "--output-directory"
    desc: "Where to write the report files"
  - name: "Regions"
    flag: "--region"
    desc: "Limit the scan to one or more AWS Regions"
:::

## Basic Syntax

```
prowler aws
prowler aws --service <service>
prowler aws --compliance cis_2.0_aws
prowler aws --severity critical high
```

**Common flags:**
- Scope to one account's default credentials: no flags needed beyond `aws`
- Assume a role: `--role arn:aws:iam::<account-id>:role/<role-name>`
- Only critical/high findings: `--severity critical high`
- HTML report for a class writeup: `--output-formats html`

---

:::scenario{id="scenario-1" level="beginner"}
title: "Run a Full Account Scan and Read the Summary"
goal: "Get a first read on an account's overall security posture."
hint: "The scan can take a few minutes on a real account. Start with the default output — it prints a pass/fail summary per check to the terminal before you touch report formats."
command: "prowler aws --output-formats html --output-directory ./prowler-report"
expected_output: |
  Prowler is executing 297 checks...
  AWS Region: us-east-1

  IAM
  ✓ PASS iam_root_mfa_enabled
  ✗ FAIL iam_password_policy_uppercase — password policy does not require an uppercase letter
  ✗ FAIL iam_user_mfa_enabled_console_access — user 'dev-alice' has console access without MFA

  S3
  ✓ PASS s3_bucket_public_access_block
  ✗ FAIL s3_bucket_server_side_encryption — bucket 'app-logs-2026' has no default encryption

  KMS
  ✓ PASS kms_cmk_rotation_enabled

  Overview: 297 checks, 231 PASS, 66 FAIL
  HTML report written to ./prowler-report/prowler-output.html
:::

:::scenario{id="scenario-2" level="intermediate"}
title: "Scope to Network and Encryption Checks Only"
goal: "Focus a scan on this week's topics — VPC exposure and encryption — instead of the full check set."
hint: "Use --service to limit which service group runs, and --severity to cut noise from low-severity findings you won't act on this week."
command: "prowler aws --service ec2 kms --severity critical high"
expected_output: |
  Prowler is executing checks for services: ec2, kms
  Severity filter: critical, high

  EC2
  ✗ FAIL [high] ec2_securitygroup_allow_ingress_from_internet_to_any_port — sg-0a1b2c3d allows 0.0.0.0/0 on all ports
  ✓ PASS [high] ec2_instance_imdsv2_enabled

  KMS
  ✗ FAIL [critical] kms_key_not_publicly_accessible — key policy for alias/app-data grants Principal: "*"

  Overview: 2 findings requiring immediate attention
:::

---

## Reading This Week's Findings Against Capital One

Two Prowler checks map directly to the failures in the Capital One breach: an IAM check for over-permissive roles attached to compute instances, and an S3 check for public or under-encrypted buckets. Running a CSPM scan before an incident, not after, is the whole point — Prowler would have flagged the over-privileged instance role and the exposed data as findings weeks before an attacker found them.
