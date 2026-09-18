# Checkov

Checkov is an open-source static analysis tool from Bridgecrew/Palo Alto Networks purpose-built for policy-as-code scanning of Infrastructure as Code — Terraform, CloudFormation, Kubernetes YAML, Dockerfiles, and more. It ships with thousands of built-in policies mapped to frameworks like CIS Benchmarks, so a `terraform plan` gets the same kind of structured, prioritized findings a CSPM tool gives a live account — just earlier, before `apply` ever runs.

## Overview

Checkov is essential for:
- **Pre-Apply Policy Enforcement**: Fail a build before a misconfigured resource is ever provisioned
- **Framework Coverage**: Terraform, CloudFormation, Kubernetes, Dockerfile, ARM, Serverless, and more in one tool
- **CIS Benchmark Mapping**: Findings map to the same benchmark families used by Prowler and Security Hub (Week 3)
- **CI/CD Integration**: Designed to run as a pipeline gate — a natural fit for this week's shift-left/DevSecOps discussion

### Installation

```bash
# Install via pip (requires Python 3.8+)
pip install checkov

# Verify
checkov --version
```

:::command-builder{id="checkov-builder"}
tool_name: checkov
target_placeholder: "-d ."
scan_types:
  - name: "Scan a Directory"
    flag: "-d ."
    desc: "Recursively scan every IaC file in the current directory"
  - name: "Scan a Single File"
    flag: "-f main.tf"
    desc: "Scan just one Terraform, CloudFormation, or Kubernetes file"
  - name: "Framework Filter"
    flag: "-d . --framework terraform"
    desc: "Limit the scan to one IaC framework: terraform, cloudformation, kubernetes, dockerfile"
  - name: "List Checks"
    flag: "--list"
    desc: "List every built-in policy Checkov can run, without executing them"
options:
  - name: "Compact Output"
    flag: "--compact"
    desc: "Hide the code block for each finding — just the summary"
  - name: "Output Format"
    flag: "--output"
    desc: "cli (default), json, junitxml, sarif — junitxml/sarif plug into most CI dashboards"
  - name: "Skip a Check"
    flag: "--skip-check"
    desc: "Suppress a specific policy ID, e.g. CKV_AWS_20, for an accepted-risk resource"
  - name: "Soft Fail"
    flag: "--soft-fail"
    desc: "Report findings without failing the build — useful while first rolling this out in CI"
:::

## Basic Syntax

```
checkov -d .
checkov -f main.tf
checkov -d . --framework terraform --compact
checkov -d . --output junitxml > checkov-report.xml
```

**Common flags:**
- Quick pass/fail read: `checkov -d . --compact`
- Just Terraform, ignore other IaC types in the repo: `--framework terraform`
- Accept one known finding without disabling the whole check elsewhere: `--skip-check CKV_AWS_18`
- CI pipeline report artifact: `--output junitxml > checkov-report.xml`

---

:::scenario{id="scenario-1" level="beginner"}
title: "Scan a Terraform Directory and Read the Pass/Fail Summary"
goal: "See how many built-in policies a small Terraform configuration passes and fails."
hint: "Run it from the directory containing your .tf files. Each FAILED check names the specific resource, the policy ID, and a link to the remediation guidance."
command: "checkov -d . --compact"
expected_output: |
  Check: CKV_AWS_18: "Ensure the S3 bucket has access logging enabled"
      FAILED for resource: aws_s3_bucket.data
      File: /main.tf:1-8

  Check: CKV_AWS_20: "Ensure the S3 bucket does not allow READ permissions to everyone"
      FAILED for resource: aws_s3_bucket.data
      File: /main.tf:1-8

  Check: CKV_AWS_24: "Ensure no security groups allow ingress from 0.0.0.0:0 to port 22"
      PASSED for resource: aws_security_group.web

  Passed checks: 21, Failed checks: 2, Skipped checks: 0
:::

:::scenario{id="scenario-2" level="intermediate"}
title: "Fix a Failed Check and Confirm It's Clean"
goal: "Close the loop this week's lecture describes — catch a misconfiguration in code, fix the code, re-scan to prove it."
hint: "Pick one FAILED check, open the referenced file and line, make the smallest change that satisfies the policy (e.g. remove a public ACL), then re-run the same command."
command: "checkov -d . --compact --framework terraform"
expected_output: |
  Check: CKV_AWS_20: "Ensure the S3 bucket does not allow READ permissions to everyone"
      PASSED for resource: aws_s3_bucket.data
      File: /main.tf:1-8

  Passed checks: 22, Failed checks: 0, Skipped checks: 0
:::

---

## Reading This Week's Findings

Checkov and Trivy's IaC mode cover overlapping ground — either is a valid choice for Lab 4's Terraform scanning step. The point of both is the same: catch the class of misconfiguration Prowler and Security Hub (Week 3) would eventually flag in a live account, but at the pull-request stage, where fixing it costs a one-line diff instead of an incident response.
