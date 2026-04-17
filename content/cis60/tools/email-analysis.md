# Email Header Analysis

Email forensics focuses on the metadata stored in message headers: sender and recipient fields, relay path, timestamps, authentication results, and unique identifiers like `Message-ID`. This lab mirrors the GUI workflow from Thunderbird and adds explicit Linux/Kali methods for saving, extracting, and parsing headers offline.

## Overview

Email headers can answer questions such as:

- **Who sent the message** — `From`, `Return-Path`, and `Message-ID`
- **Who received it** — `To`, `Cc`, `Delivered-To`
- **When it moved** — `Date` and each `Received` timestamp
- **Which servers handled it** — relay hostnames and IP addresses in the `Received` chain
- **Whether it was authenticated** — `SPF`, `DKIM`, `ARC`, and `Authentication-Results`
- **Whether it was replied to or forwarded** — `In-Reply-To` and `References`

Headers should be read **from the bottom up**. Each mail server prepends its own `Received` line to the top, so the oldest transmission data is closest to the message body.

---

## Tool Comparison

| Task | Windows / GUI | Linux / Kali |
|------|---------------|--------------|
| Open mailbox | Thunderbird / Outlook | Thunderbird |
| View raw source | `More > View Source` | Thunderbird `More > View Source` |
| Save raw header/source | Save as `.txt` from source window | Save as `.txt`, or extract from `.eml` with `awk` / `sed` |
| Search key header fields | Notepad / text editor find | `grep -E`, `less`, `awk` |
| Parse header offline | Email Header Analyzer in browser | Email Header Analyzer via local `python3 server.py -d` |
| Quick triage of routing/auth | Visual review of `Received`, SPF, DKIM | `grep -n "^(Received|Message-ID|Authentication-Results|DKIM-Signature|ARC-|In-Reply-To|References):"` |

---

## Important Header Fields

| Field | What it tells you | Forensic value |
|------|--------------------|----------------|
| `From` | Claimed sender address | User-visible sender identity |
| `To` / `Cc` | Recipient list | Intended recipients |
| `Date` | Sender-side send time | Timeline anchor |
| `Message-ID` | Unique message identifier | Helps prove the message existed and trace the sending domain |
| `Received` | Each server hop | Relay path, timestamps, and sometimes sender IP |
| `Return-Path` | Bounce address | May differ from visible sender |
| `Authentication-Results` | SPF/DKIM/DMARC result summary | Spoofing/tampering detection |
| `DKIM-Signature` | Domain signing metadata | Integrity/authenticity evidence |
| `ARC-*` | Authenticated Received Chain | Preserved auth results across forwarding |
| `In-Reply-To` / `References` | Prior `Message-ID` values | Shows reply/forward relationships |

---

:::command-builder{id="email-header-builder"}
tool_name: grep
target_placeholder: "message.eml"
scan_types:
  - name: "Key Routing Fields"
    flag: "-E '^(Received|Message-ID|Return-Path|Date):' message.eml"
    desc: "Show transmission path, unique ID, return path, and sent date"
  - name: "Auth Fields"
    flag: "-E '^(Authentication-Results|DKIM-Signature|ARC-|Received-SPF):' message.eml"
    desc: "Surface SPF, DKIM, ARC, and related authentication metadata"
  - name: "Conversation Fields"
    flag: "-E '^(From|To|Cc|Subject|In-Reply-To|References):' message.eml"
    desc: "Show the visible sender/recipient/conversation metadata"
  - name: "Only Header Section"
    flag: "-n '^$' message.eml"
    desc: "Find the blank line that separates the header from the body"
options:
  - name: "Show line numbers"
    flag: "-n"
    desc: "Helpful when citing offsets/locations in the source file"
  - name: "Ignore case"
    flag: "-i"
    desc: "Useful when field capitalization varies"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Open the Message and View the Raw Header"
goal: "Open an email in Thunderbird and display the full message source so the raw header can be examined."
hint: "In Thunderbird, open the inbox, double-click the target email so it gets its own tab, then use `More > View Source`. On Kali or CAINE, this is the same Thunderbird workflow. The source window shows both header and body, with the header ending at the first blank line."
command: "thunderbird  OR  Thunderbird GUI: More > View Source"
expected_output: |
  Thunderbird source window:
    Return-Path: <sender@mail.com>
    Received: from 174.128.225.186 by web-mail.mail.com ...
    Message-ID: <abc123xyz@mail.com>
    Date: Tue, 04 Oct 2022 14:23:18 +0000
    Subject: The deadline
    From: Example Sender <sender@mail.com>
    To: recipient@gmail.com

    [blank line]
    Email body begins here...

  Key observation:
    Everything above the first blank line is header metadata.
    Everything below it is the message body.
:::

