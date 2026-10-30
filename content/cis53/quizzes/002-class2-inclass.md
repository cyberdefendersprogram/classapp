---
title: Class 2 In-Class Check (Reading Traffic)
---

## Q1 [mcq_single, 2pts]

Which kind of filter changes what is saved to the capture file?

- [x] A capture filter (BPF)
- [ ] A display filter
- [ ] Both, equally
- [ ] Neither; Wireshark saves everything

## Q2 [mcq_single, 2pts]

Which is a capture (BPF) filter for DNS traffic to or from host 10.0.0.5?

- [ ] ip.addr == 10.0.0.5 && dns
- [x] host 10.0.0.5 and port 53
- [ ] dns.host == 10.0.0.5
- [ ] src 10.0.0.5 dns

## Q3 [mcq_single, 2pts]

Which Wireshark display filter finds the first packet of a TCP handshake (SYN, no ACK)?

- [ ] tcp.flags == 0x12
- [ ] tcp.flags.reset == 1
- [x] tcp.flags.syn == 1 && tcp.flags.ack == 0
- [ ] tcp.analysis.retransmission

## Q4 [mcq_single, 2pts]

In `tcpdump -n -i en0 -c 100`, what does `-n` do?

- [ ] Shows only new connections
- [x] Does not resolve addresses to names, so you do not wait on DNS lookups
- [ ] Captures only network-layer headers
- [ ] Numbers the packets

## Q5 [mcq_single, 2pts]

Bejtlich recommends capturing with a minimal tool such as dumpcap and analyzing the saved file afterwards. Why?

- [ ] Dumpcap decodes more protocols than Wireshark
- [x] Protocol dissectors can contain vulnerabilities, so you avoid running them with high privileges on a live sensor
- [ ] Saved files cannot be modified
- [ ] Wireshark cannot read live traffic

## Q6 [mcq_single, 2pts]

You send a SYN to a port and receive RST,ACK back. What does that most likely mean?

- [ ] The host is down
- [ ] A firewall silently dropped the packet
- [x] The host is reachable and nothing is listening on that port
- [ ] The connection was established

## Q7 [mcq_multi, 3pts]

Which are typical signs of beaconing? (Select all that apply)

- [x] The same destination contacted at regular intervals
- [x] Requests and responses of similar size each time
- [ ] One huge download that finishes in a minute
- [ ] A one-time DNS lookup that is never followed by a connection

## Q8 [mcq_single, 2pts]

In the Mitnick attack, why did the predictable initial sequence numbers matter?

- [ ] They let the attacker decrypt the session
- [x] The attacker could forge the final ACK of a handshake without ever seeing the target's reply
- [ ] They disabled the target's firewall
- [ ] They allowed the SYN flood to succeed

## Q9 [mcq_single, 2pts]

What was the SYN flood against the trusted server for?

- [ ] To steal files from the server
- [ ] To fill the target's disk
- [x] To keep the server from answering (and resetting) the forged connection made in its name
- [ ] To measure the target's sequence numbers

## Q10 [mcq_single, 2pts]

A host holds one long HTTPS connection to an AI provider's API, with a small request and a long streamed response. What do you do first?

- [ ] Block it as command and control
- [ ] Ignore it because it is encrypted
- [x] Check the destination and the process against approved services before deciding; streaming can look like C2 but is a common false positive
- [ ] Delete the capture file
