# Lab Setup and Troubleshooting Guide

Read this once before Lab 1, and come back to it whenever a lab command fails. Most lost time in this course is tool setup, not the security concepts — so this page lists exactly what each lab needs, how to install it on Windows, macOS, or Linux, and the errors students hit most often.

## What each lab needs

| Lab | You need | Docker required? |
|---|---|---|
| Lab 1 — IAM fundamentals | AWS account, browser | No |
| Lab 2 — IAM policies, conditions, KMS | AWS account, browser (AWS CloudShell optional) | No |
| Lab 3 — Posture and secrets | AWS CLI or CloudShell, Prowler **or** Security Hub | No |
| Lab 4 — Container, IaC, pipeline | Trivy (all parts) | **Only Part 2** (`docker build`) |
| Lab 5 — Breach case study | Word/Docs, slides | No |

**Key point for Lab 4:** Parts 1, 3, and 4 only need Trivy. `trivy image <image>:<tag>` pulls the image straight from the registry — you do **not** need Docker running for it. Only Part 2 (building an image and running `docker history`) needs Docker.

## AWS access (all AWS labs)

- Use the AWS Console in a browser for Labs 1–2. **AWS CloudShell** (the `>_` icon in the console's top bar) gives you a ready-made terminal with the AWS CLI already signed in as your console user — no access keys needed.
- If you use the CLI on your own computer: `aws configure`, then confirm with `aws sts get-caller-identity`. **Never screenshot a terminal that shows an access key or secret key** — crop or black them out, and delete the keys when the lab is done.
- Check which **region** the console shows (top right). Resources are region-scoped; a bucket or key created in one region won't appear in another.
- Find your public IPv4 address with `curl https://checkip.amazonaws.com`. Lab rules expect **IPv4** (`1.2.3.4/32`), not an IPv6 address.

## Installing Trivy

| OS | Command / steps |
|---|---|
| macOS | `brew install trivy` |
| Linux (Debian/Ubuntu) | Follow the install steps on the Trivy docs page, then `sudo apt-get install trivy` |
| Windows | Download the `windows-64bit` zip from the Trivy GitHub Releases page, unzip it, and either run `trivy.exe` from that folder in PowerShell or add the folder to your `PATH`. (If you use Chocolatey: `choco install trivy`.) |
| Any OS, with Docker | `docker run --rm aquasec/trivy image <image>:<tag>` |

Verify with `trivy --version`.

## Installing Docker (Lab 4 Part 2 only)

- **Windows/macOS:** install Docker Desktop. On Windows it needs WSL 2 and CPU virtualization turned on. If you see *"Docker Desktop - virtualization support not detected"* or *"Cannot connect to the Docker daemon"*, enable virtualization (Intel VT-x / AMD-V / SVM) in your BIOS/UEFI, then enable the **Windows Subsystem for Linux** and **Virtual Machine Platform** features and reboot. This can take 30+ minutes — **start it before the week the lab is due, not the night before.**
- **Linux:** install `docker.io` (or Docker Engine) and add your user to the `docker` group.
- **Can't run Docker locally?** You have three ways to still complete Part 2:
  1. Use a free browser sandbox such as **Play with Docker** (labs.play-with-docker.com).
  2. Use **GitHub Codespaces** (a free tier is available), which comes with Docker.
  3. Use **AWS CloudShell** if Docker is available there for your account.
  Whichever you use, show the `docker build` and `docker history --no-trunc` output in your screenshot. Tell the instructor in your submission which environment you used.

## Installing Prowler (Lab 3)

```bash
pip install prowler        # needs Python 3.9 or newer
prowler aws --version
```

- On Windows use `py -m pip install prowler` in PowerShell if `pip` isn't found.
- The easiest option is often **AWS CloudShell**: it already has Python and your AWS credentials.
- Prowler only **reads** your account; it creates nothing and needs no cleanup.
- Prefer a console-only route? Enabling Security Hub with the CIS AWS Foundations Benchmark works too — but disable it afterward (it is billed).

## Common errors and fixes

| Symptom | Likely cause and fix |
|---|---|
| `trivy: command not found` / not recognized | Trivy isn't on your `PATH`. Run it from the folder you unzipped it into (`.\trivy.exe`) or add the folder to `PATH`. |
| Trivy hangs or says `TOOMANYREQUESTS` while downloading its database | Wait a few minutes and retry, or use `--db-repository public.ecr.aws/aquasecurity/trivy-db`. |
| `Cannot connect to the Docker daemon` | Docker Desktop isn't running (or virtualization is off). Start it, or use a fallback above. |
| `AccessDenied` when you expected success | Check the region, the exact bucket/object name (a **leading or trailing space** in an object name is a classic cause), and whether you are signed in as the principal you think you are. |
| `AccessDenied` when you expected an *explicit deny* | The error text says whether it's an explicit deny in a resource-based policy or simply "no identity-based policy allows" the action. Only the first proves your Deny statement worked. |
| Policy JSON works in the console but fails in PowerShell | PowerShell mangles quotes. Save the JSON to a file and pass it as `file://policy.json`. |
| Command fails with `<YOUR-BUCKET>` or `<ACCOUNT-ID>` | Placeholders were not replaced. Re-read the command before running it. |
| KMS key policy edit locks everyone out | Keep the default statement that lets the account root user administer the key, and add your Deny **in addition**. |
| IP condition never matches | You used an IPv6 address or a VPN/proxy address. Use the IPv4 from `checkip.amazonaws.com`, with `/32`. |

## Using AI tools for setup help

Asking an AI tool "why does this error happen?" is fine. Treat the answer as **untrusted until you've checked it against the tool's or AWS's own documentation**, never paste keys, tokens, or account IDs into it, and don't submit its output as your own explanation. If you used AI to get unstuck, say so in a sentence in your submission.
