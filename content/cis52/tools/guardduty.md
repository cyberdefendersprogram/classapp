# Amazon GuardDuty

Amazon GuardDuty is a managed threat-detection service — the "during" layer in this week's Detect → Investigate framing. It doesn't collect any new data of its own; it continuously analyzes **CloudTrail events, VPC Flow Logs, and DNS query logs** you're likely already generating, correlates them against threat-intelligence feeds (known-bad IPs, malicious domains, anonymizing proxies), and raises **findings** when it sees a pattern worth a human's attention — a port scan, a call to a cryptomining domain, or an unusual API call from a credential that doesn't normally behave that way.

## Overview

GuardDuty is essential for:
- **Continuous Threat Detection**: No agent to install, no infrastructure to manage — it turns on and starts analyzing log sources you likely already have
- **Correlated Findings, Not Raw Logs**: A finding names the resource, the behavior, and a severity — the same "prioritized list, not a wall of logs" principle as Prowler (Week 3), but for live threats instead of static misconfiguration
- **This Week's Pipeline, Managed**: It's a working example of the aggregation → correlation → alerting chain from lecture, built and run by AWS
- **Multi-Account Visibility**: A GuardDuty administrator account can view and manage findings across an entire AWS Organization

### Enabling GuardDuty (Console)

GuardDuty has no separate agent to install — it's an account-level toggle plus optional data-source add-ons (S3 protection, EKS protection, Malware Protection).

1. Console → GuardDuty → **Enable GuardDuty** (30-day free trial per account)
2. Findings begin appearing within a few minutes for existing log activity — no backfill of historical data
3. **Cost control: GuardDuty bills based on the volume of CloudTrail/VPC Flow/DNS data it analyzes — disable it when you're done experimenting in a lab or personal account.**

## Basic Syntax (AWS CLI)

GuardDuty can also be enabled and queried entirely from the CLI, which is useful for scripting or for an account where you don't want to click through the console.

```
aws guardduty create-detector --enable
aws guardduty list-detectors
aws guardduty list-findings --detector-id <detector-id>
aws guardduty get-findings --detector-id <detector-id> --finding-ids <finding-id>
```

:::command-builder{id="guardduty-builder"}
tool_name: aws guardduty
target_placeholder: "list-findings"
scan_types:
  - name: "Create/Enable a Detector"
    flag: "create-detector --enable"
    desc: "Turn on GuardDuty for the current account/region"
  - name: "List Detectors"
    flag: "list-detectors"
    desc: "Get the detector ID needed for every other command"
  - name: "List Findings"
    flag: "list-findings --detector-id <detector-id>"
    desc: "List finding IDs for the detector, newest first by default"
  - name: "Get Finding Detail"
    flag: "get-findings --detector-id <detector-id> --finding-ids <finding-id>"
    desc: "Full detail for one or more specific findings — resource, action, severity"
  - name: "Generate Sample Findings"
    flag: "create-sample-findings --detector-id <detector-id>"
    desc: "Instantly populate one finding of every type GuardDuty supports — no real attack needed, free, ideal for class"
options:
  - name: "Filter by Severity"
    flag: "--finding-criteria"
    desc: "JSON criteria to filter list-findings, e.g. severity >= 7 (High)"
  - name: "Archive a Finding"
    flag: "archive-findings --detector-id <detector-id> --finding-ids <finding-id>"
    desc: "Mark a reviewed, non-actionable finding as archived so it stops surfacing"
  - name: "Disable"
    flag: "update-detector --detector-id <detector-id> --no-enable"
    desc: "Turn off analysis without deleting the detector (billing stops)"
:::

---

:::scenario{id="scenario-1" level="beginner"}
title: "Enable GuardDuty and List Your First Findings"
goal: "Turn on GuardDuty and see what it surfaces from your account's existing CloudTrail/VPC Flow/DNS activity."
hint: "Findings can take a few minutes to appear after enabling, and only reflect activity from the moment you turn it on forward — there's no historical backfill."
command: "aws guardduty create-detector --enable && aws guardduty list-detectors"
expected_output: |
  {
      "DetectorId": "a1b2c3d4e5f6g7h8i9j0"
  }
  {
      "DetectorIds": [
          "a1b2c3d4e5f6g7h8i9j0"
      ]
  }
