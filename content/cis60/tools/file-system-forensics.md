# File System Forensics with HxD

Understanding file systems at the hex level is a core skill in digital forensics. Partitions define how much data is accessible; file systems define how that data is stored and addressed. This lab covers how to read MBR partition tables and VBRs for the three most common Windows file systems — FAT, NTFS, and exFAT — using HxD on Windows and equivalent Linux commands.

## Overview

This lab uses **Forensic Evidence Files (FEFs)** — raw disk images opened directly in a hex editor:

- **MBR (Master Boot Record)** — sector 0 of every disk; contains the partition table
- **VBR (Volume Boot Record)** — the first sector of each partition; identifies the file system
- **Little-endian byte order** — most MBR and VBR values are stored in reverse byte order
- **Offset navigation** — all artifacts are found by jumping to known byte offsets
- **Data Inspector** — HxD's built-in pane that converts selected bytes into decimal, hex, and date values in real time

The three FEFs used in this lab:
- `NDG FAT Lab5.001` — FAT16-formatted volume
- `NDG NTFS Lab5.001` — NTFS-formatted volume
- `NDG exFAT Lab5.001` — exFAT-formatted volume

---

## Tool Comparison

| Task | HxD (Windows) | Linux |
|------|---------------|-------|
| Open a disk image | Tools > Open disk image (`Shift+Ctrl+I`) | `xxd`, `hexdump -C`, or `gdisk -l` |
| Jump to a byte offset | Search > Go to (`Ctrl+G`) | `xxd -s <offset> -l <len>` |
| Read values in decimal | View > Offset base > Decimal | `python3 -c "import struct; ..."` |
| Interpret bytes live | Data Inspector pane | `python3 struct.unpack` or `xxd` + math |
| Parse partition table | Navigate to offset 446 | `fdisk -l image.001` or `mmls image.001` |
| Find file system type | 5th byte of partition entry at offset 446 | `fsstat image.001` (TSK) |
| Read VBR OEM ID | Offset 32259 (sector 63, byte 3) | `xxd -s 32259 -l 8 image.001` |
| Get volume serial number | Offset 32295 (FAT), 32328 (NTFS/exFAT) | `xxd -s <offset> -l 4 image.001` |

---

## MBR Structure Reference

The **Master Boot Record** occupies sector 0 (bytes 0–511) and has three sections:

| Decimal Offset | Hex Offset | Length (bytes) | Description |
|----------------|------------|----------------|-------------|
| 0 – 445 | 0x000 – 0x1BD | 446 | Bootstrap Code Area |
| 446 – 509 | 0x1BE – 0x1FD | 64 | Partition Table (four 16-byte entries) |
| 510 – 511 | 0x1FE – 0x1FF | 2 | Boot Record Signature (`0x55 AA`) |

Each 16-byte partition entry breaks down as:

| Bytes | Length | Description |
|-------|--------|-------------|
| 1 | 1 | Status: `0x80` = bootable, `0x00` = inactive |
| 3 | 3 | CHS start of partition (little-endian) |
| 1 | 1 | **File system type**: `0x0E` = FAT16, `0x07` = NTFS or exFAT |
| 3 | 3 | CHS end of partition (little-endian) |
| 4 | 4 | LBA start sector (little-endian) — multiply × 512 for byte offset |
| 4 | 4 | Number of sectors (little-endian) — multiply × 512 for volume size |

---

## VBR Artifacts by File System

### FAT VBR (sector 63 → byte offset 32256)

