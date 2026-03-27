# Censys

Censys is an internet-wide scanning and attack surface management platform. It continuously scans the public internet, indexing hosts, open ports, TLS certificates, and web properties. Unlike Shodan, Censys emphasizes certificate transparency logs and structured data, making it especially powerful for subdomain discovery and tracking organizational exposure.

## Overview

Censys is essential for:
- **Attack Surface Discovery**: Find all internet-facing assets tied to an organization
- **Certificate Intelligence**: Enumerate subdomains and services via TLS certificate logs
- **Host and Service Enumeration**: Identify open ports, running software, and banners
- **Vulnerability Research**: Locate hosts running specific vulnerable software versions

### Installation

Censys has a web UI at search.censys.io and an official Python SDK with CLI:

```bash
# Install via pip
pip install censys

# Configure with your API credentials (free account at censys.io)
censys config
# Enter your API ID and API Secret when prompted

# Verify setup
censys account
```

:::command-builder{id="censys-builder"}
tool_name: censys
target_placeholder: "services.port=443 and autonomous_system.name=\"Target Corp\""
scan_types:
  - name: "Search Hosts"
    flag: "hosts search"
    desc: "Search for hosts matching a query"
  - name: "View Host"
    flag: "hosts view"
    desc: "Get all data for a specific IP address"
  - name: "Search Certs"
    flag: "certs"
    desc: "Search TLS certificates"
  - name: "Find Subdomains"
    flag: "subdomains"
    desc: "Enumerate subdomains via certificate logs"
options:
  - name: "Fields"
    flag: "--fields"
    desc: "Comma-separated list of fields to display"
  - name: "Output Format"
    flag: "--format"
    desc: "Output format: screen, json, csv"
  - name: "Max Records"
    flag: "--max-records"
    desc: "Limit the number of returned results"
  - name: "Virtual Hosts"
    flag: "--virtual-hosts"
    desc: "Include virtual hosts (INCLUDE, ONLY, EXCLUDE)"
:::

## Basic Syntax

The basic Censys CLI command structure is:

```
censys hosts search "query"
censys hosts view [ip]
censys subdomains [domain]
```

**Common search filters (Censys Search 2.0 syntax):**
- Organization/ASN: `autonomous_system.name="Acme Corp"`
- IP range: `ip="192.168.1.0/24"`
- Port: `services.port=3389`
- Product: `services.software.product="Apache httpd"`
- Country: `location.country_code="DE"`
- TLS certificate domain: `services.tls.certificates.leaf_data.names="*.example.com"`
- HTTP server header: `services.http.response.headers.server="nginx"`
- OS: `operating_system.product="Windows Server 2019"`
- CVE: `services.software.vulnerabilities.cve_id="CVE-2021-44228"`

---

:::scenario{id="scenario-1" level="beginner"}
title: "Search for Hosts by Organization"
goal: "Find all internet-facing hosts attributed to a specific organization."
hint: "Use the autonomous_system.name field to search by company ASN. Wrap the org name in quotes. Use --fields to control which columns appear in output."
command: "censys hosts search 'autonomous_system.name=\"Target University\"' --fields ip,services.port,services.service_name,location.country"
expected_output: |
  Searching hosts ...
  ip               services.port  services.service_name  location.country
  198.51.100.1     [22, 80, 443]  [SSH, HTTP, HTTPS]     United States
  198.51.100.10    [3389, 443]    [RDP, HTTPS]           United States
  198.51.100.15    [21, 22]       [FTP, SSH]             United States
  198.51.100.20    [5432]         [POSTGRESQL]           United States
  198.51.100.25    [8080, 8443]   [HTTP, HTTPS]          United States

  Showing 5 of 47 results
:::

:::scenario{id="scenario-2" level="beginner"}
title: "Look Up a Specific IP Address"
goal: "Get a comprehensive view of all services and metadata for a single host."
hint: "The 'hosts view' command returns every open port, TLS certificate, banner, and label Censys has collected for an IP. It's the most detailed view of a single host."
command: "censys hosts view 198.51.100.10"
expected_output: |
  {
    "ip": "198.51.100.10",
    "autonomous_system": {
      "name": "Target University",
      "asn": 12345,
      "country_code": "US"
    },
    "services": [
      {
        "port": 443,
        "service_name": "HTTPS",
        "transport_protocol": "TCP",
        "software": [{"product": "Apache httpd", "version": "2.4.49"}],
        "tls": {
          "certificates": {
            "leaf_data": {
              "names": ["target.edu", "www.target.edu", "portal.target.edu"]
            }
          }
        }
      },
      {
        "port": 3389,
        "service_name": "RDP",
        "transport_protocol": "TCP"
      }
    ],
    "labels": ["cloud", "windows"]
  }
