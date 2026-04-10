# Live Forensics & System Triage

Live forensics examines a running Windows system **without shutting it down first**, capturing system configuration, user activity, and file system structure from a live environment. The DEFT 8 **DART** (Digital Advanced Recovery Toolkit) provides a curated launcher for Windows tools; Linux analysts use equivalent CLI utilities.

## Overview

Live forensics collects:

- **Disk geometry & drive info** — serial numbers, partition layout, capacity, sectors-per-cluster
- **File system structure** — partition tree, user directories, hidden and system folders
- **Disk usage by folder** — locate large or suspicious files without opening each one
- **System configuration** — OS version, hardware, installed software, users, network state
- **Browser history** — visited URLs, timestamps, and visit counts across multiple browsers

All output must be saved to an **external evidence drive** — never write artifacts back to the machine under examination.

---

## DART Overview

DART organizes Windows forensic tools into 8 categories:

| Category | Purpose |
|----------|---------|
| **Acquire** | Image memory and disks (FTK Imager, RAM Capture) |
| **Data Recovery** | Recover deleted and carved files |
| **Forensics** | Browser history, registry, file analysis |
| **Incident Resp.** | System info, running processes, auditing |
| **Networking** | Network connections, DNS, ARP |
| **Password** | Password recovery and cracking |
| **Visualize** | Timeline and data visualization |
| **Utility** | General utilities |

> DART logs must always be saved to the external Evidence Repository drive — never to the drive under examination.

---

:::command-builder{id="du-builder"}
tool_name: du
target_placeholder: "/home/user"
scan_types:
  - name: "Top-level breakdown"
    flag: "--max-depth=1 -h /home/user"
    desc: "Show sizes one level deep (mirrors TreeSizeFree top view)"
  - name: "Two-level breakdown"
    flag: "--max-depth=2 -h /home/user"
    desc: "Expand one more level to see subfolder sizes"
  - name: "Sort by size descending"
    flag: "--max-depth=1 -h /home/user | sort -rh"
    desc: "Ranked list — biggest subdirectories at top"
  - name: "Scan entire filesystem"
    flag: "--max-depth=2 -h / 2>/dev/null | sort -rh | head -30"
    desc: "Find the largest directories across the whole system"
options:
  - name: "Human-readable sizes"
    flag: "-h"
    desc: "Show KB/MB/GB instead of raw bytes"
  - name: "Stay on one filesystem"
    flag: "-x"
    desc: "Skip /proc, /sys, and other virtual mounts"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Identify Drives and Disk Geometry"
goal: "Enumerate attached storage devices and confirm serial numbers, capacity, partition layout, and sector geometry before touching any evidence."
hint: "On Windows, DART > Incident Resp. > System Info > DriveMan lists every drive with its serial number, volume serial, capacity, bytes per sector, and sectors per cluster. On Linux, lsblk gives a quick tree view; hdparm -I gives the drive serial and model; fdisk -l shows partition geometry. Always confirm device identifiers before any further action."
command: 'lsblk && sudo hdparm -I /dev/sdb | grep -E "Model|Serial|sector"'
expected_output: |
  lsblk:
    NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
    sda      8:0    0    34G  0 disk
    ├─sda1   8:1    0    33G  0 part /
    └─sda2   8:2    0     1G  0 part [SWAP]
    sdb      8:16   1     8G  0 disk          ← evidence USB
    └─sdb1   8:17   1     8G  0 part

  hdparm -I /dev/sdb:
    Model Number:       SAMSUNG MZ7LN256HAJQ
    Serial Number:      S2WANX0J123456
    Logical  Sector size:                   512 bytes
    Physical Sector size:                  4096 bytes

  Windows DriveMan (DART > Incident Resp. > System Info > DriveMan):
    Drive 0: Serial: WD-WCC4M0123456  Capacity: 45.0 GB  Bytes/Sector: 512
    Drive 1: Serial: USB001-20200615  Capacity: 8.0 GB   Sectors/Cluster: 8
:::

