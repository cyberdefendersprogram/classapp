---
title: Class 4 In-Class Check (Rules, Zeek Logs and Monitoring Architecture)
---

## Q1 [mcq_single, 2pts]

In a Suricata rule, which part is the header and which part is the options?

- [ ] The header is everything in the brackets; the options are the action and protocol
- [x] The header is the action, protocol, addresses, ports and direction; the options in brackets hold the message, content matches and sid
- [ ] The header is the msg field; the options are the content matches
- [ ] A rule has no header, only options

## Q2 [mcq_single, 2pts]

A rule that matches any POST to a URI containing /upload fires on staff uploading a timesheet to the intranet as well as on one host posting a customer file to an unknown outside server. What is the best tuning step?

- [ ] Delete the rule, because it produces false positives
- [ ] Raise the rule's priority so analysts see it first
- [x] Change the header to $HOME_NET -> $EXTERNAL_NET and add flow:established,to_server, then rerun it on known-good and known-bad traffic
- [ ] Add the word "upload" to the message

## Q3 [mcq_single, 2pts]

A beacon rule uses threshold:type threshold, track by_src, count 5, seconds 600. A host beacons only four times in ten minutes. What happens?

- [ ] An alert fires on the fourth request
- [x] No alert fires, which is a false negative that a lower count would have caught
- [ ] The rule is disabled
- [ ] Two alerts fire

## Q4 [mcq_single, 2pts]

The same upload now happens over TLS 1.3 on port 443. Which rule can still alert, and on what?

- [ ] An http.uri rule, on the URI
- [ ] An http.method rule, on POST
- [x] A tls.sni rule, on the server name in the ClientHello
- [ ] None; a sensor cannot see anything in TLS

## Q5 [mcq_single, 2pts]

A rule keyed only on the user agent "python-requests" fires on both a suspect host and a build server polling an internal health API. What does this teach?

- [ ] The rule is perfect because it caught the suspect host
- [x] A user agent is a weak, easily changed indicator that many normal tools share; combine it with direction, destination and behavior
- [ ] User agents cannot be seen in HTTP
- [ ] The build server must be compromised

## Q6 [mcq_single, 2pts]

You have a Suricata alert with a source address, port and time. How do you find everything else Zeek recorded about that session?

- [ ] Search every log for the destination port
- [x] Find the connection in conn.log, take its uid, and read the rows with the same uid in http.log, ssl.log and files.log
- [ ] Open the capture and count packets by hand
- [ ] Run the alert again with a lower threshold

## Q7 [mcq_multi, 3pts]

Which of these would you record when you escalate an alert? (Select all that apply)

- [x] The host, user and time window involved
- [x] What you enriched it with and what you found
- [x] Whether you judge it benign, suspicious or confirmed, and why
- [ ] Only the alert name, since the rest is in the SIEM

## Q8 [mcq_single, 2pts]

What is Sigma?

- [ ] A packet capture format
- [x] A vendor-neutral YAML format for detections over logs, which tools convert into the query language of your SIEM
- [ ] A Suricata plug-in that blocks traffic
- [ ] A Zeek script that decrypts TLS

## Q9 [mcq_single, 2pts]

An AI support agent fetches a web page. Hidden text in the page says to read a customer file and post it to an outside host, and the agent does so. Which detection catches this even if the attacker rewords the hidden instruction?

- [ ] A rule on the phrase "ignore previous instructions" in the fetched page
- [x] A rule on the agent's behavior: a write-type tool such as http_post sending to a host that is not on the approved list
- [ ] A rule on the length of the user's prompt
- [ ] A rule on the agent's model name

## Q10 [mcq_single, 2pts]

In the OPM breach, why could the sensors not reveal the data theft for months?

- [ ] OPM used no network at all
- [x] The stolen data left over encrypted connections that OPM's sensors could not inspect
- [ ] The attackers deleted all logs on day one
- [ ] The traffic used UDP only

## Q11 [mcq_single, 2pts]

Roddie et al. list three ways to judge a good detection. Which set is correct?

- [ ] Price, vendor and license
- [x] How much of the adversary activity it detects, what it costs the defenders to run, and what it costs the adversary to evade it
- [ ] Rule length, number of options and sid number
- [ ] Number of alerts per day, regardless of whether they are true
