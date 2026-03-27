# Hashcat

Hashcat is the world's fastest and most advanced password recovery tool. It uses GPU acceleration to crack password hashes at billions of attempts per second, supporting over 300 hash types including MD5, SHA, NTLM, bcrypt, and SSH private key passphrases. It is used by penetration testers to validate password strength and recover credentials from captured hashes.

## Overview

Hashcat is essential for:
- **Password Auditing**: Test whether an organization's passwords can be cracked in a realistic timeframe
- **Post-Exploitation**: Recover plaintext passwords from dumped hashes (Windows NTLM, Linux shadow, etc.)
- **SSH Passphrase Recovery**: Crack encrypted SSH private key passphrases discovered during assessments
- **CTF Challenges**: Solve hash-cracking challenges in competitions

### Installation

Hashcat is pre-installed on Kali Linux. For other systems:

```bash
# Ubuntu/Debian
sudo apt install hashcat

# macOS
brew install hashcat

# Verify GPU support (recommended for performance)
hashcat -I
```

:::command-builder{id="hashcat-builder"}
tool_name: hashcat
target_placeholder: "hashes.txt"
scan_types:
  - name: "Dictionary Attack"
    flag: "-a 0"
    desc: "Try every word in a wordlist (most common)"
  - name: "Brute Force / Mask"
    flag: "-a 3"
    desc: "Try all combinations matching a pattern"
  - name: "Rule-Based Attack"
    flag: "-a 0 -r"
    desc: "Apply transformation rules to a wordlist"
  - name: "Combinator Attack"
    flag: "-a 1"
    desc: "Combine words from two wordlists"
options:
  - name: "Hash Type"
    flag: "-m"
    desc: "Specify the hash type (e.g., -m 0 for MD5)"
  - name: "Show Cracked"
    flag: "--show"
    desc: "Display previously cracked hashes"
  - name: "Output File"
    flag: "-o"
    desc: "Save cracked passwords to a file"
  - name: "Status Update"
    flag: "--status"
    desc: "Automatically show cracking progress"
:::

## Basic Syntax

The basic Hashcat command structure is:

```
hashcat -m [hash-type] -a [attack-mode] [hashfile] [wordlist/mask]
```

**Common hash types (`-m`):**

| Flag | Hash Type | Where It Appears |
|------|-----------|-----------------|
| `-m 0` | MD5 | Web apps, old databases |
| `-m 100` | SHA-1 | Git commits, old web apps |
| `-m 1000` | NTLM | Windows login credentials |
| `-m 1800` | SHA-512crypt (`$6$`) | Modern Linux `/etc/shadow` |
| `-m 3200` | bcrypt (`$2*$`) | Modern web apps (slow to crack) |
| `-m 22000` | WPA-PBKDF2 | Wi-Fi handshake captures |
| `-m 22921` | RSA/DSA/EC/OpenSSH Private Keys | SSH key passphrases |

---

:::scenario{id="scenario-1" level="beginner"}
title: "Crack MD5 Hashes with a Wordlist"
goal: "Use the rockyou wordlist to crack a set of MD5 hashes from a captured database dump."
hint: "MD5 (-m 0) with a dictionary attack (-a 0) against rockyou.txt is the most common starting point. Hashcat checks billions of MD5 hashes per second on a GPU."
command: "hashcat -m 0 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt"
expected_output: |
  hashcat (v6.2.6) starting...

  OpenCL API (OpenCL 3.0): Platform #1
  * Device #1: NVIDIA GeForce RTX 3080, 9824/10017 MB

  Dictionary cache built:
  * Filename..: /usr/share/wordlists/rockyou.txt
  * Passwords.: 14344391
  * Bytes.....: 139921497

  5f4dcc3b5aa765d61d8327deb882cf99:password
  e99a18c428cb38d5f260853678922e03:abc123
  d8578edf8458ce06fbc5bb76a58c5ca4:qwerty

  Session..........: hashcat
  Status...........: Cracked
  Hash.Type........: MD5
  Time.Started.....: 0 secs ago
  Recovered........: 3/3 (100.00%)
:::

:::scenario{id="scenario-2" level="beginner"}
title: "Crack Windows NTLM Hashes"
goal: "Recover plaintext passwords from NTLM hashes dumped from a Windows system."
hint: "NTLM hashes (-m 1000) are extracted from Windows SAM databases or via tools like Mimikatz. They crack extremely fast — a single GPU can test 100+ billion NTLM hashes per second."
command: "hashcat -m 1000 -a 0 ntlm_hashes.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule"
expected_output: |
  hashcat (v6.2.6) starting...

  * Device #1: NVIDIA GeForce RTX 3080

  31d6cfe0d16ae931b73c59d7e0c089c0:
  aad3b435b51404eeaad3b435b51404ee:(empty — blank password)
  e19ccf75ee54e06b1f5f94d1db5ab3ee:Summer2023!
  8846f7eaee8fb117ad06bdd830b7586c:Password1

  Recovered........: 3/4 (75.00%)
  Speed.#1.........: 98432.1 MH/s (NTLM is very fast to crack)
