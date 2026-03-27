# Recon-ng

Recon-ng is a full-featured web reconnaissance framework written in Python. Its modular structure — modeled after Metasploit — provides a consistent interface for automating OSINT tasks: subdomain enumeration, email harvesting, contact discovery, and credential exposure checks, with all results stored in a local database per workspace.

## Overview

Recon-ng is essential for:
- **Subdomain Enumeration**: Discover hosts and subdomains using passive DNS and API sources
- **Email Harvesting**: Collect email addresses from PGP servers, search engines, and breach data
- **Contact Discovery**: Find people, phone numbers, and organizational relationships
- **Structured Reporting**: Aggregate all findings into HTML, CSV, or JSON reports

### Installation

Recon-ng is pre-installed on Kali Linux. For other systems:

```bash
# Clone from GitHub
git clone https://github.com/lanmaster53/recon-ng.git
cd recon-ng
pip install -r REQUIREMENTS

# Launch
python3 recon-ng

# Or install via pip
pip install recon-ng
recon-ng
```

:::command-builder{id="recon-ng-builder"}
tool_name: recon-ng
target_placeholder: "example.com"
scan_types:
  - name: "Search Modules"
    flag: "modules search"
    desc: "Find modules by keyword"
  - name: "Load Module"
    flag: "modules load"
    desc: "Load a specific recon module"
  - name: "Marketplace Install"
    flag: "marketplace install"
    desc: "Install a module from the marketplace"
  - name: "Run Module"
    flag: "run"
    desc: "Execute the currently loaded module"
options:
  - name: "Set Source"
    flag: "options set SOURCE"
    desc: "Set the target domain or value"
  - name: "Show Hosts"
    flag: "show hosts"
    desc: "List all discovered hosts in workspace"
  - name: "Show Contacts"
    flag: "show contacts"
    desc: "List all discovered contacts"
  - name: "Generate Report"
    flag: "modules load reporting/html"
    desc: "Load the HTML reporting module"
:::

## Core Concepts

### Framework Structure

| Concept | Description | Example |
|---------|-------------|---------|
| **Workspace** | Isolated database for an engagement | `workspaces create client_pentest` |
| **Module** | A specific recon task | `recon/domains-hosts/hackertarget` |
| **Marketplace** | Module repository (install on demand) | `marketplace install all` |
| **Table** | Stored results (hosts, contacts, etc.) | `show hosts` |
| **Source** | Input for a module (domain, IP, etc.) | `options set SOURCE example.com` |

### Module Naming Convention

```
[category]/[input_type]-[output_type]/[module_name]

recon/domains-hosts/hackertarget
│     │       │     └── module name
│     │       └── output type (what it produces)
│     └── input type (what it takes)
└── category (recon, reporting, import, export)
```

### Basic Workflow

```
1. workspaces create [name]          # Start a new investigation
2. marketplace install [module]      # Install needed modules
3. modules load [module/path]        # Load a module
4. options set SOURCE [target]       # Set the target
5. run                               # Execute the module
6. show hosts / show contacts        # Review results
7. Repeat steps 3-6 with new modules # Chain modules together
8. modules load reporting/html       # Generate final report
```

---

:::scenario{id="scenario-1" level="beginner"}
title: "Set Up a Workspace and Find Subdomains"
goal: "Create a new workspace for a target and enumerate subdomains using a passive DNS source."
hint: "Always start with a workspace to keep results organized per engagement. The hackertarget module uses a free API — no key needed — making it a good first module to run."
command: "workspaces create acme_recon\nmarketplace install recon/domains-hosts/hackertarget\nmodules load recon/domains-hosts/hackertarget\noptions set SOURCE example.com\nrun"
expected_output: |
  [recon-ng][acme_recon] > workspaces create acme_recon
  [*] Workspace 'acme_recon' created.

  [recon-ng][acme_recon] > modules load recon/domains-hosts/hackertarget
  [recon-ng][acme_recon][hackertarget] > options set SOURCE example.com
  SOURCE => example.com

  [recon-ng][acme_recon][hackertarget] > run
  [*] example.com
  [*] www.example.com
  [*] mail.example.com
  [*] api.example.com
  [*] dev.example.com
  [*] vpn.example.com
  [*] staging.example.com

  -------
  SUMMARY
  -------
  [*] 7 total (7 new) hosts found.
:::

:::scenario{id="scenario-2" level="beginner"}
title: "Harvest Email Addresses from a Domain"
goal: "Collect email addresses associated with a domain using public sources."
hint: "The pgp_search module queries PGP keyservers for email addresses. The whois_pocs module extracts registrant contacts from WHOIS data. Chain both for better coverage."
command: "modules load recon/domains-contacts/pgp_search\noptions set SOURCE example.com\nrun\nshow contacts"
expected_output: |
  [recon-ng][acme_recon] > modules load recon/domains-contacts/pgp_search
  [recon-ng][acme_recon][pgp_search] > options set SOURCE example.com
  SOURCE => example.com

  [recon-ng][acme_recon][pgp_search] > run
  [*] Searching PGP keyservers for example.com...
  [*] alice@example.com
  [*] bob.smith@example.com
  [*] security@example.com
  [*] devops@example.com

  -------
  SUMMARY
  -------
  [*] 4 total (4 new) contacts found.

  [recon-ng][acme_recon][pgp_search] > show contacts
  +----+--------------+-------------------+--------+
  | rowid | first_name | email             | region |
  +----+--------------+-------------------+--------+
  | 1     | Alice       | alice@example.com | None  |
  | 2     | Bob         | bob.smith@...     | None  |
  +----+--------------+-------------------+--------+
