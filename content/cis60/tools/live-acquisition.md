# Live Memory Acquisition & Analysis

RAM forensics captures volatile data — running processes, open network connections, encryption keys, and file fragments — that disappears the moment a system is powered off. This lab covers the full workflow: capturing process memory and full RAM, carving files from a memory dump, and analyzing it for evidentiary artifacts.

## Overview

RAM is volatile — it only exists while power is applied. It often contains evidence that **never reaches the hard drive**:

- Plaintext passwords and encryption keys
- Running malware that lives entirely in memory
- Browser session data, clipboard contents
- Network connections and socket state
- File fragments of recently opened documents

Two paths cover the same workflow: **Magnet tools + Redline** on Windows (GUI) and **LiME / avml + Volatility** on Linux/Kali (CLI).

---

## Order of Volatility

When collecting evidence from a live system, collect the most volatile data first — it disappears fastest:

| Priority | Data Type | Why It Disappears |
|----------|-----------|------------------|
| 1 | CPU registers & cache | Lost on any context switch |
| 2 | RAM contents | Lost on power-off or reboot |
| 3 | Running processes & network state | Changed constantly |
| 4 | Temp files / swap / pagefile | Overwritten by OS |
| 5 | Disk (filesystem) | Persistent but changes on writes |
| 6 | Logs & remote monitoring | Usually preserved |

> Always image RAM **before** you image the disk. Every tool you run on a live system modifies some RAM — keep notes of what you ran and when.

---

## Tool Comparison

| Task | Windows (GUI) | Linux / Kali (CLI) |
|------|-------------|-------------------|
| Process memory dump | Magnet Process Capture (.dmp) | `gcore [pid]` or `procdump` |
| Full RAM image | Magnet RAM Capture (.raw) | `avml`, `LiME` kernel module |
| File carving from RAM | FTK Imager hex search + Save selection | `foremost`, `scalpel`, `binwalk` |
| Full memory analysis | Redline (FireEye) | `volatility3` / `vol.py` |
| Strings search | FTK Imager View pane > Find | `strings memdump.raw \| grep keyword` |

---

## File Magic Bytes (File Carving Reference)

File carving finds files by searching for known byte signatures regardless of file system structure.

| File Type | Header (hex) | Footer (hex) | Notes |
|-----------|-------------|-------------|-------|
| JPEG | `FF D8 FF E0` | `FF D9` | Most common image format |
| PNG | `89 50 4E 47` | `49 45 4E 44 AE 42 60 82` | |
| PDF | `25 50 44 46` | `25 25 45 4F 46` | `%PDF` in ASCII |
| ZIP / DOCX | `50 4B 03 04` | `50 4B 05 06` | Office docs are ZIP archives |
| EXE / DLL | `4D 5A` | — | `MZ` header; no fixed footer |

---

:::command-builder{id="volatility-builder"}
tool_name: volatility3
target_placeholder: "memdump.raw"
scan_types:
  - name: "Image Info"
    flag: "-f memdump.raw windows.info"
    desc: "Identify OS version and profile of the memory image"
  - name: "Process List"
    flag: "-f memdump.raw windows.pslist"
    desc: "List all running processes (PID, PPID, name, start time)"
  - name: "Process Tree"
    flag: "-f memdump.raw windows.pstree"
    desc: "Show processes in parent-child tree — reveals suspicious spawning"
  - name: "Network Connections"
    flag: "-f memdump.raw windows.netstat"
    desc: "Show active and recently closed network connections"
  - name: "File Scan"
    flag: "-f memdump.raw windows.filescan"
    desc: "List all file objects cached in memory"
  - name: "Dump Files"
    flag: "-f memdump.raw windows.dumpfiles --virtaddr 0xADDR"
    desc: "Extract a specific file from memory by virtual address"
options:
  - name: "Output to file"
    flag: "--output-file results.txt"
    desc: "Save plugin output to a text file"
  - name: "Verbose"
    flag: "-vvv"
    desc: "Enable verbose output for debugging"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Explore the Tool Landscape"
