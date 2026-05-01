# Data Carving with HxD and Autopsy

Data recovery is a core facet of digital forensics. Deleted files linger in unallocated space long after they are removed from the file system. **Data carving** recovers those files by scanning raw disk data for known file signatures — the distinctive byte patterns that mark the beginning and end of each file type — without relying on the file system at all.

This lab covers manual carving using **HxD Hex Editor** and automated carving using **Autopsy's PhotoRec Carver** ingest module.

## Overview

- **File signatures** — every file type has a known header (and often a footer) in hex; carving searches for these patterns in raw data
- **Manual carving** — find the header offset, find the footer offset, select the block, export; time-consuming but teaches the fundamentals
- **Automated carving** — Autopsy's PhotoRec Carver does this at scale across the entire unallocated space of a forensic image
- **Evidence file used:** `NDG Lab7.001` — a raw disk image (FEF) containing deleted XLSX, PDF, and JPEG files

---

## File Signature Reference

| File Type | Header (hex) | Header (text) | Footer (hex) | Footer (text) |
|---|---|---|---|---|
| XLSX, DOCX, PPTX | `50 4B 03 04 14 00 06 00` | `PK......` | `50 4B 05 06` + 18 more bytes | `PK..` |
| PDF | `25 50 44 46` | `%PDF` | `0A 25 25 45 4F 46 0D 0A` (or variants) | `.%%EOF..` |
| JPEG / JPG | `FF D8 FF E0` | `ÿØÿà` | `FF D9` | `ÿÙ` |

**Important notes:**
- PDF can have multiple `%%EOF` markers — use the **last** one where zeros follow to the sector boundary
- JPEG `FF D9` footers can produce false positives; confirm by checking that zeros follow through to the end of the sector
- Some file types (like JPEG) have no reliable footer — the carver must estimate file end

---

## Tool Comparison

| Task | HxD (Manual) | Autopsy (Automated) |
|---|---|---|
| Open forensic image | Tools > Open disk image (`Shift+Ctrl+I`) | Add Data Source > Disk Image or VM File |
| Set offset display | View > Offset base > Decimal | N/A |
| Search for hex signature | Search > Find > Hex-values tab (`Ctrl+F`) | PhotoRec Carver ingest module |
| Select a file block | Edit > Select block (`Ctrl+E`) | N/A — automatic |
| Export carved file | File > Save Selection | Right-click > Open in External Viewer (`Ctrl+E`) |
| View carved results | Open saved file | `$CarvedFiles` folder in tree pane |
| Expand archive contents | N/A | Embedded File Extractor ingest module |

---

## Part 1 – Getting to Know File Signatures

### Setup

1. Launch the **WinOS** virtual machine; log in as `Administrator` / `Train1ng$`
2. Open **HxD**: Start Menu > HxD Hex Editor, or double-click the desktop icon
3. Enable the Data Inspector pane: **View > Toolbars > Data Inspector** (ensure it is checked)
4. Open the forensic image: **Tools > Open disk image** (`Shift+Ctrl+I`), browse to `Desktop > Toolbox > Datasets > Lab7`, select `NDG Lab7.001`, click **Open**
5. Sector size prompt: leave as **512 (hard disks/floppy disks)**, click **OK**
6. Set offset display to decimal: **View > Offset base > Decimal**

---

## Part 2 – Manual Carving: XLSX

### Find the XLSX header

1. Open **Find** (`Ctrl+F`), go to **Hex-values** tab
2. Search for: `50 4B 03 04 14 00 06 00`, direction **Forward**, click **OK**
3. The cursor jumps to the XLSX header — note the offset: **6917632**

### Find the XLSX footer

1. Open **Find** again, search for: `50 4B 05 06`, direction **Forward**
2. Navigate to the footer match; find the offset of the last byte of `0x06` — **6931437**
3. Add 18 bytes (the trailer that follows the `PK..` signature): end offset = **6931455**