:::

:::scenario{id="scenario-3" level="beginner"}
title: "Resolve Discovered Hostnames to IP Addresses"
goal: "Convert the list of discovered subdomains into IP addresses for further investigation."
hint: "After populating the hosts table, use the resolve module to look up IP addresses. The module automatically reads from the hosts table, so you don't need to set SOURCE manually."
command: "modules load recon/hosts-hosts/resolve\nrun\nshow hosts"
expected_output: |
  [recon-ng][acme_recon] > modules load recon/hosts-hosts/resolve
  [recon-ng][acme_recon][resolve] > run

  [*] Resolving www.example.com...
  [*] 93.184.216.34
  [*] Resolving mail.example.com...
  [*] 93.184.216.50
  [*] Resolving api.example.com...
  [*] 93.184.216.60
  [*] Resolving dev.example.com...
  [*] 93.184.216.70

  -------
  SUMMARY
  -------
  [*] 4 total (4 new) IP addresses resolved.

  [recon-ng][acme_recon][resolve] > show hosts
  +-------+--------------------+---------------+
  | rowid | host               | ip_address    |
  +-------+--------------------+---------------+
  | 1     | www.example.com    | 93.184.216.34 |
  | 2     | mail.example.com   | 93.184.216.50 |
  | 3     | api.example.com    | 93.184.216.60 |
  | 4     | dev.example.com    | 93.184.216.70 |
  +-------+--------------------+---------------+
:::

:::scenario{id="scenario-4" level="intermediate"}
title: "Chain Modules for a Full Passive Recon Workflow"
goal: "Run a multi-module recon sequence to enumerate subdomains, resolve IPs, and enrich with WHOIS data."
hint: "Chaining modules is Recon-ng's core strength. Each module reads from and writes to the same workspace database. Run subdomain modules first, then resolve, then enrich — building up the picture layer by layer."
command: "modules load recon/domains-hosts/certificate_transparency\noptions set SOURCE example.com\nrun\nmodules load recon/hosts-hosts/resolve\nrun\nmodules load recon/hosts-hosts/ssltools\nrun"
expected_output: |
  [*] Loading certificate_transparency...
  [*] Querying crt.sh for example.com
  [*] Found 23 subdomains via certificate transparency logs:
  [*] portal.example.com, cdn.example.com, jira.example.com,
      confluence.example.com, gitlab.example.com ... (18 more)

  SUMMARY: 23 total (16 new) hosts found.

  [*] Loading recon/hosts-hosts/resolve...
  [*] Resolving 23 hosts...
  SUMMARY: 23 total (16 new) IP addresses resolved.

  [*] Loading recon/hosts-hosts/ssltools...
  [*] Checking TLS certificate details...
  [*] portal.example.com: cert valid until 2025-06-01
  [*] gitlab.example.com: cert valid until 2025-03-15 ← expiring soon

  Workspace totals:
  - Hosts: 23
  - IP Addresses: 18 unique
  - Domains: 1
:::

:::scenario{id="scenario-5" level="intermediate"}
title: "Generate a Structured Recon Report"
goal: "Export all gathered reconnaissance data into an HTML report for review or hand-off."
hint: "The reporting modules read from all workspace tables and compile a structured report. Run this at the end of a recon session. The HTML report is well-formatted and suitable for client delivery."
command: "marketplace install reporting/html\nmodules load reporting/html\noptions set FILENAME /tmp/acme_report.html\noptions set CREATOR 'Security Team'\noptions set CUSTOMER 'Acme Corp'\nrun"
expected_output: |
  [recon-ng][acme_recon] > modules load reporting/html
  [recon-ng][acme_recon][html] > options set FILENAME /tmp/acme_report.html
  [recon-ng][acme_recon][html] > options set CREATOR 'Security Team'
  [recon-ng][acme_recon][html] > options set CUSTOMER 'Acme Corp'
  [recon-ng][acme_recon][html] > run

  Generating report...
  [*] 23 hosts exported
  [*] 4 contacts exported
  [*] 1 domain exported
  [*] 2 vulnerabilities exported

  [*] Report saved to: /tmp/acme_report.html

  Report sections:
  - Summary Statistics
  - Discovered Hosts (with IPs and ports)
  - Contacts and Emails
  - Vulnerabilities
  - Raw Data Tables
:::

## Tips & Tricks

### Key Module Categories

