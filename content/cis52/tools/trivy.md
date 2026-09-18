# Trivy

Trivy is a free, open-source scanner from Aqua Security that finds vulnerabilities, misconfigurations, and secrets in one binary — container images, filesystems, git repositories, and Infrastructure as Code (Terraform, CloudFormation, Kubernetes manifests). It's the fastest way to answer this week's core question — "what's actually wrong with this image or this IaC file?" — before either one is ever deployed.

## Overview

Trivy is essential for:
- **Container Image Scanning**: Find known CVEs in a base image and every package layered on top of it
- **IaC Misconfiguration Scanning**: Catch a public S3 bucket or an open security group in Terraform before `apply`
- **Secret Detection**: Flag a hardcoded API key or credential baked into an image layer or a repo
- **Kubernetes Manifest Scanning**: Check a Pod spec against common misconfigurations (privileged mode, root user, missing resource limits)

### Installation

```bash
# macOS
brew install trivy

# Linux (Debian/Ubuntu)
sudo apt-get install trivy

# Or run via Docker — no local install needed
docker run --rm aquasec/trivy image <image>:<tag>

# Verify
trivy --version
```

:::command-builder{id="trivy-builder"}
tool_name: trivy
target_placeholder: "image node:18-alpine"
scan_types:
  - name: "Image Scan"
    flag: "image"
    desc: "Scan a container image for OS and library vulnerabilities"
  - name: "Filesystem Scan"
    flag: "fs ."
    desc: "Scan a local directory (source code, dependencies) for vulnerabilities"
  - name: "IaC / Config Scan"
    flag: "config ."
    desc: "Scan Terraform, CloudFormation, Kubernetes YAML, or Dockerfiles for misconfigurations"
  - name: "Repository Scan"
    flag: "repo <git-url>"
    desc: "Clone and scan a remote git repository"
options:
  - name: "Severity Filter"
    flag: "--severity"
    desc: "Only report at this severity: CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN"
  - name: "Scanners"
    flag: "--scanners"
    desc: "Choose which scanners run: vuln, misconfig, secret, license"
  - name: "Exit Code"
    flag: "--exit-code 1"
    desc: "Return a non-zero exit code on findings — for failing a CI job on critical issues"
  - name: "Output Format"
    flag: "--format"
    desc: "table (default), json, sarif, or a template for a custom report"
:::

## Basic Syntax

```
trivy image <image>:<tag>
trivy image --severity CRITICAL,HIGH <image>:<tag>
trivy config .
trivy fs --scanners vuln,secret .
```

**Common flags:**
- Only critical/high findings for a quick read: `--severity CRITICAL,HIGH`
- Fail a CI job on any critical finding: `--exit-code 1 --severity CRITICAL`
- Scan an image and its filesystem for secrets in one pass: `trivy image --scanners vuln,secret <image>`
- Scan just Terraform/IaC in the current directory: `trivy config .`

---

:::scenario{id="scenario-1" level="beginner"}
title: "Scan a Container Image and Read the Summary"
goal: "Get a first read on how many known vulnerabilities a base image carries, and compare a heavier image to a slimmer one."
hint: "Run it once against an older/full-OS image tag, then again against a slim or alpine tag for the same app, and compare the CRITICAL/HIGH counts."
command: "trivy image --severity CRITICAL,HIGH node:14"
expected_output: |
  node:14 (debian 10.13)
  ==================================
  Total: 187 (CRITICAL: 12, HIGH: 61)

  ┌──────────────┬────────────────┬──────────┬───────────────────┬───────────────┬──────────────────────────────┐
  │   Library     │ Vulnerability  │ Severity │ Installed Version │ Fixed Version │             Title             │
  ├──────────────┼────────────────┼──────────┼───────────────────┼───────────────┼──────────────────────────────┤
  │ openssl       │ CVE-2023-0464  │ HIGH     │ 1.1.1n-0+deb10u3  │ 1.1.1n-0+deb10u5 │ Excessive Resource Usage...  │
  │ libc6         │ CVE-2023-4911  │ CRITICAL │ 2.28-10           │ 2.31-13+deb11u5 │ glibc: buffer overflow...    │
  └──────────────┴────────────────┴──────────┴───────────────────┴───────────────┴──────────────────────────────┘
:::

:::scenario{id="scenario-2" level="intermediate"}
title: "Scan Terraform for Misconfigurations"
goal: "Catch a misconfigured cloud resource in IaC before it's ever applied — the shift-left version of this week's CSPM logic."
hint: "Run trivy config against the directory holding your .tf files. Each finding includes the specific attribute and a remediation suggestion."
command: "trivy config --severity CRITICAL,HIGH ."
expected_output: |
  main.tf (terraform)
  ====================
  Tests: 24 (SUCCESSES: 21, FAILURES: 3)

  AVD-AWS-0089 (HIGH): Bucket does not have logging enabled.
  AVD-AWS-0132 (CRITICAL): S3 Bucket has an ACL defined which allows public access.
    → resource "aws_s3_bucket" "data": acl = "public-read"
    → Remediation: remove the public ACL or set it to "private"

  AVD-AWS-0107 (HIGH): An ingress security group rule allows traffic from /0.
    → resource "aws_security_group" "web": cidr_blocks = ["0.0.0.0/0"]
:::

---

## Reading This Week's Findings

Two Trivy modes map directly onto this week's two halves: `trivy image` catches the base-image and dependency risk from Part 1 of lecture, and `trivy config` catches the IaC misconfiguration risk from Part 2 — both scanners exist so a problem is caught in a pull request, not in a CSPM scan after the resource is already live.
