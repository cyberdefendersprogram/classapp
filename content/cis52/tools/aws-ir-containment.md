# AWS IR Containment Playbook

A set of pre-written AWS CLI commands for the first hour of a cloud incident — the "Act" step of this week's OODA loop. The reading's advice is to build these tools *before* you need them: when an access key leaks or an instance is compromised, you want to run tested commands, not search documentation.

## Overview

This playbook is essential for:
- **Scoping**: Finding out what a suspicious credential actually did, using CloudTrail (Week 5)
- **Blocking Unauthorized Access**: Deactivating keys, denying a principal everything, and invalidating role sessions that were already issued
- **Isolating Without Destroying Evidence**: Cutting a compromised instance off the network while keeping it running for forensics
- **Preserving Evidence**: Snapshotting disks and recording hashes so you can later show the copy wasn't altered

### The Order Matters

1. **Scope**: what did this identity or instance do? (CloudTrail)
2. **Preserve**: snapshot first, then change things. Don't terminate a compromised instance; it's evidence.
3. **Contain**: deactivate and deny for identities; isolate for instances.
4. **Recover**: rebuild from known-good images and issue new credentials (Ch. 7: "redeploy, don't clean").

**Safety note:** practice these commands only against resources you created in your own lab account. Deactivating keys or attaching `AWSDenyAll` to the wrong principal will lock out a real user or application.

## Basic Syntax (AWS CLI)

```
aws cloudtrail lookup-events --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=<key-id>
aws iam update-access-key --user-name <user> --access-key-id <key-id> --status Inactive
aws iam attach-user-policy --user-name <user> --policy-arn arn:aws:iam::aws:policy/AWSDenyAll
aws ec2 modify-instance-attribute --instance-id <id> --groups <quarantine-sg-id>
aws ec2 create-snapshot --volume-id <vol-id> --description "IR evidence"
```

:::command-builder{id="ir-containment-builder"}
tool_name: aws
target_placeholder: "cloudtrail lookup-events"
scan_types:
  - name: "Scope: What Did This Key Do?"
    flag: "cloudtrail lookup-events --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=<key-id> --max-results 50"
    desc: "Management events made with one access key over the last 90 days of CloudTrail event history"
  - name: "Scope: What Did This User Do?"
    flag: "cloudtrail lookup-events --lookup-attributes AttributeKey=Username,AttributeValue=<user>"
    desc: "Same query, pivoting on the IAM user name instead of the key"
  - name: "Deactivate an Access Key"
    flag: "iam update-access-key --user-name <user> --access-key-id <key-id> --status Inactive"
    desc: "Immediately stops the key from working. Reversible, so prefer it to deleting the key while you investigate"
  - name: "Deny-All a User"
    flag: "iam attach-user-policy --user-name <user> --policy-arn arn:aws:iam::aws:policy/AWSDenyAll"
    desc: "AWS-managed explicit Deny on every action. Overrides any Allow (Week 5's explicit-vs-implicit deny lesson)"
  - name: "Isolate an EC2 Instance"
    flag: "ec2 modify-instance-attribute --instance-id <id> --groups <quarantine-sg-id>"
    desc: "Swap all security groups for a quarantine group with no inbound or outbound rules"
  - name: "Snapshot a Volume for Forensics"
    flag: "ec2 create-snapshot --volume-id <vol-id> --description \"IR evidence - <ticket>\""
    desc: "Point-in-time copy of the disk. Take it before changing or rebuilding anything"
options:
  - name: "Tag as Under Investigation"
    flag: "ec2 create-tags --resources <id> --tags Key=ir-status,Value=quarantined"
    desc: "Lets everyone (and your automation) see the instance is evidence, not something to clean up"
  - name: "Block Termination"
    flag: "ec2 modify-instance-attribute --instance-id <id> --disable-api-termination"
    desc: "Stops anyone, including an attacker with API access, from terminating the instance and destroying evidence"
  - name: "List a User's Keys"
    flag: "iam list-access-keys --user-name <user>"
    desc: "Find every key the user has. Attackers often create a second key for persistence (T1098.001)"
  - name: "Check When a Key Was Last Used"
    flag: "iam get-access-key-last-used --access-key-id <key-id>"
    desc: "Last service, Region, and time the key was used"
:::

---

