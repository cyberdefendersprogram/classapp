# Maltego

Maltego is a visual link analysis and OSINT platform that maps relationships between entities — domains, IPs, people, organizations, emails, and social profiles — on an interactive graph. It uses "Transforms" to query hundreds of data sources and automatically expand connections, making it the standard tool for threat intelligence, infrastructure mapping, and open-source investigations.

## Overview

Maltego is essential for:
- **OSINT Investigation**: Map relationships between people, organizations, and digital infrastructure
- **Infrastructure Mapping**: Enumerate DNS records, IP ranges, hosting providers, and certificates
- **Threat Intelligence**: Track threat actor infrastructure and campaign connections
- **Email and Identity Research**: Discover email addresses, breach data, and social accounts

### Installation

Maltego has a free Community Edition (CE) and paid Professional/Enterprise tiers:

```bash
# Download from maltego.com
# Available for Windows, macOS, Linux (requires Java 11+)

# macOS via Homebrew
brew install --cask maltego

# Linux (Debian/Ubuntu)
# Download .deb from maltego.com
sudo dpkg -i maltego_*.deb

# Launch
maltego
```

After launching, create a free account at maltego.com and activate your CE license in the application.

:::command-builder{id="maltego-builder"}
tool_name: maltego
target_placeholder: "example.com"
scan_types:
  - name: "Domain Investigation"
    flag: "Entity: Domain"
    desc: "Start from a domain and expand DNS, IPs, and emails"
  - name: "IP Investigation"
    flag: "Entity: IP Address"
    desc: "Start from an IP and find hosting, domains, and netblock"
  - name: "Person Investigation"
    flag: "Entity: Person"
    desc: "Start from a person and find emails, profiles, and orgs"
  - name: "Organization Investigation"
    flag: "Entity: Organization"
    desc: "Start from a company and find domains, people, and infrastructure"
options:
  - name: "Run All Transforms"
    flag: "Run All Transforms"
    desc: "Execute every available transform on selected entity"
  - name: "Run Machine"
    flag: "Machines > Run Machine"
    desc: "Run an automated multi-step transform sequence"
  - name: "Merge Nodes"
    flag: "Edit > Merge Entities"
    desc: "Combine duplicate entities on the graph"
  - name: "Export Graph"
    flag: "File > Export Graph"
    desc: "Export graph as PDF, image, or spreadsheet"
:::

## Core Concepts

### Entities and Transforms

| Concept | Description | Example |
|---------|-------------|---------|
| **Entity** | An object on the graph | Domain, IP, Person, Email |
| **Transform** | A query that expands an entity | DNS lookup, WHOIS, HaveIBeenPwned |
| **Machine** | Automated sequence of transforms | Footprint L1, L2, L3 |
| **Hub** | Transform marketplace | Install community transforms |
| **Graph** | Visual canvas of relationships | Shows all discovered connections |

### Basic Workflow

```
1. New Graph                 # Create a blank investigation graph
2. Add Entity                # Drag target entity onto canvas (e.g., Domain)
3. Enter entity value        # Type the target (e.g., "example.com")
4. Right-click entity        # Open transform menu
5. Select Transform(s)       # Run queries to expand the graph
6. Analyze connections       # Review discovered relationships
7. Export results            # Save graph or export to spreadsheet
```

---

:::scenario{id="scenario-1" level="beginner"}
title: "Investigate a Domain's Infrastructure"
goal: "Map all DNS records, IP addresses, and mail servers for a target domain."
hint: "Start with a Domain entity, then run DNS-based transforms. The 'To DNS Name' and 'To IP Address' transforms are the foundation of any infrastructure investigation."
command: "New Graph > Add Entity: Domain (example.com) > Right-click > DNS from Domain > Run All DNS Transforms"
expected_output: |
  Graph expanded from: example.com

  DNS Records discovered:
  ├── example.com → A → 93.184.216.34 (IP Address)
  ├── example.com → MX → mail.example.com
  │   └── mail.example.com → A → 93.184.216.50
  ├── example.com → NS → ns1.example.com
  │   └── ns1.example.com → A → 93.184.216.1
  ├── example.com → NS → ns2.example.com
  ├── www.example.com → CNAME → example.com
  └── example.com → TXT → "v=spf1 include:_spf.google.com ~all"

  New entities added: 8
  Relationships mapped: 11
:::

