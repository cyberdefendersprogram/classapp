# CIS 52 — Week 4 Notes
**Cloud-Native Security**

Friday, September 18, 2026 · 9:00 a.m.–12:00 p.m.

---

## Before We Start

Lab 3 was due today at 9:00 a.m. Late work is accepted through the last class session with a 10% deduction; your lowest lab and lowest quiz score are each dropped. Quiz 4 opens today at 1:00 p.m. and closes Sunday, September 20, at 11:59 p.m.

## Today's Agenda

**Part 1 — Containers and Kubernetes**
- Recap Week 3 + Lab 3 debrief (segmentation, KMS, CSPM, API scanning)
- Container fundamentals: images, layers, registries — and why a container is not a VM
- Container image risk: base images, vulnerable dependencies, secrets baked into layers
- Kubernetes security concepts: RBAC, namespaces, network policies, pod security standards, secrets
- Cloud workload protection: runtime scanning vs. build-time scanning

**Break — 10 minutes**

**Part 2 — IaC, DevSecOps, and Supply Chain**
- Infrastructure as Code: Terraform state, drift, and policy as code
- Shifting left: SAST, SCA, and IaC scanning in the CI/CD pipeline
- Software supply-chain risk: dependency confusion, malicious packages, build provenance, SBOMs
- Case study: the Codecov Bash Uploader compromise — one poisoned CI script, thousands of victims
- Setup: Lab 4 preview

---

## Books + Reading

Required — Practical Cloud Security, 2nd Ed. (Dotson), Ch. 5 (Cloud-Native Vulnerability Management). Required — NIST SP 800-190, Application Container Security Guide. Required — NIST SP 800-204C, DevSecOps for a Microservices-Based Application with Service Mesh. Optional — Julien Vehent, *Securing DevOps* (Manning).

**Reading question:** Which security problems should be detected before deployment, and which can only be detected effectively at runtime? Which CI/CD controls can be automated before deployment, and what class of incidents does that prevent?

---

## Part 1 — Containers and Kubernetes

### Containers Are Not Small VMs

- A **container** packages an application with its dependencies into a single image, run as an isolated process sharing the host kernel — unlike a VM, there's no hypervisor and no separate guest kernel.
- Because containers share a kernel, a **kernel-level exploit or a misconfigured container runtime** can escape a container in ways that don't have a VM equivalent. Isolation is real but thinner than a VM's.
- An **image** is a stack of read-only layers (base OS, runtime, dependencies, app code) plus metadata; a running container adds a writable layer on top. Anything baked into a layer — including a secret — persists in the image even if a later layer "deletes" it.

### Container Image Risk

- **Base image choice matters** — a full OS base image (e.g., `ubuntu`) carries far more packages, and therefore far more CVEs, than a minimal or distroless base image. Smaller attack surface, fewer things to patch.
- **Vulnerable dependencies** — the same OWASP/SCA problem from application security, but baked into an image and redeployed every time someone builds from that `FROM` line. A vulnerable base image poisons every image built on top of it.
- **Secrets in images** — `COPY .env .` or a hardcoded API key in a `Dockerfile` `ENV` line ends up permanently embedded in the image history, extractable by anyone who can pull the image, even after a later layer removes the file. Secrets belong in a secrets manager or injected at runtime, never in the image.
- **Registry hygiene** — a public or misconfigured private registry is a distribution point for a compromised image; pin to digests (not just `:latest`), and control who can push.

### Kubernetes Security Concepts

- **RBAC (Role-Based Access Control)** — Kubernetes' version of IAM (Week 2): roles and role bindings scope *who* can do *what* to *which* resources, per namespace or cluster-wide. The same least-privilege discipline applies — a default `cluster-admin` binding is the Kubernetes version of an over-privileged IAM role.
- **Namespaces** — logical partitions within a cluster; not a hard security boundary by themselves, but the unit RBAC and network policy attach to.
- **Network policies** — Kubernetes' equivalent of security groups (Week 3): without one, every pod can reach every other pod by default. A network policy is required to enforce segmentation between workloads.
- **Pod Security Standards** — cluster-level guardrails against running containers as root, with privileged mode, or with host filesystem/network access — the settings that let a container escape have the most blast radius.
- **Secrets objects** — Kubernetes `Secret` objects are base64-encoded, **not encrypted**, by default; they need encryption at rest (etcd encryption) and RBAC restricting who can `get`/`list` them, or they're barely better than a plaintext ConfigMap.
- **Admission control** — a policy engine (e.g., OPA/Gatekeeper, Kyverno) that inspects and can reject a manifest at deploy time — the automated control that stops a privileged pod or an unscanned image from ever reaching the cluster.

### Build-Time vs. Runtime Protection

- **Build-time (shift left):** scan the image and its dependencies before it's ever pushed to a registry — cheapest place to catch a known-CVE base image or a leaked secret.
- **Runtime (cloud workload protection):** monitor running containers for anomalous behavior — a process spawning a shell, an unexpected outbound connection — because a scan can't catch a zero-day or a logic flaw that only shows up in execution.
- Neither replaces the other: build-time scanning has zero visibility into what a container actually *does* once deployed, and runtime protection alone means you're catching known-bad images only after they're already running.

---

## Part 2 — IaC, DevSecOps, and Supply Chain

### Infrastructure as Code

- **IaC** (Terraform, CloudFormation, Pulumi) defines cloud infrastructure as versioned code instead of console clicks — which means the same code-review, diffing, and scanning practices from application security now apply to *infrastructure changes*, including IAM policies, security groups, and KMS key policies from the last two weeks.
- **State files are sensitive** — Terraform state can contain resource attributes in plaintext, including some secrets and connection strings. A state file in an unencrypted, publicly readable S3 bucket is its own data exposure incident.
- **Drift** — when the live infrastructure no longer matches the IaC definition (someone made a manual console change). Drift breaks the "code is the source of truth" guarantee IaC is supposed to provide, and can silently reintroduce a misconfiguration a scan already flagged as fixed.
- **Policy as code** — tools like `tfsec` or `checkov` scan Terraform *before apply*, catching the same class of misconfiguration CSPM (Week 3) catches *after* deployment — but before it ever becomes a live resource an attacker could find.

