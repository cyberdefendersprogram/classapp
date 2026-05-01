# Recycle Bin Forensics with Autopsy and Rifiuti

The Recycle Bin is a forensic gold mine. When a user deletes a file, Windows does not immediately destroy it — it moves the file to a special hidden folder and records metadata about the deletion, including the original path and the exact time it was deleted. From a forensic examiner's perspective, the recycle bin can identify **who deleted what, when, and from where**, tied directly to a specific user account via Security Identifiers (SIDs).

This lab covers two recycle bin formats across two eras of Windows:
- **RECYCLER** (Windows XP and earlier) — parsed with `rifiuti`
- **$Recycle.bin** (Windows Vista and later) — parsed with `rifiuti-vista`

Both analyses use **Autopsy 4.13** on CSI-Linux to navigate forensic images and export artifacts, and **Rifiuti** to decode the index files.

## Overview

- **RECYCLER** folder — pre-Vista; one `INFO2` index file tracks all deleted files for a user
- **$Recycle.bin** folder — Vista+; individual `$I` index files, one per deleted item paired with a `$R` content file
- **SID subfolders** — each user gets their own subfolder named by their Security Identifier; maps to a specific user account
- **Rifiuti** — command-line tool that parses `INFO2` (XP) and `$I` (Vista+) files and outputs deletion metadata as plain text
- **Evidence files:** `Lab9-1.E01` (Windows XP NTFS) and `Lab9-2.E01` (Windows 10)

---

## Recycle Bin Locations by OS