:::scenario{id="scenario-2" level="beginner"}
title: "Enumerate Subdomains and Related Domains"
goal: "Discover subdomains and other domains hosted on the same infrastructure."
hint: "After resolving a domain to an IP, run 'To Domain' on the IP to find other domains hosted on the same server. This reveals related infrastructure and sometimes internal naming conventions."
command: "Select IP entity (93.184.216.34) > Right-click > To Domain [From IP] and To Netblock [From IP]"
expected_output: |
  Expanding from IP: 93.184.216.34

  Domains on same IP:
  ├── example.com
  ├── www.example.com
  ├── dev.example.com
  └── staging.example.com

  Netblock: 93.184.216.0/24
  ├── Registered to: EDGECAST Inc.
  ├── Country: United States
  └── ASN: AS15133

  New entities added: 6
:::

:::scenario{id="scenario-3" level="beginner"}
title: "Find Email Addresses for an Organization"
goal: "Discover email addresses associated with a target domain for OSINT research."
hint: "Maltego can extract email addresses from public sources like search engines, PGP keyservers, and breach databases. Run 'To Email Address' transforms on a Domain entity."
command: "Select Domain entity (example.com) > Right-click > Email Addresses > To Email Address [From Domain]"
expected_output: |
  Email addresses discovered for example.com:

  ├── john.smith@example.com
  │   └── Source: LinkedIn public profile
  ├── admin@example.com
  │   └── Source: PGP keyserver
  ├── security@example.com
  │   └── Source: security.txt
  ├── j.doe@example.com
  │   └── Source: Public GitHub commits
  └── info@example.com
      └── Source: WHOIS registrant

  Expand email entities → To Person, To Social Profile, To HaveIBeenPwned
:::

:::scenario{id="scenario-4" level="intermediate"}
title: "Run an Automated Footprint Machine"
goal: "Use a Maltego Machine to automatically run a multi-step infrastructure enumeration."
hint: "Machines automate sequences of transforms. 'Footprint L1' runs passive DNS and WHOIS only. 'Footprint L2' adds active queries. 'Footprint L3' is the most thorough. Start with L1 to avoid detection."
command: "Select Domain entity (example.com) > Machines menu > Run Machine > Footprint L1 > Start"
expected_output: |
  Running Machine: Footprint L1 on example.com

  Phase 1 — DNS Enumeration
  [+] A records: 2 IPs found
  [+] MX records: 3 mail servers found
  [+] NS records: 4 nameservers found
  [+] TXT records: SPF, DMARC, DKIM policies extracted

  Phase 2 — WHOIS / Registration Data
  [+] Registrar: GoDaddy LLC
  [+] Registrant org: Example Corporation
  [+] Created: 2005-08-14
  [+] Admin email: admin@example.com (→ new Person entity)

  Phase 3 — Passive Certificate Analysis
  [+] 14 subdomains found via certificate logs
  [+] New domains: api.example.com, vpn.example.com, mail.example.com...

  Machine complete | Entities: 47 | Relationships: 63
:::

:::scenario{id="scenario-5" level="intermediate"}
title: "Map a Person's Digital Footprint"
goal: "Build a relationship graph connecting a person to their online accounts, employer, and associated infrastructure."
hint: "Start with a Person or Email entity. Run social profile transforms to find linked accounts, then expand each profile to find more connections. This is standard procedure in fraud and threat actor attribution investigations."
command: "New Graph > Add Entity: Email Address (target@example.com) > Run All Transforms"
expected_output: |
  Expanding from: target@example.com

  Identity Connections:
  ├── Person: Jane Smith
  │   ├── LinkedIn: linkedin.com/in/janesmith
  │   ├── Twitter/X: @janesmith_sec
  │   ├── GitHub: github.com/janesmith
  │   └── Organization: Acme Corporation

  Breach Intelligence (HaveIBeenPwned):
  ├── [!] Found in 3 breaches:
  │   ├── LinkedIn (2012)
  │   ├── Adobe (2013)
  │   └── Collection#1 (2019)

  Infrastructure Links:
  ├── GitHub repos → Domain: janesmith.dev → IP: 104.21.44.3
  └── Twitter bio URL → acmecorp.com (target organization)

  Entities added: 18 | Relationships: 24
:::

## Tips & Tricks

### Transform Hub — Useful Transform Sets

Install these from the Maltego Transform Hub (Transforms menu > Transform Hub):

