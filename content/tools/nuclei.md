# Nuclei

Nuclei is a fast, template-based vulnerability scanner by ProjectDiscovery. It uses YAML-based templates to send targeted requests, enabling rapid detection of CVEs, misconfigurations, exposed services, and default credentials across web applications and infrastructure.

## Overview

Nuclei is essential for:
- **CVE Detection**: Scan for thousands of known vulnerabilities using community templates
- **Misconfiguration Auditing**: Find exposed admin panels, default credentials, and insecure settings
- **Exposure Discovery**: Locate sensitive files, backup archives, and unintended endpoints
- **Technology Fingerprinting**: Identify software versions and underlying technology stacks

### Installation

Nuclei is available via Go, Homebrew, or pre-built binaries:

```bash
# Go (recommended — always gets latest)
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# macOS
brew install nuclei

# Update templates after install (required before first scan)
nuclei -update-templates
```

:::command-builder{id="nuclei-builder"}
tool_name: nuclei
target_placeholder: "https://example.com"
scan_types:
  - name: "Single URL"
    flag: "-u"
    desc: "Scan a single target URL"
  - name: "URL List"
    flag: "-l"
    desc: "Scan a list of targets from a file"
  - name: "By Tags"
    flag: "-tags"
    desc: "Run templates matching a tag (cve, misconfig, exposure)"
  - name: "By Severity"
    flag: "-severity"
    desc: "Run templates of a specific severity level"
options:
  - name: "Output File"
    flag: "-o"
    desc: "Save results to a file"
  - name: "JSON Output"
    flag: "-json"
    desc: "Output results in JSON format"
  - name: "Rate Limit"
    flag: "-rate-limit"
    desc: "Max requests per second (default: 150)"
  - name: "Concurrency"
    flag: "-c"
    desc: "Number of concurrent template executions"
:::

## Basic Syntax

The basic Nuclei command structure is:

```
nuclei -u [target] [options]
nuclei -l [targets-file] [options]
```

**Target formats:**
- Single URL: `https://example.com`
- URL list file: `-l urls.txt`
- CIDR range (with `-target`): `192.168.1.0/24`

**Template selection:**
- All default templates: *(no flag — runs recommended set)*
- By tag: `-tags cve,misconfig`
- By severity: `-severity critical,high`
- Specific template: `-t http/cves/2021/CVE-2021-44228.yaml`
- Template directory: `-t /path/to/templates/`

---

:::scenario{id="scenario-1" level="beginner"}
title: "Run Your First Nuclei Scan"
goal: "Scan a target URL using the default recommended templates."
hint: "Running nuclei without specifying templates uses the built-in recommended set, which covers high-signal CVEs and misconfigurations. Always update templates first with -update-templates."
command: "nuclei -u https://testphp.vulnweb.com"
expected_output: |
  [INF] Current nuclei version: v3.1.0
  [INF] Current nuclei-templates version: v9.6.4
  [INF] Loaded 4532 templates

  [CVE-2018-10517] [http] [medium] https://testphp.vulnweb.com/search.php?test=query
  [apache-detect] [http] [info] https://testphp.vulnweb.com [Apache/2.4.7 (Ubuntu)]
  [php-detect] [http] [info] https://testphp.vulnweb.com [PHP/5.5.9-1]
  [http-missing-security-headers] [http] [info] https://testphp.vulnweb.com

  [INF] Templates executed: 4532 | Matched: 4 | Skipped: 0
:::

:::scenario{id="scenario-2" level="beginner"}
title: "Scan for Critical and High CVEs"
goal: "Focus the scan on templates that detect critical and high severity vulnerabilities."
hint: "Use -severity to filter by severity level. Combine with -tags cve to only run CVE-detection templates. This is faster than running all templates and targets the most impactful findings."
command: "nuclei -u https://target.example.com -tags cve -severity critical,high"
expected_output: |
  [INF] Loaded 1243 templates (filtered by: tags=cve, severity=critical,high)

  [CVE-2021-44228] [http] [critical] https://target.example.com/api/login
    [info] Matched: Log4j JNDI RCE - CVE-2021-44228

  [CVE-2022-22965] [http] [critical] https://target.example.com/
    [info] Spring4Shell - Remote Code Execution

  [INF] Templates executed: 1243 | Matched: 2 | Skipped: 0