:::

:::scenario{id="scenario-2" level="intermediate"}
title: "Read a Sample Finding and Map It to a Tactic"
goal: "Pull the detail of one finding and connect its finding type to a MITRE ATT&CK tactic from this week's lecture."
hint: "GuardDuty finding types follow a `ThreatPurpose:ResourceType/DetectionName` pattern — the ThreatPurpose segment (e.g. CredentialAccess, Discovery, Exfiltration) often maps directly to an ATT&CK tactic name."
command: "aws guardduty get-findings --detector-id a1b2c3d4e5f6g7h8i9j0 --finding-ids <finding-id>"
expected_output: |
  {
      "Findings": [
          {
              "Type": "UnauthorizedAccess:EC2/MetadataDNSRebind",
              "Severity": 8.0,
              "Title": "Unusual DNS resolution pattern associated with an SSRF attack was observed.",
              "Description": "EC2 instance i-0abc123 is querying a domain associated with SSRF/DNS rebinding attacks targeting the EC2 instance metadata service.",
              "Resource": {
                  "ResourceType": "Instance",
                  "InstanceDetails": { "InstanceId": "i-0abc123" }
              }
          }
      ]
  }
:::

:::scenario{id="scenario-3" level="beginner"}
title: "Generate Sample Findings (No Real Attack Required)"
goal: "Populate a detector with one example of every GuardDuty finding type instantly — the basis for this week's in-class exercise."
hint: "Sample findings are clearly flagged (their finding ID and description say 'sample') and cost nothing extra — this is the intended way to explore GuardDuty's finding catalog without waiting for real malicious activity or running anything risky."
command: "aws guardduty create-sample-findings --detector-id a1b2c3d4e5f6g7h8i9j0"
expected_output: |
  (no output on success)

  aws guardduty list-findings --detector-id a1b2c3d4e5f6g7h8i9j0
  {
      "FindingIds": [
          "82b1a2c3d4e5f6a7b8c9d0e1f2a3b4c5",
          "93c2b3d4e5f6a7b8c9d0e1f2a3b4c5d6",
          "... one finding ID per supported finding type"
      ]
  }
:::

---

## In-Class Exercise (15 minutes)

Work through this in pairs during Part 2 of lecture.

1. **Enable GuardDuty** (Scenario 1) if it isn't already on for your lab account.
2. **Generate sample findings** (Scenario 3) — this instantly creates one finding of every type GuardDuty supports, so you don't need to wait for or simulate a real attack.
3. In the console (GuardDuty → Findings) or via `list-findings`/`get-findings`, **sort by severity** and pick one **High** (7.0+) finding.
4. For your chosen finding, answer:
   - What is the finding **Type** (the `ThreatPurpose:ResourceType/DetectionName` string), and what resource does it apply to?
   - Which **MITRE ATT&CK tactic** from today's lecture table does its `ThreatPurpose` prefix map to (e.g., `CredentialAccess`, `Discovery`, `Exfiltration`, `Backdoor`)?
   - What telemetry (CloudTrail, VPC Flow Logs, or DNS logs) is GuardDuty most likely drawing on for this specific finding type?
5. **Be ready to share** your finding type and tactic mapping with the class — we'll build a shared list on the board covering as many tactics as the room can find.
6. **Cleanup:** archive your sample findings when done (`archive-findings`) or simply disable GuardDuty if you enabled it just for this exercise.

---

## Reading This Week's Findings Against Capital One and Codecov

- `UnauthorizedAccess:EC2/MetadataDNSRebind` and the related instance-metadata findings are GuardDuty's direct answer to the **Capital One** attack path (Week 3) — the exact SSRF-to-instance-metadata request pattern that let the attacker mint credentials from an over-privileged role.
- GuardDuty's `Backdoor:EC2/C2Activity.B!DNS` and other command-and-control-style findings are built to catch a compromised workload phoning home to an unfamiliar host — the same shape of signal that, watched on outbound CI traffic, could have flagged the **Codecov** Bash Uploader compromise (Week 4) while it was still exfiltrating secrets.
- Neither finding replaces the underlying control (least-privilege IAM, IMDSv2, pipeline credential scoping) — GuardDuty's whole value is telling you **when** one of those controls was missing or bypassed, which is this week's core detection lesson.