:::

:::scenario{id="scenario-3" level="beginner"}
title: "Use a Mask Attack for Pattern-Based Passwords"
goal: "Crack passwords that follow a known pattern — e.g., a capital letter, 5 lowercase letters, and 2 digits."
hint: "Mask attacks replace brute force guessing by defining character sets per position. ?u=uppercase, ?l=lowercase, ?d=digit, ?s=special. This is much faster than pure brute force."
command: "hashcat -m 0 -a 3 hashes.txt ?u?l?l?l?l?l?d?d"
expected_output: |
  hashcat (v6.2.6) starting...

  Mask: ?u?l?l?l?l?l?d?d [8 chars]
  Keyspace: 3276800000

  5e8aef3a09a1f609d1af91f2e32c65a2:Monkey42
  c07b9ff2e7e23c19e4d5b78f3ac023a1:Summer23
  a1b2c3d4e5f6789012345678abcdef01:Winter99

  Recovered........: 3/5 (60.00%)
  Time.Elapsed.....: 4 mins, 12 secs
:::

:::scenario{id="scenario-4" level="intermediate"}
title: "Crack an SSH Private Key Passphrase"
goal: "Recover the passphrase protecting an SSH private key found during a penetration test."
hint: "Encrypted SSH private keys have their passphrase hashed internally. Use ssh2john to extract the crackable hash first, then feed it to hashcat with -m 22921. This is a common post-exploitation step when you find a key but can't use it."
command: "ssh2john id_rsa > ssh_hash.txt\nhashcat -m 22921 -a 0 ssh_hash.txt /usr/share/wordlists/rockyou.txt"
expected_output: |
  # Step 1: Extract the hash from the SSH key
  $ ssh2john id_rsa > ssh_hash.txt
  $ cat ssh_hash.txt
  id_rsa:$sshng$2$16$...long hash...$

  # Step 2: Crack with hashcat
  hashcat (v6.2.6) starting...
  * Hash mode #22921: RSA/DSA/EC/OpenSSH Private Keys

  $sshng$2$16$...hash...:butterfly123

  Recovered........: 1/1 (100.00%)

  # Step 3: Use the recovered passphrase to connect
  $ ssh -i id_rsa user@target.com
  Enter passphrase for key 'id_rsa': butterfly123
  Welcome to Ubuntu 22.04...
:::

:::scenario{id="scenario-5" level="intermediate"}
title: "Rule-Based Attack to Maximize Wordlist Coverage"
goal: "Apply transformation rules to a wordlist to crack passwords with common substitutions and suffixes."
hint: "Rules transform wordlist entries — e.g., 'password' becomes 'P@ssw0rd!'. The best64.rule file ships with hashcat and covers the most common real-world password mutations. Combine with rockyou.txt for maximum coverage."
command: "hashcat -m 1800 -a 0 shadow_hashes.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule -o cracked.txt --status"
expected_output: |
  hashcat (v6.2.6) starting...
  * Hash mode #1800: sha512crypt $6$, SHA512 (Unix)
  * Rules: /usr/share/hashcat/rules/best64.rule (77 rules)

  [s]tatus [p]ause [b]ypass [c]heckpoint [f]inish [q]uit

  Session..........: hashcat
  Status...........: Running
  Hash.Type........: sha512crypt $6$, SHA512 (Unix)
  Time.Started.....: Fri Feb 20 14:32:01 2026
  Speed.#1.........: 12345 H/s
  Recovered........: 2/10 (20.00%)
  Progress.........: 1107936/1107936 (100.00%)

  Results saved to: cracked.txt
  $6$rounds=5000$salt$longhash:Welcome1!
  $6$rounds=5000$salt$longhash:P@ssw0rd
:::

## Password Lists

The wordlist you use is as important as the tool. Password cracking is only as good as your wordlist.

### Essential Wordlists

| Wordlist | Size | Best For |
|----------|------|---------|
| **rockyou.txt** | 14M passwords | Starting point for almost every crack — from the 2009 RockYou breach |
| **SecLists** | Huge collection | Specialized lists: common passwords, usernames, web content |
| **Kaonashi** | 1.4B passwords | Large merged breach data — high coverage |
| **CrackStation** | 1.5B passwords | Pre-built lookup tables for common hashes |
| **Custom wordlist** | Varies | Built from target context (company name, location, sports teams) |

### Where to Get Wordlists

```bash
# rockyou.txt — already on Kali at:
/usr/share/wordlists/rockyou.txt.gz
gunzip /usr/share/wordlists/rockyou.txt.gz

# SecLists (comprehensive collection)
sudo apt install seclists
# Located at: /usr/share/seclists/

# Or clone directly
git clone https://github.com/danielmiessler/SecLists.git
```

### Building a Targeted Wordlist with CeWL

```bash
# Spider a target website and generate a custom wordlist
cewl https://targetcompany.com -d 3 -m 6 -w custom.txt

# Combine with rules for company-specific passwords
hashcat -m 1000 hashes.txt custom.txt -r /usr/share/hashcat/rules/best64.rule
```

