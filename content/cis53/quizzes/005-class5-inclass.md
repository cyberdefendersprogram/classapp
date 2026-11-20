---
title: Class 5 In-Class Check (Intelligence, Hunting, Testing Detections and AI-Assisted Triage)
---

## Q1 [mcq_single, 2pts]

An analyst writes rules for an attacker's IP address, domain and file hash. A week later the same attacker returns with a new IP, a new domain and a new file, but polls the same URI pattern once a minute. Which rule still fires?

- [ ] The IP rule
- [ ] The domain rule
- [ ] The file hash rule
- [x] A rule on the polling behavior (the URI shape and the schedule)

## Q2 [mcq_single, 2pts]

On the Pyramid of Pain, which of these costs the attacker the most to change?

- [ ] A file hash
- [ ] An IP address
- [x] Their tactics, techniques and procedures (how they operate)
- [ ] A domain name

## Q3 [mcq_single, 2pts]

Brown and Roberts separate data from intelligence. Which of these is intelligence rather than data?

- [ ] A list of 500 IP addresses
- [ ] A file hash with no other information
- [x] "This IP contacted our kiosk on Nov 13; seen by our own sensor; moderate confidence it is malicious; stale after two weeks"
- [ ] A raw packet capture

## Q4 [mcq_single, 2pts]

An indicator list says an IP address is malicious, but the entry is eight months old. What is the best next step?

- [ ] Block it, because indicators never expire
- [x] Check its age and source and whether the address is now used by someone else, then lower your confidence or retire the entry
- [ ] Ignore all indicators from now on
- [ ] Add it to the allowlist

## Q5 [mcq_single, 2pts]

Put the hunting loop in order.

- [ ] Query, hypothesis, data, validate
- [ ] Data, validate, hypothesis, query
- [x] Hypothesis, data, query, validate, then record or automate what worked
- [ ] Alert, ticket, close, report

## Q6 [mcq_single, 2pts]

In the Demo 15 hunt, three host pairs connected on a very regular schedule: a PC and the internal time server, a build server and an internal API, and a reception kiosk and an outside address. Which step separated the suspicious one from the other two?

- [ ] The coefficient of variation, because the kiosk was the most regular
- [x] Context: the first two destinations are inside the network and expected for those hosts; a kiosk calling an outside address on a schedule is not
- [ ] The packet count alone
- [ ] The protocol, because only the kiosk used TCP

## Q7 [mcq_single, 2pts]

A Scapy-built test sends one request in seven forms. A rule using `content:"/api/v1/poll?id="` without `nocase` catches six and misses the version with the path in capital letters. What is the right conclusion?

- [ ] The rule is fine, because capital letters are unusual
- [x] The test found a gap; add `nocase`, rerun all seven and also rerun the benign request to confirm it still stays quiet
- [ ] Delete the rule
- [ ] Scapy is unreliable

## Q8 [mcq_multi, 3pts]

Which of these are good reasons to test a detection with crafted or simulated traffic before relying on it? (Select all that apply)

- [x] To confirm it fires on the behavior it was written for
- [x] To find variants it misses
- [x] To check that known-good traffic does not trigger it
- [ ] To avoid having to write a description of the rule

## Q9 [mcq_single, 2pts]

A model's triage summary says a host "uploaded about 750 KB to an AI service: likely exfiltration." The log shows about 750 KB received and 2.5 to 9 KB sent per session, to a service on the approved list. What went wrong?

- [ ] Nothing; the model is 99% confident
- [x] The model reversed the direction of the data flow and ignored the approved list; every claim needs a log line behind it
- [ ] The log is wrong
- [ ] AI models cannot read logs

## Q10 [mcq_single, 2pts]

Anthropic reported in November 2025 that a state-linked group used an AI coding agent to carry out most of an intrusion, and some researchers criticized the report for giving no indicators of compromise. What does that criticism teach about intelligence quality?

- [ ] Reports from AI companies are always wrong
- [x] A claim you cannot check against shared evidence deserves a lower confidence rating until you find independent confirmation
- [ ] Indicators of compromise are the most valuable part of any report
- [ ] Only government sources count

## Q11 [mcq_single, 2pts]

In the EchoLeak case (CVE-2025-32711), an email from outside the company caused Microsoft 365 Copilot to leak internal data with no user click. Which description fits best?

- [ ] A phishing link that stole a password
- [x] Untrusted content reached an assistant that could read privileged data and was treated as instructions (a prompt injection)
- [ ] A denial-of-service attack on the mail server
- [ ] A weak WiFi password

## Q12 [mcq_single, 2pts]

Which MITRE resource describes tactics and techniques used against AI systems, in the same style as ATT&CK?

- [ ] CVE
- [ ] OWASP Top 10 for web apps
- [x] MITRE ATLAS
- [ ] The Pyramid of Pain