:::

:::scenario{id="scenario-3" level="beginner"}
title: "Find Exposed Admin Panels and Default Credentials"
goal: "Discover unprotected admin interfaces and systems using default passwords."
hint: "The 'default-logins' and 'exposed-panels' tags target common admin UIs and weak credentials. These are high-value findings in real assessments."
command: "nuclei -u https://target.example.com -tags default-logins,exposed-panels"
expected_output: |
  [INF] Loaded 312 templates (filtered by: tags=default-logins,exposed-panels)

  [tomcat-manager-panel] [http] [info] https://target.example.com:8080/manager/html
  [tomcat-default-login] [http] [high] https://target.example.com:8080/manager/html
    [info] Default credentials found: tomcat:tomcat

  [phpmyadmin-panel] [http] [info] https://target.example.com/phpmyadmin/
  [phpmyadmin-default-login] [http] [high] https://target.example.com/phpmyadmin/
    [info] Default credentials found: root:(blank)

  [INF] Templates executed: 312 | Matched: 4 | Skipped: 0
:::

:::scenario{id="scenario-4" level="intermediate"}
title: "Scan Multiple Targets from a File"
goal: "Run a misconfiguration scan against a list of URLs and save results to a file."
hint: "Use -l to provide a newline-separated list of targets. Combine with -o to save results. Use -rate-limit to avoid overloading targets. -stats shows live progress during long scans."
command: "nuclei -l urls.txt -tags misconfig -severity medium,high,critical -o results.txt -rate-limit 50 -stats"
expected_output: |
  [INF] Loaded 876 templates (filtered by: tags=misconfig, severity=medium,high,critical)
  [INF] Scanning 25 targets with rate-limit: 50 req/sec

  [INF] Progress: [templates: 876] [hosts: 25] [matched: 12] [requests: 21900]

  [cors-misconfiguration] [http] [medium] https://api.example.com
  [directory-listing] [http] [medium] https://dev.example.com/uploads/
  [exposed-git-repo] [http] [high] https://legacy.example.com/.git/config
  [springboot-actuator-env] [http] [high] https://app.example.com/actuator/env

  [INF] Scan complete | Total: 21900 requests | Matched: 12 | Duration: 4m32s
  [INF] Results saved to: results.txt
:::

:::scenario{id="scenario-5" level="intermediate"}
title: "Technology Fingerprinting and Exposure Discovery"
goal: "Identify what technologies a target runs and find unintended exposed files."
hint: "The 'tech' and 'exposure' tags fingerprint software stacks and find backup files, config files, and sensitive endpoints. Useful for scoping before a deeper assessment."
command: "nuclei -u https://target.example.com -tags tech,exposure -json -o fingerprint.json"
expected_output: |
  [INF] Loaded 654 templates (filtered by: tags=tech,exposure)

  [nginx-detect] [http] [info] https://target.example.com [nginx/1.18.0]
  [wordpress-detect] [http] [info] https://target.example.com [WordPress 6.1.1]
  [php-detect] [http] [info] https://target.example.com [PHP/8.1.12]
  [mysql-detect] [tcp] [info] target.example.com:3306

  [exposed-wp-config] [http] [high] https://target.example.com/wp-config.php.bak
  [exposed-env-file] [http] [high] https://target.example.com/.env
  [backup-files] [http] [medium] https://target.example.com/backup.zip

  [INF] Results saved to: fingerprint.json (JSON format)
:::

## Tips & Tricks

### Template Tags Reference

Common tags for targeting specific vulnerability classes:

| Tag | What It Covers |
|-----|---------------|
| `cve` | Known CVEs with public PoCs |
| `misconfig` | Security misconfigurations |
| `exposure` | Sensitive file and data exposure |
| `default-logins` | Default credentials on common services |
| `exposed-panels` | Admin and management interfaces |
| `tech` | Technology fingerprinting |
| `rce` | Remote code execution vulnerabilities |
| `sqli` | SQL injection detection |
| `xss` | Cross-site scripting |
| `takeover` | Subdomain takeover opportunities |
| `osint` | Open source intelligence gathering |

