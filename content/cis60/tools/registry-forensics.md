# Registry Forensics

The Windows Registry is a hierarchical database that stores configuration settings and user activity. It is one of the richest sources of forensic artifacts — revealing recently opened files, typed URLs, connected USB devices, installed software, user accounts, and system configuration — much of which never appears anywhere else on disk.

## Overview

Registry hives are binary files. Six hives appear in nearly every investigation:

| Hive File | Location on Disk | Scope | Key Evidence |
|-----------|-----------------|-------|-------------|
| **NTUSER.DAT** | `C:\Users\<username>\` | Per-user | Recent files, typed URLs, UserAssist run counts, MRU lists |
| **UsrClass.dat** | `C:\Users\<username>\AppData\Local\Microsoft\Windows\` | Per-user | Shellbags — folder sizes, positions, access times |
| **SAM** | `C:\Windows\System32\config\` | System-wide | User accounts, RIDs, login counts, password dates |
| **SECURITY** | `C:\Windows\System32\config\` | System-wide | Audit policy, cached credentials |
| **SYSTEM** | `C:\Windows\System32\config\` | System-wide | Computer name, USB history, NIC/IP config, shutdown time |
| **SOFTWARE** | `C:\Windows\System32\config\` | System-wide | Installed programs, default browser, run keys |

> Each hive has a paired transaction log (e.g., `NTUSER.DAT.LOG`). Always export the log alongside the hive — it may contain changes not yet committed to the main file.

---

## Tool Comparison

| Task | Windows (GUI) | Linux / Kali (CLI) |
|------|-------------|-------------------|
| Navigate hive in disk image | FTK Imager — Evidence Tree | `reglookup -p / <hivefile>` or mount with `libregf` |
| Export hives from live system | FTK Imager > Obtain Protected Files | `cp` from mounted image; `reg export` in cmd.exe |
| Export hives from disk image | FTK Imager > right-click > Export Files | `icat`/`tsk_recover` from TSK; or mount E01 with `ewfmount` |
| Parse hive — all plugins | RegRipper v2.8 GUI (rr.exe) | `rip.pl -r <hivefile> -f <profile>` |
| Parse hive — single plugin | RegRipper > select profile | `rip.pl -r <hivefile> -p <plugin>` |
| Browse hive interactively | Registry Explorer (Zimmerman) | `hivexsh <hivefile>` |
| List all keys/values | RegRipper report | `reglookup <hivefile>` |
| Search strings in hive | Notepad > Find in report | `reglookup <hivefile> \| grep -i keyword` |

---

## Registry Hive Locations (Quick Reference)

```
# System-wide hives (all in same folder)
C:\Windows\System32\config\SAM
C:\Windows\System32\config\SECURITY
C:\Windows\System32\config\SYSTEM
C:\Windows\System32\config\SOFTWARE

# Per-user hives (one set per account)
C:\Users\<username>\NTUSER.DAT
C:\Users\<username>\AppData\Local\Microsoft\Windows\UsrClass.dat