| Category | Path Pattern | What It Does |
|----------|-------------|--------------|
| Domain → Hosts | `recon/domains-hosts/*` | Find subdomains and hostnames |
| Domain → Contacts | `recon/domains-contacts/*` | Find people and emails |
| Hosts → Hosts | `recon/hosts-hosts/*` | Enrich host data (resolve, SSL) |
| Hosts → Ports | `recon/hosts-ports/*` | Find open ports (via Shodan/Censys) |
| Contacts → Contacts | `recon/contacts-contacts/*` | Enrich contact data |
| Contacts → Creds | `recon/contacts-credentials/*` | Check breach databases |
| Reporting | `reporting/*` | Export results (HTML, CSV, JSON) |

### Essential Modules to Install

```bash
# Install everything at once (large download)
marketplace install all

# Or install selectively:
marketplace install recon/domains-hosts/hackertarget
marketplace install recon/domains-hosts/certificate_transparency
marketplace install recon/domains-contacts/pgp_search
marketplace install recon/domains-contacts/whois_pocs
marketplace install recon/hosts-hosts/resolve
marketplace install recon/hosts-ports/shodan_ip
marketplace install recon/contacts-credentials/hibp_breach
marketplace install reporting/html
marketplace install reporting/csv
```

### API Key Management

Many modules require API keys for third-party services:

```bash
# View all configured keys
keys list

# Add a key
keys add shodan_api  YOUR_SHODAN_KEY
keys add github_api  YOUR_GITHUB_TOKEN
keys add hibp_api    YOUR_HIBP_KEY
keys add hunter_api  YOUR_HUNTER_KEY

# Check which modules need keys
marketplace search
# Columns show: K (requires key), D (has dependencies)
```

### Working with Workspaces

```bash
# List all workspaces
workspaces list

# Switch to a different workspace
workspaces load other_project

# Export workspace database for backup
# Workspace stored at: ~/.recon-ng/workspaces/[name]/data.db

# Query workspace data directly
db query SELECT * FROM hosts WHERE ip_address IS NOT NULL
db query SELECT email FROM contacts WHERE email LIKE '%@example.com'
```

### Useful Console Commands

```bash
# Search for modules
modules search github
modules search subdomain
modules search breach

# Get module details before loading
marketplace info recon/domains-hosts/hackertarget

# View all loaded module options
options list

# Set source to the full hosts table (run module on all hosts)
options set SOURCE default

# Show summary of workspace contents
show dashboard

# Get help for any command
help
help modules
```

---

:::quiz{id="quiz-1"}
Q: What is the purpose of a "workspace" in Recon-ng?
- [ ] A visual graph of entity relationships
- [x] An isolated database that stores all results for a specific engagement
- [ ] A collection of API keys
- [ ] A template for running multiple modules at once
:::

:::quiz{id="quiz-2"}
Q: What does the module path `recon/domains-hosts/hackertarget` tell you about the module?
- [ ] It targets the HackerTarget organization
- [ ] It requires a HackerTarget API key
- [x] It takes a domain as input and produces hosts as output using HackerTarget's API
- [ ] It brute-forces subdomains on HackerTarget servers
:::

:::quiz{id="quiz-3"}
Q: Which command installs a new module from the Recon-ng module repository?
- [ ] modules install
- [ ] modules load
- [x] marketplace install
- [ ] pip install
:::

## Quick Reference

| Command | Purpose |
|---------|---------|
| `workspaces create NAME` | Create a new investigation workspace |
| `workspaces list` | List all workspaces |
| `workspaces load NAME` | Switch to a workspace |
| `marketplace search TERM` | Search available modules |
| `marketplace install MODULE` | Download and install a module |
| `marketplace install all` | Install all available modules |
| `modules load MODULE/PATH` | Load a module |
| `modules search TERM` | Search loaded modules |
| `options list` | Show current module options |
| `options set KEY VALUE` | Set a module option |
| `run` | Execute the loaded module |
| `show hosts` | View discovered hosts table |
| `show contacts` | View discovered contacts table |
| `show domains` | View domains table |
| `show dashboard` | Summary of workspace contents |
| `keys list` | View configured API keys |
| `keys add NAME VALUE` | Add an API key |
| `db query SQL` | Run raw SQL on workspace database |
| `help` | Show help |
| `exit` | Exit Recon-ng |

## Common Module Reference

| Module | Input | Output | Notes |
|--------|-------|--------|-------|
| `recon/domains-hosts/hackertarget` | Domain | Subdomains | Free, no key |
| `recon/domains-hosts/certificate_transparency` | Domain | Subdomains | crt.sh, free |
| `recon/domains-hosts/brute_hosts` | Domain | Subdomains | Active brute-force |
| `recon/domains-contacts/pgp_search` | Domain | Emails | PGP keyservers |
| `recon/domains-contacts/whois_pocs` | Domain | Contacts | WHOIS registrant |
| `recon/hosts-hosts/resolve` | Hosts table | IPs | DNS resolution |
| `recon/hosts-ports/shodan_ip` | IP | Ports | Requires Shodan key |
| `recon/contacts-credentials/hibp_breach` | Email | Breaches | Requires HIBP key |
| `reporting/html` | All tables | HTML report | Full report |
| `reporting/csv` | All tables | CSV file | For spreadsheets |
| `reporting/json` | All tables | JSON file | For automation |
