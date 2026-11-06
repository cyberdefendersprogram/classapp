# CIS 53 — Week 3 Notes
**Application Protocols and Encrypted Traffic**

Friday, November 6, 2026 · 9:00 a.m.–12:00 p.m. PT (online)

---

**Class Zoom:** https://peralta-edu.zoom.us/j/9402327279
**Syllabus:** [Canvas — CIS 53 Syllabus](https://peralta.instructure.com/courses/89432/assignments/syllabus)

## Today's Agenda

- Feedback on Case Studies 1 and 2 and Lab 1, and using AI well
- Case study review: Target (alerts fired, nobody acted)
- DNS in depth: normal, tunneling, DGA, fast flux
- HTTP and file carving
- TLS metadata: what encryption hides and what it leaves
- Email, phishing evidence and authentication
- AI thread: shadow AI and data egress
- Server-side compromise (Bejtlich Ch. 10) and client-side compromise (Ch. 11)
- Hands-on: four demos (DNS, HTTP, TLS and AI egress, vsftpd backdoor)

---

## Books + Reading

Required — Bejtlich, *The Practice of Network Security Monitoring*, Ch. 10: Server-side Compromise and Ch. 11: Client-side Compromise. Required — OWASP Top 10 for LLM Applications.

**Reading questions:**
1. Follow one investigation: which evidence led the analyst from the first alert to a conclusion?
2. What network or log evidence would show data leaving through an AI service or an LLM-powered application?

---

## Part 1 — DNS

DNS is the phone book, and nearly everything starts with it, so it is a rich place to look.

- **Normal:** short queries, answers with sane TTLs, a few record types.
- **Tunneling:** data encoded in long or high-entropy subdomains; many TXT or NULL queries to one domain; lots of unique names under one parent.
- **DGA (domain generation algorithm):** malware generates many random-looking domains and most return NXDOMAIN.
- **Fast flux:** very low TTLs and rapidly changing IPs for one name.

Useful views: **Statistics → DNS**, filters such as `dns.qry.name.len > 50` and `dns.flags.rcode == 3`.

## Part 2 — HTTP and Carving

Cleartext HTTP shows methods, hosts, user agents, URIs and file contents. In Wireshark, **File → Export Objects → HTTP** pulls out files; **hash** them (SHA-256) and compare with intelligence sources. Unusual user agents, POSTs to odd hosts, and executables served as images are classic clues.

## Part 3 — TLS Without Decrypting

Most traffic is encrypted. You still see metadata:

- **SNI** (the server name), the **certificate** (issuer, validity, subject), the TLS version and ciphers.
- **JA3/JA4 fingerprints** summarize how a client builds its handshake, which helps identify a malware family or tool even when the destination changes.
- Flow shape: sizes, directions and timing.

What you do **not** see: URLs, headers, and payloads. That is why endpoint and application logs matter, and why encrypted traffic is a monitoring-architecture decision (Week 4).

## Part 4 — Email and Authentication

Phishing evidence lives in message headers, links and attachments. On the wire, watch for SMTP/IMAP in cleartext, odd SMB or Kerberos authentication patterns, and repeated failures followed by a success (password guessing).

## Part 5 — The AI Thread: Shadow AI and Egress

Employees paste data into AI tools, and applications send data to model APIs. Defenders ask:

- **Which AI services are people and systems contacting?** DNS and SNI answer this.
- **How much data leaves?** Look at bytes sent, upload sizes and timing.
- **What would a proxy or DLP log show?** URL, user, size, and sometimes content.
- **What is approved?** Detection needs an allowlist; without it everything is noise.

Tie this to the OWASP Top 10 for LLM Applications (e.g., sensitive information disclosure, excessive agency).

## Part 6 — Server-side and Client-side Compromise

Bejtlich Ch. 10 and Ch. 11 show the investigation flow on two attack types.

- **Server-side:** the attacker comes to an exposed service (probe, exploit, open a channel, act). In Ch. 10 an exposed FTP server (vsftpd 2.3.4, with a backdoor triggered by a username ending in `:)`) opens a root shell on port 6200, and the intruder steals an archive. Work: alert, then session data, then full content with tshark, then scope.
- **Client-side:** the user takes the bait (phishing, a link, a compromised site). In Ch. 11 a link in a tweet leads to a malicious Java applet, then a covert channel hidden in DNS (NULL queries, more than 65,000 records in one `dns.log`).
- His intrusion categories: attempt = Cat 3, user-level access = Cat 2, administrator = Cat 1, C2 channel = Breach 3.

## Feedback on Work So Far

Individual scores and comments are in Canvas. This is what we discuss as a class.

- **Case Study 1 (Mitnick):** the core idea landed (trust by IP address, SYN flood, forged ACK, guessed sequence numbers). Points were lost on ATT&CK IDs whose name or tactic did not match (check each on attack.mitre.org), incomplete Wireshark filters (a SYN flood is `tcp.flags.syn == 1 && tcp.flags.ack == 0`), summaries that did not end with the detection sentence, and sources without one primary account.
- **Case Study 2 (Target):** stronger ATT&CK accuracy. The most skipped part was the alerts question: Symantec flagged malicious behavior around Nov 28, FireEye alerted on Nov 30, Dec 2 and Dec 3, the alert name was generic (`malware.binary`), Bloomberg (not the Senate report) says the Bangalore team escalated to Minneapolis, and FireEye's automatic delete was off. Also needed: an outbound row in the sensor table (`ftp.request.command == "STOR"`), a stated choice of which source you trust, and "possibly" for what the Senate report calls unclear.
- **Lab 1:** the NetLab capture problem (`ens160` saw the traffic, `ens192` did not) is a lesson about where a sensor sits. Capture filters and display filters are different languages. Part 1 evidence means the room marked 100% completed with your username.
- **AI use:** allowed, with rules. Disclose unedited or lightly edited AI text, attach your prompts, and verify every fact and ATT&CK ID. Use AI as a critic (find what is missing, check IDs, quiz you), not as the author. A command an AI gave you is unverified until you have run it.
- **Before you submit Case Study 3 and Lab 2:** every table row filled, gray instructions deleted, one PDF, step numbers consistent, sources with author, title, date and link that open, evidence screenshots with your username, personal data cropped, and AI use disclosed.

## Target Case Study Review

The Target breach (2013) is the "alerts fired, nobody acted" case: a vendor's credentials, stolen card data staged on an internal server, and cleartext FTP out to an outside server. The alerts were there; the response was not. Compare it with Demo 010, which has the same FTP-out pattern, and with Mitnick (the trust abused was different).

---

## Hands-On: Class 3 Demos

- [Demo 007: DNS, tunnel, DGA and fast flux](/demos/007-dns-tunnel-dga-fast-flux): find three behaviors hidden among normal lookups.
- [Demo 008: HTTP and file carving](/demos/008-http-and-file-carving): a disguised executable, a beacon, Export Objects and hashing.
- [Demo 009: TLS without decrypting, and AI egress](/demos/009-tls-metadata-and-ai-egress): SNI, certificates, JA3/JA4 and byte counts to find a shadow-AI upload.
- [Demo 010: the vsftpd backdoor](/demos/010-vsftpd-backdoor-and-ftp-exfil): a server-side compromise with FTP exfiltration, after Bejtlich Ch. 10.

For each: what is the evidence, which packet shows it, and what would you tell a manager in two sentences?

---

## Lab 2 and Case Studies

Lab 1 (Weeks 1 and 2) is due this morning at 9:00 a.m. **Lab 2** (Week 3: application protocols, DNS, encrypted traffic, an AI egress capture) is due Fri Nov 13, 9:00 a.m.: [assignment on Canvas](https://peralta.instructure.com/courses/89432/assignments/1820970). Case Study 2 (Target) is due this morning. **Case Study 3** (Incident Response Startup Research) is assigned today and due Fri Nov 13, 9:00 a.m.: [assignment on Canvas](https://peralta.instructure.com/courses/89432/assignments/1820967). The company list and full instructions are on the portal Tools page.