# On a mounted disk image (Linux path example)
/mnt/windows/Windows/System32/config/SYSTEM
/mnt/windows/Users/<username>/NTUSER.DAT
```

---

:::command-builder{id="regripper-builder"}
tool_name: rip.pl
target_placeholder: "NTUSER.DAT"
scan_types:
  - name: "NTUSER — All Plugins"
    flag: "-r NTUSER.DAT -f ntuser"
    desc: "Run all NTUSER.DAT plugins: recent files, URLs, UserAssist, MRU lists"
  - name: "SAM — All Plugins"
    flag: "-r SAM -f sam"
    desc: "Parse user accounts, RIDs, login counts, password dates"
  - name: "SYSTEM — All Plugins"
    flag: "-r SYSTEM -f system"
    desc: "Computer name, USB history, NIC config, shutdown time, services"
  - name: "SOFTWARE — All Plugins"
    flag: "-r SOFTWARE -f software"
    desc: "Installed software, default browser, run keys, application paths"
  - name: "Recent Files (MRU)"
    flag: "-r NTUSER.DAT -p recentdocs"
    desc: "List recently opened documents from NTUSER.DAT RecentDocs key"
  - name: "Typed URLs"
    flag: "-r NTUSER.DAT -p typedurls"
    desc: "URLs typed in Internet Explorer / Edge from NTUSER.DAT"
  - name: "UserAssist (Execution)"
    flag: "-r NTUSER.DAT -p userassist"
    desc: "Programs run by the user, run count, and last-run timestamp"
  - name: "USB Devices"
    flag: "-r SYSTEM -p usbstor"
    desc: "USB storage devices ever connected: Vendor ID, serial number, last connect time"
  - name: "Computer Name"
    flag: "-r SYSTEM -p compname"
    desc: "Hostname and TCP/IP hostname from SYSTEM hive"
  - name: "Shutdown Time"
    flag: "-r SYSTEM -p shutdown"
    desc: "Last clean shutdown timestamp from SYSTEM hive"
options:
  - name: "Output to file"
    flag: "> report.txt"
    desc: "Redirect plugin output to a text file for review"
  - name: "List available plugins"
    flag: "-l"
    desc: "Print all available RegRipper plugins"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Locate Registry Hives in a Disk Image"
goal: "Use FTK Imager (Windows) or reglookup (Kali) to navigate to the registry hive files in a disk image and confirm their locations before exporting."
hint: "In FTK Imager, load the E01 image as an Evidence Item, expand the partition (NONAME [NTFS]), open the root folder, then browse WINDOWS > System32 > config to see SAM, SECURITY, SYSTEM, SOFTWARE. The per-user NTUSER.DAT lives in Documents and Settings (XP) or Users (Vista+) under each username's folder. On Kali with a mounted image, the path is /mnt/windows/Windows/System32/config/. The hive files have no extension and no icon — they look like plain files. Always export the matching .LOG transaction log file alongside each hive."
command: reglookup -p / /mnt/evidence/SYSTEM | head -20
expected_output: |
  Kali — list root keys of SYSTEM hive:
    reglookup -p / /mnt/evidence/SYSTEM
    PATH,TYPE,VALUE,MTIME
    /,KEY,,2014-11-12T12:33:03Z
    /ControlSet001,KEY,,2014-11-12T12:33:03Z
    /ControlSet001/Control,KEY,,2014-11-12T12:33:03Z
    /ControlSet001/Enum,KEY,,2014-11-12T12:33:03Z
    /ControlSet001/Hardware,KEY,,2014-11-12T12:33:03Z
    /ControlSet001/Services,KEY,,2014-11-12T12:33:03Z
    /Select,KEY,,2012-10-12T13:36:07Z

  Windows FTK Imager path:
    Evidence Tree > C_drive.E01 > NONAME [NTFS] > [root] > WINDOWS > System32 > config
    Files visible in File List pane: SAM, SAM.LOG, SECURITY, SECURITY.LOG,
      SOFTWARE, SOFTWARE.LOG, SYSTEM, SYSTEM.LOG

  Key files to export (always grab the .LOG too):
    SAM + SAM.LOG
    SECURITY + SECURITY.LOG
    SYSTEM + SYSTEM.LOG
    SOFTWARE + SOFTWARE.LOG
    NTUSER.DAT + NTUSER.DAT.LOG  (from each user folder)
    UsrClass.dat + UsrClass.dat.LOG
:::

:::scenario{id="task-2" level="beginner"}
title: "Task 2 — Export Registry Files from a Live System"
goal: "Understand how to collect registry hives from a running Windows system. On Windows use FTK Imager's Obtain Protected Files. On Kali, use reg.exe over a remote share or copy from a mounted image."
hint: "On a live Windows system, the SAM, SECURITY, SYSTEM, and SOFTWARE files are locked by the OS — you cannot copy them with File Explorer. FTK Imager's File > Obtain Protected Files feature uses Volume Shadow Copy to extract them. Select 'Password recovery and all registry files' to get everything except UsrClass.dat (which can be copied normally). On Kali, if you have admin access to a live Windows target, you can use: reg save HKLM\SAM /tmp/SAM.hiv over a shared drive or via impacket-reg."
command: sudo cp /mnt/windows/Windows/System32/config/SYSTEM /mnt/evidence/SYSTEM
expected_output: |
  Kali — copy hives from mounted Windows image (offline):
    sudo mount -o loop,ro evidence.img /mnt/windows
    sudo cp /mnt/windows/Windows/System32/config/SAM      /mnt/evidence/
    sudo cp /mnt/windows/Windows/System32/config/SYSTEM   /mnt/evidence/
    sudo cp /mnt/windows/Windows/System32/config/SOFTWARE /mnt/evidence/
    sudo cp /mnt/windows/Windows/System32/config/SECURITY /mnt/evidence/
    # Also grab transaction logs
    sudo cp /mnt/windows/Windows/System32/config/SYSTEM.LOG /mnt/evidence/

  Windows FTK Imager live export:
    File > Obtain Protected Files
    Select: "Password recovery and all registry files"
    Browse to output folder on evidence drive
    Click OK
    Result: all system hives + NTUSER.DAT files saved to destination folder

  Verify files were collected:
    ls -lh /mnt/evidence/
    -rw-r--r-- 1 root root 256K SAM
    -rw-r--r-- 1 root root  64K SECURITY
    -rw-r--r-- 1 root root 3.8M SYSTEM
    -rw-r--r-- 1 root root  10M SOFTWARE
:::

:::scenario{id="task-3" level="beginner"}
title: "Task 3 — Parse Hives with RegRipper"
goal: "Run RegRipper against the exported hive files to generate text reports. Parse NTUSER.DAT, SAM, SYSTEM, and SOFTWARE using their matching profiles."
hint: "RegRipper profiles match hive names: ntuser, sam, system, software, security. On Windows, open rr.exe, browse to the hive file, set a report file path on the evidence drive, select the matching profile, then click Rip It. On Kali, rip.pl is the CLI equivalent — use -r for the hive file and -f for the profile. 'Plugins completed with errors' is normal — some plugins look for keys that don't exist on every system. Always save reports with descriptive names (SAM_report.txt, SYSTEM_report.txt) so you can identify them later."
command: rip.pl -r /mnt/evidence/NTUSER.DAT -f ntuser > /mnt/evidence/reports/NTUSER_report.txt
expected_output: |
  Kali — parse all four main hives:
    rip.pl -r /mnt/evidence/NTUSER.DAT -f ntuser  > /mnt/evidence/reports/NTUSER_report.txt
    rip.pl -r /mnt/evidence/SAM        -f sam      > /mnt/evidence/reports/SAM_report.txt
    rip.pl -r /mnt/evidence/SYSTEM     -f system   > /mnt/evidence/reports/SYSTEM_report.txt
    rip.pl -r /mnt/evidence/SOFTWARE   -f software > /mnt/evidence/reports/SOFTWARE_report.txt

  Terminal output while running (normal):
    winrar...Done.
    winrar2...Done.
    winscp...Done.
    winscp_sessions...Done.
    winvnc...Done.
    winzip...Done.
    wordwheelquery...Done.
    yahoo_cu...Done.
    0 plugins completed with errors.

  Verify reports were created:
    ls -lh /mnt/evidence/reports/
    -rw-r--r-- 1 root root 264K NTUSER_report.txt
    -rw-r--r-- 1 root root   5K SAM_report.txt
    -rw-r--r-- 1 root root 234K SYSTEM_report.txt
    -rw-r--r-- 1 root root 530K SOFTWARE_report.txt
:::

:::scenario{id="task-4" level="intermediate"}
title: "Task 4 — NTUSER.DAT Artifacts: Recent Files, Typed URLs, UserAssist"
goal: "Search the NTUSER.DAT report for three key artifact types: recently opened documents (RecentDocs), URLs typed in the browser (TypedURLs), and programs the user ran (UserAssist)."
hint: "Use grep on Kali or Ctrl+F in Notepad on Windows. RecentDocs entries are in MRUList order — the item at the top was opened most recently. Each file also appears in a sub-key sorted by extension (.txt, .zip, .pcap) which is useful for filtering by file type. TypedURLs lists URLs in order of most-recently-typed first (url1 = most recent). UserAssist shows each executable with a run count in brackets and a last-run UTC timestamp. All times in RegRipper output are UTC — convert to local time for your report."
command: grep -A 20 "recentdocs" /mnt/evidence/reports/NTUSER_report.txt | head -30
expected_output: |
  Kali — search NTUSER.DAT report:

  # Recently opened documents
  grep -A 20 "RecentDocs" /mnt/evidence/reports/NTUSER_report.txt | head -40
    recentdocs v.20100405
    (NTUSER.DAT) Gets contents of user's RecentDocs key
    RecentDocs
    Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs
    LastWrite Time Wed Nov 12 12:32:33 2014 (UTC)
    13 = ---README---.txt     ← most recently opened
    7 = Wallpaper
    12 = nothing-here.txt.txt
    ...

  # URLs typed in IE/Edge
  grep -A 15 "TypedURLs" /mnt/evidence/reports/NTUSER_report.txt
    typedurls v.20080924
    TypedURLs
    LastWrite Time Wed Nov 12 12:06:56 2014 (UTC)
    url1 -> http://google.com/   ← most recently typed
    url2 -> elcar.com.txt
    url3 -> http://www.bing.com/search?q=elcar+test+file...

  # Programs run by user (UserAssist)
  grep -A 30 "UserAssist" /mnt/evidence/reports/NTUSER_report.txt | head -40
    userassist v.20170714
    Wed Nov 12 12:08:48 2014 Z
      UEME_RUNPATH:C:\Program Files\Internet Explorer\iexplore.exe (25)
      UEME_RUNPIDL (35)
    Wed Nov 12 12:12:56 2014 Z
      UEME_RUNPATH:C:\WINDOWS\system32\NOTEPAD.EXE (5)
:::

:::scenario{id="task-5" level="intermediate"}
title: "Task 5 — SAM and SYSTEM Artifacts: User Accounts and USB History"
goal: "Extract user account details from SAM (username, RID, login count, password dates) and USB device history from SYSTEM (Vendor ID, serial number, last connection time)."
hint: "In the SAM report, look for the 'User Information' section. Each user has a Relative Identifier (RID) — built-in Administrator is always RID 500, Guest is 501. User-created accounts start at RID 1000 and increment. A gap in RIDs means an account was deleted. In the SYSTEM report, search for USBStor — each entry shows the Vendor/Product ID and serial number with the date last connected. Match the GUID in USBStor to the network adapter GUID from the Network Key to identify IP addresses assigned to specific adapters."
command: grep -A 15 "User Information" /mnt/evidence/reports/SAM_report.txt
expected_output: |
  Kali — SAM user accounts:
    grep -A 15 "User Information" /mnt/evidence/reports/SAM_report.txt
      User Information
      Username   : IEUser [1003]
      SID        : S-1-5-21-776561741-308236825-1417001333-1003
      Account Type    : Default Admin User
      Account Created : Fri Oct 12 20:47:08 2012 Z
      Last Login Date : Wed Nov 12 19:35:13 2014 Z
      Pwd Reset Date  : Thu Oct 31 21:26:00 2013 Z
      Pwd Fail Date   : Thu Oct 31 21:30:48 2013 Z
      Login Count     : 76
      --> Password does not expire
      --> Normal user account

  Kali — SYSTEM USB history:
    grep -A 10 "USBStor" /mnt/evidence/reports/SYSTEM_report.txt
      usbstor v.20141111
      (System) Get USBStor key info
      USBStor
      ControlSet001\Enum\USB
      ROOT_HUB [Fri Oct 12 13:36:07 2012]
        S/N: 4&24d6eb65&0  [Wed Nov 12 22:35:07 2014]   ← last connected
      Vid_80ee&Pid_0021 [Fri Oct 12 13:36:07 2012]
        S/N: 5&18f54cb7&0&1 [Wed Nov 12 22:35:07 2014]

  Kali — SYSTEM computer name and shutdown time:
    rip.pl -r /mnt/evidence/SYSTEM -p compname
      ComputerName = IE8WINXP
    rip.pl -r /mnt/evidence/SYSTEM -p shutdown
      ShutdownTime = Wed Nov 12 12:33:03 2014 (UTC)
      ShutdownCount = 48
:::

---

## Full Kali Workflow

End-to-end: copy hives from a mounted image, parse all four main hives, search for key artifacts.

```bash
# --- SETUP ---