:::scenario{id="task-2" level="beginner"}
title: "Task 2 — Browse the File System and Locate User Directories"
goal: "Navigate the partition tree to find the main NTFS partition and the Users folder containing user profile directories including hidden AppData."
hint: "In FTK Imager (DART > Acquire > Image > FTK Imager), expand the Evidence Tree for the physical drive. The largest partition (Basic data partition) holds the OS. Expand it: NONAME [NTFS] > [root] > Users > Administrator. FTK Imager reveals hidden folders like AppData that are invisible in Windows Explorer. On Linux, mount the partition read-only and use ls or find."
command: 'sudo mount -o ro /dev/sdb1 /mnt/evidence && ls /mnt/evidence/Users/'
expected_output: |
  Windows FTK Imager — Evidence Tree:
    \\.\PHYSICALDRIVE0
    ├── Partition 1 [500MB]
    ├── Partition 2 [35038MB]   ← largest = main OS partition
    │     └── NONAME [NTFS]
    │           ├── [orphan]         ← deleted/recovered files with no parent
    │           ├── [root]           ← C:\ drive root
    │           │     ├── Users
    │           │     │     ├── Administrator
    │           │     │     │     ├── AppData  (hidden in Windows Explorer)
    │           │     │     │     ├── Desktop
    │           │     │     │     ├── Documents
    │           │     │     │     └── Downloads
    │           │     │     └── Public
    │           │     └── Windows
    │           └── [unallocated space]
    └── Partition 3 [9215MB]

  Linux (mounted read-only):
    /mnt/evidence/Users/
      Administrator/  Default/  Public/
    /mnt/evidence/Users/Administrator/
      AppData  Desktop  Documents  Downloads  Favorites  Pictures  Videos
:::

:::scenario{id="task-3" level="beginner"}
title: "Task 3 — Analyze Disk Usage to Find Large Files"
goal: "Identify the largest folders on the system to pinpoint where evidence may be concentrated, such as large Downloads or Desktop folders."
hint: "On Windows, DART > Incident Resp. > System Info > TreeSizeFree > Start As Admin, then Scan > Local Disk (C:). Expand Users > Administrator to see per-folder sizes. Hidden/grayed-out folders still appear with their sizes. On Linux, use du with --max-depth and pipe to sort -rh to rank directories. ncdu provides an interactive terminal UI similar to TreeSizeFree."
command: 'sudo du -h --max-depth=2 /mnt/evidence/Users/Administrator 2>/dev/null | sort -rh | head -20'
expected_output: |
  Linux du output (sorted by size):
    4.3G  /mnt/evidence/Users/Administrator
    3.9G  /mnt/evidence/Users/Administrator/Desktop
    401M  /mnt/evidence/Users/Administrator/AppData
     75M  /mnt/evidence/Users/Administrator/Documents
    8.2M  /mnt/evidence/Users/Administrator/Downloads

  Windows TreeSizeFree scan of C:\:
    28,624.7 MB  C:\
      17,294.7 MB  Windows
       4,346.6 MB  Users
         4,343.7 MB  Administrator
           3,855.7 MB  Desktop      ← unusually large — investigate
             401.9 MB  AppData
              75.4 MB  Documents
               8.2 MB  Downloads
    Free Space: 11.6 GB (of 34.2 GB)   16,410 Files   4096 Bytes/Cluster (NTFS)

  Note: Grayed-out entries in TreeSizeFree are hidden files — they are counted
  in the totals but not normally visible in Windows File Explorer.
:::

:::scenario{id="task-4" level="beginner"}
title: "Task 4 — Full System Audit with WinAudit"
goal: "Capture a comprehensive snapshot of system configuration: OS version, hardware, installed software, user accounts, scheduled tasks, error logs, and network settings."
hint: "On Windows, DART > Incident Resp. > System Info > WinAudit > Start As Admin. Click Options to review audit categories (leave defaults), then click Apply. Back in the main window, click Audit. When complete, save the report: File > Save as HTML to the Evidence Repository drive. On Linux, combine uname/lsb_release for OS, dmidecode/lshw for hardware, and dpkg -l or rpm -qa for software."
command: 'uname -a && lsb_release -a 2>/dev/null && sudo dmidecode -t system | grep -E "Manufacturer|Product|Serial"'
expected_output: |
  Linux system info:
    uname -a:
      Linux kali 5.18.0-kali2-amd64 #1 SMP x86_64 GNU/Linux

    lsb_release -a:
      Distributor ID: Kali
      Description:    Kali GNU/Linux Rolling
      Release:        2022.3

    dmidecode -t system:
      Manufacturer: VMware, Inc.
      Product Name: VMware Virtual Platform
      Serial Number: VMware-42 19 06 e6 ...

  Windows WinAudit — System Overview section:
    Computer Name:     WORKSTATION-01
    Operating System:  Microsoft Windows Server 2012 R2 (64-bit)
    Total Memory:      4096MB
    Total Hard Drive:  45.2GB
    BIOS Version:      INTEL - 6040000 PhoenixBIOS 4.0 Release 6.0
    User Account:      Administrator
    System Uptime:     8 Days, 1 Hours, 65 Minutes

  WinAudit audit categories include: System Overview, Installed Software,
  Operating System, Groups and Users, Scheduled Tasks, Error Logs,
  Environment Variables, Network TCP/IP, Physical Disks, Drives,
  Communication Ports, Services, Running Programs, Startup Programs