| Hex Offset | Dec Offset | Universal | Len | Name | Example Value |
|------------|------------|-----------|-----|------|---------------|
| 0x7E00 | 32256 | 0x00 | 3 | Jump Instruction | `EB 3C 90` |
| 0x7E03 | 32259 | 0x03 | 8 | OEM ID | `MSDOS5.0` |
| 0x7E0B | 32267 | 0x0B | 2 | Bytes per Sector | `0x00 02` → 512 |
| 0x7E0D | 32269 | 0x0D | 1 | Sectors per Cluster | `0x02` → 2 (cluster = 1024 bytes) |
| 0x7E15 | 32277 | 0x15 | 1 | Media Descriptor | `0xF8` = fixed disk, `0xF0` = removable |
| 0x7E20 | 32288 | 0x20 | 8 | Total Sectors on Volume | `86 39 01 00` → 80262 sectors (≈41 MB) |
| 0x7E27 | 32295 | 0x27 | 4 | Volume Serial Number | Little-endian: read right-to-left |
| 0x7E36 | 32310 | 0x36 | 8 | File System Type | ASCII `FAT16` |
| 0x7FFE | 32766 | 0x1FE | 2 | Boot Signature | `55 AA` |

### NTFS VBR (sector 63 → byte offset 32256)

| Hex Offset | Dec Offset | Universal | Len | Name | Example Value |
|------------|------------|-----------|-----|------|---------------|
| 0x7E00 | 32256 | 0x00 | 3 | Jump Instruction | `EB 52 90` |
| 0x7E03 | 32259 | 0x03 | 8 | OEM ID | `NTFS    ` |
| 0x7E0B | 32267 | 0x0B | 2 | Bytes per Sector | `0x00 02` → 512 |
| 0x7E0D | 32269 | 0x0D | 1 | Sectors per Cluster | `0x08` → 8 (cluster = 4096 bytes) |
| 0x7E20 | 32296 | 0x28 | 8 | Total Sectors on Volume | `85 39 01 00 00 00 00 00` → 80261 |
| 0x7E04 | 32304 | 0x30 | 8 | MFT Starting Cluster | `10 0D 00...` → 3344 |
| 0x7E48 | 32328 | 0x48 | 4 | Volume Serial Number | Little-endian, e.g. `A02A-DDC0` |
| 0x7FFE | 32766 | 0x1FE | 2 | Boot Signature | `55 AA` |

### exFAT VBR (sector 63 → byte offset 32256)

| Hex Offset | Dec Offset | Universal | Len | Name | Note |
|------------|------------|-----------|-----|------|------|
| 0x7E00 | 32256 | 0x00 | 3 | Jump Instruction | `EB 76 90` |
| 0x7E03 | 32259 | 0x03 | 8 | OEM ID | ASCII `EXFAT   ` |
| 0x7E0B | 32267 | 0x0B | 53 | Must be zero | 53 null bytes — unique exFAT identifier |
| 0x7E40 | 32320 | 0x40 | 8 | Partition Offset | Sectors from start of media |
| 0x7E48 | 32328 | 0x48 | 8 | Volume Length | Total sectors, e.g. 80262 (≈41 MB) |
| 0x7E6C | 32364 | 0x6C | 1 | Bytes per Sector shift | 2^N = bytes per sector |
| 0x7E6D | 32365 | 0x6D | 1 | Sectors per Cluster shift | 2^N = sectors per cluster |
| 0x7E48 | 32356 | 0x64 | 4 | Volume Serial Number | Little-endian, e.g. `7CC5-06E4` |
| 0x7FFE | 32766 | 0x1FE | 2 | Boot Signature | `55 AA` |

---

