---
title: Class 3 In-Class Check (Application Protocols and Encrypted Traffic)
---

## Q1 [mcq_single, 2pts]

Which DNS display filter finds queries that are unusually long, a common sign of tunneling?

- [ ] dns.flags.rcode == 3
- [x] dns.qry.name.len > 50
- [ ] dns.resp.ttl < 60
- [ ] dns.count.answers == 0

## Q2 [mcq_single, 2pts]

One host sends 45 queries for random 11 to 15 letter names, and 44 of them return NXDOMAIN. What is the most likely explanation?

- [ ] A fast-flux network rotating addresses
- [ ] A normal browser warming its cache
- [x] Malware using a domain generation algorithm (DGA) to find its command server
- [ ] A DNS amplification attack against the resolver

## Q3 [mcq_single, 2pts]

In Bejtlich's client-side compromise (Ch. 11), what first made the analyst suspect DNS was being abused?

- [ ] An antivirus alert on the victim laptop
- [x] The dns.log file was far larger than expected, full of NULL queries with random-looking labels under one domain
- [ ] A user reported a slow network
- [ ] The resolver ran out of memory

## Q4 [mcq_single, 2pts]

A server answers a request for /docs/invoice.jpg with Content-Type: image/jpeg, but the body starts with the bytes MZ. What do you conclude, and what do you do next?

- [ ] Nothing; the Content-Type header is authoritative
- [x] The file is probably a Windows program disguised as an image; export it, hash it with SHA-256, and check the hash against intelligence sources
- [ ] The server is down
- [ ] The file is encrypted, so you cannot learn anything

## Q5 [mcq_multi, 3pts]

Which are signs of an HTTP beacon? (Select all that apply)

- [x] POST requests to the same URI at a fixed interval
- [x] A user agent that does not match the host's other browser traffic
- [ ] One large file download that completes in seconds
- [x] Small, similar-sized request bodies, with the response carrying instructions

## Q6 [mcq_multi, 3pts]

Which can a sensor still see when a session uses TLS 1.3 with no decryption? (Select all that apply)

- [x] The server name in the SNI field
- [x] Bytes sent and received, and timing
- [x] A JA3 or JA4 fingerprint of the client
- [ ] The URL path and request headers

## Q7 [mcq_single, 2pts]

Why can you read the server certificate in a TLS 1.2 session but not in a TLS 1.3 session?

- [ ] TLS 1.3 does not use certificates
- [ ] Certificates are only sent for HTTP
- [x] TLS 1.3 encrypts the certificate, so a passive sensor no longer sees it
- [ ] Wireshark cannot parse TLS 1.3

## Q8 [mcq_single, 2pts]

Two different destinations show the same JA4 fingerprint from the same laptop. What does the fingerprint tell you?

- [ ] That both destinations are run by the same company
- [x] That the same client software built both handshakes, regardless of where it connected
- [ ] That the traffic is malicious
- [ ] That the sessions carried identical data

## Q9 [mcq_single, 2pts]

A host sends about 665 kB to an unfamiliar AI service and receives about 4 kB back. A scripted app on another host sends about 3 kB and receives about 13 kB on a regular schedule to an approved AI API. Which is the better lead for possible data egress, and why?

- [ ] The scripted app, because it is regular
- [x] The first host, because a large upload with a tiny reply is the opposite of normal chat use; confirm it against the approved-service list and who owns the host
- [ ] Neither; encrypted traffic cannot be analyzed
- [ ] Both are identical

## Q10 [mcq_single, 2pts]

In the vsftpd backdoor investigation, why is it significant that port 6200 refused connections during the scan but accepted one right after a login attempt with a username ending in ":)"?

- [ ] It proves the attacker used a firewall rule
- [x] A port that begins listening immediately after a login attempt shows the backdoor was triggered, even if no signature fired
- [ ] Port 6200 is the standard FTP data port
- [ ] It shows the server was rebooted