### Output and Reporting

```bash
# Save plain text results
nuclei -u https://target.com -o results.txt

# Save JSON (for automation / SIEM ingestion)
nuclei -u https://target.com -json -o results.json

# Markdown report
nuclei -u https://target.com -markdown-export report/

# Show only matched results (suppress info-level noise)
nuclei -u https://target.com -severity medium,high,critical
```

### Tuning Scan Performance

```bash
# Faster scan (increase concurrency and rate)
nuclei -l urls.txt -c 50 -rate-limit 500

# Slower, safer scan (avoid overwhelming targets)
nuclei -l urls.txt -c 10 -rate-limit 20 -timeout 10

# Bulk scan with resume support
nuclei -l urls.txt -resume resume.cfg
```

### Using Custom Templates

```bash
# Run a single template
nuclei -u https://target.com -t /path/to/my-template.yaml

# Run all templates in a directory
nuclei -u https://target.com -t /path/to/my-templates/

# Run templates from a URL (GitHub raw)
nuclei -u https://target.com -tu https://raw.githubusercontent.com/user/repo/main/template.yaml
```

### Writing a Simple Template

```yaml
id: example-detect

info:
  name: Example - Exposed Debug Endpoint
  author: yourname
  severity: medium
  tags: misconfig,exposure

http:
  - method: GET
    path:
      - "{{BaseURL}}/debug"
      - "{{BaseURL}}/actuator/info"

    matchers:
      - type: word
        words:
          - "debug"
          - "heap"
        condition: or
```

### Integrating with Other Tools

```bash
# Pipe subfinder output into nuclei
subfinder -d example.com -silent | nuclei -tags cve,misconfig

# Pipe httpx output into nuclei
cat domains.txt | httpx -silent | nuclei -severity critical,high

# Pipe nmap output targets into nuclei
nmap -iL targets.txt -oG - | awk '/open/{print $2}' | nuclei -tags exposure
```

---

:::quiz{id="quiz-1"}
Q: Which flag filters Nuclei templates by vulnerability category (e.g., CVE, misconfig)?
- [ ] -severity
- [x] -tags
- [ ] -t
- [ ] -filter
:::

:::quiz{id="quiz-2"}
Q: What command updates Nuclei's template library before scanning?
- [ ] nuclei -sync
- [ ] nuclei -refresh
- [x] nuclei -update-templates
- [ ] nuclei -pull
:::

:::quiz{id="quiz-3"}
Q: Which flag scans a list of multiple target URLs from a text file?
- [ ] -u
- [x] -l
- [ ] -targets
- [ ] -input
:::

## Quick Reference

| Flag | Purpose |
|------|---------|
| `-u URL` | Single target URL |
| `-l FILE` | File with list of target URLs |
| `-t TEMPLATE` | Specific template file or directory |
| `-tags TAG` | Filter by template tag(s) |
| `-severity LEVEL` | Filter by severity (critical/high/medium/low/info) |
| `-o FILE` | Save output to file |
| `-json` | JSON output format |
| `-markdown-export DIR` | Export markdown report |
| `-rate-limit N` | Max requests per second |
| `-c N` | Concurrent template executions |
| `-timeout N` | Request timeout in seconds |
| `-stats` | Show live scan statistics |
| `-resume FILE` | Resume an interrupted scan |
| `-update-templates` | Update template library |
| `-tl` | List all available templates |

## Severity Levels

| Severity | Meaning | Action |
|----------|---------|--------|
| `critical` | Remote code execution, auth bypass | Immediate remediation |
| `high` | Exposed secrets, severe misconfig | Remediate within days |
| `medium` | Information exposure, CORS issues | Remediate within weeks |
| `low` | Minor misconfigurations | Track and remediate |
| `info` | Technology fingerprinting | No action, use for recon |