### Select and export

1. **Edit > Select block** (`Ctrl+E`)
2. Start-offset: `6917632`, End-offset: `6931455`, radio button: **dec**, click **OK**
3. Status bar should read: `Block(d): 6917632-6931455`, Length: `13824`
4. **File > Save Selection** (not Save As), browse to `Evidence Repository (E:) > FOR_LAB_007 > Exported_Files`, filename: `Carved.xlsx`, click **Save**
5. Open `Carved.xlsx` in File Explorer to verify — it should open as a valid spreadsheet (~14 KB)

---

## Part 3 – Manual Carving: PDF

### Find the PDF header

1. Open **Find** (`Ctrl+F`), search for: `25 50 44 46`, direction **All** (PDF is located before the XLSX on this volume), click **OK**
2. Jump to the PDF header — note the offset: **3735040**

### Find the PDF footer

1. Open **Find**, search for: `0D 0A 25 25 45 4F 46 0D 0A`, direction **Forward**
2. Watch for false positives — the real footer has **all zeros** from the last `0A` byte through to the end of the sector; blank spaces (hex `20`) are a false positive
3. Continue searching forward until zeros fill the sector
4. Note the offset of the last byte (`0A`): **6911314**

### Select and export

1. **Edit > Select block** (`Ctrl+E`)
2. Start-offset: `3735040`, End-offset: `6911314`, radio: **dec**, click **OK**
3. Status bar: `Block(d): 3735040-6911314`, Length: `3176275`
4. **File > Save Selection**, save as `Carved.pdf` in `Exported_Files`
5. Open `Carved.pdf` to verify — should open as a valid 4-page PDF (~3.6 MB)

---

## Part 4 – Manual Carving: JPEG

### Find the JPEG header

1. Open **Find** (`Ctrl+F`), search for: `FF D8 FF E0`, direction **Forward**, click **OK**
2. Jump to the JPEG header — note the offset: **6934016**

### Find the JPEG footer

1. Open **Find**, search for: `FF D9`, direction **Forward**
2. Watch for false positives — confirm the real footer by verifying that **zeros fill the remainder of the sector** after the `D9` byte
3. Continue searching (`Ctrl+F` → OK) until you reach the actual end
4. Note the offset of the `D9` byte: **6995053**

### Select and export

1. **Edit > Select block** (`Ctrl+E`)
2. Start-offset: `6934016`, End-offset: `6995053`, radio: **dec**, click **OK**
3. Status bar: `Block(d): 6934016-6995053`, Length: `61038`
4. **File > Save Selection**, save as `Carved.jpg` in `Exported_Files`
5. Open `Carved.jpg` to verify — should display a valid image (~60 KB)

---

## Part 5 – Automated Carving with Autopsy

Manual carving is instructive but impractical at scale. Autopsy's **PhotoRec Carver** automates the same process across the entire unallocated space of a forensic image.

### Create a new case

1. Launch **Autopsy**: Start > Autopsy > Autopsy 4.15.0
2. Click **New Case**
3. Case Name: `FOR_LAB_007_Carving`
4. Base Directory: browse to `Evidence Repository (E:) > FOR_LAB_007`, create a new folder called `Autopsy_Cases`, select it
5. Click **Next**, fill in Optional Information (case number: `NDG007`, examiner name), click **Finish**

### Add the data source

1. In **Add Data Source**, leave **Disk Image or VM File** selected, click **Next**
2. Click **Browse**, navigate to `Desktop > Toolbox > Datasets > Lab7`, select `NDG Lab7.001`, click **Open**
3. Set your time zone from the dropdown, leave sector size as Auto Detect, click **Next**

### Configure ingest modules

1. Click **Deselect All** to clear all modules
2. Check only **PhotoRec Carver** — this runs PhotoRec against unallocated space; leave "Keep corrupted files" unchecked
3. Click **Next**, then **Finish** — Autopsy begins carving; monitor progress in the status bar

