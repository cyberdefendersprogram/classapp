# CIS 53 — Week 4 Notes
**IDS/IPS, SIEM and Monitoring Architecture**

Friday, November 13, 2026 · 9:00 a.m.–12:00 p.m. PT (online)

---

**Class Zoom:** https://peralta-edu.zoom.us/j/9402327279
**Syllabus:** [Canvas — CIS 53 Syllabus](https://peralta.instructure.com/courses/89432/assignments/syllabus)

## Today's Agenda

- IDS and IPS concepts; signature vs. behavioral vs. anomaly detection
- Rule anatomy: write, test and tune a Suricata/Snort rule live
- Zeek logs and correlating by connection ID
- Sigma and SIEM triage
- Monitoring architecture, including cloud and TLS blind spots
- AI thread: attacks on LLM apps and agents, and the telemetry they leave
- **Final-format demo:** solving a level live

---

## Books + Reading

Required — Bejtlich, *The Practice of Network Security Monitoring*, Ch. 9: NSM Operations. Required — Roddie et al., *Practical Threat Detection Engineering*, Ch. 1 (Fundamentals: the three qualities of good detection, the Pyramid of Pain) and Ch. 2 (the detection life cycle, especially Test with known-bad and known-good data). Required — Suricata Documentation, Rules: Introduction. Optional — NSM Ch. 4: Distributed Deployment; Sigma Rules basics.

**Reading questions:**
1. How does an analyst decide whether an alert is worth escalating, and what should be recorded?
2. When does a signature-based detection beat a behavioral one, and when does it fail?
3. Name the parts of a rule header and rule options, and say what a rule needs to avoid false positives.

---

## Part 1 — IDS and IPS

- **IDS** watches a copy of traffic and alerts. **IPS** sits in line and can block, so a mistake can cause an outage.
- **Signature:** matches known bad patterns; precise, but blind to the new.
- **Behavioral / anomaly:** flags deviation from a baseline; finds the new, but noisier.
- **Evasion** (fragmentation, encoding, encryption) still matters: a detection is only as good as what the sensor can see and reassemble.
- **False positives and negatives:** every detection trades one against the other. Record your tuning decisions.

## Part 2 — Rule Anatomy

A Suricata/Snort rule has a **header** (action, protocol, source, ports, direction, destination) and **options** (message, content matches, flow, thresholds, reference, sid, rev).

```
alert http $HOME_NET any -> $EXTERNAL_NET any (msg:"Suspicious upload to unknown host"; flow:established,to_server; http.method; content:"POST"; http.uri; content:"/upload"; sid:1000001; rev:1;)
```

**Demo 11** ([write and tune a Suricata rule](/demos/011-write-and-tune-a-suricata-rule)) uses `rule-lab.pcap` and `class4-suricata.rules` (sids 9100001–9100005): a too-broad rule (3 alerts), the tuned rule (1), a beacon threshold (1), a TLS SNI rule for the same upload over HTTPS (1), and a user-agent rule that shows a weak indicator (15 alerts). Tested with Suricata 8.0.8. Suricata and Snort 3 syntax are close; we use Suricata documentation.

## Part 3 — Zeek

Zeek turns traffic into structured logs: `conn.log`, `dns.log`, `http.log`, `ssl.log`, `files.log`. Every connection has a **uid** you can use to join logs. Question flow: start from an alert or odd `conn.log` row, take the uid, and read the matching DNS, HTTP and TLS records. **Demo 12** ([from alert to uid](/demos/012-zeek-from-alert-to-uid)) follows the same incident from the Suricata alert through `conn.log`, `http.log`, `dns.log` and `ssl.log` (tested with Zeek 9.0.1).

## Part 4 — Sigma and the SIEM

**Sigma** is a vendor-neutral format for log detections, so a rule can be translated to different SIEMs. A SIEM collects logs, lets you search, and fires alerts. Triage steps: scope (which host, user, time), enrich (intelligence, asset context), decide (benign, suspicious, confirmed), and document. **Demo 13** ([Sigma and an AI agent log](/demos/013-sigma-and-an-ai-agent-log)) converts three Sigma rules with pySigma to Splunk and Lucene and runs them against `agent-tool-calls.jsonl`.

## Part 5 — Architecture

- Sensor placement: internet edge, internal segments, data center, cloud.
- Cloud visibility: VPC flow logs, traffic mirroring, and the provider's threat detection service.
- **TLS blind spots:** decide where decryption is legitimate and legal, and where you rely on metadata and endpoint logs.
- Retention: full packets are expensive; keep flow and logs longer.

## Part 6 — The AI Thread: Attacks on LLM Apps and Agents

- **Prompt injection:** hostile instructions hidden in content the model reads (a web page, a document, an email).
- **Tool and agent abuse:** an agent with excessive permissions calls tools it should not, or sends data somewhere unexpected.
- **Telemetry that exposes it:** the agent's tool-call log, outbound requests to new domains, unusual data volumes, and prompts or responses containing secrets.
- **Know normal first:** what a healthy agent's log looks like (which tools, which destinations, how often).

Map to **MITRE ATLAS** (AML.T0051, LLM prompt injection) as well as ATT&CK.

## Final-Format Demo

We solve a network-based level live, thinking aloud and using hints, so you see the format before the Final is released next week.

---

## Lab 3

[Lab 3 on Canvas](https://peralta.instructure.com/courses/89432/assignments/1820972) — due **Fri Nov 20, 9:00 a.m. PT**. TryHackMe IDS Fundamentals, Snort and Network Monitoring with Zeek (assigned in the Business group as "CIS 53 Lab 3: …"); a NetLab alert-review lab; and Part 3 on `agent-tool-calls.jsonl`: Prompt Injection room, a detection you write and run, and a 150-word short answer.

## Case Study 4 — OPM

[Case Study 4 on Canvas](https://peralta.instructure.com/courses/89432/assignments/1820973) — due **Fri Nov 20, 9:00 a.m. PT**. The OPM breach, rebuilt for 2026 with a new Word template and a required section where you write one detection (requirement, data source, rule or query, false positive, test data).

## Quizzes

- **In-class quiz** (portal): `quizzes/004-class4-inclass.md`, 11 questions.
- **Week 4 Canvas quiz:** Class 3 content, due Sun Nov 15, 11:59 p.m. PT.

## Feedback from Weeks 1–3

Covered in class from the grading notes: no late penalty on late Lab 1, Case Studies 1 and 2; resubmission and regrade open; ATT&CK IDs must match names; complete filters; alert timeline for Target; AI use is allowed with disclosure.
