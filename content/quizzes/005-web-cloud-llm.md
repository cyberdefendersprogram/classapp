---
title: CIS 55 – Web Attacks, Cloud Security & LLM Quiz
---

## Q1 [mcq_single, 2pts]

According to the OWASP Top 10 (2021), what is the #1 web application security risk?

- [ ] Injection
- [x] Broken Access Control
- [ ] Cryptographic Failures
- [ ] Security Misconfiguration

## Q2 [mcq_single, 2pts]

How does a Stored XSS attack differ from a Reflected XSS attack?

- [ ] Stored XSS only targets server-side code, while Reflected XSS targets clients
- [ ] Stored XSS requires SSL to execute, while Reflected XSS does not
- [x] In Stored XSS, the attacker's malicious script is saved on the server and executed when victims visit the page
- [ ] Stored XSS uses GET requests, while Reflected XSS uses POST requests

## Q3 [mcq_multi, 3pts]

Which of the following are server-side defenses against Cross-Site Request Forgery (CSRF)? (Select all that apply)

- [x] Require all POST requests to contain a pseudo-random token value
- [x] Restrict GET requests to only retrieve data, not modify server state
- [ ] Use SSL/TLS certificates to encrypt all traffic
- [x] Validate that the form value matches the cookie value set by the trusted site

## Q4 [mcq_single, 2pts]

In an XSS attack, what is the primary goal of stealing the victim's session cookie?

- [ ] To modify the web server's database directly
- [ ] To decrypt the victim's HTTPS traffic
- [x] To impersonate the victim and perform actions on the trusted site on their behalf
- [ ] To gain access to the victim's operating system

## Q5 [mcq_single, 2pts]

Why does SSL alone NOT prevent Cross-Site Request Forgery (CSRF) attacks?

- [ ] SSL is too slow to validate CSRF tokens in time
- [ ] SSL only protects data at rest, not data in transit
- [x] Browsers automatically append session information to subsequent requests, so the malicious site can still trigger authenticated actions
- [ ] SSL certificates expire too frequently to provide consistent protection