| Windows Version | Recycle Bin Folder | Index File | Deleted File Prefix |
|---|---|---|---|
| Windows XP / 2000 / 98 | `RECYCLER\[SID]\` | `INFO2` | `D[drive][sequence]` |
| Windows Vista / 7 / 8 / 10 / 11 | `$Recycle.bin\[SID]\` | `$I[alphanumeric]` | `$R[alphanumeric]` |

**Identifying OS age** from folder structure:
- `Documents and Settings` folder → pre-Vista (Windows XP or earlier)
- `Users` folder → Vista or later
- `RECYCLER` folder → pre-Vista
- `$Recycle.bin` folder → Vista or later

---

## Tool Comparison

| Task | Autopsy 4.13 | Rifiuti (command line) |
|---|---|---|
| Load forensic image | Add Data Source > Disk Image or VM File | N/A |
| Navigate to recycle bin | Click RECYCLER or $Recycle.bin in tree | N/A |
| Read SID folder names | View in File List pane | N/A |
| Export index files | Right-click > Extract File(s) | N/A |
| Parse XP INFO2 file | Hex view only | `rifiuti [path/INFO2] > output.txt` |
| Parse Vista+ $I files | Hex view only | `rifiuti-vista [folder/] > output.txt` |
| View parsed deletion records | N/A | `gedit output.txt` |

---

## SID Anatomy

Every user on a Windows machine has a unique **Security Identifier (SID)**. The recycle bin subfolder for each user is named after their SID.

**Example SID:** `S-1-5-21-2000478354-688789844-1708537768-1003`

| Component | Value | Meaning |
|---|---|---|
| `S` | S | Indicates the value is a SID |
| `1` | 1 | Revision level of the SID specification (always 1) |
| `5` | 5 | Identifier Authority Value — defines the authority that created the SID (normally 5) |
| `21-2000478354-688789844-1708537768` | 21-... | Domain or Local Computer Identifier — uniquely identifies the computer |
| `1003` | 1003 | **Relative Identifier (RID)** — identifies the specific user account |

### RID Ranges

| RID | Account |
|---|---|
| 500 | Administrator (built-in) |
| 501 | Guest (built-in) |
| 1000+ | User-created accounts (never recycled, even if account is deleted) |

**Forensic implication of RID ≥ 1000:** The RID tells you the order of account creation and whether previous accounts existed. RID 1003 means it is the 4th non-system user account ever created on that machine.

### Mapping SID to Username

The SID-to-username mapping is stored in the **SAM registry hive**. Parse it with **RegRipper** to get output like:

```
Username    : Administrator [500]
Username    : Guest         [501]
Username    : HelpAssistant [1000]
Username    : SUPPORT_388945a0 [1002]
Username    : Mr. Evil      [1003]
```

This confirms that SID ending in `1003` belongs to **Mr. Evil**.

**Multiple SIDs in $Recycle.bin** with the same Local Computer Identifier = multiple user accounts on the same machine. Different Local Computer Identifiers = files from different computers were stored on this volume.

---

## Part 1 – Parsing the RECYCLER Folder (Windows XP)

### Setup in Autopsy (CSI-Linux)

1. Launch **CSI-Linux** VM; log in as `csi` / `csi`
2. Open **Autopsy**: Application Menu > Computer Forensics > Autopsy 4.13
3. Create new case: **New Case**, Case Name: `FOR_LAB_009`, click **Next**
4. Fill in Optional Information (Case Number: `NDG009`, your name), click **Finish**
5. Add Data Source: **Disk Image or VM File** > **Next**
6. Browse to `home > csi > Desktop > Evidence Files > FOR_LAB_009 > Lab9-1`, select `Lab9-1.E01`, click **Open**
7. Set time zone (e.g., GMT-5:00 America/New_York), click **Next**
8. **Deselect All** ingest modules, click **Next**, then **Finish**

### Navigate to the RECYCLER folder

9. In the tree pane: **Data Sources** → **Lab9-1.E01** → **vol2 (NTFS/exFAT 0x07)** → click **RECYCLER**
10. The RECYCLER folder contains:
    - `[current folder]` and `[parent folder]` (Autopsy references)
    - `S-1-5-21-2000478354-688789844-1708537768-1003` — Mr. Evil's SID subfolder

### Examine the SID subfolder

11. Click the SID folder: `S-1-5-21-2000478354-688789844-1708537768-1003`
12. File List shows 6 items (plus 2 Autopsy folder references):
    - `Dc1.exe` — 1st file deleted from C drive
    - `Dc2.exe` — 2nd file deleted from C drive
    - `Dc3.exe` — 3rd file deleted from C drive
    - `Dc4.exe` — 4th file deleted from C drive
    - `INFO2` — index file (deletion records for all files)
    - `desktop.ini` — system file (ignore)

### RECYCLER file naming convention (Windows XP)

| Character | Meaning |
|---|---|
| `D` | Indicates file was deleted (always D) |
| `c` (second char) | Drive letter the file was deleted from |
| `1`, `2`, `3`... | Sequential deletion order |

`Dc1.exe` = first file deleted from the **C** drive by this user.

### Export the INFO2 file

13. Right-click **INFO2** → **Extract File(s)**
14. In the Save window, create new folder `Lab9-1`, open it, verify filename is `INFO2`, click **Save**
15. Click **OK** on the confirmation dialog

### Parse INFO2 with Rifiuti

16. Open **Terminal Emulator** (Application Menu > Terminal Emulator, or dock icon)
17. Run Rifiuti to parse the INFO2 file:

```bash
rifiuti ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-1/INFO2 > \
  ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-1/INFO2.txt