:::command-builder{id="hxd-navigation-builder"}
tool_name: HxD (Go to)
target_placeholder: "offset_value"
scan_types:
  - name: "MBR partition table"
    flag: "446"
    desc: "Jump to the first 16-byte partition entry; read file system type at byte 5"
  - name: "FAT VBR start"
    flag: "32256"
    desc: "Jump to sector 63 — beginning of the FAT/NTFS/exFAT Volume Boot Record"
  - name: "OEM ID (file system name)"
    flag: "32259"
    desc: "Highlight 8 bytes to read ASCII OEM ID: MSDOS5.0, NTFS, or EXFAT"
  - name: "Bytes per sector"
    flag: "32267"
    desc: "Highlight 2 bytes; little-endian value, usually 512 (0x00 02)"
  - name: "Sectors per cluster (FAT/NTFS)"
    flag: "32269"
    desc: "Highlight 1 byte; multiply by bytes-per-sector to get cluster size"
  - name: "Media descriptor (FAT)"
    flag: "32277"
    desc: "Highlight 1 byte; 0xF8 = fixed disk, 0xF0 = removable media"
  - name: "Total sectors (FAT)"
    flag: "32288"
    desc: "Highlight 8 bytes; little-endian; multiply by 512 for volume size in bytes"
  - name: "Volume serial number (FAT)"
    flag: "32295"
    desc: "Highlight 4 bytes; read right-to-left (little-endian) for VSN"
  - name: "Total sectors (NTFS)"
    flag: "32296"
    desc: "Highlight 8 bytes; little-endian; e.g. 80261 sectors = 41 MB"
  - name: "MFT starting cluster (NTFS)"
    flag: "32304"
    desc: "Highlight 8 bytes; tells you where the Master File Table begins"
  - name: "Volume serial number (NTFS/exFAT)"
    flag: "32328"
    desc: "Highlight 4 bytes; little-endian VSN"
  - name: "Volume length (exFAT)"
    flag: "32328"
    desc: "Highlight 8 bytes; total sectors in the exFAT volume"
  - name: "Volume serial number (exFAT)"
    flag: "32356"
    desc: "Highlight 4 bytes; little-endian VSN, e.g. 7CC5-06E4"
options:
  - name: "Decimal offset mode"
    flag: "View > Offset base > Decimal"
    desc: "Switch the offset column to decimal so you can jump directly to decimal offsets"
  - name: "Little-endian read"
    flag: "Reverse byte order"
    desc: "All multi-byte MBR/VBR values are little-endian — read bytes right-to-left"
  - name: "Data Inspector"
    flag: "View > Toolbars > Data Inspector"
    desc: "Shows real-time decimal/hex/date interpretation of highlighted bytes"
:::

---

:::command-builder{id="linux-hex-builder"}
tool_name: xxd / mmls / fsstat
target_placeholder: "image.001"
scan_types:
  - name: "List partitions"
    flag: "-l image.001"
    desc: "Use mmls (The Sleuth Kit) to list all partition entries with start/end sectors"
  - name: "Read MBR partition table"
    flag: "-s 446 -l 64 image.001 | xxd"
    desc: "Dump the 64-byte partition table starting at byte 446"
  - name: "Read VBR OEM ID"
    flag: "-s 32259 -l 8 image.001"
    desc: "Dump 8 bytes of OEM ID at sector 63 (offset 32259) — tells you FAT, NTFS, or exFAT"
  - name: "File system stats"
    flag: "fsstat image.001"
    desc: "Use The Sleuth Kit fsstat to parse all VBR fields automatically"
  - name: "Read volume serial number (FAT)"
    flag: "-s 32295 -l 4 image.001"
    desc: "Dump 4 bytes at offset 32295; reverse byte order to get VSN"
  - name: "Read volume serial number (NTFS/exFAT)"
    flag: "-s 32328 -l 4 image.001"
    desc: "Dump 4 bytes at offset 32328; reverse byte order to get VSN"
options:
  - name: "Hex dump with offset"
    flag: "xxd -s <offset> -l <length>"
    desc: "Jump to any byte offset and dump N bytes in hex + ASCII"
  - name: "Convert little-endian to decimal (Python)"
    flag: "python3 -c \"import struct; print(struct.unpack('<I', bytes.fromhex('86390100'))[0])\""
    desc: "Parse a little-endian 4-byte hex value into decimal"
  - name: "Calculate volume size"
    flag: "python3 -c \"print(80262 * 512)\""
    desc: "Sectors × sector size = total bytes in the volume"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Open the FAT Image and Navigate to the MBR Partition Table"