### Review carved results

1. In the tree pane: **Data Sources > NDG Lab7.001 > vol2 (NTFS/exFAT 0x07) > $CarvedFiles**
2. Autopsy recovers **13 carved files** — PDF, XLSX, JPG, DOCX, PPTX, 7z, WMA, PNG, MP4, RAR, MP3, and others
3. Click any file to preview content in the lower pane; right-click > **Open in External Viewer** (`Ctrl+E`) to open it in the associated application
4. Carved file names are assigned by PhotoRec using cluster/block numbers, not the original filenames

### Expand archive files

1. **Tools > Run Ingest Modules > NDG Lab7.001**
2. Click **Deselect All**, then check **Embedded File Extractor**
3. Click **Finish** — this expands ZIP, RAR, 7z, and Office compound files and adds their contents to the case
4. Results appear in the tree pane alongside `$CarvedFiles` (e.g., `arc1.7z`, `arc2.zip`, `D7.potx` with their extracted children)

---

:::command-builder{id="hxd-carving-builder"}
tool_name: HxD (Find / Select block)
target_placeholder: "hex_signature"
scan_types:
  - name: "Find XLSX/DOCX/PPTX header"
    flag: "50 4B 03 04 14 00 06 00"
    desc: "PK header for all Office Open XML formats; search Forward from top"
  - name: "Find XLSX/DOCX/PPTX footer"
    flag: "50 4B 05 06"
    desc: "PK end-of-central-directory record; add 18 bytes to get true file end"
  - name: "Find PDF header"
    flag: "25 50 44 46"
    desc: "%PDF — use direction All to catch files that appear before current cursor"
  - name: "Find PDF footer"
    flag: "0D 0A 25 25 45 4F 46 0D 0A"
    desc: "%%EOF with CR/LF; may have false positives — confirm with all-zero tail"
  - name: "Find JPEG header"
    flag: "FF D8 FF E0"
    desc: "JPEG SOI + APP0 marker; search Forward"
  - name: "Find JPEG footer"
    flag: "FF D9"
    desc: "JPEG EOI marker; false positives common — confirm with all-zero sector tail"
options:
  - name: "Decimal offset mode"
    flag: "View > Offset base > Decimal"
    desc: "Switch offsets to decimal so Select block values match directly"
  - name: "Select block"
    flag: "Edit > Select block (Ctrl+E)"
    desc: "Enter Start-offset and End-offset in decimal; radio button must be dec"
  - name: "Save selection"
    flag: "File > Save Selection"
    desc: "Exports only the highlighted bytes as a new file — do NOT use Save As"
  - name: "Data Inspector"
    flag: "View > Toolbars > Data Inspector"
    desc: "Live interpretation of selected bytes; useful for verifying offsets"
:::

---

:::command-builder{id="autopsy-carving-builder"}
tool_name: Autopsy 4.15 (PhotoRec Carver)
target_placeholder: "image.001"
scan_types:
  - name: "Carve unallocated space"
    flag: "PhotoRec Carver (ingest module)"
    desc: "Runs PhotoRec against all unallocated sectors in the image; finds 13+ file types"
  - name: "Expand archive files"
    flag: "Embedded File Extractor (ingest module)"
    desc: "Extracts contents of ZIP, RAR, 7z, DOCX, XLSX, PPTX compound files into the case"
options:
  - name: "Keep corrupted files"
    flag: "PhotoRec Settings > Keep corrupted files"
    desc: "Toggle whether Autopsy retains partially carved files that may not open correctly"
  - name: "Open in external viewer"
    flag: "Right-click file > Open in External Viewer (Ctrl+E)"
    desc: "Opens the carved file in the OS-associated application for verification"
  - name: "View carved files"
    flag: "Data Sources > image.001 > vol > $CarvedFiles"
    desc: "Tree pane location for all PhotoRec results; number in brackets = file count"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Identify File Signatures in a Raw Disk Image"