```

18. Open the output file:

```bash
gedit ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-1/INFO2.txt
```

### INFO2.txt structure

```
INDEX  DELETED TIME              DRIVE  PATH                                                              SIZE
1      08/25/2004 12:18:25       2      C:\Documents and Settings\Mr. Evil\Desktop\lalsetup250.exe        2160128
2      08/27/2004 11:12:30       2      C:\Documents and Settings\Mr. Evil\Desktop\netstumblerinstaller_0_4_0.exe  1325056
3      08/27/2004 11:15:26       2      C:\Documents and Settings\Mr. Evil\Desktop\WinPcap_3_01_a.exe     442880
4      08/27/2004 11:29:58       2      C:\Documents and Settings\Mr. Evil\Desktop\ethereal-setup-0.10.6.exe  8460800
```

**Columns explained:**

| Column | Description |
|---|---|
| INDEX | Sequential order of deletion (matches filename number in RECYCLER) |
| DELETED TIME | Date and time the file was sent to the Recycle Bin |
| DRIVE | Physical drive number (2 = C drive in this case) |
| PATH | Original full path of the file before deletion |
| SIZE | File size in bytes |

---

## Part 2 – Parsing the $Recycle.bin Folder (Windows Vista / 10)

### Add the Windows 10 image to Autopsy

1. In Autopsy, click **Add Data Source**
2. Select **Disk Image or VM File** > **Next**
3. Browse to `home > csi > Desktop > Evidence Files > FOR_LAB_009 > Lab9-2`, select `Lab9-2.E01`, click **Open**
4. Set time zone, click **Next** → **Deselect All** → **Next** → **Finish**

### Navigate to $Recycle.bin

5. In the tree: **Lab9-2.E01** → click **$Recycle.bin**
6. Three SID subfolders visible — 2 share the same Local Computer Identifier (same machine), 1 is from a different computer
7. Click `S-1-5-21-1843218942-199276559-4149176266-1001` (14 files)

### $Recycle.bin file naming convention (Vista+)

Each deleted file produces two files with the same alphanumeric suffix:

| Prefix | Role | Example |
|---|---|---|
| `$R` | The actual deleted file content | `$REYEZMZ.exe` |
| `$I` | The index/metadata file | `$IEYEZMZ.exe` |

The `$I` file stores: original filename, deletion timestamp, and file size.

### Export $I index files

8. Hold **Ctrl** and click each `$I` file (files starting with `$I`)
9. Right-click → **Extract File(s)** → create new folder `Lab9-2`, open it, click **Save**
10. Click **OK** on confirmation

### Rename exported $I files (remove Autopsy offset prefix)

When Autopsy exports files in bulk, it prepends an offset number to each filename (e.g., `20156-$IEYEZMZ.exe`). Rifiuti requires the standard `$I` prefix. Rename them:

```bash
cd ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-2/
ls
```

Output shows files like: `'20156-$IEYEZMZ.exe'  '20157-$IFPGAC2.exe'  '20158-$IJM50U0.exe'  '20159-$INVG66K.exe'  '20160-$IO4I1J9.exe'`

Rename each file (use `\$` to escape the `$` sign, or Tab to auto-complete):

```bash
mv 20156-\$IEYEZMZ.exe \$IEYEZMZ.exe
mv 20157-\$IFPGAC2.exe \$IFPGAC2.exe
mv 20158-\$IJM50U0.exe \$IJM50U0.exe
mv 20159-\$INVG66K.exe \$INVG66K.exe
mv 20160-\$IO4I1J9.exe \$IO4I1J9.exe
```

### Parse $I files with rifiuti-vista

```bash
rifiuti-vista ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-2/ > \
  ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-2/Index.txt
```

Open the result:

```bash
gedit Index.txt
```

### Index.txt structure (Vista+)

```
Recycle bin path: '/home/csi/Desktop/Cases/FOR_LAB_009/Export/Lab9-2/'
Version: 2
OS Guess: Windows 10 or above
Time zone: Coordinated Universal Time (UTC) [+8000]