goal: "Use HxD to open a forensic evidence file and locate the partition entry at offset 446."
hint: "Open the FAT image via Tools > Open disk image. Switch offset display to Decimal (View > Offset base > Decimal). Then use Search > Go to (Ctrl+G) to jump to offset 446. Highlight the next 16 bytes — this is the first partition entry. Use the Data Inspector to read field values."
command: "Go to → 446 (decimal)"
expected_output: |
  Highlighted 16 bytes at offset 446:
    0x80 | 0x01 01 00 | 0x0E | 0xFE 3F 04 | 0x3F 00 00 00 | 0x86 39 01 00

  Breakdown:
    0x80         → partition is bootable
    0x0E         → file system type = FAT16
    0x3F 00 00 00 → starting sector = 63 (little-endian)
    0x86 39 01 00 → number of sectors = 80262 (little-endian)
                   → volume size = 80262 × 512 = 41,094,144 bytes (≈41 MB)

  Boot Record Signature (bytes 510–511):
    55 AA → valid MBR signature
:::

:::scenario{id="task-2" level="beginner"}
title: "Task 2 — Read the FAT VBR: OEM ID, Cluster Size, and Volume Size"
goal: "Navigate to sector 63 in the FAT image and identify key VBR fields."
hint: "The starting sector is 63; multiply by 512 = 32256. Jump to 32256 to reach the VBR. The OEM ID is 8 bytes starting at byte 3 of the sector (offset 32259). Highlight each field and use the Data Inspector to interpret the values."
command: "Go to → 32256 (decimal)"
expected_output: |
  OEM ID (offset 32259, 8 bytes):
    4D 53 44 4F 53 35 2E 30 → "MSDOS5.0" → FAT file system

  Bytes per sector (offset 32267, 2 bytes):
    00 02 → little-endian → 512 bytes per sector

  Sectors per cluster (offset 32269, 1 byte):
    02 → 2 sectors per cluster
    Cluster size = 512 × 2 = 1024 bytes

  Media descriptor (offset 32277, 1 byte):
    F8 → fixed disk (hard drive or USB)

  Total sectors (offset 32288, 4 bytes):
    86 39 01 00 → little-endian → 80262 sectors → 41,094,144 bytes (≈41 MB)

  Volume serial number (offset 32295, 4 bytes):
    E8 7D 54 20 → read right-to-left → 2054-7D6E

  File system type (offset 32310, 8 bytes):
    46 41 54 31 36 20 20 20 → "FAT16   "
:::

:::scenario{id="task-3" level="intermediate"}
title: "Task 3 — Identify an NTFS Partition and Read Its VBR"
goal: "Open the NTFS image, confirm the file system type in the MBR, then parse NTFS-specific VBR fields including the MFT starting cluster."
hint: "The partition entry byte 5 for NTFS shows 0x07 (shared with exFAT). Jump to offset 32256 and look at the OEM ID — it will read 'NTFS    ' for an NTFS volume. The sectors-per-cluster value for NTFS is 0x08 (8), giving a cluster size of 4096 bytes."
command: "Go to → 446 (decimal), then Go to → 32256"
expected_output: |
  Partition table (offset 446):
    5th byte = 0x07 → NTFS or exFAT (differentiate using VBR OEM ID)

  OEM ID (offset 32259, 8 bytes):
    4E 54 46 53 20 20 20 20 → "NTFS    " → NTFS file system

  Bytes per sector (offset 32267, 2 bytes):
    00 02 → 512

  Sectors per cluster (offset 32269, 1 byte):
    08 → 8 sectors per cluster
    Cluster size = 512 × 8 = 4096 bytes

  Total sectors (offset 32296, 8 bytes):
    85 39 01 00 00 00 00 00 → 80261 sectors → 41,093,632 bytes (≈41 MB)

  MFT starting cluster (offset 32304, 8 bytes):
    10 0D 00 00 00 00 00 00 → 3344
    → Navigate to cluster 3344 to browse the Master File Table

  Volume serial number (offset 32328, 4 bytes):
    C0 D9 2A A0 → read right-to-left → A02A-DDC0
:::

