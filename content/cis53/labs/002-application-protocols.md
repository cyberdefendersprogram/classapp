# Lab 2: Application Protocols, DNS, and Encrypted Traffic

**CIS 53 — Intrusion Detection In-Depth**

**Open now. Due:** Friday, November 13, 2026, 9:00 a.m.
**Canvas:** [Lab 2 assignment](https://peralta.instructure.com/courses/89432/assignments/1820970)

Covers Week 3 (Class 3): DNS, HTTP, TLS metadata, and server-side compromise. Submit everything as a single PDF.

**Before you take any screenshots:** crop or black out any passwords, tokens, or personal data. Never submit credentials. Use only the lab environments and capture files we provide — do not capture or scan any other network.

**Reading:** Bejtlich, *The Practice of Network Security Monitoring*, Ch. 10 (Server-side Compromise) and Ch. 11 (Client-side Compromise), plus the OWASP Top 10 for LLM Applications.

## Part 1 — TryHackMe rooms (30 points)

Complete these rooms from your **TryHackMe assignments** (Business group `2026-Fall-CIS53`). Screenshot each room showing it as completed, with your username visible.

- [DNS in Detail](https://tryhackme.com/room/dnsindetail)
- [Data Exfiltration Detection](https://tryhackme.com/room/dataexfildetection) — **optional** (extra practice, no points lost if skipped): DNS tunneling, FTP, HTTP and ICMP exfiltration; the same patterns as Class 3 Demos 7, 8 and 10
- Wireshark: Traffic Analysis — [room](https://tryhackme.com/room/wiresharktrafficanalysis)

If a room is not in your assignments, email me at vbhandari@peralta.edu with the email address tied to your TryHackMe account.

## Part 2 — NetLab (20 points)

Log in at [openlab.baccc.net](https://openlab.baccc.net/) and complete **NDG Ethical Hacking v2 → Lab 01: DNS Footprinting**.

- Screenshot the record types you found (A, MX, NS, TXT) for the lab's target domain.
- In two or three sentences: if a sensor sat on the lab network, which of your queries would it have logged, and which one would you flag as reconnaissance?
- If the lab will not start or the steps do not match the screen, tell us **before the deadline** with a screenshot of the problem. You will not be penalized for a lab that is broken.

## Part 3 — Find the AI egress (30 points)

Download `tls-metadata-ai-egress.pcap` from this Canvas assignment (attached here; you do not need the class portal). The capture is synthetic. A company wants to know which hosts send data to AI services, and whether any of it is not approved. The approved service is `api.openai.com`, used only by host `10.0.0.60`.

1. **Findings table** (12 points): one row per TLS session with source host, server name (SNI), TLS version, bytes sent, bytes received, and a verdict (approved, unapproved, or needs review). Use Statistics → Conversations and the display filter `tls.handshake.type == 1`.
2. **Evidence** (6 points): for the largest upload, give the frame number of the ClientHello, the certificate subject and issuer (if visible), and the JA3 or JA4 value. Say why the certificate is or is not visible for other sessions.
3. **One detection** (8 points): a Suricata rule, Zeek script idea, Sigma rule or SIEM query that flags large uploads to an AI service that is not on the allowlist. Name one false positive it would produce.
4. **What you cannot know** (4 points): one sentence on what the capture does not tell you about the upload, and which log or tool would.

Screenshots: the Conversations table sorted by bytes, and the packet with the evidence highlighted. Say which display filter you used (or "none").

## Part 4 — Short answers (20 points)

About 100 words each:

1. A DNS tunnel and a DGA both produce unusual DNS. How would each look in a `dns.log` or Wireshark, and which one display filter would you use for each?
2. A server answers `GET /docs/invoice.jpg` with `Content-Type: image/jpeg`, but the first two bytes of the body are `MZ`. List the steps you take and the evidence you would record for a colleague to check.
3. In Bejtlich Ch. 10, follow the investigation from the first alert to the conclusion that the server was compromised. Which three pieces of evidence mattered most, and which data type (alert, session, full content) provided each?
4. A host sends a large upload to an AI service over TLS 1.3. Name two things you can see and two you cannot. Where would you put a control to see the rest?

**Optional (+10 points):** complete the TryHackMe room *Carnage* (a Wireshark challenge on a compromised workstation) and add one sentence on which data type found the command-and-control traffic fastest.

## What your screenshots must show

| Item | A good screenshot shows |
|---|---|
| Part 1 — each room | The room page marked 100% / completed, with your TryHackMe username visible |
| Part 2 — NetLab | The record types in the lab's terminal output |
| Part 3 — conversations | Statistics → Conversations → TCP sorted by bytes, with the suspect row visible |
| Part 3 — evidence | The ClientHello or Certificate packet highlighted, with the SNI, issuer or JA4 column visible |

## Please note: do the following before you submit

- [ ] Each TryHackMe screenshot shows the room **completed / 100%** and **your username**. An assignments list is not proof.
- [ ] Capture screenshots show the capture file name, the filter bar and the packet list, with the evidence highlighted.
- [ ] If a lab breaks, tell me **before the deadline** with a screenshot, and document the step number, the commands you ran and what you saw.
- [ ] Each short answer is 100–150 words and about **your own capture or lab**, not a generic description.
- [ ] Crop your Student ID and email from screenshots and headers. One **PDF**, not .docx.
- [ ] AI use disclosed and prompts attached (see below).

## Submission

- One PDF with all screenshots and your answers.
- Short answers: keep each to the length stated; write in your own words and be ready to explain them.
- Late submissions follow the syllabus's 10% deduction policy.
- You may use AI tools to *study* or to explain an error, but anything an AI tells you about a tool or a command is unverified until you have run it (a suggested command that does not work is the lesson). The analysis must come from your own capture. Disclose any AI text and attach your prompts. Do not paste AI output as your answer.
