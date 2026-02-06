# Nmap

Nmap (Network Mapper) is a free, open-source tool for network discovery and security auditing. It's used to discover hosts and services on a network by sending packets and analyzing responses.

## Overview

Nmap is essential for:
- **Host Discovery**: Find live hosts on a network
- **Port Scanning**: Identify open ports on target systems
- **Service Detection**: Determine what services are running
- **OS Fingerprinting**: Identify the operating system of targets

### Installation

Nmap is pre-installed on most security-focused Linux distributions (Kali, Parrot). To install on other systems:

```bash
# Ubuntu/Debian
sudo apt install nmap

# macOS
brew install nmap

# Windows
# Download from https://nmap.org/download.html
```

:::command-builder{id="nmap-builder"}
tool_name: nmap
target_placeholder: "192.168.1.1"
scan_types:
  - name: "Ping Scan"
    flag: "-sn"
    desc: "Host discovery only, no port scan"
  - name: "SYN Scan"
    flag: "-sS"
    desc: "Stealthy half-open scan (requires root)"
  - name: "TCP Connect"
    flag: "-sT"
    desc: "Full TCP connection scan"
  - name: "UDP Scan"
    flag: "-sU"
    desc: "Scan UDP ports (slow)"
options:
  - name: "Version Detection"
    flag: "-sV"
    desc: "Probe open ports for service/version info"
  - name: "OS Detection"
    flag: "-O"
    desc: "Enable OS detection (requires root)"
  - name: "Fast Mode"
    flag: "-T4"
    desc: "Faster execution (aggressive timing)"
  - name: "All Ports"
    flag: "-p-"
    desc: "Scan all 65535 ports"
:::

## Basic Syntax

The basic Nmap command structure is:

```
nmap [scan type] [options] [target]
```

**Target formats:**
- Single IP: `192.168.1.1`
- IP range: `192.168.1.1-50`
- Subnet: `192.168.1.0/24`
- Hostname: `example.com`

---