goal: "Open the FEF in HxD and locate the headers for XLSX, PDF, and JPEG files using hex search."
hint: "Set offset display to Decimal first. Use Search > Find > Hex-values tab. Search Forward for each header. Note the decimal offset shown in the status bar when the header is highlighted."
command: "Search → Find → Hex-values: 50 4B 03 04 14 00 06 00 (Forward)"
expected_output: |
  XLSX header found at offset: 6917632
    50 4B 03 04 14 00 06 00  → PK......  (Office Open XML)
    Sector: 13,511

  PDF header found at offset: 3735040
    25 50 44 46              → %PDF
    Sector: 7,295

  JPEG header found at offset: 6934016
    FF D8 FF E0              → ÿØÿà (JFIF marker)
    Sector: 13,543
:::

:::scenario{id="task-2" level="intermediate"}
title: "Task 2 — Manually Carve an XLSX File"
goal: "Use HxD Select block to highlight the full XLSX file from header to footer+18, then export with Save Selection."
hint: "Footer signature is 50 4B 05 06. Find it, note the offset of 0x06, add 18 bytes. Use Edit > Select block with Start=6917632, End=6931455. Use File > Save Selection (not Save As) and name the file Carved.xlsx."
command: "Edit → Select block: Start 6917632, End 6931455 (dec)"
expected_output: |
  Block(d): 6917632-6931455
  Length(d): 13824

  File saved as Carved.xlsx (~14 KB)
  Opens in Excel without errors — 3-sheet spreadsheet showing forensic tool comparison data
:::

:::scenario{id="task-3" level="intermediate"}
title: "Task 3 — Distinguish Real PDF Footer from False Positives"
goal: "Locate the true PDF %%EOF footer by confirming that only zeros follow the footer bytes to the end of the sector."
hint: "Search for 0D 0A 25 25 45 4F 46 0D 0A (Forward). The first hit may show blank spaces (0x20) after it — that is a false positive. Keep searching Forward until you find the hit followed entirely by 0x00 bytes to the sector boundary."
command: "Search → Find → Hex-values: 0D 0A 25 25 45 4F 46 0D 0A (Forward)"
expected_output: |
  False positive at ~3742748 — followed by 0x20 (space) bytes, NOT zeros. Continue.

  Real footer at offset 6911306:
    0D 0A 25 25 45 4F 46 0D 0A  → .%%EOF..
  Followed by: 00 00 00 00 00...  (zeros to sector boundary)
  
  End-offset of last 0A byte: 6911314
  Block(d): 3735040-6911314, Length: 3176275
:::

:::scenario{id="task-4" level="intermediate"}
title: "Task 4 — Automate Carving with Autopsy PhotoRec Carver"
goal: "Create an Autopsy case, load the FEF, run only the PhotoRec Carver ingest module, and locate the 13 carved files in $CarvedFiles."
hint: "Case name: FOR_LAB_007_Carving. Add data source: NDG Lab7.001. In Configure Ingest Modules, click Deselect All first, then check only PhotoRec Carver. After Finish, navigate to Data Sources > NDG Lab7.001 > vol2 > $CarvedFiles."
command: "Autopsy: New Case → Add Data Source → PhotoRec Carver → Finish"
expected_output: |
  $CarvedFiles (13):
    f000000.pdf   — 3,176,275 bytes
    f0006208.xlsx — 13,824 bytes
    f0006240.jp   — 61,038 bytes
    f0008256.zip  — (archive)
    f0008520.7z   — (archive)
    f0011728.wma
    f0024488.png
    f0049816.mp4
    f0052040.rar
    f0057744.mp3
    ... and more

  Carved files are renamed by PhotoRec using cluster/block numbers.
  Original filenames are not preserved.
:::

---

## Key Concepts

### Why File Signatures?