Index          Deleted Time          Size      Path
$IEYEZMZ.exe  2020-08-01 05:39:26   27867252  C:\Users\Mr Good\Desktop\tor-browser-2.3.25-6_en-US.exe
$INVG66K.exe  2020-08-01 05:39:26   632696    C:\Users\Mr Good\Desktop\FreePortScanner.exe
$IFPGAC2.exe  2020-08-01 05:40:49   1128960   C:\Users\Mr Good\Downloads\DiskWipe.exe
$IJM50U0.exe  2020-08-01 05:40:49   36247536  C:\Users\Mr Good\Downloads\VeraCrypt Setup 1.24-Update6.exe
$IO4I1J9.exe  2020-08-01 05:40:49   60082856  C:\Users\Mr Good\Downloads\Wireshark-win64-3.2.5.exe
```

**Vista+ columns explained:**

| Column | Description |
|---|---|
| Index | The $I filename (corresponds to the $R content file with same suffix) |
| Deleted Time | UTC timestamp when file was sent to Recycle Bin |
| Size | Original file size in bytes |
| Path | Original full path of the file before deletion |

Note: **No Drive column** in Vista+ format — the drive is embedded in the path itself.

---

:::command-builder{id="rifiuti-xp-builder"}
tool_name: rifiuti (Windows XP / RECYCLER)
target_placeholder: "INFO2"
scan_types:
  - name: "Parse INFO2 to text file"
    flag: "~/path/to/INFO2 > ~/path/to/INFO2.txt"
    desc: "Parse the INFO2 index file from a Windows XP RECYCLER folder and redirect output to a text file"
  - name: "Parse INFO2 to terminal"
    flag: "~/path/to/INFO2"
    desc: "Print parsed deletion records directly to the terminal without saving"
options:
  - name: "View output with gedit"
    flag: "gedit ~/path/to/INFO2.txt"
    desc: "Open the parsed text file in the gedit graphical text editor"
  - name: "Case sensitivity"
    flag: "Linux commands are case-sensitive"
    desc: "INFO2 must be typed exactly as shown — uppercase I, N, F, O, 2"
:::

---

:::command-builder{id="rifiuti-vista-builder"}
tool_name: rifiuti-vista (Windows Vista / 7 / 8 / 10 / 11)
target_placeholder: "Lab9-2/"
scan_types:
  - name: "Parse entire $I folder to text file"
    flag: "~/path/to/folder/ > ~/path/to/Index.txt"
    desc: "Parse all $I index files in the folder (pass the folder path, not individual files)"
  - name: "Parse single $I file"
    flag: "~/path/to/\\$IXXXXXXX.exe"
    desc: "Parse a single $I index file — escape the $ with a backslash"
options:
  - name: "Rename Autopsy-exported files first"
    flag: "mv OFFSET-\\$IFILE.exe \\$IFILE.exe"
    desc: "Autopsy prepends an offset number to filenames on bulk export — strip it before running rifiuti-vista"
  - name: "Use Tab for auto-complete"
    flag: "Tab key"
    desc: "Start typing the filename and press Tab to auto-complete, avoiding issues with the $ character"
  - name: "View output with gedit"
    flag: "gedit Index.txt"
    desc: "Open the parsed Index.txt in gedit for review"
:::

---

:::command-builder{id="autopsy-recyclebin-builder"}
tool_name: Autopsy 4.13 (Recycle Bin Navigation)
target_placeholder: "Lab9-1.E01"
scan_types:
  - name: "Load forensic image"
    flag: "Add Data Source > Disk Image or VM File"
    desc: "Load .E01 image; Deselect All ingest modules for manual navigation"
  - name: "Navigate to RECYCLER (XP)"
    flag: "Data Sources > image > vol > RECYCLER"
    desc: "Pre-Vista recycle bin; contains SID subfolders"
  - name: "Navigate to $Recycle.bin (Vista+)"
    flag: "Data Sources > image > vol > $Recycle.bin"
    desc: "Vista+ recycle bin; contains SID subfolders with $R and $I file pairs"
  - name: "Export index file"
    flag: "Right-click INFO2 or $I files > Extract File(s)"
    desc: "Export the recycle bin index file(s) to the Autopsy case Export folder"
options:
  - name: "Deselect All ingest modules"
    flag: "Configure Ingest Modules > Deselect All"
    desc: "Skip all ingest modules for faster loading when doing manual navigation"
  - name: "Multiple $I file export"
    flag: "Ctrl+click each $I file > right-click > Extract File(s)"
    desc: "Select all $I files before exporting; Autopsy adds offset prefixes in bulk export"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Navigate the RECYCLER Folder and Decode a SID"
goal: "Load Lab9-1.E01 in Autopsy, navigate to the RECYCLER folder, identify the SID subfolder, and determine which user it belongs to and how many non-system accounts existed on this machine."
hint: "Expand the tree: vol2 > RECYCLER. You will see one SID folder. Break down S-1-5-21-2000478354-688789844-1708537768-1003 into its components. The last number is the RID. RID 1000+ = non-system user accounts."
command: "Autopsy tree → RECYCLER → SID folder"
expected_output: |
  SID: S-1-5-21-2000478354-688789844-1708537768-1003

  Breakdown:
    S                                    = SID identifier
    1                                    = Revision level
    5                                    = Identifier Authority (NT Authority)
    21-2000478354-688789844-1708537768   = Local Computer Identifier
    1003                                 = Relative Identifier (RID)

  Interpretation:
    RID 1003 = 4th non-system user account on this machine
    (1000=1st, 1001=2nd, 1002=3rd, 1003=4th)

  From RegRipper SAM output:
    Administrator [500], Guest [501], HelpAssistant [1000],
    SUPPORT_388945a0 [1002], Mr. Evil [1003]

  Conclusion: SID 1003 = Mr. Evil
:::

:::scenario{id="task-2" level="beginner"}
title: "Task 2 — Decode RECYCLER Filenames and Identify Deletion Order"
goal: "Inside Mr. Evil's RECYCLER subfolder, identify the 4 deleted files and determine what drive they were deleted from and in what order."
hint: "The naming convention is D[drive letter][sequence]. D=deleted, the second character is the drive letter, the number is the order. Dc1 = first file deleted from C drive."
command: "Autopsy → RECYCLER → SID folder → File List"
expected_output: |
  Files in Mr. Evil's RECYCLER folder:
    Dc1.exe  → 1st file deleted from C: drive (2004-08-25)
    Dc2.exe  → 2nd file deleted from C: drive (2004-08-27)
    Dc3.exe  → 3rd file deleted from C: drive (2004-08-27)
    Dc4.exe  → 4th file deleted from C: drive (2004-08-27)
    INFO2    → index file (parse with rifiuti)
    desktop.ini → system file (ignore)

  Pattern: All files from drive C:, deletion order 1-4
:::

:::scenario{id="task-3" level="intermediate"}
title: "Task 3 — Parse the INFO2 File with Rifiuti"
goal: "Export INFO2 from Autopsy and use rifiuti to extract the original filenames, deletion timestamps, and paths for all 4 deleted files."
hint: "Right-click INFO2 > Extract File(s) > save as INFO2 in Lab9-1 folder. Open Terminal. Run: rifiuti ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-1/INFO2 > ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-1/INFO2.txt. Then: gedit ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-1/INFO2.txt"
command: "rifiuti ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-1/INFO2 > ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-1/INFO2.txt"
expected_output: |
  INDEX  DELETED TIME           DRIVE  PATH                                                                       SIZE
  1      08/25/2004 12:18:25    2      C:\Documents and Settings\Mr. Evil\Desktop\lalsetup250.exe                 2160128
  2      08/27/2004 11:12:30    2      C:\Documents and Settings\Mr. Evil\Desktop\netstumblerinstaller_0_4_0.exe  1325056
  3      08/27/2004 11:15:26    2      C:\Documents and Settings\Mr. Evil\Desktop\WinPcap_3_01_a.exe              442880
  4      08/27/2004 11:29:58    2      C:\Documents and Settings\Mr. Evil\Desktop\ethereal-setup-0.10.6.exe       8460800

  Findings:
    - All 4 files deleted from Mr. Evil's Desktop on C: drive
    - File 1 deleted Aug 25, files 2-4 deleted Aug 27 in a 17-minute window
    - lalsetup250.exe, netstumblerinstaller, WinPcap, Ethereal = network tools
:::

:::scenario{id="task-4" level="intermediate"}
title: "Task 4 — Parse Vista+ $I Files with rifiuti-vista"
goal: "Load Lab9-2.E01, export the $I index files from the $Recycle.bin SID folder, rename them to remove Autopsy offset prefixes, then run rifiuti-vista to recover the 5 deleted files' original paths and deletion times."
hint: "Navigate to $Recycle.bin > SID folder ending in 1001. Ctrl+click all $I files > Extract File(s) > Lab9-2 folder. In Terminal: cd to Lab9-2/, run ls to see offset filenames, then mv each 20156-\\$IFILE.exe \\$IFILE.exe. Finally: rifiuti-vista ./ > Index.txt"
command: "rifiuti-vista ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-2/ > ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-2/Index.txt"
expected_output: |
  Recycle bin path: '.../Export/Lab9-2/'
  Version: 2
  OS Guess: Windows 10 or above
  Time zone: Coordinated Universal Time (UTC) [+8000]

  Index          Deleted Time          Size      Path
  $IEYEZMZ.exe  2020-08-01 05:39:26   27867252  C:\Users\Mr Good\Desktop\tor-browser-2.3.25-6_en-US.exe
  $INVG66K.exe  2020-08-01 05:39:26   632696    C:\Users\Mr Good\Desktop\FreePortScanner.exe
  $IFPGAC2.exe  2020-08-01 05:40:49   1128960   C:\Users\Mr Good\Downloads\DiskWipe.exe
  $IJM50U0.exe  2020-08-01 05:40:49   36247536  C:\Users\Mr Good\Downloads\VeraCrypt Setup 1.24-Update6.exe
  $IO4I1J9.exe  2020-08-01 05:40:49   60082856  C:\Users\Mr Good\Downloads\Wireshark-win64-3.2.5.exe

  Findings:
    - User: Mr Good (path contains Users\Mr Good)
    - All 5 files deleted Aug 1, 2020 in an 11-minute window
    - Files include Tor Browser, port scanner, disk wipe tool, VeraCrypt, Wireshark
    - Two batch deletions: 05:39:26 (2 files) and 05:40:49 (3 files)
:::

---

## Full Linux Workflow

### Windows XP (RECYCLER / INFO2)

```bash
# Parse INFO2 and save to text file
rifiuti ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-1/INFO2 > \
  ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-1/INFO2.txt

