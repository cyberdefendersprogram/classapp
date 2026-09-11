# OWASP ZAP

OWASP Zed Attack Proxy (ZAP) is a free, open-source web application and API security scanner. It sits as a proxy between a client and a target, letting you intercept, replay, and fuzz requests, and it ships automated scanners for the exact issue classes on this week's OWASP API Security Top 10 reading — broken authorization, injection, and misconfiguration.

## Overview

ZAP is essential for:
- **API Authorization Testing**: Replay a request with a different object ID or a different user's token to probe for Broken Object Level Authorization (API1)
- **Automated Scanning**: Passive scanning flags issues just from observed traffic; active scanning sends crafted requests to find more
- **SSRF and Injection Probes**: Fuzz parameters that accept URLs or file paths — the exact input class behind the Capital One-style SSRF
- **Misconfiguration Checks**: Flags missing security headers, verbose error messages, and permissive CORS (API8)

### Installation

```bash
# Docker (recommended for class use — no local Java setup needed)
docker pull zaproxy/zap-stable

# Run the baseline scan against a target
docker run -t zaproxy/zap-stable zap-baseline.py -t https://target.example.com

# Or install the desktop app from zaproxy.org for interactive proxy use
```

:::command-builder{id="zap-builder"}
tool_name: zap-baseline.py
target_placeholder: "https://api.target.example.com"
scan_types:
  - name: "Baseline Scan"
    flag: "zap-baseline.py"
    desc: "Passive scan only — safe against production, spiders and observes traffic"
  - name: "Full Scan"
    flag: "zap-full-scan.py"
    desc: "Passive + active scan — sends attack payloads, authorized test targets only"
  - name: "API Scan"
    flag: "zap-api-scan.py"
    desc: "Scan a target using its OpenAPI/GraphQL/SOAP definition"
options:
  - name: "Target"
    flag: "-t"
    desc: "Target URL or API definition URL"
  - name: "Report Format"
    flag: "-r"
    desc: "Write an HTML report to this filename"
  - name: "Auth Header"
    flag: "-z \"-config replacer.full_list...\""
    desc: "Inject an Authorization header for authenticated scanning"
  - name: "Fail on Risk"
    flag: "-l"
    desc: "Minimum alert level that causes a non-zero exit code: PASS, WARN, FAIL"
:::

## Basic Syntax

```
zap-baseline.py -t <target-url> -r report.html
zap-api-scan.py -t <openapi-spec-url> -f openapi -r report.html
zap-full-scan.py -t <target-url> -r report.html
```

**Authorized targets only** — as with every tool in this course, only scan instructor-approved lab environments or systems you own. Active scans send real attack payloads.

---

:::scenario{id="scenario-1" level="beginner"}
title: "Baseline Scan an API for Misconfiguration"
goal: "Run a safe, passive scan and read the alert summary for API8-class misconfiguration findings."
hint: "Baseline scans only observe traffic ZAP generates by spidering the site — they don't send attack payloads, so they're safe to run against a lab target without asking permission first."
command: "docker run -t zaproxy/zap-stable zap-baseline.py -t https://lab-api.example.com -r baseline-report.html"
expected_output: |
  ZAP is spidering the target...
  Found 14 URLs

  PASS: X-Content-Type-Options Header Missing (0)
  WARN-NEW: Missing Anti-clickjacking Header (3)
  WARN-NEW: CORS misconfiguration — Access-Control-Allow-Origin: * with credentials allowed (1)
  WARN-NEW: Server Leaks Version Information via 'Server' HTTP Response Header (7)

  FAIL-NEW: 0  FAIL-INPROG: 0  WARN-NEW: 3  WARN-INPROG: 0  INFO: 2  IGNORE: 0  PASS: 41
  Report written to baseline-report.html
:::

:::scenario{id="scenario-2" level="intermediate"}
title: "Probe for Broken Object Level Authorization"
goal: "Manually replay an authenticated API request with a different object ID to test for API1 — the same pattern as the Lab 2 Eve exercise, applied to an API instead of S3."
hint: "Use the ZAP desktop proxy (or docker with -z to inject headers) to capture one authenticated request, then replay it in the Manual Request Editor with only the object ID changed. A 200 response where you expected a 403 is the finding."
command: "# In ZAP desktop: right-click a captured GET /orders/1042 request -> Open/Resend with Request Editor -> change to GET /orders/1043 -> Send"
expected_output: |
  Original request (your own order):
  GET /orders/1042 HTTP/1.1
  Authorization: Bearer <your-token>
  -> 200 OK { "order_id": 1042, "owner": "you", ... }

  Replayed request (someone else's order, same token):
  GET /orders/1043 HTTP/1.1
  Authorization: Bearer <your-token>
  -> 200 OK { "order_id": 1043, "owner": "another-student", ... }

  Finding: API1 — Broken Object Level Authorization. The API authenticates
  the request but never checks that order 1043 belongs to the caller.
:::

---

## Connecting Back to This Week

ZAP's passive scanner catches the "everything else" bucket — API8 misconfiguration — automatically. Its manual replay workflow is how you actually prove API1 (Broken Object Level Authorization) and probe for API7 (SSRF) the same way Lab 2 asked you to prove an IAM deny with a screenshot, not just claim it works: run the request, show the response, and reason about why it succeeded or failed.