File extensions are metadata — they can be renamed or removed. File signatures are embedded in the actual file content and cannot be easily changed. A renamed `.jpg` with `.txt` extension still begins with `FF D8 FF E0` — the signature tells the truth.

### Manual vs. Automated Carving

| | Manual (HxD) | Automated (Autopsy) |
|---|---|---|
| Speed | Slow — one file at a time | Fast — entire unallocated space at once |
| Precision | Exact — examiner controls every byte | Variable — depends on PhotoRec heuristics |
| False positives | Examiner must evaluate each hit | Tool filters some; examiner reviews results |
| Learning value | Teaches how carving works internally | Production-ready; used in real investigations |

### False Positives

Both PDF (`%%EOF`) and JPEG (`FF D9`) footers appear frequently inside other files and in slack space. To confirm a real footer:
- **PDF** — the sector should be all zeros after the final `0A` byte
- **JPEG** — zeros should fill from `D9` to the end of the sector

### Unallocated Space

When a file is deleted, the file system removes its directory entry and marks the clusters as available — but the raw bytes remain until overwritten. Carving works by scanning those "available" clusters for file signatures before they are reused.

### PhotoRec Naming Convention

Autopsy uses **PhotoRec** for automated carving. PhotoRec names carved files using the cluster or block number where the file began (e.g., `f0006208.xlsx`). If the file contains enough embedded metadata, PhotoRec may rename it automatically. Carved files will not have their original names.

---

## Quick Reference — Offsets in NDG Lab7.001

| File | Type | Header Offset | Footer Offset | Block Length |
|---|---|---|---|---|
| Carved.pdf | PDF | 3,735,040 | 6,911,314 | 3,176,275 |
| Carved.xlsx | XLSX | 6,917,632 | 6,931,455 | 13,824 |
| Carved.jpg | JPEG | 6,934,016 | 6,995,053 | 61,038 |

> These offsets are specific to `NDG Lab7.001`. Real-world drives will have different values — always search, never assume.

---

:::quiz{id="quiz-1"}
Q: What is the hexadecimal file signature (header) for a JPEG file?
- [ ] 25 50 44 46
- [ ] 50 4B 03 04
- [x] FF D8 FF E0
- [ ] 89 50 4E 47
:::

:::quiz{id="quiz-2"}
Q: Why can a PDF carve produce false positives when searching for the %%EOF footer?
- [ ] PDF files do not have footers
- [x] The %%EOF byte sequence appears inside the PDF body, not just at the end; the real footer is followed by zeros to the sector boundary
- [ ] HxD cannot search for hex values with letters
- [ ] The PDF header and footer are identical
:::

:::quiz{id="quiz-3"}
Q: What is the key difference between using File > Save As and File > Save Selection in HxD when carving?
- [ ] There is no difference; both export the same bytes
- [ ] Save As is faster for large files
- [x] Save Selection exports only the highlighted block; Save As saves the entire open file
- [ ] Save Selection requires administrator privileges
:::

:::quiz{id="quiz-4"}
Q: In Autopsy, which ingest module performs automated file carving against unallocated space?
- [ ] Embedded File Extractor
- [ ] Keyword Search
- [x] PhotoRec Carver
- [ ] Extension Mismatch Detector
:::

:::quiz{id="quiz-5"}
Q: After running PhotoRec Carver in Autopsy, where are the recovered files located in the tree pane?
- [ ] Views > Deleted Files
- [ ] Results > Extracted Content
- [x] Data Sources > [image] > [volume] > $CarvedFiles
- [ ] Tags > Carved
:::

:::quiz{id="quiz-6"}
Q: XLSX, DOCX, and PPTX files all share the same file header. What is it?
- [x] 50 4B 03 04 (the PK ZIP header — all Office Open XML formats are ZIP archives)
- [ ] D0 CF 11 E0 (the older OLE compound document header)
- [ ] 25 50 44 46 (%PDF)
- [ ] FF D8 FF E0 (JPEG)
:::
