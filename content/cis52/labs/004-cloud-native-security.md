# Lab 4: Container, IaC, and Pipeline Security

**CIS 52 — Cloud Security Fundamentals**

**Due:** Friday, September 25, 2026, 9:00 a.m.
**Canvas:** Lab 4 assignment (link posted on Canvas)
**Student template:** a Word template with placeholder sections for each part is available at [`templates/004-lab-template.docx`](templates/004-lab-template.docx) — use it if you want a starting structure.

This lab puts this week's lecture directly into practice: scanning a container image and remediating a real finding (Part 1), proving that a "removed" secret still lives in an image's history (Part 2), scanning Infrastructure as Code before it's ever applied (Part 3), and reviewing a Kubernetes manifest for the exact class of misconfiguration Pod Security Standards exist to catch (Part 4). Complete all four parts, plus the optional bonus, and submit everything as **one PDF**.

**Before you take any screenshots:** black out or crop any real API keys, tokens, or passwords if they ever appear on screen. Use only fake/placeholder secrets for this lab — never a real credential.

**No billed cloud resources are required.** Everything in this lab runs locally against sample files. If you choose to spin up anything in AWS for extra exploration, delete it once you have your screenshots.

---

## Part 1 — Container Image Scanning and Remediation

This week's lecture argued that image risk starts with the base image, and that a scan at build time is the cheapest place to catch a known vulnerability. Prove it on a real image.

1. Install **Trivy** (see the Trivy tool page in this course's Tools section).
2. Pick a container image with known vulnerabilities to scan — for example, an older tag like `node:14` or `python:3.9`. Run `trivy image <image>:<tag>` and screenshot the summary (counts by severity: CRITICAL/HIGH/MEDIUM/LOW).
3. Note the base image's OS and one specific CRITICAL or HIGH finding — the CVE ID, the affected package, and the fixed version Trivy recommends.
4. Now scan a smaller or more current base image that addresses the same use case (e.g., `node:20-alpine` instead of `node:14`, or `python:3.12-slim` instead of `python:3.9`). Screenshot the new summary.
5. In 2–3 sentences: how much did the finding count change, and why does a smaller/distroless-style base image tend to carry fewer vulnerabilities in the first place?

## Part 2 — Secrets Baked into Image Layers

Lecture argued that a secret baked into a Dockerfile persists in the image history even after a later layer removes it. Prove this end-to-end with a fake secret.

1. Write a small `Dockerfile` that does the following across two layers:
   - Layer A: `ENV API_KEY=fake-lab4-secret-DO-NOT-USE-1234`
   - Layer B: a later `RUN` step that unsets or overwrites the variable (e.g., `ENV API_KEY=""`)
2. Build the image locally: `docker build -t lab4-secret-test .`
3. Run `docker history --no-trunc lab4-secret-test` (or `trivy image lab4-secret-test` if you have a secret-scanning plugin enabled) and screenshot the output showing the fake secret is still visible in an earlier layer.
4. In 2–3 sentences: why doesn't "removing" a value in a later layer protect it, and where should a real secret live instead (tie this back to a mechanism you've used in a prior lab, e.g., a secrets manager or environment injection at runtime)?
5. **Cleanup:** remove the test image locally with `docker rmi lab4-secret-test`. Never push this image anywhere.

## Part 3 — Infrastructure as Code Scanning

Lecture argued that policy-as-code scanning catches a misconfiguration before it's ever applied — the IaC equivalent of the CSPM scanning from Lab 3, but shifted left.

1. Write (or use a provided) small Terraform file, `main.tf`, that provisions one deliberately misconfigured resource — for example, an S3 bucket with public read access, or a security group with `0.0.0.0/0` ingress on port 22. **Do not run `terraform apply`** — this part is scan-only, no real infrastructure needed.
2. Scan it with **Trivy in IaC/config mode** (`trivy config .`) or **Checkov** (`checkov -d .`) — see the Trivy or Checkov tool page in this course's Tools section. Screenshot the finding, including the rule ID and the specific misconfigured attribute.
3. Fix the misconfiguration in `main.tf` (e.g., remove the public ACL, restrict the CIDR to your own IP).
4. Re-run the same scan and screenshot the clean result.
5. In 2–3 sentences: what's the practical advantage of catching this in `main.tf` before `apply`, versus catching the same misconfiguration with a CSPM tool (Lab 3) after the resource is already live?

## Part 4 — Kubernetes Manifest Review

Lecture covered Pod Security Standards as the guardrail against a container running with more privilege than it needs.

1. Start from this Kubernetes Pod manifest (save as `pod.yaml`):
   ```yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: lab4-pod
   spec:
     containers:
       - name: app
         image: nginx:latest
         securityContext:
           privileged: true
           runAsUser: 0
         volumeMounts:
           - name: host-root
             mountPath: /host
     volumes:
       - name: host-root
         hostPath:
           path: /
   ```
2. Identify and list every Pod Security Standard violation in this manifest (there are at least three: privileged mode, running as root, and a hostPath mount of the host's root filesystem).
3. Rewrite `pod.yaml` correcting each violation (e.g., `privileged: false`, a non-root `runAsUser`, removing the `hostPath` mount or replacing it with a scoped volume type). Screenshot your corrected YAML.
4. If you have access to a local cluster (kind/minikube) or `kubesec`, validate your corrected manifest and screenshot the result. If not, explain in 2–3 sentences how each fix reduces the pod's blast radius if the container inside it were compromised.

---

## Bonus — TryHackMe: Containers/Kubernetes Security (20 points)

Complete a TryHackMe room covering container or Kubernetes security fundamentals (e.g., "Docker Security" or "Introduction to Kubernetes") and include one screenshot showing your completion. This is optional and worth 20 points on top of the lab's normal scoring — it reinforces this week's material from a hands-on, attacker-facing angle.

---

## Submission

- **One PDF** combining all screenshots and written answers from Parts 1–4 (and the bonus, if attempted).
- Due Friday, September 25, 2026, 9:00 a.m. — late submissions follow the syllabus's 10% deduction policy.
- Remember: this lab has no billed cloud resources by design — just remove local test images/containers when you're done.