goal: "Understand what Magnet Process Capture shows and what the Linux equivalents look like before doing any acquisition."
hint: "On Windows, Magnet Process Capture opens to a list of every running process by name and PID. On Linux, ps aux gives you the same view from the terminal. The key difference is Magnet can dump the actual memory pages used by a process — not just list it. Know this before you start: every tool you run on a live system writes something to RAM and may alter evidence. Document everything."
command: ps aux --sort=-%mem
expected_output: |
  Linux (ps aux):
    USER       PID %CPU %MEM    VSZ   RSS  COMMAND
    root         1  0.0  0.1 225896  9876  /sbin/init
    root       512  0.0  0.5 678432 42312  /usr/bin/python3
    www-data   883  0.1  1.2 456123 98234  /usr/sbin/apache2
    user      1234  2.3  4.5 1234567 368901 firefox

  Windows equivalent:
    Magnet Process Capture > Select Processes to Capture pane
    Each entry: process_name (pid: XXXX)
    svchost (pid: 1664), svchost (pid: 1852), chrome.exe (pid: 4012)...

  Key fields to note:
    PID   — process identifier, unique per run
    PPID  — parent PID (reveals what spawned the process)
    RSS   — resident set size (actual RAM used right now)
:::

:::scenario{id="task-2" level="beginner"}
title: "Task 2 — Capture Specific Process Memory"
goal: "Dump the memory pages used by a specific process. On Linux use gcore. On Windows use Magnet Process Capture, select only the target processes, and save to a separate drive."
hint: "Store output on a separate drive — never write evidence artifacts back to the same disk you are investigating. On Windows, Magnet Process Capture creates a folder named after the capture timestamp containing .dmp files for each selected process. On Linux, gcore creates a core dump file. Warnings about processes no longer running at capture time are normal for short-lived processes."
command: sudo gcore -o /mnt/evidence/proc_dump [pid]
expected_output: |
  Linux (gcore):
    Saved corefile /mnt/evidence/proc_dump.1234

  Windows Magnet Process Capture:
    Status bar: "Memory of selected processes captured successfully"
    Warning (normal): "svchost (pid: 2312) was no longer running when capture attempted"
    Saved to: E:\case_folder\LAB_Running_Processes\MagnetProcessCapture-YYYYMMDD-HHMMSS\
    Contents: one .dmp file per captured process

  Inspect the dump on Linux:
    strings /mnt/evidence/proc_dump.1234 | grep -i password
    strings /mnt/evidence/proc_dump.1234 | grep -i http
:::

:::scenario{id="task-3" level="beginner"}
title: "Task 3 — Full RAM Capture"
goal: "Image the entire contents of RAM to a file. On Linux use avml (no kernel module required). On Windows use Magnet RAM Capture with a 500MB segment size."
hint: "RAM capture writes a file equal to the size of installed RAM. A 16GB system produces a ~16GB image. Use 500MB segments if writing to a FAT32 drive (max 4GB per file). avml is preferred on Linux because it runs as a userspace binary — no kernel module insertion needed, which minimizes system impact. Always store the output on a separate drive."
command: sudo avml /mnt/evidence/ram_capture.lime
expected_output: |
  Linux (avml):
    sudo avml /mnt/evidence/ram_capture.lime
    # No output on success — check file size
    ls -lh /mnt/evidence/ram_capture.lime
    -rw-r--r-- 1 root root 16G  Apr 9 10:22 ram_capture.lime

  Alternative with LiME kernel module:
    sudo insmod lime.ko "path=/mnt/evidence/ram.lime format=lime"
    # Creates a LiME-format image recognized by Volatility

  Windows Magnet RAM Capture:
    Browse > select output folder (separate drive)
    Segment size: 500MB  (important for FAT32 drives)
    Click Start
    Completion popup: "RAM successfully saved to [path]\capture.raw"
    Files created: capture.raw, capture.raw.001, capture.raw.002 ...
:::