:::

:::scenario{id="task-5" level="beginner"}
title: "Task 5 — Capture Browser History with BrowsingHistoryView"
goal: "Extract web browsing history from all user profiles and save to the evidence drive. History reveals visited URLs, search queries, titles, timestamps, and visit counts."
hint: "On Windows, DART > Forensics > Browser > BrowsingHistoryView 64-bit > Start As Admin. Click OK on the Advanced Options dialog (leave defaults to scan all browsers and all user profiles). Then Edit > Select All, File > Save Selected Items to the Evidence Repository drive as a text file. On Linux, Chrome and Firefox store history in SQLite databases inside each user profile directory."
command: 'sqlite3 ~/.config/google-chrome/Default/History "SELECT url, title, visit_count FROM urls ORDER BY last_visit_time DESC LIMIT 20"'
expected_output: |
  Linux Chrome history (sqlite3):
    https://google.com/search?q=autopsy+forensics|Autopsy Forensics - Google Search|3
    https://forensicfocus.com/forums/|Forensic Focus Forums|1
    https://github.com/volatilityfoundation|Volatility Foundation - GitHub|2

  Firefox history (Linux):
    sqlite3 ~/.mozilla/firefox/*.default-release/places.sqlite \
      "SELECT url, title, visit_count FROM moz_places ORDER BY last_visit_date DESC LIMIT 20"

  Windows BrowsingHistoryView columns:
    URL                               Title                       Visit Time           Count  Browser   Profile
    https://google.com/search?q=...   Autopsy Forensics - Google  10/15/2023 2:22 PM   3      Chrome    Administrator
    https://forensicfocus.com/...     Forensic Focus Forums       10/15/2023 2:21 PM   1      Chrome    Administrator

  Browsers supported: Internet Explorer, Chrome, Firefox, Safari
  Export: Edit > Select All (Ctrl+A), then File > Save Selected Items (Ctrl+S)
  Save to: Evidence Repository (external drive) — never to the machine being examined
:::

---

## Linux Equivalents Cheatsheet

| Windows (DART) | Linux Command | Purpose |
|----------------|---------------|---------|
| DriveMan | `lsblk` / `sudo hdparm -I /dev/sdX` | Drive geometry and serial numbers |
| FTK Imager (browse) | `mount -o ro /dev/sdX1 /mnt/e` + `ls` / `find` | Browse partition read-only |
| TreeSizeFree | `du -h --max-depth=2 /path \| sort -rh` | Directory size ranking |
| TreeSizeFree (interactive) | `ncdu /path` | Interactive terminal disk usage viewer |
| WinAudit — system info | `uname -a` / `lshw` / `sudo dmidecode` | OS and hardware info |
| WinAudit — installed SW | `dpkg -l` / `rpm -qa` | Installed packages |
| WinAudit — users | `getent passwd` / `cat /etc/passwd` | Local user accounts |
| WinAudit — network | `ip addr` / `ss -tunap` / `cat /etc/hosts` | Network configuration |
| BrowsingHistoryView | `sqlite3 ~/.config/google-chrome/.../History` | Chrome browsing history |
| BrowsingHistoryView | `sqlite3 ~/.mozilla/firefox/.../places.sqlite` | Firefox browsing history |

---

## Key Forensic Concepts

### Why a Separate Evidence Drive?

Every write to the source drive risks:
- Overwriting timestamps on files not yet examined
- Contaminating unallocated space where deleted files live
- Changing last-accessed metadata (atime)

Save DART logs, WinAudit reports, and browser history exports to a dedicated **Evidence Repository** volume.

### Hidden Files and Forensic Visibility

Windows File Explorer hides system folders by default. FTK Imager reveals everything, including:

| Folder | Forensic significance |
|--------|----------------------|
| `AppData` | Application caches, saved credentials, cookies |
| `$Recycle.Bin` | Recently deleted items with original filenames |
| `[orphan]` | Recovered deleted files with no parent directory |
| `[unallocated space]` | Free space — where deleted file data lives |

TreeSizeFree grays out hidden folders but still accounts for their size — useful for spotting large hidden caches.

### Browser History as Evidence

BrowsingHistoryView reads across four browsers simultaneously. Key columns:

| Column | Forensic value |
|--------|---------------|
| URL | Exact page visited |
| Title | Page title at time of visit |
| Visit Time | Timestamp — establishes a timeline |
| Visit Count | Distinguishes accidental from intentional access |
| Visited From | Referrer URL — how the user arrived |
| User Profile | Which Windows user account was active |

On Linux, the identical data lives in SQLite files inside each user's browser profile directory.

---

:::quiz{id="quiz-1"}
Q: In DART, which category contains DriveMan, TreeSizeFree, and WinAudit?
- [ ] Acquire
- [ ] Forensics
- [x] Incident Resp.
- [ ] Utility
:::

:::quiz{id="quiz-2"}
Q: Why must all DART tool output be saved to an Evidence Repository drive rather than Local Disk (C:)?
- [ ] The C: drive is too slow to store forensic data
- [ ] DART tools cannot write to NTFS volumes
- [x] Writing to the source drive risks overwriting evidence, changing timestamps, and contaminating unallocated space
- [ ] Evidence Repository drives automatically encrypt the data
:::

:::quiz{id="quiz-3"}
Q: In FTK Imager's Evidence Tree, what does the [orphan] folder contain?
- [ ] Files that belong to other user accounts
- [x] Deleted or recovered files that have no parent directory
- [ ] System files protected by Windows Resource Protection
- [ ] Files that are currently locked by running processes
:::

:::quiz{id="quiz-4"}
Q: You scan a drive with TreeSizeFree and find the Administrator Desktop folder is 3.8 GB. What is the forensic significance?
- [ ] This is normal — Windows stores system caches on the Desktop
- [x] An unusually large Desktop may indicate the user stored downloaded files or evidence there and warrants closer examination
- [ ] Large Desktop folders are automatically encrypted by Windows
- [ ] TreeSizeFree cannot accurately measure hidden folders
:::

:::quiz{id="quiz-5"}
Q: Which BrowsingHistoryView column best indicates that a user deliberately sought out a specific site rather than landing on it accidentally?
- [ ] URL
- [ ] Visit Time
- [x] Visit Count
- [ ] User Profile
:::

:::quiz{id="quiz-6"}
Q: On Linux, where does Google Chrome store its browsing history database?
- [x] ~/.config/google-chrome/Default/History (SQLite format)
- [ ] /var/log/chrome/history.db
- [ ] /etc/chrome/browsing.log
- [ ] ~/Documents/chrome_history.txt
:::

---

## Quick Reference

| Task | Windows (DART) | Linux |
|------|----------------|-------|
| Drive geometry | Incident Resp. > System Info > DriveMan | `lsblk` / `sudo hdparm -I /dev/sdX` |
| Browse file system | Acquire > FTK Imager > Add Evidence Item | `mount -o ro /dev/sdX1 /mnt/e && ls` |
| Disk usage by folder | Incident Resp. > TreeSizeFree > Scan > C: | `du -h --max-depth=2 /path \| sort -rh` |
| Full system audit | Incident Resp. > WinAudit > Audit | `lshw` / `dmidecode` / `inxi -Fxz` |
| Installed software | WinAudit > Installed Software category | `dpkg -l` / `rpm -qa` |
| Browser history | Forensics > Browser > BrowsingHistoryView | `sqlite3 ~/.config/google-chrome/.../History` |
| Save evidence | File > Save Selected Items → Evidence Repository (E:) | Redirect output to external mount |