| Transform Set | Data Source | Use Case |
|---------------|------------|---------|
| **Shodan** | Shodan.io | Find open ports and banners for IPs |
| **Have I Been Pwned** | HIBP | Check emails against breach databases |
| **VirusTotal** | VirusTotal | Check domains/IPs for malware associations |
| **Hunter.io** | Hunter | Discover company email addresses |
| **SecurityTrails** | SecurityTrails | Historical DNS, subdomain enum |
| **WhoisXML** | WhoisXML API | Deep WHOIS and registrant tracking |
| **Social Links** | Social media | Map social profiles and connections |
| **PassiveTotal** | RiskIQ | Passive DNS and threat intelligence |

### Working Efficiently with Large Graphs

```
# Reduce visual clutter
View > Layouts > Hierarchical   — shows parent-child relationships
View > Layouts > Circular       — shows network clusters
View > Entity List              — tabular view of all entities

# Filter the graph
View > Filters > By Entity Type — show only IPs, only Emails, etc.

# Select all entities of one type
Right-click canvas > Select All [Entity Type]

# Remove low-value nodes
Select entities > Delete         — clean up info-only entities
```

### Exporting Investigation Results

```
# Export options
File > Export Graph > As PDF     — visual graph report
File > Export Graph > As Image   — PNG/SVG screenshot
File > Export Graph > To Spreadsheet — entity list as CSV/XLSX

# Copy entity values to clipboard
Select entities > Right-click > Copy to Clipboard

# Save investigation to share
File > Save Graph                — .mtgx file (Maltego native format)
```

### Using Maltego with Other Tools

```bash
# Import Nmap scan results as Maltego entities
# Use the PATERVA import tool or manual entity creation

# Combine with Shodan
# Install Shodan transform set → right-click IP → Shodan: To Open Ports

# Combine with theHarvester output
theHarvester -d example.com -b all -f results.xml
# Import results.xml into Maltego via File > Import

# Combine with Recon-ng
# Export recon-ng results and import email/domain entities
```

### Community Edition Limitations

| Feature | Community Edition | Professional |
|---------|-----------------|--------------|
| Transform results | Capped at 12 per transform | Unlimited |
| Graph size | Limited | Unlimited |
| Commercial use | Not allowed | Allowed |
| API integrations | Limited hub access | Full hub access |
| Price | Free | Paid license |

---

:::quiz{id="quiz-1"}
Q: What are "Transforms" in Maltego?
- [ ] Visual layout options for the graph
- [ ] Types of entities you can add to a graph
- [x] Queries that expand an entity by fetching data from external sources
- [ ] Export formats for investigation reports
:::

:::quiz{id="quiz-2"}
Q: Which Maltego Machine is best for passive-only infrastructure enumeration (no active scanning)?
- [x] Footprint L1
- [ ] Footprint L2
- [ ] Footprint L3
- [ ] Footprint Full
:::

:::quiz{id="quiz-3"}
Q: What is a key advantage of starting an investigation from an IP address entity?
- [ ] It automatically creates a person profile
- [ ] It exports results to a spreadsheet
- [x] You can find other domains hosted on the same IP, revealing shared infrastructure
- [ ] It runs faster than starting from a domain
:::

## Quick Reference

| Action | How To |
|--------|--------|
| New investigation | File > New Graph |
| Add entity | Drag from Entity Palette or double-click canvas |
| Run transform | Right-click entity > [Transform category] |
| Run all transforms | Right-click entity > Run All Transforms |
| Run a Machine | Machines menu > Run Machine |
| Change graph layout | View > Layouts > [Layout type] |
| Filter by entity type | View > Filters > By Entity Type |
| Merge duplicate entities | Select both > Edit > Merge Entities |
| Export graph | File > Export Graph > [Format] |
| Install transforms | Transforms > Transform Hub |
| Open entity editor | Double-click entity on graph |
| Undo last transform | Ctrl+Z / Cmd+Z |

## Entity Types Reference

| Entity | Icon | Common Transforms To Run |
|--------|------|--------------------------|
| Domain | Globe | DNS records, IPs, subdomains, emails, WHOIS |
| IP Address | Server | Domains, netblock, geolocation, open ports |
| Email Address | Envelope | Person, social profiles, breach check |
| Person | Person | Emails, social profiles, employer, phone |
| Organization | Building | Domains, people, locations, subsidiaries |
| Phone Number | Phone | Person, carrier, social accounts |
| URL | Link | Domain, IP, linked pages, technologies |
| Netblock | Network | IPs in range, owner, country |