:::scenario{id="scenario-1" level="beginner"}
title: "Scope a Leaked Access Key"
goal: "An access key was found in a public GitHub repository (like the Uber 2016 and Toyota cases presented today). Find out what it has been used for before you change anything."
hint: "lookup-events covers management events from the last 90 days in the current Region. Look closely at any iam:CreateAccessKey, CreateUser, or AttachUserPolicy calls; those are persistence and privilege escalation."
command: "aws cloudtrail lookup-events --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=AKIAEXAMPLELEAKED01 --max-results 5 --query 'Events[].{Time:EventTime,Name:EventName,Source:EventSource}'"
expected_output: |
  [
      { "Time": "2026-10-01T03:12:44-07:00", "Name": "CreateAccessKey",  "Source": "iam.amazonaws.com" },
      { "Time": "2026-10-01T03:11:02-07:00", "Name": "ListBuckets",      "Source": "s3.amazonaws.com" },
      { "Time": "2026-10-01T03:10:57-07:00", "Name": "GetCallerIdentity","Source": "sts.amazonaws.com" }
  ]
:::

:::scenario{id="scenario-2" level="intermediate"}
title: "Contain the Compromised Identity"
goal: "Stop the leaked key and anything the attacker created with it, without deleting evidence."
hint: "Deactivating the key you found isn't enough if the attacker already created a second key (Scenario 1's CreateAccessKey). AWSDenyAll attached to the user blocks every key that user has, and an explicit Deny always wins."
command: "aws iam update-access-key --user-name ci-deploy --access-key-id AKIAEXAMPLELEAKED01 --status Inactive && aws iam attach-user-policy --user-name ci-deploy --policy-arn arn:aws:iam::aws:policy/AWSDenyAll && aws iam list-access-keys --user-name ci-deploy"
expected_output: |
  {
      "AccessKeyMetadata": [
          { "UserName": "ci-deploy", "AccessKeyId": "AKIAEXAMPLELEAKED01", "Status": "Inactive" },
          { "UserName": "ci-deploy", "AccessKeyId": "AKIAEXAMPLEATTACKER", "Status": "Active" }
      ]
  }

  (The attacker's second key is still Active, but AWSDenyAll blocks it. Deactivate it as well.)
:::

:::scenario{id="scenario-3" level="advanced"}
title: "Isolate and Preserve a Compromised Instance"
goal: "GuardDuty (Week 5) raised a cryptomining finding on an EC2 instance. Preserve the evidence, then cut it off the network."
hint: "Snapshot first. Then block termination, tag it, and swap in a quarantine security group. Security groups are stateful: connections that are already tracked can continue after you change the rules. For an immediate cut, also add a deny rule to the subnet's network ACL."
command: "aws ec2 create-snapshot --volume-id vol-0abc1234 --description \"IR evidence - GD finding 7c1e\" && aws ec2 modify-instance-attribute --instance-id i-0abc1234 --disable-api-termination && aws ec2 modify-instance-attribute --instance-id i-0abc1234 --groups sg-0quarantine00"
expected_output: |
  {
      "SnapshotId": "snap-0123456789abcdef0",
      "VolumeId": "vol-0abc1234",
      "State": "pending",
      "Description": "IR evidence - GD finding 7c1e"
  }
  (no output on success for the two modify-instance-attribute calls)
:::

---

## Revoking Sessions for a Compromised Role

Deactivating a key doesn't affect **temporary credentials** a role already issued. Those stay valid until they expire. To invalidate them:

- **Console:** IAM → Roles → *role* → **Revoke sessions** tab → **Revoke active sessions**. AWS attaches an inline policy named `AWSRevokeOlderSessions` that denies every action for credentials issued before that moment (using the `aws:TokenIssueTime` condition key).
- Applications that legitimately use the role just call `AssumeRole` again and get fresh credentials. An attacker holding stolen session credentials is cut off.

This is how you contain the Capital One pattern from Week 3: credentials pulled from the instance metadata service are role session credentials, not access keys.

---

## Tabletop: "The Key Is on GitHub" (15 minutes, pairs)

Talk through this out loud. You don't need to run anything.

1. **9:02 a.m.** GitHub secret scanning emails you: an access key for IAM user `ci-deploy` was pushed to a public repo 40 minutes ago. **Observe:** which command do you run first, and what are you looking for in its output?
2. **9:10 a.m.** CloudTrail shows `CreateAccessKey`, `CreateUser backup-admin`, and `AttachUserPolicy AdministratorAccess`. **Orient:** which MITRE ATT&CK tactics are these (Week 5 table)? What's the attacker's likely next move?
3. **9:15 a.m.** **Decide and act:** list every containment action, in order, and say who has to approve each one (Ch. 7: business lead vs. technical lead).
4. **Recover and improve:** what replaces a long-lived access key in a CI pipeline (Week 2: roles and OIDC federation instead of stored keys)? What alert would have caught step 2 in under five minutes? Who has to be notified?