# Open output in text editor
gedit ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-1/INFO2.txt
```

### Windows Vista / 10 ($Recycle.bin / $I files)

```bash
# Navigate to the export folder
cd ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-2/

# List files to see Autopsy-prefixed names
ls

# Rename each file to strip the offset prefix (your numbers will differ)
mv 20156-\$IEYEZMZ.exe \$IEYEZMZ.exe
mv 20157-\$IFPGAC2.exe \$IFPGAC2.exe
mv 20158-\$IJM50U0.exe \$IJM50U0.exe
mv 20159-\$INVG66K.exe \$INVG66K.exe
mv 20160-\$IO4I1J9.exe \$IO4I1J9.exe

# Parse all $I files in the folder
rifiuti-vista ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-2/ > \
  ~/Desktop/Cases/FOR_LAB_009/Export/Lab9-2/Index.txt

# Open result in text editor
gedit Index.txt
```

---

## Key Concepts

### RECYCLER vs $Recycle.bin

| Feature | RECYCLER (XP) | $Recycle.bin (Vista+) |
|---|---|---|
| Index file | One `INFO2` per user | One `$I[suffix]` per deleted file |
| Content file | `D[drive][seq].[ext]` | `$R[suffix].[ext]` |
| Drive column | Yes (physical drive number) | No (drive letter in path) |
| Parse tool | `rifiuti` | `rifiuti-vista` |
| Folder name | `RECYCLER` | `$Recycle.bin` |
| Both hidden? | Yes (system/hidden) | Yes (system/hidden) |

### Why Recycle Bin Evidence Matters

When a file is deleted normally (not Shift+Delete):
1. Windows moves the file bytes to the recycle bin folder
2. Windows records the **original path**, **deletion time**, and **file size** in an index entry
3. The SID subfolder ties the deletion to a **specific user account**

Even if the user later empties the recycle bin, the metadata is gone but the file content may remain in unallocated space — recoverable via data carving.

### INFO2 vs $I File Format Differences

| Field | INFO2 (XP) | $I file (Vista+) |
|---|---|---|
| Index | Sequential number | $I filename suffix |
| Deleted time | Local time | UTC |
| Drive number | Physical drive # | Not present |
| Original path | Full path | Full path |
| File size | Bytes | Bytes |
| OS detection | Not present | Guessed by rifiuti-vista |

### Forensic Significance of Deleted Files

The files found on Mr. Evil's machine in this lab are particularly telling:
- `netstumblerinstaller` — wireless network discovery tool
- `WinPcap` — packet capture library (prerequisite for network sniffers)
- `ethereal` — precursor to Wireshark (network protocol analyzer)

The files found on Mr. Good's machine in Lab9-2:
- `tor-browser` — anonymous browsing (Tor network)
- `FreePortScanner` — network port scanning
- `DiskWipe` — secure file/disk wiping tool
- `VeraCrypt` — disk encryption software
- `Wireshark` — network traffic analyzer

The combination and timing of deletions (all deleted within minutes of each other) is strong behavioral evidence.

### Emptying the Recycle Bin vs Shift+Delete

| Method | Recycle Bin entry? | File recoverable? |
|---|---|---|
| Delete key | Yes — full metadata saved | Yes (from recycle bin) |
| Empty Recycle Bin | No — metadata destroyed | Possible (data carving from unallocated) |
| Shift+Delete | No — bypasses recycle bin entirely | Possible (data carving only) |

---

:::quiz{id="quiz-1"}
Q: In Windows XP, what folder stores deleted files and where is it located on the volume?
- [ ] $Recycle.bin at the volume root
- [x] RECYCLER at the volume root, with SID-named subfolders for each user
- [ ] Trash inside each user's home directory
- [ ] .recycle in the Windows system folder
:::

:::quiz{id="quiz-2"}
Q: A RECYCLER folder contains the file "Dc3.exe". What does this tell you?
- [ ] It was the 3rd file deleted from the D drive
- [x] It was the 3rd file deleted from the C drive (D=deleted, c=C drive, 3=third)
- [ ] It is a system file created by Windows named after drive C
- [ ] It was deleted 3 times before being permanently removed
:::

:::quiz{id="quiz-3"}
Q: What is the Relative Identifier (RID) and what does a RID of 1003 indicate?
- [ ] The file was deleted 1003 times
- [ ] It is the 3rd administrator account
- [x] It identifies the user account; RID ≥ 1000 means a non-system user account, and 1003 means the 4th such account created on this machine
- [ ] It is the physical drive number where files were deleted from
:::

:::quiz{id="quiz-4"}
Q: In the $Recycle.bin format (Vista+), what is the difference between a $R file and a $I file?
- [ ] $R files are read-only; $I files are hidden
- [x] $R contains the actual deleted file content; $I contains the metadata (original path, deletion time, size)
- [ ] $R is for regular files; $I is for images only
- [ ] They are identical copies — one is a backup of the other
:::

:::quiz{id="quiz-5"}
Q: Why must you use `rifiuti-vista` instead of `rifiuti` for Windows 10 recycle bin artifacts?
- [ ] rifiuti-vista is faster and works on both XP and Vista
- [ ] rifiuti does not work on Linux
- [x] The two formats are structurally different: INFO2 (XP) vs individual $I files (Vista+); each tool is built to parse its respective format
- [ ] rifiuti-vista adds color to the output
:::

:::quiz{id="quiz-6"}
Q: When Autopsy exports multiple $I files in bulk, what must you do before running rifiuti-vista?
- [ ] Convert them to CSV format first
- [ ] Combine them into a single INFO2 file
- [x] Rename each file to remove the numeric offset prefix Autopsy prepends (e.g., rename "20156-$IEYEZMZ.exe" to "$IEYEZMZ.exe")
- [ ] Move them to the /tmp directory
:::

---

## Quick Reference

### rifiuti Command Syntax

```bash
# Windows XP — parse a single INFO2 file
rifiuti /path/to/INFO2 > output.txt

# Windows Vista/7/8/10 — parse a folder of $I files
rifiuti-vista /path/to/folder/ > output.txt

# View output
gedit output.txt
```

### Recycle Bin Forensic Checklist

| Step | Action |
|---|---|
| 1 | Identify OS version (Documents and Settings = XP; Users = Vista+) |
| 2 | Locate RECYCLER or $Recycle.bin at volume root |
| 3 | List SID subfolders — one per user who deleted files |
| 4 | Decode SID to identify user (check SAM via RegRipper) |
| 5 | Note RIDs ≥ 1000 — tells you how many non-system accounts existed |
| 6 | Export INFO2 (XP) or $I files (Vista+) |
| 7 | If Vista+: rename files to strip Autopsy offset prefix |
| 8 | Run rifiuti or rifiuti-vista, redirect output to .txt |
| 9 | Document: original paths, deletion timestamps, file sizes |
| 10 | Correlate deleted file names with investigation context |

### OS Detection by Folder Name

| Folder present | OS conclusion |
|---|---|
| `Documents and Settings` + `RECYCLER` | Windows XP or earlier |
| `Users` + `$Recycle.bin` | Windows Vista or later |
| Both present | Vista+ with XP compatibility folder |