# Mount the evidence image (read-only)
sudo mkdir -p /mnt/windows /mnt/evidence/reports
sudo mount -o loop,ro /path/to/evidence.img /mnt/windows
# For E01: sudo ewfmount image.E01 /mnt/ewf && sudo mount -o ro /mnt/ewf/ewf1 /mnt/windows

# --- COLLECT HIVES ---

# System-wide hives
sudo cp /mnt/windows/Windows/System32/config/SAM      /mnt/evidence/
sudo cp /mnt/windows/Windows/System32/config/SYSTEM   /mnt/evidence/
sudo cp /mnt/windows/Windows/System32/config/SOFTWARE /mnt/evidence/
sudo cp /mnt/windows/Windows/System32/config/SECURITY /mnt/evidence/
sudo cp /mnt/windows/Windows/System32/config/SAM.LOG      /mnt/evidence/
sudo cp /mnt/windows/Windows/System32/config/SYSTEM.LOG   /mnt/evidence/

# Per-user hive (adjust username)
sudo cp "/mnt/windows/Users/IEUser/NTUSER.DAT"         /mnt/evidence/
sudo cp "/mnt/windows/Users/IEUser/NTUSER.DAT.LOG"     /mnt/evidence/

# Hash for integrity
sha256sum /mnt/evidence/SYSTEM > /mnt/evidence/SYSTEM.sha256

