# Shodan

Shodan is a search engine for internet-connected devices. Unlike traditional web search engines, Shodan indexes banners returned by servers, revealing open ports, running services, software versions, and misconfigurations across the public internet.

## Overview

Shodan is essential for:
- **Asset Discovery**: Find exposed systems belonging to an organization
- **Attack Surface Mapping**: Identify what services are visible to the internet
- **Vulnerability Research**: Locate systems running vulnerable software
- **Threat Intelligence**: Track attacker infrastructure and C2 servers

### Installation

Shodan has a web UI at shodan.io and an official CLI tool:

```bash
# Install via pip
pip install shodan

# Initialize with your API key (free account available at shodan.io)
shodan init YOUR_API_KEY

# Verify setup
shodan info
```

:::command-builder{id="shodan-builder"}
tool_name: shodan
target_placeholder: "apache org:\"Target Corp\""
scan_types:
  - name: "Search"
    flag: "search"
    desc: "Search Shodan with a query string"
  - name: "Host Lookup"
    flag: "host"
    desc: "Get all information about an IP address"
  - name: "Count Results"
    flag: "count"
    desc: "Count how many results match a query"
  - name: "Stats"
    flag: "stats"
    desc: "Get aggregate stats for a query"
options:
  - name: "Limit Results"
    flag: "--limit"
    desc: "Max number of results to return"
  - name: "Fields"
    flag: "--fields"
    desc: "Comma-separated list of fields to display"
  - name: "Save to File"
    flag: "--save"
    desc: "Save results to a file"
  - name: "No Color"
    flag: "--no-color"
    desc: "Disable colored output"
:::

## Basic Syntax

The basic Shodan CLI command structure is:

```
shodan search [query]
shodan host [ip]
```

**Common search filters:**
- Organization: `org:"Acme Corp"`
- Country: `country:US`
- Port: `port:3389`
- Product: `product:nginx`
- Operating system: `os:"Windows Server 2016"`
- Vulnerability: `vuln:CVE-2021-44228`
- Network: `net:192.168.1.0/24`
- Hostname: `hostname:vpn.example.com`

---

:::scenario{id="scenario-1" level="beginner"}
title: "Search for Apache Web Servers"
goal: "Find publicly exposed Apache servers in a specific country."
hint: "Combine a product filter with a country filter. Shodan search filters use key:value syntax. Wrap multi-word values in quotes."
command: "shodan search 'product:Apache country:US' --limit 5 --fields ip_str,port,org"
expected_output: |
  198.51.100.10    80    Acme Hosting LLC
  203.0.113.44     443   US Web Services
  198.51.100.88    8080  CloudHost Inc
  203.0.113.201    80    Example ISP
  198.51.100.7     443   FastServe Co
:::

:::scenario{id="scenario-2" level="beginner"}
title: "Look Up an IP Address"
goal: "Get detailed information about all services running on a specific IP."
hint: "The 'host' command returns open ports, banners, location, and known vulnerabilities for an IP. Use it to understand a target's full internet exposure."
command: "shodan host 8.8.8.8"
expected_output: |
  8.8.8.8
  City:           Mountain View
  Country:        United States
  Organization:   Google LLC
  Updated:        2024-01-15T08:22:01.000000
  Number of open ports: 3

  Ports:
       53/udp
       53/tcp    (DNS)
      443/tcp    (HTTPS)
:::

:::scenario{id="scenario-3" level="beginner"}
title: "Find Exposed Databases"
goal: "Discover MongoDB instances with no authentication exposed to the internet."
hint: "Many databases are accidentally exposed without passwords. Search for the product name and look for port 27017 (MongoDB default). Always use this for authorized assessments only."
command: "shodan count 'product:MongoDB port:27017'"
expected_output: |
  45821

  # To see details:
  # shodan search 'product:MongoDB port:27017' --fields ip_str,port,org,location.country_name --limit 10
  203.0.113.15    27017    FutureHost Ltd        Brazil
  198.51.100.33   27017    Digital Ocean         Germany
  203.0.113.78    27017    Alibaba Cloud         China
:::

:::scenario{id="scenario-4" level="intermediate"}
title: "Find Systems Vulnerable to a CVE"
goal: "Identify internet-facing systems affected by a specific vulnerability."
hint: "Use the vuln: filter with a CVE ID. Shodan tags hosts with known CVEs based on version banners. This is useful for scoping vulnerability assessments."
command: "shodan search 'vuln:CVE-2021-44228' --fields ip_str,port,org,location.country_name --limit 5"
expected_output: |
  # CVE-2021-44228 = Log4Shell (Apache Log4j)
  203.0.113.5     8080    Tech Solutions AG     Switzerland
  198.51.100.20   443     MidWest Hosting       United States
  203.0.113.91    80      Asia Pacific Net      Singapore
  198.51.100.67   8443    EU Cloud Svc          Netherlands
  203.0.113.112   8080    South America DC      Brazil
:::