:::scenario{id="task-4" level="intermediate"}
title: "Task 4 — Identify an exFAT Partition and Distinguish It from NTFS"
goal: "Open the exFAT image, confirm the OEM ID distinguishes it from NTFS, and read volume length and serial number."
hint: "Both NTFS and exFAT show 0x07 in the partition type byte — you must jump to the VBR and read the 8-byte OEM ID. The definitive exFAT identifier is that the 53 bytes immediately after the OEM ID are all 0x00. The volume length and serial number are at different offsets than FAT/NTFS."
command: "Go to → 32256, highlight 8 bytes at offset 32259"
expected_output: |
  OEM ID (offset 32259, 8 bytes):
    45 58 46 41 54 20 20 20 → "EXFAT   " → exFAT file system

  Post-OEM ID (offsets 32267–32319, 53 bytes):
    All 0x00 → unique exFAT signature (FAT/NTFS use this space for BIOS parameters)

  Volume length (offset 32328, 8 bytes):
    86 39 01 00 00 00 00 00 → 80262 sectors → 41,094,144 bytes (≈41 MB)

  Volume serial number (offset 32356, 4 bytes):
    E4 06 C5 7C → read right-to-left → 7CC5-06E4

  Key distinction:
    FAT  → OEM ID "MSDOS5.0", partition type byte 0x0E
    NTFS → OEM ID "NTFS    ", partition type byte 0x07
    exFAT→ OEM ID "EXFAT   ", partition type byte 0x07, 53 zero bytes after OEM ID
:::

---

## Full Linux Workflow

End-to-end file system identification from a raw FEF using command-line tools:

```bash
# 1. List all partitions in the image
mmls NDG_FAT_Lab5.001

# 2. Get full file system stats (auto-parses VBR)
fsstat NDG_FAT_Lab5.001

# 3. Manually read the MBR partition table
xxd -s 446 -l 64 NDG_FAT_Lab5.001

# 4. Jump to sector 63 and read the VBR OEM ID (8 bytes at offset 32259)
xxd -s 32259 -l 8 NDG_FAT_Lab5.001

# 5. Read bytes-per-sector and sectors-per-cluster
xxd -s 32267 -l 3 NDG_FAT_Lab5.001

# 6. Read total sectors (FAT, offset 32288)
xxd -s 32288 -l 4 NDG_FAT_Lab5.001

# 7. Convert little-endian hex to decimal (e.g. "86 39 01 00")
python3 -c "import struct; print(struct.unpack('<I', bytes.fromhex('86390100'))[0])"
# → 80262

# 8. Calculate volume size in bytes
python3 -c "print(80262 * 512)"
# → 41094144

# 9. Read FAT volume serial number (offset 32295)
xxd -s 32295 -l 4 NDG_FAT_Lab5.001

# 10. Read NTFS/exFAT volume serial number (offset 32328)
xxd -s 32328 -l 4 NDG_NTFS_Lab5.001

# 11. Read exFAT volume length (offset 32328, 8 bytes)
xxd -s 32328 -l 8 NDG_exFAT_Lab5.001

# 12. Verify Boot Record Signature at end of MBR (bytes 510–511)
xxd -s 510 -l 2 NDG_FAT_Lab5.001
# → 55 aa
```

---

## Key Concepts

### Partitions vs. File Systems

| Concept | What it controls | Where it lives |
|---------|-----------------|----------------|
| Partition | How much space is allocated | MBR at sector 0 |
| File system | How data within that space is organized | VBR at the partition's first sector |

A drive can have up to 4 primary partitions (one MBR has 64 bytes of partition table, each entry is 16 bytes). Extended partitions allow more logical partitions beyond that limit.

### Little-Endian Byte Order

Nearly all MBR and VBR numeric values are stored in **little-endian** order — bytes are reversed:

| Raw bytes on disk | Little-endian value | Decimal |
|-------------------|---------------------|---------|
| `3F 00 00 00` | `0x0000003F` | 63 |
| `86 39 01 00` | `0x00013986` | 80262 |
| `E8 7D 54 20` | `2054-7D6E` (VSN) | — |

When reading a volume serial number, reverse the 4-byte pairs: `E8 7D 54 20` becomes `2054-7DE8`.

### File System Type Byte (MBR Partition Entry)

