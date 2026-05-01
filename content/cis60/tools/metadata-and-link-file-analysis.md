# Metadata and Link File Analysis

Metadata is one of the most delicate but useful forensic artifacts available. Digital devices constantly record and update data about files — when a file was created, last modified, last accessed, which drive it was opened from, and what computer it was on. **Link files** (`.lnk` shortcuts) are a gold mine: Windows automatically creates them in the `Recent` folder every time a user opens a file, capturing target path, timestamps, volume type, volume serial number, network path, NetBIOS name, and MAC address. This lab covers two metadata workflows: link file analysis with **FTK Imager** + **Lnk Examiner**, and embedded document metadata extraction with **MetaExtractor**.

## Overview

Two types of metadata examined in this lab:

- **File system metadata** — stored by the OS in the MFT (NTFS) or FAT directory entry: Date Created, Date Modified, Date Accessed, file size, owner, permissions
- **Embedded metadata** — stored inside the file itself by the creating application: author, title, creation date, last modified by, revision count, application name, print history

Two forensic evidence files used:
- `Lab8-1.E01` — Windows XP NTFS image; user **Mr. Evil**; `Documents and Settings\Mr. Evil\Recent\` contains 8 link files
- `Lab8-2.E01` — FAT16 USB drive labeled **RICHARDUSB**; contains documents with embedded metadata

---

## Tool Comparison

| Task | FTK Imager | Lnk Examiner (via DART) | MetaExtractor |
|---|---|---|---|
| Open forensic image | File > Add Evidence Item > Image File | N/A — loads exported .lnk files | N/A — loads exported documents |
| View file system metadata | Click file → Properties tab | — | First 3 columns |
| View $I30 INDX attributes | Scroll down in Properties | — | — |
| Export files from image | Right-click → Export Files... | — | — |
| Parse link file data | Hex only | Process > Folder | — |
| Export link metadata | — | Export > Save as CSV File | — |
| Parse embedded doc metadata | — | — | Open Folder or Files toolbar |
| Export embedded metadata | — | — | Save to CSV toolbar |

---

## Part 1 – Exporting and Analyzing Link Files with FTK Imager

### Setup

1. Launch **WinOS** VM; log in as `Administrator` / `Train1ng$`
2. Open **FTK Imager**: Start > AccessData > FTK Imager (or double-click desktop icon)
3. Load the image: **File > Add Evidence Item**, select **Image File**, click **Next**
4. Click **Browse**, navigate to `Desktop > Toolbox > Datasets > Lab8 > Lab8-1`, select `Lab8-1.E01`, click **Open**, then **Finish**

### Navigate to the Recent folder

5. In the Evidence Tree, expand: `Lab8-1.E01` → `Partition 1 [4643MB]` → `NONAME [NTFS]` → `[root]`
6. Expand `Documents and Settings` → `Mr. Evil` → `Recent`
7. The File List pane shows 10 items — 8 `.lnk` files and one `$I30` index file

### Read file system metadata

8. Click `yng13.lnk` in the File List, then click the **Properties** tab in the Properties pane
9. File system metadata visible:
   - **Date Accessed:** 8/27/2004 3:14:40 PM
   - **Date Created:** 8/26/2004 3:08:12 PM
   - **Date Modified:** 8/26/2004 3:08:12 PM
   - File Size: 575 bytes; Physical Size: 576 bytes

10. Scroll down in the Properties pane to see **$I30 INDX** attributes — these are index entries stored in the `$I30` file and mirror MFT timestamps:
    - **INDX Entry Filename:** yng13.lnk
    - **INDX Entry File Size:** 575
    - **INDX Entry Date Created:** 8/26/2004 3:08:12 PM
    - **INDX Entry Date Modified:** 8/26/2004 3:08:12 PM
    - **INDX Entry Date Accessed:** 8/27/2004 3:14:40 PM
    - **INDX Entry Date Changed:** 8/26/2004 3:08:12 PM

### Export link files

11. Select all 8 `.lnk` files (hold `Ctrl` and click each: `Anonymizer.lnk`, `channels (2).lnk`, `channels.lnk`, `GhostWare.lnk`, `keys.lnk`, `Receipt.lnk`, `Temp on m1200 (4.12.220.254).lnk`, `yng13.lnk`)
12. Right-click any highlighted file → **Export Files...**
13. Navigate to `Evidence Repository (E:)`, click **Make New Folder**, name it `FOR_LAB_008`, click it, click **Make New Folder** again, name it `Link_Files`, click **OK**
14. Export Results: 8 file(s) exported successfully, 3965 bytes copied

---

## Part 2 – Lnk Examiner via DART

**Lnk Examiner** (LNK File Previewer) is a lightweight tool in the **Digital Advanced Response Toolkit (DART)** that parses all link file fields into a table view and exports to CSV.

### Launch DART and Lnk Examiner

1. Open Windows File Explorer, browse to `Desktop > Toolbox > deft-8.2-002`
2. Double-click **dart.exe** — accept the DART DISCLAIMER by clicking **Yes**
3. When prompted for a log directory: browse to `Evidence Repository (E:) > FOR_LAB_008`, create a new folder `DART_LOGS`, select it, click **OK**
4. In the DART main window: click **Forensics** category → expand **Windows Forensics** → click **LnkExaminer** → click **START AS ADMIN**

### Lnk Examiner interface

| Option | Description |
|---|---|
| Process > Folder | Select the folder containing .lnk files to parse |
| Export > Save as CSV File | Export the entire parsed table to CSV |
| Recurse Sub-folders | Include sub-folders within the selected folder |
| Target Details pane | View extracted metadata for the selected file |
| Process Log pane | View volume of files processed |

---

## Part 3 – Extracting Data from Link Files with Lnk Examiner

### Load and parse link files

1. In Lnk Examiner: **Process > Folder**
2. Browse to `Evidence Repository (E:) > FOR_LAB_008 > Link_Files`, click **OK**
3. The table populates with 8 rows — one per link file

### Reading the columns

**Left columns (target file info):**

| Column | Description | Example values |
|---|---|---|
| Filename | Name of the .lnk file | `yng13.lnk` |
| Path | Local path to the target file | `D:\Drivers\Anonymizer` |
| Created (UTC) | Target file creation timestamp | `7/28/2004 12:39:49 PM` |
| Last Written (UTC) | Target file last modified timestamp | `8/26/2004 1:49:28 PM` |
| Last Access (UTC) | Target file last access timestamp | `8/26/2004 3:07:04 PM` |
| File Size | Size of the target file | `921654` |
| Attributes | Type of item the shortcut points to | `Archive`, `Directory`, `Read Only` |

**Right columns (volume and network info):**

| Column | Description | Example values |
|---|---|---|
| Volume Type | Storage type of the volume | `CD-ROM`, `Fixed Disk` |
| Volume Serial | Serial number of the volume | `1A3A-D55E`, `6CB1-8D9B` |
| Volume Name | Name of the volume | `Jul 28 2004` (CD label) |
| Network Path | UNC path if file was on a network share | `\\4.12.220.254\TEMP` |
| NetBIOS | Computer name the file resided on | `n-1a9odn6zx4lq` |
| MAC Address | MAC of the computer the file was on | `00:10:A4:93:3E:09` |

**Key observations from the lab data:**
- 4 files/folders resided on a **CD-ROM** (volume serial `1A3A-D55E`, named "Jul 28 2004")
- 2 files resided on a **Fixed Disk** (internal drive, volume serial `6CB1-8D9B`)
- 2 files were accessed from **network path** `\\4.12.220.254\TEMP` — this reveals the IP address of the network device
- 2 files with network path entries have a MAC address of `00:02:3F:B3:E5:70`

### Export to CSV

9. **Export > Save as CSV File**
10. Navigate to `FOR_LAB_008`, create a new folder `Lnk_Report`, open it
11. Filename: `Exported Lnk Metadata`, click **Save**

---

## Part 4 – Exporting Regular Files with FTK Imager

### Load the second image

1. In FTK Imager: **File > Remove All Evidence Items**
2. **File > Add Evidence Item** → **Image File** → Browse to `Desktop > Toolbox > Datasets > Lab8 > Lab8-2 > Lab8-2.E01` → **Open** → **Finish**
3. Expand: `Lab8-2.E01` → `RICHARDUSB [FAT16]` → `[root]`

### Select and export document files

4. In the File List, hold `Ctrl` and select these 7 files:
   - `19861-sc-clients-national.xls`
   - `Ar17_en.pdf`
   - `Kaczynski2.pdf`
   - `Kpmg-feature-sep-2010.pdf`
   - `LBTH_Tall_Buildings_Report_24_07_17.pdf`
   - `Only Death Pablo Neruda.docx`
   - `TuringComputing.pdf`

5. Right-click → **Export Files...**
6. Navigate to `FOR_LAB_008`, create new folder `Metadata_Analysis`, click **OK**
7. Export Results: 7 file(s) exported, 48,783,357 bytes copied

---

## Part 5 – MetaExtractor Overview

**MetaExtractor v1.5** by **4Discovery** extracts embedded metadata from document files (PDF, DOCX, XLS, etc.) and presents all fields in a scrollable table.

### Launch

Browse to `Desktop > Toolbox > MetaExtractor`, double-click **MetaExtractor.exe**

### Toolbar options

| Toolbar Icon | Option | Description |
|---|---|---|
| Floppy disk | Save to CSV | Export the entire metadata table to CSV |
| File icon | Open File(s) | Choose specific files to extract metadata from |
| Folder icon | Open Folder or Files | Choose a folder — processes all supported files within it |

---

## Part 6 – Extracting Metadata with MetaExtractor

### Load files

1. Click the **Open Folder or Files** toolbar icon
2. Browse to `Evidence Repository (E:) > FOR_LAB_008 > Metadata_Analysis`, select the folder, click **Select Folder**
3. MetaExtractor parses all 7 files — status bar shows "Parsed 7 files."

### MetaExtractor columns reference

**File system metadata (first 3 columns):**

| Column | Description | Forensic significance |
|---|---|---|
| File Modified Date | OS-level last modified date | Can be manipulated; compare with embedded |
| File Access Date | OS-level last access date | Updated when file is opened |
| File Creation Date | OS-level creation date on this volume | Changes when file is copied to a new volume |

**Embedded metadata (scroll right):**

| Column | Description | Forensic significance |
|---|---|---|
| File Name | Name of the file | — |
| File Path | Current path on analysis workstation | Use with caution — reflects export path, not original |
| File MD5 | MD5 hash of the file | Verify integrity; check against known-file databases |
| Author | User name recorded when file was created | Identifies original creator |
| Title | Document title field | May reveal original filename or InDesign source |
| Subject | Document subject field | — |
| Category / Company / Keywords | Additional document properties | Organizational metadata |
| Created | Embedded creation date | More reliable than file system date — harder to spoof |
| Modified | Embedded last modified date | Reflects last save, not OS copy |
| Last Modified By | Username of last person to save | Identifies last editor |
| Revision | Number of times the document was saved | Helps gauge authenticity |
| Application Name | Software that created/last edited the file | Traces file origins (e.g., Adobe InDesign, MS Word) |
| Char Count / Word Count / Page Count | Document statistics | — |
| Paragraph Count / Line Count | Document statistics | — |
| Last Printed / Last Printed By | Print history | Shows if/when/who printed |
| Edit Time | Total time document was open in edit mode | — |
| Template / Template Filename | Template used to create the document | — |

### Key findings from the lab data

- **Modified dates predate Creation dates** for all 7 files — this indicates the files were created on a different device and copied to the RICHARDUSB drive (FAT16 resets the creation date on copy)
- `kpmg-feature-sep-2010.pdf`: Author = **Production1**, Title = **026-029_FMW_KPMG.indd** — reveals the file was originally an Adobe InDesign document
- `Only Death Pablo Neruda.docx`: Author = **Connor Cleak**, Last Modified By = **Connor Cleak** (11 revisions)
- Application Name column reveals the software used: Adobe InDesign CC 13.0 (Macintosh), Adobe InDesign CS3, Adobe InDesign CC 2015 (Macintosh), Microsoft Office Word

### Save results

16. Click **Save to CSV** toolbar icon
17. Navigate to `FOR_LAB_008`, create new folder `Metadata_Report`, enter filename `Exported File Metadata`, click **Save**

---

:::command-builder{id="ftk-imager-lnk-builder"}
tool_name: FTK Imager (Link File Export)
target_placeholder: "Lab8-1.E01"
scan_types:
  - name: "Load forensic image"
    flag: "File > Add Evidence Item > Image File"
    desc: "Select .E01 or other FEF; FTK Imager auto-detects partitions and file systems"
  - name: "Navigate to Recent folder (Windows XP)"
    flag: "[root] > Documents and Settings > [username] > Recent"
    desc: "Windows XP stores LNK shortcuts here; Vista+ uses Users\\[username]\\AppData\\Roaming\\Microsoft\\Windows\\Recent"
  - name: "View file system metadata"
    flag: "Click file → Properties tab"
    desc: "Shows Date Accessed, Date Created, Date Modified, file size, owner, Security ID"
  - name: "View $I30 INDX attributes"
    flag: "Scroll down in Properties tab"
    desc: "INDX entries mirror MFT timestamps and can provide accurate creation/access/modified dates"
  - name: "Export selected files"
    flag: "Ctrl+click files → right-click → Export Files..."
    desc: "Exports selected files to the destination folder while preserving file content"
  - name: "Remove loaded evidence"
    flag: "File > Remove All Evidence Items"
    desc: "Clears the Evidence Tree before loading a new FEF"
options:
  - name: "Image File source type"
    flag: "Select Source: Image File"
    desc: "Use for .E01, .001, .dd, and other raw/EnCase forensic image formats"
  - name: "Export Files vs Export File Hash List"
    flag: "right-click → Export Files..."
    desc: "Export Files saves the actual file bytes; Export File Hash List saves MD5/SHA1 hashes only"
:::

---

:::command-builder{id="lnk-examiner-builder"}
tool_name: Lnk Examiner (LNK File Previewer v1.0)
target_placeholder: "Link_Files folder"
scan_types:
  - name: "Load a folder of .lnk files"
    flag: "Process > Folder"
    desc: "Select the folder containing exported .lnk files; populates the table immediately"
  - name: "Export parsed data"
    flag: "Export > Save as CSV File"
    desc: "Saves the entire table (all columns) as a CSV — no need to select individual rows"
options:
  - name: "Recurse Sub-folders"
    flag: "Recurse Sub-folders checkbox"
    desc: "Also process .lnk files in any sub-folders within the selected directory"
  - name: "Target Details pane"
    flag: "Click a row in the table"
    desc: "Shows full metadata for the selected link file in the lower-left pane"
:::

---

:::command-builder{id="metaextractor-builder"}
tool_name: MetaExtractor v1.5
target_placeholder: "Metadata_Analysis folder"
scan_types:
  - name: "Load a folder of documents"
    flag: "Open Folder or Files toolbar icon"
    desc: "Process all supported files (PDF, DOCX, XLS, etc.) in the selected folder"
  - name: "Load specific files"
    flag: "Open File(s) toolbar icon"
    desc: "Select individual files to extract metadata from"
  - name: "Export to CSV"
    flag: "Save to CSV toolbar icon"
    desc: "Export the full table to CSV for reporting; all columns included automatically"
options:
  - name: "Scroll columns right"
    flag: "Horizontal scroll bar arrow"
    desc: "MetaExtractor has many columns; scroll right to see Author, Created, Modified, Application Name, etc."
  - name: "File Path column caveat"
    flag: "File Path column"
    desc: "Reflects path on analysis workstation (after export), NOT the original evidence path — do not use for provenance"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Read File System Metadata for a Link File in FTK Imager"
goal: "Load Lab8-1.E01 in FTK Imager, navigate to Mr. Evil's Recent folder, and read the file system metadata for yng13.lnk."
hint: "Add evidence item as Image File. Navigate: NONAME [NTFS] > [root] > Documents and Settings > Mr. Evil > Recent. Click yng13.lnk then click the Properties tab. Scroll down to see the $I30 INDX entries below the basic metadata."
command: "Evidence Tree → Recent → yng13.lnk → Properties tab"
expected_output: |
  File system metadata (from MFT):
    Name:           yng13.lnk
    File Class:     Regular File
    File Size:      575 bytes
    Physical Size:  576 bytes
    Date Accessed:  8/27/2004 3:14:40 PM
    Date Created:   8/26/2004 3:08:12 PM
    Date Modified:  8/26/2004 3:08:12 PM
    Encrypted:      False

  $I30 INDX attributes (from directory index):
    INDX Entry Filename:      yng13.lnk
    INDX Entry File Size:     575
    INDX Entry Date Created:  8/26/2004 3:08:12 PM
    INDX Entry Date Modified: 8/26/2004 3:08:12 PM
    INDX Entry Date Accessed: 8/27/2004 3:14:40 PM
    INDX Entry Date Changed:  8/26/2004 3:08:12 PM
:::

:::scenario{id="task-2" level="intermediate"}
title: "Task 2 — Parse Link Files with Lnk Examiner and Identify Network Access"
goal: "Load the exported link files into Lnk Examiner and identify which files were accessed from a network location, including the network IP, MAC address, and NetBIOS name."
hint: "In DART, go to Forensics > Windows Forensics > LnkExaminer > START AS ADMIN. Use Process > Folder, browse to Link_Files. Scroll right in the table to find the Network Path, NetBIOS, and MAC Address columns."
command: "Process > Folder → Link_Files → scroll to Network Path column"
expected_output: |
  8 link files parsed. Network-accessed files:

  Temp on m1200 (4.12.220.254).lnk:
    Path:         (blank — network only)
    Network Path: \\4.12.220.254\TEMP
    Volume Type:  (blank)
    MAC Address:  00:02:3F:B3:E5:70

  yng13.lnk:
    Path:         (blank — network only)
    Network Path: \\4.12.220.254\TEMP
    Volume Type:  (blank)
    MAC Address:  00:02:3F:B3:E5:70

  Local volume files (4 on CD-ROM, 2 on Fixed Disk):
    Volume Serial CD-ROM: 1A3A-D55E (Volume Name: Jul 28 2004)
    Volume Serial Fixed:  6CB1-8D9B
    NetBIOS for Fixed:    n-1a9odn6zx4lq
    MAC for Fixed:        00:10:A4:93:3E:09
:::

:::scenario{id="task-3" level="intermediate"}
title: "Task 3 — Detect File Origin Manipulation with MetaExtractor"
goal: "Load the 7 exported documents into MetaExtractor and identify the anomaly in dates that reveals the files were created on a different device."
hint: "Use Open Folder or Files, select the Metadata_Analysis folder. Look at the first 3 columns (File Modified Date, File Access Date, File Creation Date). Compare File Modified Date with File Creation Date — if Modified predates Created, the file was copied from elsewhere."
command: "Open Folder or Files → Metadata_Analysis → compare date columns"
expected_output: |
  Anomaly detected for all 7 files:
    File Modified Date is EARLIER than File Creation Date

  Example:
    File:              kaczynski2.pdf
    File Modified:     10/1/2018 3:28:32 PM
    File Creation:     12/10/2018 9:54:27 AM  ← LATER than Modified

  Interpretation: Modified dates predate creation dates because the files were
  created on another device and then COPIED to the RICHARDUSB FAT16 drive.
  FAT16 resets the creation date to the copy timestamp.
  This is a classic indicator of file transfer from a different system.
:::

:::scenario{id="task-4" level="intermediate"}
title: "Task 4 — Trace File Origins Using Embedded Application Metadata"
goal: "In MetaExtractor, scroll to the Application Name and Title columns to determine what software created the kpmg-feature-sep-2010.pdf file and what its original source document was."
hint: "Scroll right in MetaExtractor to the Author and Title columns first, then continue scrolling to Application Name. A .indd title extension reveals the source application."
command: "MetaExtractor → scroll to Title and Application Name columns"
expected_output: |
  File: kpmg-feature-sep-2010.pdf
    Author:           Production1
    Title:            026-029_FMW_KPMG.indd
    Application Name: Adobe InDesign CS3 (5.0.4)

  Interpretation:
    - Title ending in .indd = file was originally an Adobe InDesign document
    - The PDF was exported FROM a file named 026-029_FMW_KPMG.indd
    - Application Name confirms InDesign was the creating application
    - This traces the document's origin before it was converted to PDF

  File: Only Death Pablo Neruda.docx
    Author:          Connor Cleak
    Last Modified By: Connor Cleak
    Revision:        11
    Application Name: Microsoft Office Word
:::

---

## Key Concepts

### File System Metadata vs. Embedded Metadata

| | File System Metadata | Embedded Metadata |
|---|---|---|
| Stored by | Operating system (MFT, FAT directory) | Application (inside the file) |
| Visible in | FTK Imager Properties tab, Windows Properties | MetaExtractor, document Properties |
| Can be changed by | Copying the file, timestamp manipulation tools | Editing the file in the application |
| Reliability | Lower — easily manipulated | Higher — harder to alter without a trace |
| Key fields | Created, Modified, Accessed | Author, Created, Modified, Last Modified By, Revision, App |

When the two conflict, **embedded metadata is generally more trustworthy** and reliable as evidence. Discrepancies between file system and embedded dates are a strong indicator of tampering or file transfer.

### Link Files (.lnk) as Forensic Artifacts

Windows automatically creates a `.lnk` shortcut in the `Recent` folder every time a file is opened. These shortcuts persist even after the target file is deleted and contain:

- **Target path** — exact location of the file when it was opened
- **Timestamps** — when the target was created, last modified, last accessed (in UTC)
- **File size** — size of the target at time of access
- **Volume type** — whether the file was on a local disk, CD-ROM, or network
- **Volume serial number** — uniquely identifies the specific drive
- **Volume name** — human-readable label of the drive
- **Network path** — UNC path if the file was on a network share (reveals IP/hostname)
- **NetBIOS name** — computer name where the file resided
- **MAC address** — hardware address of the network interface

### $I30 INDX Attributes

NTFS directories store an index of their contents in a special `$I30` file. Each **INDX entry** contains a copy of the file's MFT timestamps. These can be compared with MFT entries to detect timestamp manipulation — if the MFT entry has been altered but the INDX entry has not, the discrepancy is evident.

### Modified Before Created: The Copy Artifact

When a file is copied to a new volume:
- **FAT/FAT16/FAT32** — resets the creation date to the copy timestamp
- **NTFS** — preserves the original creation date

So on a FAT volume, if `File Modified Date < File Creation Date`, the file was almost certainly created elsewhere and copied to this volume. This is a reliable indicator of file provenance.

### Volume Serial Numbers as Evidence

The Volume Serial Number (VSN) embedded in a link file proves which specific drive a file was accessed from — even if that drive is no longer available. A match between a VSN in a link file and a VSN on a recovered drive definitively places that file on that drive at a specific time.

---

:::quiz{id="quiz-1"}
Q: Where does Windows automatically store .lnk shortcut files when a user opens a document?
- [ ] The Desktop folder
- [x] The Recent folder (Documents and Settings\[user]\Recent on XP; Users\[user]\AppData\Roaming\Microsoft\Windows\Recent on Vista+)
- [ ] The Temp folder
- [ ] The Start Menu folder
:::

:::quiz{id="quiz-2"}
Q: A link file shows a Network Path of \\192.168.1.50\Share and a MAC address. What does this tell the investigator?
- [ ] The file was stored locally on the suspect's machine
- [ ] The file was deleted from a CD-ROM
- [x] The file was accessed from a network share at IP 192.168.1.50, and the MAC identifies the network interface of that device
- [ ] The file was encrypted before being accessed
:::

:::quiz{id="quiz-3"}
Q: In MetaExtractor, all 7 files show File Modified dates that are earlier than File Creation dates. What is the most likely explanation?
- [ ] The files were created with incorrect system clocks
- [ ] MetaExtractor has a bug that reverses the date columns
- [x] The files were created on a different device and later copied to this volume; the FAT file system reset the creation date to the copy timestamp
- [ ] The files were encrypted and decrypted, resetting timestamps
:::

:::quiz{id="quiz-4"}
Q: What does the $I30 INDX attribute in an NTFS directory contain, and why is it forensically useful?
- [ ] It stores encrypted file content for recovery
- [x] It stores index entries that mirror MFT file timestamps; comparing INDX entries with MFT entries can detect timestamp manipulation
- [ ] It records the last program that accessed each file
- [ ] It contains the file's hash values for integrity checking
:::

:::quiz{id="quiz-5"}
Q: A PDF's embedded Title field reads "026-029_FMW_KPMG.indd" and its Application Name is "Adobe InDesign CS3". What can the examiner conclude?
- [ ] The PDF was created directly in Adobe Reader
- [ ] The file title is corrupt and should be ignored
- [x] The PDF was exported from an Adobe InDesign source file named 026-029_FMW_KPMG.indd, tracing the document's origin before PDF conversion
- [ ] InDesign is the PDF viewer, not the creator
:::

:::quiz{id="quiz-6"}
Q: Which type of metadata is generally more reliable for establishing when a document was originally created — file system metadata or embedded metadata?
- [ ] File system metadata, because it is controlled by the OS and cannot be changed
- [x] Embedded metadata, because it is stored inside the file by the application and is harder to manipulate without leaving a trace
- [ ] Both are equally reliable
- [ ] Neither is reliable; only hash values should be used
:::

---

## Quick Reference — Link File Columns in Lnk Examiner

| Column | What it proves |
|---|---|
| Path | Where the file was when it was opened |
| Created (UTC) | When the target file was created |
| Last Written (UTC) | When the target file was last modified |
| Last Access (UTC) | When the target file was last opened |
| File Size | Size of the target at time of access |
| Attributes | Whether target was a file, directory, read-only, archive |
| Volume Type | Local disk vs. CD-ROM vs. (blank = network) |
| Volume Serial | Unique ID of the drive — ties a file to a specific disk |
| Volume Name | Human-readable drive label |
| Network Path | IP/hostname if accessed over network |
| NetBIOS | Computer name of the device holding the file |
| MAC Address | Hardware address of the network interface |

## Quick Reference — MetaExtractor Columns

| Column group | Key fields |
|---|---|
| File system | File Modified Date, File Access Date, File Creation Date |
| Identity | File Name, File Path, File MD5 |
| Authorship | Author, Last Modified By |
| Document info | Title, Subject, Category, Company, Keywords |
| Timestamps (embedded) | Created, Modified |
| Revision | Revision count, Edit Time |
| Software | Application Name |
| Content stats | Char Count, Word Count, Page Count, Paragraph Count, Line Count |
| Print history | Last Printed, Last Printed By |
| Template | Template, Template Filename |