:::scenario{id="task-4" level="beginner"}
title: "Task 4 — Carve Files from a Memory Dump"
goal: "Find and extract a JPEG image embedded in a RAM dump using file signatures. On Linux use foremost. On Windows use FTK Imager hex search."
hint: "File carving ignores the file system entirely — it scans raw bytes looking for known magic bytes. JPEG files always start with FF D8 FF E0 and end with FF D9. In FTK Imager, load the .mem or .raw file as an Image File, switch to the View pane, right-click and Find with Binary (hex) type, search for FF D8 FF E0. Then sweep from that header to the FF D9 footer and right-click > Save selection."
command: foremost -t jpg -i /mnt/evidence/ram_capture.lime -o /mnt/evidence/carved/
expected_output: |
  Linux (foremost):
    foremost -t jpg,png,pdf -i /mnt/evidence/ram_capture.lime -o /mnt/evidence/carved/
    Processing: /mnt/evidence/ram_capture.lime
    |*
    *|
    Length: 16 GB

    /mnt/evidence/carved/
    ├── audit.txt          ← carving log with offsets
    └── jpg/
          ├── 00001234.jpg
          ├── 00045678.jpg
          └── 00098765.jpg

  Linux alternative (scalpel — faster, configurable):
    scalpel -o /mnt/evidence/scalpel_out /mnt/evidence/ram_capture.lime

  Windows FTK Imager workflow:
    File > Add Evidence Item > Image File > browse to memdump.mem > Finish
    In Evidence Tree: click memdump.mem
    In View pane: right-click > Find > Binary (hex) > FF D8 FF E0 > Find
    Sweep from FF D8 FF E0 to FF D9 to select the file bytes
    Right-click > Save selection > name it Mem_001.jpg
    Open with any image viewer to verify the carved file
:::

:::scenario{id="task-5" level="intermediate"}
title: "Task 5 — Analyze Memory with Volatility / Redline"
goal: "Load the RAM dump into an analysis tool. List processes, check network connections, and search for suspicious activity."
hint: "Volatility is the Linux standard for memory forensics. Always start with windows.info to confirm the OS profile, then pslist/pstree to see processes, then netscan for connections. Look for: processes with no parent, processes with names that mimic system processes (svchost.exe in wrong locations), processes with unusual network connections, and injected code (malfind plugin). Redline on Windows provides the same capabilities through a GUI."
command: python3 vol.py -f memdump.raw windows.pstree
expected_output: |
  Volatility 3 — full workflow:

  # Step 1: Identify OS profile
  python3 vol.py -f memdump.raw windows.info
    Variable    Value
    Kernel Base     0xf80002a4a000
    DTB             0x187000
    Is64Bit         True
    NtSystemRoot    C:\Windows
    NtProductType   NtProductWinNt

  # Step 2: List processes in tree form
  python3 vol.py -f memdump.raw windows.pstree
    PID   PPID  Name
    4     0     System
    ├── 304   4     smss.exe
    ├── 520   4     csrss.exe
    └── 628   504   winlogon.exe
          └── 672   628  services.exe
                ├── 748   672  svchost.exe
                └── 2312  672  svchost.exe

  # Step 3: Check network connections
  python3 vol.py -f memdump.raw windows.netstat
    Offset  Proto  LocalAddr       LocalPort  ForeignAddr    State
    ...     TCPv4  192.168.1.5     49231      203.0.113.99   ESTABLISHED

  # Step 4: Search for suspicious strings
  strings memdump.raw | grep -i "password\|passwd\|secret\|token" | head -20

  Windows Redline workflow:
    Analyze Data > From a Saved Memory File > browse to memdump.mem
    Left panel: Processes, Network Connections, File System, Registry
    Click Processes to review running process list
    Look for suspicious parent-child relationships or unsigned executables
:::

---

## Full Linux Workflow (Kali)

End-to-end memory acquisition and analysis:

```bash
# --- ACQUISITION ---

# 1. Check available RAM
free -h

# 2. Capture full RAM with avml (no kernel module needed)
sudo avml /mnt/evidence/ram.lime

# Alternatively, with LiME:
# sudo insmod /path/to/lime.ko "path=/mnt/evidence/ram.lime format=lime"

# Hash the capture for integrity
sha256sum /mnt/evidence/ram.lime > /mnt/evidence/ram.lime.sha256

# --- PROCESS DUMP ---

# List processes, find your target PID
ps aux | grep suspicious_process

# Dump that process's memory pages
sudo gcore -o /mnt/evidence/proc_dump [PID]

# --- ANALYSIS ---

# Install Volatility 3
pip3 install volatility3

# Identify profile
python3 vol.py -f /mnt/evidence/ram.lime windows.info

# Process list and tree
python3 vol.py -f /mnt/evidence/ram.lime windows.pslist
python3 vol.py -f /mnt/evidence/ram.lime windows.pstree

# Network connections
python3 vol.py -f /mnt/evidence/ram.lime windows.netstat

# Scan for file objects in memory
python3 vol.py -f /mnt/evidence/ram.lime windows.filescan | grep -i ".pdf\|.docx\|.jpg"

# Detect injected code (malware hunting)
python3 vol.py -f /mnt/evidence/ram.lime windows.malfind

# --- FILE CARVING ---

# Carve files by type
foremost -t jpg,png,pdf,zip -i /mnt/evidence/ram.lime -o /mnt/evidence/carved/

# Search for keywords
strings /mnt/evidence/ram.lime | grep -i "password\|secret\|token\|Bearer"
```