:::scenario{id="scenario-5" level="intermediate"}
title: "Map an Organization's Attack Surface"
goal: "Enumerate all externally visible services for a specific organization."
hint: "Use the org: filter to find all hosts attributed to a company's ASN. Combine with --save to export for further analysis. Review results to identify unexpected or misconfigured services."
command: "shodan search 'org:\"Target University\"' --fields ip_str,port,product,os --limit 20"
expected_output: |
  198.51.100.1     22     OpenSSH         Ubuntu Linux
  198.51.100.1     80     Apache          Ubuntu Linux
  198.51.100.1     443    Apache          Ubuntu Linux
  198.51.100.10    3389   -               Windows Server 2019
  198.51.100.15    21     vsftpd          Ubuntu Linux
  198.51.100.20    5432   PostgreSQL      Debian Linux
  198.51.100.25    8080   Tomcat          CentOS Linux
  198.51.100.30    25     Postfix         Ubuntu Linux
:::

## Tips & Tricks

### Powerful Shodan Dorks

Common pre-built queries for finding exposed or vulnerable systems:

| Query | What It Finds |
|-------|--------------|
| `port:3389 os:"Windows"` | Exposed RDP (Remote Desktop) |
| `port:22 product:OpenSSH version:"7.2"` | Outdated SSH versions |
| `"default password" port:23` | Telnet with default creds |
| `product:Elasticsearch port:9200` | Unauthenticated Elasticsearch |
| `product:"Redis" port:6379` | Exposed Redis instances |
| `http.title:"Admin Panel"` | Exposed admin dashboards |
| `ssl.cert.subject.cn:*.example.com` | Find all subdomains via TLS cert |
| `vuln:CVE-2023-44487` | HTTP/2 Rapid Reset vulnerable hosts |

### Using Shodan Alerts (Monitoring)

Set up continuous monitoring for your own network:

```bash
# Create an alert for a CIDR range
shodan alert create "My Network" 203.0.113.0/24

# List existing alerts
shodan alert list

# Remove an alert
shodan alert remove [ALERT_ID]
```

### Downloading and Analyzing Results

```bash
# Download full result data (uses query credits)
shodan download results.json.gz 'org:"Acme Corp"'

# Parse the downloaded file
shodan parse --fields ip_str,port,product results.json.gz

# Count unique IPs in results
shodan parse --fields ip_str results.json.gz | sort -u | wc -l
```

### Aggregate Statistics

```bash
# Get top countries for a service
shodan stats --facets country 'product:nginx'

# Get top organizations running a product
shodan stats --facets org 'port:27017 product:MongoDB'

# Get version distribution
shodan stats --facets version 'product:OpenSSH'
```

### API Usage (Python)

```python
import shodan

api = shodan.Shodan('YOUR_API_KEY')

# Search
results = api.search('product:Apache country:US', limit=100)
for result in results['matches']:
    print(result['ip_str'], result.get('org', 'Unknown'))

# Host lookup
host = api.host('8.8.8.8')
print(host['org'], host['ip_str'])
for item in host['data']:
    print(f"Port: {item['port']} - Banner: {item.get('data', '')[:80]}")
```

---

:::quiz{id="quiz-1"}
Q: Which Shodan filter would you use to find all exposed services for a company?
- [ ] hostname:company.com
- [x] org:"Company Name"
- [ ] net:company
- [ ] domain:company.com
:::

:::quiz{id="quiz-2"}
Q: What does the `vuln:` filter do in a Shodan search?
- [ ] Runs a live vulnerability scan on the host
- [ ] Finds hosts with open ports
- [x] Finds hosts Shodan has tagged with a specific CVE
- [ ] Lists patch levels of software
:::

:::quiz{id="quiz-3"}
Q: Which command gives you a full picture of all open ports and services on a single IP?
- [ ] shodan search [ip]
- [ ] shodan count [ip]
- [x] shodan host [ip]
- [ ] shodan info [ip]
:::

## Quick Reference

| Command | Purpose |
|---------|---------|
| `shodan init API_KEY` | Initialize CLI with your API key |
| `shodan info` | Check account credits and plan |
| `shodan search "query"` | Search for hosts matching a query |
| `shodan host IP` | Get all data for a specific IP |
| `shodan count "query"` | Count matching results (no credits) |
| `shodan stats --facets X "query"` | Aggregate stats by field |
| `shodan download FILE "query"` | Download full results |
| `shodan parse FILE` | Parse a downloaded results file |
| `shodan alert create NAME CIDR` | Monitor a network range |
| `shodan alert list` | List active monitoring alerts |

## Common Filters Reference

| Filter | Example | Description |
|--------|---------|-------------|
| `org:` | `org:"Amazon"` | Filter by ASN/organization |
| `country:` | `country:DE` | Filter by 2-letter country code |
| `port:` | `port:22` | Filter by open port number |
| `product:` | `product:nginx` | Filter by software product |
| `version:` | `version:"2.4.49"` | Filter by software version |
| `os:` | `os:"Windows 10"` | Filter by operating system |
| `hostname:` | `hostname:vpn.corp.com` | Filter by hostname/domain |
| `net:` | `net:10.0.0.0/8` | Filter by IP range (CIDR) |
| `vuln:` | `vuln:CVE-2021-44228` | Filter by CVE identifier |
| `ssl.cert.subject.cn:` | `ssl.cert.subject.cn:*.corp.com` | Filter by TLS certificate CN |
| `http.title:` | `http.title:"Login"` | Filter by HTTP page title |
| `http.html:` | `http.html:"phpMyAdmin"` | Filter by HTTP response body |