:::scenario{id="task-2" level="beginner"}
title: "Task 2 — Save the Header to a Forensic Working Folder"
goal: "Preserve the raw source or header as a text file so it can be reviewed without reopening the mail client."
hint: "The lab saves the message source from Thunderbird into a working folder named for the lab. On Kali, you can either save from the GUI or export from an `.eml` file with shell tools. Preserve the original content exactly before making notes or excerpts."
command: "mkdir -p ~/Desktop/Working\\ Folder/FOR_LAB_012 && awk 'BEGIN{h=1} h{print} /^$/{exit}' message.eml > ~/Desktop/Working\\ Folder/FOR_LAB_012/the-deadline-header.txt"
expected_output: |
  Linux / Kali:
    mkdir -p ~/Desktop/Working\ Folder/FOR_LAB_012
    awk 'BEGIN{h=1} h{print} /^$/{exit}' message.eml > ~/Desktop/Working\ Folder/FOR_LAB_012/the-deadline-header.txt

    ls -l ~/Desktop/Working\ Folder/FOR_LAB_012/
    -rw-r--r-- 1 kali kali 6.2K the-deadline-header.txt

  Thunderbird GUI:
    File > Save Page As
    Save to: Desktop > Working Folder > FOR_LAB_012
    Filename: The deadline.txt
:::

:::scenario{id="task-3" level="beginner"}
title: "Task 3 — Read the Header from Bottom to Top"
goal: "Identify the original sending details, key user-visible metadata, and the earliest transmission entry."
hint: "Start at the bottom of the header because each mail server adds its own `Received` line to the top. Near the bottom you will usually find the visible metadata (`From`, `To`, `Subject`, `Date`), then `Message-ID`, then the earliest `Received` entry. That earliest relay can contain the sender IP address."
command: "less ~/Desktop/Working\\ Folder/FOR_LAB_012/the-deadline-header.txt"
expected_output: |
  Typical bottom-up reading order:
    [message body]
    From: Example Sender <sender@mail.com>
    To: recipient@gmail.com
    Subject: The deadline
    Date: Tue, 04 Oct 2022 14:23:18 +0000
    Message-ID: <abc123xyz@mail.com>
    Received: from 174.128.225.186 by web-mail.mail.com ...

  Evidence you can pull from this section:
    Sender address and recipient
    Subject and send time
    Unique Message-ID
    Earliest relay path and possible sender IP
:::

:::scenario{id="task-4" level="intermediate"}
title: "Task 4 — Extract Routing and Authentication Fields on Kali"
goal: "Use command-line tools to isolate the routing chain and authentication results from a raw email file."
hint: "This is the Kali equivalent of visually hunting through the source window. `grep` is fast for key fields, while `awk` can stop at the blank line so you only process the header. Focus on `Received`, `Message-ID`, `Authentication-Results`, `DKIM-Signature`, `ARC-*`, `In-Reply-To`, and `References`."
command: "grep -E '^(Received|Message-ID|Authentication-Results|DKIM-Signature|ARC-|In-Reply-To|References|Return-Path):' message.eml"
expected_output: |
  Example Kali output:
    Return-Path: <sender@mail.com>
    Received: from 174.128.225.186 by web-mail.mail.com ...
    Received: from mout-xforward.gmx.com by mx.google.com ...
    Authentication-Results: mx.google.com; spf=pass ... dkim=pass ... dmarc=pass
    DKIM-Signature: v=1; a=rsa-sha256; d=mail.com; ...
    ARC-Authentication-Results: i=1; mx.google.com; dkim=pass ...
    Message-ID: <abc123xyz@mail.com>

  If the message is a reply or forward:
    In-Reply-To: <older-message-id@example.com>
    References: <older-message-id@example.com>

  Interpretation:
    Multiple Received lines = multiple relay hops
    SPF/DKIM/ARC pass = stronger authenticity signal
    In-Reply-To / References = message belongs to an existing thread
:::

:::scenario{id="task-5" level="intermediate"}
title: "Task 5 — Parse the Header with Email Header Analyzer"
goal: "Run Email Header Analyzer locally, paste the header, and review the parsed results offline."
hint: "The lab uses the offline Email Header Analyzer project. On Kali/CAINE, start the local Python server, open Firefox to `http://127.0.0.1:8080`, paste the full header, and click `Analyze This!`. This is preferred over public web parsers because the header may contain sensitive case data."
command: "cd ~/Desktop/email-header-analyzer-master/mha/ && python3 server.py -d"
expected_output: |
  Terminal:
    cd ~/Desktop/email-header-analyzer-master/mha/
    python3 server.py -d
    Serving on http://127.0.0.1:8080

  Browser workflow:
    Open Firefox
    Browse to: http://127.0.0.1:8080
    Paste the full header into the text box
    Click: Analyze This!

  Parsed output highlights:
    Sending IP and relay servers
    SPF / DKIM / ARC evaluation
    Message-ID
    Subject / sender / recipient fields
    In-Reply-To and References when present
:::

---

## Full Kali Workflow

End-to-end header extraction and offline parsing:

