---
title: Respond, Recover, Improve
---

## Q1 [mcq_single, 2pts]

In the OODA loop used during incident response, what happens in the **Orient** phase?

- [ ] Executing containment actions such as locking down security groups
- [ ] Gathering raw information from cloud provider logs, firewalls, and metrics
- [x] Working out what is going on and what might happen next, using knowledge of your key assets plus external threat intelligence
- [ ] Choosing which systems to take offline or rebuild

## Q2 [mcq_single, 2pts]

After an attacker has had administrative access to a cloud workload, why does the reading recommend redeploying the affected systems instead of cleaning them in place?

- [ ] Cleaning in place is not allowed under the shared responsibility model
- [ ] Redeploying is always cheaper than running malware scanners
- [x] You can't be sure you found every backdoor — a single altered permission or registry entry can let the attacker back in
- [ ] Cloud providers automatically delete compromised instances

## Q3 [mcq_multi, 2pts]

Which of these are recommended ways to prepare for an incident *before* it happens? (Select all that apply)

- [x] Name a primary and a backup incident-response leader
- [x] Keep a small, pre-approved budget for the first hours of an incident
- [x] Keep a separate incident response cloud account ready to use
- [ ] Store backups in the production account so they can be restored faster

## Q4 [mcq_single, 1pt]

How does NIST SP 800-61 Rev. 3 organize incident response compared with Rev. 2?

- [ ] It removes preparation entirely and focuses only on containment
- [x] It aligns incident response with the six NIST CSF 2.0 functions, with improvement and lessons learned feeding back throughout instead of being a final phase
- [ ] It replaces incident response plans with automated SIEM rules
- [ ] It applies only to federal agencies running on-premises infrastructure

## Q5 [mcq_single, 1pt]

In the guest lecture on agent security, what does **"least agency"** add on top of least privilege?

- [ ] Giving every agent administrator access so it never gets blocked
- [ ] Relying on the system prompt to tell the agent what it must not do
- [x] Limiting an agent's tools, context, network reach, and decision authority to what the task needs, with destructive actions held for human approval
- [ ] Letting all agents share one service account so logs stay simple

## Q6 [free_response, 2pts]

Choose one breach presented by a classmate today (not your own). In 4–6 sentences: name the breach, state how the attacker got initial access, describe one **containment or recovery** action the victim took (or should have taken), and explain one change to architecture or controls that should come out of the lessons-learned review.
