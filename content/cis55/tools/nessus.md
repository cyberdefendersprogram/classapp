# Nessus

Nessus is a proprietary vulnerability scanner developed by Tenable. It's one of the most widely used vulnerability assessment tools, capable of scanning for thousands of known vulnerabilities across networks, systems, and applications.

## Overview

Nessus is essential for:
- **Vulnerability Detection**: Find known CVEs and misconfigurations
- **Compliance Auditing**: Check against CIS, PCI-DSS, HIPAA standards
- **Configuration Assessment**: Identify insecure settings
- **Patch Verification**: Confirm security updates are applied

### Installation

Nessus requires a license (free Essentials or paid Professional):

```bash
# Download from Tenable website
# https://www.tenable.com/products/nessus

# Install on Ubuntu/Debian
sudo dpkg -i Nessus-*.deb
sudo systemctl start nessusd

# Access web interface
# https://localhost:8834
```

:::command-builder{id="nessus-builder"}
tool_name: "nessuscli"
target_placeholder: "192.168.1.0/24"
scan_types:
  - name: "Basic Network Scan"
    flag: "scan --template basic"
    desc: "General vulnerability scan"
  - name: "Web App Scan"
    flag: "scan --template webapp"
    desc: "Web application vulnerabilities"
  - name: "Credentialed Scan"
    flag: "scan --template credentialed"
    desc: "Authenticated scan with credentials"
  - name: "Compliance Scan"
    flag: "scan --template compliance"
    desc: "Check against compliance standards"
options:
  - name: "All Ports"
    flag: "--all-ports"
    desc: "Scan all 65535 ports"
  - name: "Safe Checks"
    flag: "--safe"
    desc: "Avoid checks that might crash services"
  - name: "Export PDF"
    flag: "--export pdf"
    desc: "Generate PDF report"
  - name: "Verbose"
    flag: "-v"
    desc: "Verbose output"
:::

## Scan Types

Nessus offers several pre-configured scan templates:

| Template | Purpose | Use Case |
|----------|---------|----------|
| Basic Network Scan | General vulnerability detection | Initial assessment |
| Advanced Scan | Customizable, thorough scan | Detailed testing |
| Web Application Tests | OWASP Top 10, web vulns | Web app testing |
| Credentialed Patch Audit | Check installed patches | Patch management |
| Malware Scan | Detect malware indicators | Incident response |
| PCI-DSS / CIS | Compliance checking | Audit preparation |

---

:::scenario{id="scenario-1" level="beginner"}
title: "Run Your First Vulnerability Scan"
goal: "Create and launch a basic network scan against a target."
hint: "In the Nessus web interface: New Scan > Basic Network Scan > Enter targets > Launch. Start with a single IP to understand the output."
command: "Web UI: New Scan > Basic Network Scan > Targets: 192.168.1.1 > Launch"
expected_output: |
  Scan Status: Running...

  Host Discovery: 1 host found
  Port Scanning: 1000 ports scanned
  Vulnerability Detection: In progress...

  Scan Complete!

  Results Summary:
  - Critical: 2
  - High: 5
  - Medium: 12
  - Low: 8
  - Info: 45
:::

:::scenario{id="scenario-2" level="beginner"}
title: "Analyze Scan Results"
goal: "Understand and prioritize vulnerabilities from scan results."
hint: "Click on a completed scan to view results. Sort by severity (Critical first). Click individual vulnerabilities to see details, affected hosts, and remediation steps."
command: "Web UI: Scans > [Your Scan] > Vulnerabilities tab > Sort by Severity"
expected_output: |
  Vulnerability: MS17-010 (EternalBlue)
  Severity: Critical (CVSS: 9.8)

  Description:
  The remote Windows host is affected by a remote code
  execution vulnerability in SMBv1.

  Affected Hosts: 192.168.1.50
  Port: 445/tcp

  Solution:
  Apply Microsoft security update MS17-010.

  References:
  - CVE-2017-0144
  - https://docs.microsoft.com/en-us/security-updates/
:::

:::scenario{id="scenario-3" level="beginner"}
title: "Generate a Vulnerability Report"
goal: "Export scan results as a professional PDF report."
hint: "After a scan completes, use the Export feature to generate reports. Choose the format and detail level appropriate for your audience."
command: "Web UI: Scans > [Your Scan] > Export > PDF > Executive Summary"
expected_output: |
  Export Settings:
  - Format: PDF
  - Report Type: Executive Summary
  - Include: Remediation steps, CVSS scores

  Generating report...

  Report Generated: scan_report_2024-01-15.pdf

  Contents:
  1. Executive Summary
  2. Vulnerability Overview (by severity)
  3. Affected Hosts
  4. Remediation Recommendations
  5. Technical Details
:::