### DevSecOps and CI/CD Pipeline Security

- **Shift left** means moving security checks earlier in the pipeline — SAST (static code analysis), SCA (dependency/software composition analysis), and IaC scanning run on every pull request, not just in a periodic audit.
- **The pipeline itself is a privileged system** — CI/CD runners typically hold cloud credentials, signing keys, and registry push access. A compromised pipeline step doesn't just corrupt a build; it can corrupt everything the pipeline is trusted to touch.
- **Secret scanning** — CI should scan every commit and pull request for accidentally committed credentials before merge, the same discipline that should have caught secrets baked into container images above.
- **Least privilege for pipelines** — a CI job should hold only the credentials it needs for that specific job (e.g., short-lived, scoped-down role), not a long-lived key with broad account access, following the same workload-identity principle from Week 2.

### Software Supply-Chain Risk

- **Dependency confusion** — an attacker publishes a malicious public package with the same name as an internal private package; a misconfigured package manager pulls the public (malicious) one by "priority" or version number.
- **Compromised upstream dependencies** — a legitimate, widely trusted package or base image gets compromised at the source, and every downstream consumer inherits the malicious code on their next build — this is what makes supply-chain attacks so much more efficient for an attacker than targeting one victim directly.
- **SBOM (Software Bill of Materials)** — a manifest of every component and dependency in a build, the prerequisite for knowing "am I affected by this new CVE?" without needing to re-scan everything from scratch.
- **Build provenance and signing** — cryptographically signing an image or artifact (e.g., with Sigstore/cosign) and recording *how* it was built lets a downstream consumer verify a package wasn't tampered with after the trusted build step.

### Case Study — Codecov Bash Uploader (2021)

Codecov's **Bash Uploader** script — a small shell script thousands of companies' CI pipelines downloaded and ran on every build to send coverage data to Codecov — was silently modified by an attacker who first got in through a flaw in Codecov's own Docker image creation process. For roughly two months, every CI run that pulled the script also exfiltrated CI environment variables — which routinely include cloud credentials, API keys, and signing tokens — to an attacker-controlled server. Because the script ran inside customers' own CI pipelines with those pipelines' full set of secrets, one compromised distribution point turned into thousands of downstream compromises, reportedly including credential exposure at companies like HashiCorp and Rapid7.

**Where the attack path could have been broken:**
- Pinning the uploader to a fixed, hash-verified version instead of always fetching "latest" on every build
- Least-privilege pipeline credentials (Week 2's workload identity principle) — even a compromised script can only exfiltrate what the pipeline holds
- Secret scanning and anomaly detection on outbound CI traffic — a build script phoning home to an unfamiliar host is a detectable signal
- SBOM and build provenance for third-party CI dependencies, not just application dependencies
- A CSPM/DevSecOps program (Week 3's posture-management logic) that treats CI/CD infrastructure as in-scope, not just cloud accounts

Same shape of lesson as Weeks 1–3: it's rarely one dramatic exploit — it's an uninterrupted chain of unscoped trust, here running all the way from a Docker image bug into thousands of customers' secrets.

---

## Lab 4 Preview — Container, IaC, and Pipeline Security

Full instructions: Lab 4 assignment on Canvas (link posted on Canvas).

You will:
- Scan a container image with **Trivy** and remediate at least one finding by switching to a smaller/patched base image
- Deliberately bake a fake secret into a `Dockerfile`, then show how it's still extractable from the image history even after a later layer "removes" it
- Scan a Terraform configuration with **Trivy (IaC mode)** or **Checkov**, fix one misconfigured resource, and re-scan to confirm it's clean
- Review a Kubernetes manifest for at least one Pod Security Standard violation (e.g., running as root, privileged mode) and correct it
- **Bonus (20 pts):** complete a TryHackMe room on container or Kubernetes security

**Cost control:** No billed cloud resources are required for this lab — everything runs locally against sample files. If you do spin up anything in AWS, delete it once you have your screenshots.

**Setup — start early:** Parts 1, 3, and 4 only need **Trivy** (`trivy image` pulls from the registry; no Docker needed). Only Part 2 (`docker build` / `docker history`) needs Docker. If Docker Desktop won't start on your machine (it needs WSL 2 and CPU virtualization enabled), use Play with Docker, GitHub Codespaces, or AWS CloudShell if available, and say which one you used. Full steps and fixes: [Lab Setup and Troubleshooting Guide](/tools/lab-setup-guide).

**Real output only:** screenshots must be your own unedited tool output. Hand-typed, AI-simulated, or reformatted results will not receive credit.

**Due:** Friday, September 25, 2026, 9:00 a.m.

---

## Quiz 4

- Opens today, September 18, at 1:00 p.m.
- Closes Sunday, September 20, at 11:59 p.m.
- 90 minutes after starting, 2 attempts
- 6 questions, 10 points — covers today's lecture plus the Week 4 reading (Ch. 5; NIST SP 800-190; NIST SP 800-204C; Codecov breach analysis)

---

## Next Week — Detect the Attack

- Complete Lab 4 by Friday, September 25, at 9:00 a.m.
- Read Practical Cloud Security, Ch. 7 (Detection); MITRE ATT&CK for Cloud
- Be ready to reason about cloud logging, detection engineering, and how the controls from Weeks 1–4 show up (or fail to show up) in the logs when something goes wrong