:::

:::scenario{id="scenario-3" level="beginner"}
title: "Discover Subdomains via Certificate Logs"
goal: "Enumerate subdomains of a target domain using TLS certificate transparency data."
hint: "Censys indexes certificate transparency logs and can reveal subdomains that don't appear in DNS. This often uncovers staging, dev, and internal systems exposed to the internet."
command: "censys subdomains example.com"
expected_output: |
  Searching certificates for example.com ...

  Subdomains found: 23
  www.example.com
  mail.example.com
  vpn.example.com
  dev.example.com
  staging.example.com
  api.example.com
  admin.example.com
  portal.example.com
  legacy.example.com
  jira.example.com
  confluence.example.com
  gitlab.example.com
  jenkins.example.com
  ...
  (and 10 more)
:::

:::scenario{id="scenario-4" level="intermediate"}
title: "Find Hosts Running a Vulnerable Software Version"
goal: "Identify internet-facing hosts running a specific vulnerable product version."
hint: "Use services.software.product and services.software.version to target exact software. Combine with autonomous_system.name to scope to a specific organization. Always use this within authorized scope."
command: "censys hosts search 'services.software.product=\"Apache httpd\" and services.software.version=\"2.4.49\"' --fields ip,autonomous_system.name,services.port --max-records 10"
expected_output: |
  Searching hosts ...
  # Apache 2.4.49 is vulnerable to CVE-2021-41773 (path traversal / RCE)

  ip               autonomous_system.name     services.port
  203.0.113.5      Example Hosting Co         [80, 443]
  198.51.100.44    US Cloud Services          [80]
  203.0.113.91     Asia Pacific Networks      [443, 8080]
  198.51.100.67    EU Datacenter GmbH         [80, 443]
  203.0.113.112    South America DC           [80]

  Showing 5 of 10 results
:::

:::scenario{id="scenario-5" level="intermediate"}
title: "Map an Organization's Full Attack Surface"
goal: "Combine host search and certificate lookup to build a complete external asset inventory."
hint: "Use the Python SDK for more control — iterate results, combine data sources, and export structured reports. This approach is standard in Attack Surface Management (ASM) workflows."
command: "python3 censys_asm.py"
expected_output: |
  # censys_asm.py — Python SDK example:
  #
  # from censys.search import CensysHosts
  # h = CensysHosts()
  # query = 'autonomous_system.name="Target Corp"'
  # for page in h.search(query, fields=["ip","services.port","services.software"]):
  #     for host in page:
  #         print(host["ip"], host.get("services.port", []))

  Enumerating Target Corp assets...

  198.51.100.1    ports=[22, 80, 443]   software=[OpenSSH 8.2, Apache 2.4.52]
  198.51.100.10   ports=[443, 8443]     software=[nginx 1.20, WordPress 6.1]
  198.51.100.20   ports=[5432]          software=[PostgreSQL 13.4]
  198.51.100.30   ports=[3389]          software=[]
  198.51.100.45   ports=[25, 587]       software=[Postfix 3.6]

  Total hosts: 47 | Unique ports: 18 | Exposed databases: 3
:::

## Tips & Tricks

### Censys vs. Shodan

Both index the internet but have different strengths:

| Feature | Censys | Shodan |
|---------|--------|--------|
| Certificate / TLS data | Excellent | Good |
| Subdomain discovery | Native (`censys subdomains`) | Via cert filter |
| Search query syntax | Structured (field=value) | Keyword + filters |
| Free tier | 250 queries/month | 100 results/query |
| API / SDK | Python SDK (official) | Python library |
| Best for | Asset inventory, cert recon | Broad internet search |

### Useful Search Queries