| Hex | File System |
|-----|------------|
| `0x0B` | FAT32 (CHS) |
| `0x0C` | FAT32 (LBA) |
| `0x0E` | FAT16 (LBA) |
| `0x07` | NTFS **or** exFAT — must check VBR OEM ID to tell apart |

### Distinguishing NTFS from exFAT

Both use partition type `0x07`. The only reliable method is reading the VBR:

| Indicator | NTFS | exFAT |
|-----------|------|-------|
| OEM ID (offset +3) | `NTFS    ` | `EXFAT   ` |
| Bytes after OEM ID (53 bytes) | BIOS parameter block data | All `0x00` |
| MFT field present | Yes (offset +48 in sector) | No |

### Volume Serial Numbers

The VSN is created when a volume is **formatted**. It can:
- Link a file to a specific drive even after the file is deleted
- Detect if an image has been reformatted since a previous acquisition
- Confirm chain-of-custody integrity when compared across acquisitions

VSNs are stored in little-endian and displayed as two 4-hex-digit groups separated by a dash (e.g. `A02A-DDC0`).

### Sector Offset Math

```
VBR byte offset = starting sector × 512
Cluster size    = bytes per sector × sectors per cluster
Volume size     = total sectors × 512
```

Example (FAT): starting sector 63 → `63 × 512 = 32256`. Jump to offset 32256 in the FEF to reach the VBR.

---

:::quiz{id="quiz-1"}
Q: Where in a disk image is the MBR partition table located?
- [ ] The first 446 bytes of sector 0
- [x] Bytes 446–509 of sector 0
- [ ] The first sector of each partition
- [ ] Offset 32256 in the image
:::

:::quiz{id="quiz-2"}
Q: What partition type byte value is shared by both NTFS and exFAT in the MBR?
- [ ] 0x0E
- [ ] 0x0B
- [x] 0x07
- [ ] 0x83
:::

:::quiz{id="quiz-3"}
Q: How do you tell an NTFS volume apart from an exFAT volume when both show 0x07 in the partition type byte?
- [ ] Compare the total number of sectors
- [ ] Look at the volume serial number length
- [x] Read the 8-byte OEM ID in the VBR — NTFS shows "NTFS    ", exFAT shows "EXFAT   "
- [ ] Check whether the Boot Signature is 0x55AA
:::

:::quiz{id="quiz-4"}
Q: A FAT VBR shows bytes-per-sector = 512 and sectors-per-cluster = 4. What is the cluster size?
- [ ] 512 bytes
- [ ] 1024 bytes
- [x] 2048 bytes
- [ ] 4096 bytes
:::

:::quiz{id="quiz-5"}
Q: The NTFS VBR at offset 32304 stores the MFT starting cluster value. Why is this forensically useful?
- [x] It tells you where the Master File Table begins, allowing direct navigation to file metadata
- [ ] It reveals the volume serial number
- [ ] It tells you the total number of deleted files
- [ ] It stores the volume creation date
:::

:::quiz{id="quiz-6"}
Q: Raw bytes at a little-endian offset read as `86 39 01 00`. What is the decimal value?
- [ ] 860x3910
- [ ] 1397766
- [x] 80262
- [ ] 4026531840
:::

---

## Quick Reference

| Artifact | FAT offset (dec) | NTFS offset (dec) | exFAT offset (dec) |
|----------|-----------------|-------------------|--------------------|
| MBR partition table | 446 | 446 | 446 |
| Boot signature | 510 | 510 | 510 |
| VBR start (sector 63) | 32256 | 32256 | 32256 |
| OEM ID | 32259 | 32259 | 32259 |
| Bytes per sector | 32267 | 32267 | — (shift value at 32364) |
| Sectors per cluster | 32269 | 32269 | — (shift value at 32365) |
| Media descriptor | 32277 | 32277 | — |
| Total sectors | 32288 | 32296 | 32328 |
| MFT start cluster | — | 32304 | — |
| Volume serial number | 32295 | 32328 | 32356 |
| File system type string | 32310 (`FAT16`) | 32259 (`NTFS`) | 32259 (`EXFAT`) |
| VBR boot signature | 32766 | 32766 | 32766 |