:::scenario{id="scenario-4" level="intermediate"}
title: "Run a Credentialed Scan"
goal: "Perform an authenticated scan to detect more vulnerabilities."
hint: "Credentialed scans can detect missing patches and misconfigurations that unauthenticated scans miss. Add SSH or Windows credentials in the scan settings."
command: "Web UI: New Scan > Credentialed Patch Audit > Credentials > Add SSH/Windows credentials"
expected_output: |
  Credentialed Scan Results:

  Authentication Status: Success
  - SSH Login: Successful (192.168.1.10)
  - Privilege Level: root

  Additional Findings (vs uncredentialed):
  - Missing patches: 15 additional found
  - Local vulnerabilities: 8 additional found
  - Configuration issues: 12 additional found

  Total Vulnerabilities:
  - Uncredentialed: 25
  - Credentialed: 60 (+35 findings)
:::

:::scenario{id="scenario-5" level="intermediate"}
title: "Create a Custom Scan Policy"
goal: "Build a tailored scan policy for specific testing needs."
hint: "Custom policies let you enable/disable specific plugins, set port ranges, and tune scan intensity. Save policies for reuse across multiple scans."
command: "Web UI: Policies > New Policy > Advanced Scan > Customize plugins and settings"
expected_output: |
  Custom Policy: Web Server Assessment

  Settings:
  - Port Range: 80, 443, 8080, 8443
  - Plugin Families Enabled:
    * Web Servers (245 plugins)
    * CGI abuses (1,203 plugins)
    * SSL/TLS (89 plugins)
  - Plugin Families Disabled:
    * Windows (saves time)
    * Databases (not in scope)

  Scan Intensity:
  - Network timeout: 5 seconds
  - Max concurrent hosts: 10
  - Max concurrent plugins: 5

  Policy saved successfully!
:::

## Tips & Tricks

### Scan Performance

Optimize scans for speed and accuracy:

```
# Reduce scan time
- Limit port range to relevant ports
- Disable plugin families not needed
- Increase concurrent host/plugin limits (carefully)

# Improve accuracy
- Use credentialed scans when possible
- Enable safe checks to avoid false positives
- Schedule scans during low-traffic periods
```

### Credential Management

```
# Supported authentication methods
- SSH (password or key-based)
- Windows (SMB, WMI)
- SNMP (v1, v2c, v3)
- Database (Oracle, SQL Server, MySQL)
- VMware ESXi/vCenter
- Cisco devices
```

### Plugin Management

```
# Update plugins regularly
nessuscli update --plugins-only

# Check plugin status
nessuscli scan --info

# Plugin families include:
- Backdoors
- CGI abuses
- Denial of Service
- Firewalls
- General
- Misc
- Port scanners
- SCADA
- Service detection
- Web Servers
- Windows
```

### Scheduling and Automation

```
# Schedule recurring scans
Web UI: Scans > New Scan > Schedule > Weekly

# API automation (with API keys)
curl -k -X POST \
  "https://localhost:8834/scans/launch" \
  -H "X-ApiKeys: accessKey=xxx;secretKey=yyy" \
  -d "scan_id=123"
```

---

:::quiz{id="quiz-1"}
Q: What is the main advantage of a credentialed scan over an uncredentialed scan?
- [ ] It runs faster
- [x] It can detect more vulnerabilities including missing patches
- [ ] It doesn't require network access
- [ ] It only scans web applications
:::

:::quiz{id="quiz-2"}
Q: Which Nessus scan template would you use to check against security standards like PCI-DSS?
- [ ] Basic Network Scan
- [ ] Web Application Tests
- [x] Compliance Scan
- [ ] Malware Scan
:::

:::quiz{id="quiz-3"}
Q: What does the "Safe Checks" option do in Nessus?
- [x] Avoids tests that might crash or disrupt services
- [ ] Encrypts the scan traffic
- [ ] Only scans during business hours
- [ ] Limits the number of vulnerabilities reported
:::

## Quick Reference

| Action | How To |
|--------|--------|
| Start Nessus | `sudo systemctl start nessusd` |
| Access Web UI | `https://localhost:8834` |
| Update Plugins | `nessuscli update --plugins-only` |
| New Scan | Web UI > Scans > New Scan |
| Add Credentials | Scan Settings > Credentials |
| Export Report | Scan Results > Export > PDF/CSV/HTML |
| Create Policy | Policies > New Policy |
| Schedule Scan | New Scan > Schedule tab |
| View Plugin Info | Settings > Plugins |
| Check License | `nessuscli fetch --check` |

## Severity Ratings

| Severity | CVSS Score | Action |
|----------|------------|--------|
| Critical | 9.0 - 10.0 | Immediate remediation |
| High | 7.0 - 8.9 | Remediate within days |
| Medium | 4.0 - 6.9 | Remediate within weeks |
| Low | 0.1 - 3.9 | Remediate when possible |
| Info | 0.0 | No action required |