```bash
# Find exposed RDP
censys hosts search "services.port=3389"

# Find self-signed certificates (potential misconfig)
censys hosts search "services.tls.certificates.leaf_data.issuer.organization=\"Self-Signed\""

# Find services with expired TLS certificates
censys hosts search "services.tls.certificates.leaf_data.validity.end < \"2024-01-01T00:00:00Z\""

# Find hosts by CVE
censys hosts search "services.software.vulnerabilities.cve_id=\"CVE-2021-44228\""

# Find hosts with specific HTTP title
censys hosts search "services.http.response.html_title=\"phpMyAdmin\""

# Find exposed Kubernetes API servers
censys hosts search "services.port=6443 and services.kubernetes.version.minor!=\"\""
```

### Using the Python SDK

```python
from censys.search import CensysHosts, CensysCerts

# Host search
h = CensysHosts()
for page in h.search('autonomous_system.name="Acme"', fields=["ip", "services.port"]):
    for host in page:
        print(host["ip"], host.get("services.port"))

# Certificate search — find subdomains
c = CensysCerts()
query = 'parsed.names: example.com'
for page in c.search(query, fields=["parsed.names", "parsed.subject.common_name"]):
    for cert in page:
        for name in cert.get("parsed.names", []):
            print(name)
```

### Saving and Exporting Results

```bash
# Export as JSON
censys hosts search "services.port=3389" --format json > rdp_hosts.json

# Export as CSV
censys hosts search 'autonomous_system.name="Target"' --format csv > assets.csv

# Count results without fetching all data
censys hosts search "services.port=27017" --count
```

### Setting Up Attack Surface Monitoring

Censys ASM (Attack Surface Management) allows continuous monitoring:

```bash
# Install ASM SDK
pip install censys[asm]

# List your organization's seeds (root domains/IPs/ASNs)
censys asm subdomains list

# Get logbook events (new/changed assets)
censys asm logbook
```

---

:::quiz{id="quiz-1"}
Q: Which Censys CLI command discovers subdomains using certificate transparency logs?
- [ ] censys hosts search
- [ ] censys certs search
- [x] censys subdomains
- [ ] censys dns
:::

:::quiz{id="quiz-2"}
Q: What field in Censys Search 2.0 filters results by the owning organization or ASN?
- [ ] org:
- [ ] owner.name=
- [x] autonomous_system.name=
- [ ] company.name=
:::

:::quiz{id="quiz-3"}
Q: What is a key advantage Censys has over Shodan for reconnaissance?
- [ ] It supports more countries
- [ ] It scans faster
- [x] It natively integrates certificate transparency logs for subdomain discovery
- [ ] It has a free unlimited tier
:::

## Quick Reference

| Command | Purpose |
|---------|---------|
| `censys config` | Set up API credentials |
| `censys account` | View account info and quota |
| `censys hosts search "query"` | Search for hosts by query |
| `censys hosts view IP` | Full details for a specific IP |
| `censys subdomains DOMAIN` | Find subdomains via cert logs |
| `censys certs "query"` | Search TLS certificates |
| `censys hosts search ... --format json` | JSON output |
| `censys hosts search ... --format csv` | CSV output |
| `censys hosts search ... --count` | Count matching hosts |
| `censys hosts search ... --max-records N` | Limit results |
| `censys hosts search ... --fields f1,f2` | Select output fields |

## Common Search Fields

| Field | Example | Description |
|-------|---------|-------------|
| `ip` | `ip="8.8.8.8"` | Exact IP or CIDR range |
| `autonomous_system.name` | `autonomous_system.name="Google"` | Organization / ASN name |
| `autonomous_system.asn` | `autonomous_system.asn=15169` | ASN number |
| `location.country_code` | `location.country_code="DE"` | 2-letter country code |
| `services.port` | `services.port=22` | Open port number |
| `services.service_name` | `services.service_name="SSH"` | Protocol name |
| `services.software.product` | `services.software.product="nginx"` | Software product name |
| `services.software.version` | `services.software.version="1.18.0"` | Software version |
| `services.software.vulnerabilities.cve_id` | `...cve_id="CVE-2021-44228"` | Known CVE on the host |
| `services.tls.certificates.leaf_data.names` | `...names="*.corp.com"` | Domain in TLS certificate |
| `services.http.response.html_title` | `...html_title="Login"` | HTTP page title |
| `services.http.response.headers.server` | `...headers.server="Apache"` | HTTP Server header |
| `operating_system.product` | `operating_system.product="Windows"` | Detected OS |
| `labels` | `labels="cloud"` | Censys-applied host labels |