:::scenario{id="scenario-1" level="beginner"}
title: "Discover Devices on Your Network"
goal: "Find all active devices connected to your local network without scanning their ports."
hint: "Use a ping scan (-sn) which only checks if hosts are up, without doing a port scan. This is fast and less intrusive."
command: "nmap -sn 192.168.1.0/24"
expected_output: |
  Starting Nmap 7.94 ( https://nmap.org )
  Nmap scan report for 192.168.1.1
  Host is up (0.0024s latency).
  Nmap scan report for 192.168.1.100
  Host is up (0.0031s latency).
  Nmap scan report for 192.168.1.105
  Host is up (0.0045s latency).
  Nmap done: 256 IP addresses (3 hosts up) scanned in 2.41 seconds
:::

:::scenario{id="scenario-2" level="beginner"}
title: "Find Open Ports on a Target"
goal: "Identify which ports are open on a specific host using the default scan."
hint: "A basic Nmap scan without extra options will perform a SYN scan on the most common 1000 ports."
command: "nmap 192.168.1.1"
expected_output: |
  Starting Nmap 7.94 ( https://nmap.org )
  Nmap scan report for 192.168.1.1
  Host is up (0.0023s latency).
  Not shown: 997 closed ports
  PORT    STATE SERVICE
  22/tcp  open  ssh
  80/tcp  open  http
  443/tcp open  https

  Nmap done: 1 IP address (1 host up) scanned in 1.23 seconds
:::

:::scenario{id="scenario-3" level="beginner"}
title: "Identify Running Services"
goal: "Determine what software and versions are running on open ports."
hint: "Use version detection (-sV) to probe open ports and identify the service name and version."
command: "nmap -sV 192.168.1.1"
expected_output: |
  Starting Nmap 7.94 ( https://nmap.org )
  Nmap scan report for 192.168.1.1
  Host is up (0.0021s latency).
  Not shown: 997 closed ports
  PORT    STATE SERVICE VERSION
  22/tcp  open  ssh     OpenSSH 8.9p1 Ubuntu 3
  80/tcp  open  http    Apache httpd 2.4.52
  443/tcp open  ssl/http Apache httpd 2.4.52

  Service detection performed.
  Nmap done: 1 IP address (1 host up) scanned in 11.42 seconds
:::

:::scenario{id="scenario-4" level="intermediate"}
title: "Detect Operating System"
goal: "Fingerprint the target's operating system using TCP/IP stack analysis."
hint: "OS detection (-O) requires root/admin privileges and works best when at least one open and one closed port are found."
command: "sudo nmap -O 192.168.1.1"
expected_output: |
  Starting Nmap 7.94 ( https://nmap.org )
  Nmap scan report for 192.168.1.1
  Host is up (0.0019s latency).
  Not shown: 997 closed ports
  PORT    STATE SERVICE
  22/tcp  open  ssh
  80/tcp  open  http
  443/tcp open  https
  Device type: general purpose
  Running: Linux 5.X
  OS CPE: cpe:/o:linux:linux_kernel:5
  OS details: Linux 5.4 - 5.19

  OS detection performed.
  Nmap done: 1 IP address (1 host up) scanned in 3.82 seconds
:::

:::scenario{id="scenario-5" level="intermediate"}
title: "Comprehensive Reconnaissance Scan"
goal: "Perform a thorough scan combining service detection, OS detection, and script scanning."
hint: "Combine multiple options: -sS for SYN scan, -sV for versions, -O for OS, and -T4 for faster timing. The -A flag is a shortcut for aggressive scanning."
command: "sudo nmap -sS -sV -O -T4 192.168.1.1"
expected_output: |
  Starting Nmap 7.94 ( https://nmap.org )
  Nmap scan report for 192.168.1.1
  Host is up (0.0018s latency).
  Not shown: 997 closed ports
  PORT    STATE SERVICE VERSION
  22/tcp  open  ssh     OpenSSH 8.9p1 Ubuntu 3
  80/tcp  open  http    Apache httpd 2.4.52 ((Ubuntu))
  443/tcp open  ssl/http Apache httpd 2.4.52 ((Ubuntu))
  Device type: general purpose
  Running: Linux 5.X
  OS CPE: cpe:/o:linux:linux_kernel:5
  OS details: Linux 5.4 - 5.19

  OS and Service detection performed.
  Nmap done: 1 IP address (1 host up) scanned in 15.67 seconds
:::

## Tips & Tricks

### Speed vs Stealth

Nmap timing templates range from `-T0` (paranoid) to `-T5` (insane):

| Template | Name | Use Case |
|----------|------|----------|
| `-T0` | Paranoid | IDS evasion |
| `-T1` | Sneaky | IDS evasion |
| `-T2` | Polite | Reduced bandwidth |
| `-T3` | Normal | Default |
| `-T4` | Aggressive | Fast, reliable networks |
| `-T5` | Insane | Very fast, may miss ports |

### Save Output

Save scan results for later analysis:

```bash
# Normal output
nmap -oN scan.txt target

# All formats (normal, XML, grepable)
nmap -oA scan target
```

### Scan Specific Ports

```bash
# Single port
nmap -p 80 target

# Port range
nmap -p 1-1000 target

# Multiple ports
nmap -p 22,80,443 target

# All ports
nmap -p- target
```

### Common Port Shortcuts

```bash
# Top 100 ports
nmap --top-ports 100 target

# Fast scan (top 100)
nmap -F target
```

---

:::quiz{id="quiz-1"}
Q: Which Nmap flag performs a ping scan to discover hosts without port scanning?
- [ ] -sS
- [ ] -sT
- [x] -sn
- [ ] -sV
:::

:::quiz{id="quiz-2"}
Q: What flag enables service version detection?
- [ ] -O
- [x] -sV
- [ ] -sS
- [ ] -A
:::

:::quiz{id="quiz-3"}
Q: Which timing template is recommended for fast scans on reliable networks?
- [ ] -T1
- [ ] -T2
- [x] -T4
- [ ] -T5
:::

## Quick Reference

| Flag | Purpose |
|------|---------|
| `-sn` | Ping scan (host discovery) |
| `-sS` | SYN scan (stealth) |
| `-sT` | TCP connect scan |
| `-sU` | UDP scan |
| `-sV` | Version detection |
| `-O` | OS detection |
| `-A` | Aggressive (OS + version + scripts) |
| `-T4` | Fast timing |
| `-p-` | All 65535 ports |
| `-oN` | Save normal output |
| `-oA` | Save all formats |
