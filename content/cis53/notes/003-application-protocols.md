# CIS 53 — Week 3 Notes
**Application Protocols and Encrypted Traffic**

Friday, November 6, 2026 · 9:00 a.m.–12:00 p.m. PT (online)

---

**Class Zoom:** https://peralta-edu.zoom.us/j/9402327279
**Syllabus:** [Canvas — CIS 53 Syllabus](https://peralta.instructure.com/courses/89432/assignments/syllabus)

## Today's Agenda

- Case study share-out (APT1 or IR Startup Research)
- DNS in depth: normal, tunneling, DGA, fast flux
- HTTP and file carving
- TLS metadata: what encryption hides and what it leaves
- Email, phishing evidence and authentication
- AI thread: shadow AI and data egress
- Hands-on: a DNS tunnel and a TLS capture

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

## Hands-On

A DNS tunnel capture and a TLS capture. For each: what is the evidence, which packet shows it, and what would you tell a manager in two sentences?

---

## Lab 2 and Case Study

Lab 2 is due this morning at 9:00 a.m. The Week 3 case study (APT1 or IR Startup Research) is due today: [assignment on Canvas](https://peralta.instructure.com/courses/89432/assignments/1820967). Option B instructions and the company list are on the portal Tools page.