### SSH and Password Lists

When attacking SSH services, password lists are used differently:

- **Online attacks** (Hydra/Medusa): Try passwords directly against the SSH service — slow, detectable, often rate-limited
- **Offline attacks** (Hashcat): Crack the passphrase of a captured SSH private key — fast, undetectable by the target

```bash
# Online SSH brute force (use sparingly — leaves log entries)
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.10

# Offline SSH key passphrase cracking (preferred — no network noise)
ssh2john id_rsa > hash.txt
hashcat -m 22921 hash.txt /usr/share/wordlists/rockyou.txt
```

---

## Other Password Cracking Tools

Hashcat is not the only tool in the password cracking arsenal. Each has different strengths:

| Tool | Type | Best For |
|------|------|---------|
| **John the Ripper (JtR)** | Offline / CPU+GPU | Versatile; built-in format auto-detection; great for SSH keys via `ssh2john` |
| **Hydra** | Online | Brute-forcing live services: SSH, FTP, HTTP login forms, RDP |
| **Medusa** | Online | Parallel online brute force — faster than Hydra for multiple hosts |
| **CrackStation** | Online lookup | Instant lookup of common MD5/SHA hashes — no cracking needed |
| **Ophcrack** | Offline / Rainbow tables | Windows NTLM cracking using pre-computed rainbow tables |

### John the Ripper (JtR)

John is hashcat's closest counterpart — CPU-focused, with excellent format auto-detection. Its `*2john` utility family converts many file formats into crackable hashes:

```bash
# Auto-detect hash format and crack
john hashes.txt --wordlist=/usr/share/wordlists/rockyou.txt

# Convert SSH key to crackable format
ssh2john id_rsa > ssh.hash
john ssh.hash --wordlist=/usr/share/wordlists/rockyou.txt

# Convert ZIP password to crackable format
zip2john protected.zip > zip.hash
john zip.hash --wordlist=/usr/share/wordlists/rockyou.txt

# Show cracked passwords
john --show hashes.txt
```

### Hydra (Online SSH Brute Force)

Hydra attacks live services directly. Use only with authorization — it generates significant log noise:

```bash
# SSH brute force with a username list and password list
hydra -L users.txt -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.10

# SSH with known username, limit rate to avoid lockout
hydra -l admin -P passwords.txt -t 4 ssh://192.168.1.10

# HTTP POST login form
hydra -l admin -P rockyou.txt 192.168.1.10 http-post-form \
  "/login:username=^USER^&password=^PASS^:Invalid credentials"
```

---

:::quiz{id="quiz-1"}
Q: Which hashcat attack mode uses a wordlist to try passwords?
- [x] -a 0 (Dictionary attack)
- [ ] -a 1 (Combinator attack)
- [ ] -a 3 (Brute force / Mask attack)
- [ ] -a 6 (Hybrid attack)
:::

:::quiz{id="quiz-2"}
Q: What tool must you use to prepare an SSH private key for cracking with hashcat?
- [ ] hashcat --convert
- [ ] keydump
- [x] ssh2john
- [ ] openssl pkcs8
:::

:::quiz{id="quiz-3"}
Q: What is the key difference between offline password cracking (hashcat) and online brute forcing (hydra)?
- [ ] Offline cracking requires network access to the target
- [x] Offline cracking works on captured hashes without contacting the target; online brute force sends attempts directly to a live service
- [ ] Hydra is faster than hashcat for all hash types
- [ ] Offline cracking only works on Windows hashes
:::

## Quick Reference

| Flag | Purpose |
|------|---------|
| `-m 0` | MD5 hash type |
| `-m 1000` | NTLM (Windows) hash type |
| `-m 1800` | SHA-512crypt Unix hash type |
| `-m 22921` | OpenSSH private key passphrase |
| `-a 0` | Dictionary attack |
| `-a 3` | Brute force / mask attack |
| `-a 1` | Combinator attack |
| `-r FILE` | Apply rules file |
| `-o FILE` | Save cracked results to file |
| `--show` | Display previously cracked hashes |
| `--status` | Show live progress during cracking |
| `-w 3` | Workload profile (1=low, 4=high) |
| `-O` | Optimized kernels (faster, shorter passwords only) |
| `--increment` | Auto-increment mask length |
| `-I` | Show detected GPU/OpenCL devices |

## Mask Character Sets

| Mask | Character Set | Example |
|------|--------------|---------|
| `?l` | Lowercase a-z | `?l?l?l?l` = four lowercase letters |
| `?u` | Uppercase A-Z | `?u?l?l?l` = capital + 3 lowercase |
| `?d` | Digits 0-9 | `?d?d?d?d` = four digit PIN |
| `?s` | Special chars | `?l?l?l?s` = three letters + symbol |
| `?a` | All printable | `?a?a?a?a?a?a?a?a` = any 8-char password |
| `?h` | Hex lowercase | Used for hash generation |