---

## Key Concepts

### Why RAM Cannot Be Hash-Verified Like a Disk Image

RAM contents change constantly — every clock tick modifies register values, cache lines, and process state. A hash computed before capture will never match one computed after. Instead:

- Hash the **capture file** after writing it to disk
- Store the hash alongside the file
- This proves the **stored image** has not been modified since capture — not that it matched RAM at the moment of capture

### Live Acquisition vs Dead Acquisition

| | Live Acquisition | Dead Acquisition |
|--|----------------|-----------------|
| System state | Powered on, running | Powered off |
| RAM available | Yes | No (lost) |
| Disk writes during collection | Yes — OS still running | No — static media |
| Risk of evidence alteration | Higher (tools run on suspect system) | Lower |
| Use when | Volatile evidence is critical (malware, encryption keys) | Standard disk forensics |

### Magnet Process Capture vs Full RAM Capture

| | Process Capture | Full RAM Capture |
|--|----------------|-----------------|
| Output format | .dmp (one per process) | .raw / .mem (whole RAM) |
| Size | Small (MB per process) | Large (= installed RAM) |
| Captures | Only selected process memory pages | All physical memory |
| Use when | Quick triage of specific suspicious process | Full investigation |

---

:::quiz{id="quiz-1"}
Q: Why should output from a live memory acquisition be stored on a separate drive rather than the suspect system's hard disk?
- [ ] It is faster to write to an external drive
- [x] Writing to the suspect's disk could overwrite evidence in unallocated space or alter timestamps
- [ ] RAM capture tools only support external drives
- [ ] The operating system prevents saving to the local disk during acquisition
:::

:::quiz{id="quiz-2"}
Q: What is the hex magic byte sequence that marks the start of a JPEG file?
- [ ] 89 50 4E 47
- [ ] 25 50 44 46
- [x] FF D8 FF E0
- [ ] 50 4B 03 04
:::

:::quiz{id="quiz-3"}
Q: According to the order of volatility, which should you capture first on a live system?
- [ ] Hard disk image
- [ ] Log files
- [x] RAM contents
- [ ] Swap / pagefile
:::

:::quiz{id="quiz-4"}
Q: Which Volatility plugin would you use first to identify the operating system and kernel version of a memory image?
- [x] windows.info
- [ ] windows.pslist
- [ ] windows.malfind
- [ ] windows.filescan
:::

:::quiz{id="quiz-5"}
Q: What does file carving do that a standard file system copy cannot?
- [ ] It creates an E01-formatted image of the files
- [ ] It copies files faster by skipping file system overhead
- [x] It recovers files from raw bytes using magic byte signatures, regardless of whether the file system still has an entry for them
- [ ] It verifies file integrity with hashes during extraction
:::

:::quiz{id="quiz-6"}
Q: Why can a RAM capture file NOT be verified with the same hash-comparison method used for disk images?
- [ ] RAM capture tools do not support MD5 or SHA1
- [ ] The file is too large for hash computation
- [x] RAM contents change constantly while the system runs, so the hash of the capture file will never match a hash computed while RAM was live
- [ ] Hash verification is only valid for E01 format images
:::

---

## Quick Reference

| Task | Linux / Kali | Windows |
|------|-------------|---------|
| List processes | `ps aux` | Magnet Process Capture (process list pane) |
| Dump process memory | `sudo gcore -o dump [pid]` | Magnet Process Capture > Start |
| Full RAM image | `sudo avml ram.lime` | Magnet RAM Capture > Start |
| Hash the image | `sha256sum ram.lime` | Hash separately (RAM cannot be verified live) |
| Analyze image | `python3 vol.py -f ram.lime windows.pslist` | Redline > Analyze Data > From a Saved Memory File |
| Carve files | `foremost -t jpg -i ram.lime -o carved/` | FTK Imager > Find (hex) > Save selection |
| Search strings | `strings ram.lime \| grep keyword` | FTK Imager View pane > right-click > Find (text) |