# --- PARSE WITH REGRIPPER ---

# Install if needed: sudo apt install regripper
rip.pl -r /mnt/evidence/NTUSER.DAT -f ntuser  > /mnt/evidence/reports/NTUSER_report.txt
rip.pl -r /mnt/evidence/SAM        -f sam      > /mnt/evidence/reports/SAM_report.txt
rip.pl -r /mnt/evidence/SYSTEM     -f system   > /mnt/evidence/reports/SYSTEM_report.txt
rip.pl -r /mnt/evidence/SOFTWARE   -f software > /mnt/evidence/reports/SOFTWARE_report.txt

# --- TARGETED ARTIFACT EXTRACTION ---

# Recent documents
rip.pl -r /mnt/evidence/NTUSER.DAT -p recentdocs

# Typed URLs
rip.pl -r /mnt/evidence/NTUSER.DAT -p typedurls

# Program execution history
rip.pl -r /mnt/evidence/NTUSER.DAT -p userassist

# USB devices connected
rip.pl -r /mnt/evidence/SYSTEM -p usbstor

# Computer name + shutdown time
rip.pl -r /mnt/evidence/SYSTEM -p compname
rip.pl -r /mnt/evidence/SYSTEM -p shutdown

# --- SEARCH REPORTS ---

# Find keyword across all reports
grep -i "password\|passwd\|secret" /mnt/evidence/reports/*.txt

# Browse hive interactively (alternative to RegRipper)
reglookup /mnt/evidence/NTUSER.DAT | grep -i "recentdocs"

# List all keys with timestamps
reglookup -t KEY /mnt/evidence/SYSTEM | sort -t',' -k4
```

---

## Key Concepts

### MRUList Order

Most Recently Used (MRU) lists assign a letter or number to each entry. The item **at the top of the list is the most recently accessed** — but its letter is not necessarily `a`. The letter reflects the order in which items were first added. If `office.doc` was added first (gets letter `a`) and `readme.txt` was added later (gets letter `b`), then `readme.txt` was opened again most recently, it appears at the top but keeps letter `b`. The `LastWriteTime` on the key is the time that top item was last accessed.

### RIDs and Account Deletion

Relative Identifiers (RIDs) are unique integers assigned to each account:
- `500` — built-in Administrator (always)
- `501` — built-in Guest (always)
- `1000+` — user-created accounts (increment with each new account)

A **gap in RIDs** (e.g., 1000, 1001, 1003 — no 1002) indicates an account was created and then deleted. RIDs are never reused.

### Transaction Logs and Dirty Hives

If a system crashes or loses power during a registry write, the hive may be marked **dirty** — meaning committed changes are in the `.LOG` file but not yet in the main hive. RegRipper warns when a hive is dirty. To merge the log before analysis, use `yarp + registryFlush.py` or `rla.exe` (Eric Zimmerman's Registry Log Applier).

### Live vs Offline Acquisition

| | Live System | Offline (Disk Image) |
|--|------------|---------------------|
| System hives locked? | Yes — must use FTK Imager "Obtain Protected Files" or VSS | No — copy directly from mounted image |
| Transaction logs current? | Yes — includes unsaved changes | May be stale if system crashed |
| Risk of altering evidence | Higher — OS still writes to registry | None — image is read-only |
| NTUSER.DAT accessible? | Only for logged-out users (or via VSS) | Always accessible |

---

:::quiz{id="quiz-1"}
Q: Which registry hive stores the list of recently opened documents for a specific user?
- [ ] SYSTEM
- [ ] SAM
- [x] NTUSER.DAT
- [ ] SOFTWARE
:::

:::quiz{id="quiz-2"}
Q: The built-in Windows Administrator account always has which Relative Identifier (RID)?
- [ ] 1000
- [ ] 501
- [x] 500
- [ ] 0
:::

:::quiz{id="quiz-3"}
Q: A forensic examiner finds RIDs 1000, 1001, and 1003 in the SAM hive but no RID 1002. What does this indicate?
- [ ] RID 1002 belongs to the Guest account
- [x] An account was created and then deleted — RIDs are never reused
- [ ] The SAM hive is corrupted
- [ ] RID 1002 is reserved for service accounts
:::

:::quiz{id="quiz-4"}
Q: In a RegRipper NTUSER.DAT report, the RecentDocs key shows entry "13 = ---README---.txt" at the top of the MRUList. What does this tell you?
- [ ] ---README---.txt was the 13th file ever opened on this system
- [ ] ---README---.txt was opened exactly 13 times
- [x] ---README---.txt was the most recently opened document; 13 is its MRUList order number
- [ ] ---README---.txt is stored at offset 13 in the hive
:::

:::quiz{id="quiz-5"}
Q: Which registry hive would you analyze to determine what USB storage devices have ever been connected to a Windows computer?
- [ ] SAM
- [ ] NTUSER.DAT
- [ ] SOFTWARE
- [x] SYSTEM
:::

:::quiz{id="quiz-6"}
Q: Why can't you simply copy SAM, SYSTEM, and SOFTWARE from a live Windows system using File Explorer?
- [ ] These files are encrypted by BitLocker
- [ ] File Explorer does not support files without extensions
- [x] The OS locks these files while Windows is running; tools like FTK Imager use Volume Shadow Copy to bypass the lock
- [ ] These files are stored in protected memory, not on disk
:::

---

## Quick Reference

| Goal | Kali Command | Windows Tool |
|------|-------------|-------------|
| List root keys in hive | `reglookup -p / SYSTEM` | FTK Imager — Evidence Tree |
| Parse full hive | `rip.pl -r NTUSER.DAT -f ntuser` | RegRipper > select profile > Rip It |
| Recent documents | `rip.pl -r NTUSER.DAT -p recentdocs` | Search "recentdocs" in NT_User_report.txt |
| Typed URLs | `rip.pl -r NTUSER.DAT -p typedurls` | Search "TypedURLs" in report |
| Program execution | `rip.pl -r NTUSER.DAT -p userassist` | Search "UserAssist" in report |
| User accounts | `rip.pl -r SAM -f sam` | Open SAM_report.txt, find "User Information" |
| USB devices | `rip.pl -r SYSTEM -p usbstor` | Search "USBStor" in System_report.txt |
| Computer name | `rip.pl -r SYSTEM -p compname` | Search "ComputerName" in System_report.txt |
| Shutdown time | `rip.pl -r SYSTEM -p shutdown` | Search "ShutdownTime" in System_report.txt |
| Default browser | `rip.pl -r SOFTWARE -p default_browser` | Search "Default Browser Check" in Software_report.txt |
| List plugins | `rip.pl -l` | RegRipper Profile dropdown |
