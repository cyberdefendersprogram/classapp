---
title: Final Practice (Level 3 and Level 5 style)
links:
  - label: Practice page (downloads and starter commands)
    url: /demos/018-practice-the-final-tls-beacon-and-ai-agent-levels
  - label: Level 3 practice zip
    url: /demos/files/final-practice-level3.zip
  - label: Level 5 practice zip
    url: /demos/files/final-practice-level5.zip
---

## Q1 [numeric, 1pt]

**Level 3 practice ([final-practice-level3.zip](/demos/files/final-practice-level3.zip)).** How many TLS ClientHello packets are in the capture? (Wireshark filter: tls.handshake.type == 1)

answer: 99

## Q2 [numeric, 1pt]

**Level 3 practice ([final-practice-level3.zip](/demos/files/final-practice-level3.zip)).** How many of those ClientHello packets were sent by 10.0.0.15?

answer: 14

## Q3 [short_text, 1pt]

**Level 3 practice ([final-practice-level3.zip](/demos/files/final-practice-level3.zip)).** Threat intelligence says one outside server in this capture is a command-and-control (C2) server. What is its server name (SNI)? (all lower case)

answer: api.metrics-feed.test

## Q4 [short_text, 1pt]

**Level 3 practice ([final-practice-level3.zip](/demos/files/final-practice-level3.zip)).** What is the IP address of the internal host that talks to that server?

answer: 10.0.0.63

## Q5 [numeric, 1pt]

**Level 3 practice ([final-practice-level3.zip](/demos/files/final-practice-level3.zip)).** About how many seconds pass between that host's connections? (round to the nearest 5)

answer: 30

## Q6 [numeric, 1pt]

**Level 3 practice ([final-practice-level3.zip](/demos/files/final-practice-level3.zip)).** How many cipher suites does that host's ClientHello offer?

answer: 5

## Q7 [mcq_multi, 1pt]

**Level 3 practice ([final-practice-level3.zip](/demos/files/final-practice-level3.zip)).** Which of these can a passive sensor on this network still see about that host's connections? (select all that apply)

- [x] The server name (SNI) in the ClientHello
- [x] The certificate's subject and issuer
- [x] The size and timing of each message
- [ ] The contents of the messages
- [ ] The URL path the beacon requests

## Q8 [short_text, 1pt]

**Level 3 practice ([final-practice-level3.zip](/demos/files/final-practice-level3.zip)).** What is the Organization (O) in that server's certificate? (all lower case)

answer: defaultc2

## Q9 [numeric, 1pt]

**Level 5 practice ([final-practice-level5.zip](/demos/files/final-practice-level5.zip)).** Two issues the agent fetched contain instruction-like text, but only one led to a leak. What is the issue number of the one that led to the leak? (digits only)

answer: 2204

## Q10 [mcq_single, 1pt]

**Level 5 practice ([final-practice-level5.zip](/demos/files/final-practice-level5.zip)).** Where in that issue is the hidden instruction?

- [ ] In the issue title
- [x] In an HTML comment in the issue body
- [ ] In a reply comment from another user
- [ ] In the issue labels

## Q11 [short_text, 1pt]

**Level 5 practice ([final-practice-level5.zip](/demos/files/final-practice-level5.zip)).** The unapproved POST begins with a line naming the file it carries. What is the file name? (all lower case)

answer: release-tokens.env

## Q12 [short_text, 1pt]

**Level 5 practice ([final-practice-level5.zip](/demos/files/final-practice-level5.zip)).** What is the Host header (domain) of the POST that went to a destination that is not on the approved list? (all lower case)

answer: drop.tempfile-box.test

## Q13 [numeric, 1pt]

**Level 5 practice ([final-practice-level5.zip](/demos/files/final-practice-level5.zip)).** What is the Content-Length of that POST, in bytes?

answer: 1764

## Q14 [numeric, 1pt]

**Level 5 practice ([final-practice-level5.zip](/demos/files/final-practice-level5.zip)).** The log has two http_post events and does not say where each went. Match them to the capture by time (both use UTC). How many seconds pass between the web_fetch of the issue that led to the leak and the http_post that sent the data out?

answer: 17

## Q15 [mcq_multi, 1pt]

**Level 5 practice ([final-practice-level5.zip](/demos/files/final-practice-level5.zip)).** Which of these controls would have stopped the tokens leaving, even if the attacker reworded the instruction? (select all that apply)

- [x] An allowlist of destinations for the agent's outbound write tool
- [x] Human approval before the agent's http_post runs
- [ ] A longer password on the bot's account
- [ ] Blocking the agent from using TLS
- [ ] Renaming the secrets file

## Q16 [mcq_single, 1pt]

**Level 5 practice ([final-practice-level5.zip](/demos/files/final-practice-level5.zip)).** Which technique best describes what the issue text did?

- [x] Prompt injection (untrusted text steering an AI agent)
- [ ] Training-data poisoning
- [ ] Model theft by repeated queries
- [ ] Adversarial image examples