```bash
# 1. Create a case folder
mkdir -p ~/cases/FOR_LAB_012

# 2. Hash the original email file
sha256sum message.eml > ~/cases/FOR_LAB_012/message.eml.sha256

# 3. Extract just the header (stop at the first blank line)
awk 'BEGIN{h=1} h{print} /^$/{exit}' message.eml \
  > ~/cases/FOR_LAB_012/message-header.txt

# 4. Review the visible metadata and routing/auth fields
grep -E '^(From|To|Cc|Subject|Date|Message-ID|Return-Path):' \
  ~/cases/FOR_LAB_012/message-header.txt

grep -E '^(Received|Authentication-Results|DKIM-Signature|ARC-|In-Reply-To|References):' \
  ~/cases/FOR_LAB_012/message-header.txt

# 5. Read it bottom-up in a pager
less ~/cases/FOR_LAB_012/message-header.txt

# 6. Start Email Header Analyzer locally
cd ~/Desktop/email-header-analyzer-master/mha/
python3 server.py -d

# 7. Open Firefox and browse to the local analyzer
firefox http://127.0.0.1:8080
```

---

## Key Concepts

### Why Read Email Headers Bottom-Up

Each mail transfer agent prepends a new `Received` line to the top of the header. That means:

- The **top** shows the most recent delivery steps
- The **bottom** shows the oldest transmission data
- The earliest relay often contains the most useful origin details

### Message-ID, In-Reply-To, and References

These three fields help reconstruct conversations:

| Field | Purpose |
|------|---------|
| `Message-ID` | Unique identifier for this message |
| `In-Reply-To` | Points to the message being answered |
| `References` | Lists prior message IDs in the thread |

If `In-Reply-To` and `References` are missing, the message is more likely an original composition rather than a reply or forward.

### SPF, DKIM, and ARC

| Mechanism | Purpose |
|----------|---------|
| SPF | Checks whether the sending server is authorized for the domain |
| DKIM | Verifies a cryptographic signature added by the sender's domain |
| ARC | Preserves authentication results across forwarding hops |

`pass` results strengthen authenticity, but they do not automatically prove the sender personally authored the message. They only show the message passed technical checks for the stated infrastructure.

### Why Offline Parsing Matters

Online header analyzers are convenient, but they can expose:

- Sender and recipient addresses
- Internal relay hostnames
- Message identifiers
- Possible case-sensitive timestamps and infrastructure details

For investigations, prefer local tools like Email Header Analyzer running on `127.0.0.1`.

---

:::quiz{id="quiz-1"}
Q: Why should an examiner usually read an email header from the bottom upward?
- [ ] The message body is always stored above the header
- [x] Each server adds new routing information to the top, so the oldest data is near the bottom
- [ ] DKIM signatures only appear at the bottom
- [ ] Thunderbird displays the newest data at the bottom by default
:::

:::quiz{id="quiz-2"}
Q: Which field is most useful for uniquely identifying a specific email message?
- [ ] Subject
- [ ] To
- [x] Message-ID
- [ ] Cc
:::

:::quiz{id="quiz-3"}
Q: Which header fields usually indicate that a message is a reply or forward rather than a brand-new composition?
- [ ] Return-Path and Date
- [ ] SPF and DKIM
- [x] In-Reply-To and References
- [ ] ARC and MIME-Version
:::

:::quiz{id="quiz-4"}
Q: What does a `Received` header line primarily document?
- [ ] The attachment names in the message
- [x] A server hop in the message's delivery path
- [ ] The sender's typed display name
- [ ] The body encoding method only
:::

:::quiz{id="quiz-5"}
Q: Why is a local/offline parser preferred over a public website for forensic email analysis?
- [ ] Public sites cannot parse DKIM signatures
- [ ] Local tools are always faster
- [x] Uploading headers to public services may expose sensitive investigation data
- [ ] Thunderbird cannot export headers directly
:::

:::quiz{id="quiz-6"}
Q: Which Linux command cleanly extracts only the header section from an `.eml` file?
- [ ] `tail -n 20 message.eml`
- [ ] `strings message.eml`
- [x] `awk 'BEGIN{h=1} h{print} /^$/{exit}' message.eml`
- [ ] `chmod +x message.eml`
:::

---

## Quick Reference

| Task | Linux / Kali | Windows / GUI |
|------|--------------|---------------|
| Open email | `thunderbird` | Thunderbird / Outlook |
| View raw source | Thunderbird `More > View Source` | Thunderbird `More > View Source` |
| Save source/header | `awk ... > header.txt` | `File > Save Page As` |
| Find visible metadata | `grep -E '^(From|To|Subject|Date):' message.eml` | Search in source window / Notepad |
| Find routing path | `grep '^Received:' message.eml` | Search `Received:` in source window |
| Find auth results | `grep -E '^(Authentication-Results|DKIM-Signature|ARC-|Received-SPF):' message.eml` | Search same fields in source window |
| Start local parser | `python3 server.py -d` | Same if Email Header Analyzer is installed |
| Open parser UI | `firefox http://127.0.0.1:8080` | Browser to `http://127.0.0.1:8080` |
