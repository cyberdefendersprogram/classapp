# Forensic Disk Imaging

Forensic disk imaging creates a bit-for-bit copy of a storage device that can be analyzed without touching the original evidence. Two paths cover the same workflow: **FTK Imager** on Windows (GUI) and **dd / dcfldd** on Linux (CLI).

## Overview

A forensic image is not a file copy. It captures:

- **Active files** — everything the OS can see
- **Deleted files** — data in unallocated space
- **File system metadata** — MFT, journal, timestamps
- **Slack space** — padding between file end and sector end
- **Hidden/system partitions** — boot records and reserved areas

Both tools compute cryptographic hashes (MD5 + SHA1) to prove the image is an exact, unmodified copy of the source.

---

## Tool Comparison

| | FTK Imager (Windows) | dd / dcfldd (Linux/Kali) |
|--|---------------------|--------------------------|
| Interface | GUI | CLI |
| Default image format | E01 (with metadata) | Raw / dd (no metadata) |
| E01 support | Native | `ewfacquire` (libewf) |
| Built-in hashing | Yes (MD5 + SHA1) | `dcfldd` only; `md5sum` / `sha1sum` separately for `dd` |
| Write-blocking | Manual (hardware blocker) | Mount read-only or `blockdev --setro` |
| Chain-of-custody fields | GUI form embedded in image | Documented separately |

---

## Identify the Target Device

Before imaging on either platform, identify the correct source device.

**Windows (FTK Imager):**
Navigate to `File > Create Disk Image` — the Select Drive dialog lists all attached drives by label and size.

**Linux (Kali):**

```bash
# List all block devices with sizes and mount points
lsblk

# Show detailed partition and geometry info
sudo fdisk -l

# Check by serial number / model
sudo hdparm -I /dev/sdb | grep -E "Model|Serial"
```

> Always confirm the device identifier (`/dev/sdb`, `/dev/sdc`, etc.) before imaging. Imaging the wrong device is irreversible.

---

:::command-builder{id="dd-builder"}
tool_name: dd
target_placeholder: "/dev/sdb"
scan_types:
  - name: "Physical Image (dd)"
    flag: "if=/dev/sdb of=/mnt/evidence/image.dd"
    desc: "Image the entire physical disk to a raw file"
  - name: "Logical / Partition Image"
    flag: "if=/dev/sdb1 of=/mnt/evidence/partition.dd"
    desc: "Image a single partition instead of the whole disk"
  - name: "dcfldd with Hashing"
    flag: "if=/dev/sdb of=/mnt/evidence/image.dd hash=md5,sha1 hashlog=/mnt/evidence/hashes.txt"
    desc: "Image with built-in MD5+SHA1 hash generation (dcfldd)"
options:
  - name: "Block Size 512"
    flag: "bs=512"
    desc: "512-byte blocks — matches sector size, safe default"
  - name: "Block Size 4096"
    flag: "bs=4096"
    desc: "4K blocks — faster on modern drives"
  - name: "Skip Errors"
    flag: "conv=noerror,sync"
    desc: "Continue past bad sectors; pad with zeros (forensically important)"
  - name: "Show Progress"
    flag: "status=progress"
    desc: "Print live progress to stderr (dd on Linux)"
:::

---

## Forensic Image Formats

| Format | Extension | Description | Tool |
|--------|-----------|-------------|------|
| **Raw** | .dd / .img | Uncompressed bit-for-bit dump; no metadata | `dd`, `dcfldd` |
| **E01** | .E01 | Expert Witness Format — stores case metadata + hashes inside container | FTK Imager, `ewfacquire` |
| **AFF** | .aff | Open-source; raw image + metadata in separate file | `affcat`, `aff tools` |
| **SMART** | .s01 | Legacy Linux SMART tool format | Rarely used today |

> **E01** is the court-standard. Use it for anything going to prosecution. Raw `dd` images are widely compatible but require separate hash files and documentation.

---

## Write Protection

Never image original evidence without write protection.

**Hardware write blocker** — physical device between the evidence drive and the forensic workstation. Preferred for court work.

**Linux software write-block:**

```bash
# Set a block device read-only before connecting/mounting
sudo blockdev --setro /dev/sdb

# Confirm it is read-only (returns 1)
sudo blockdev --getro /dev/sdb

# Mount read-only (belt-and-suspenders)
sudo mount -o ro /dev/sdb1 /mnt/source
```

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Identify the Target Device"
goal: "On both platforms, identify which device is the evidence drive before touching anything."
hint: "On Linux, plug in the drive and immediately run lsblk to see the new device. Look at the SIZE column to confirm it matches the expected drive capacity. On Windows, FTK Imager's Select Drive dialog shows drive labels (like Evidence Repository E:) and sizes. Never guess the device — wrong source = destroyed evidence."
command: "lsblk  OR  sudo fdisk -l  (Linux) | File > Create Disk Image (Windows)"
expected_output: |
  Linux (lsblk):
    NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
    sda      8:0    0    48G  0 disk
    ├─sda1   8:1    0    47G  0 part /
    └─sda2   8:2    0   976M  0 part [SWAP]
    sdb      8:16   1     1G  0 disk          ← evidence drive
    └─sdb1   8:17   1  1023M  0 part

  Windows FTK Imager (Select Drive dropdown):
    \\.\PHYSICALDRIVE0 — VMware Virtual disk [48G]
    \\.\PHYSICALDRIVE1 — VMware Virtual disk [1G]   ← evidence drive
    \\.\PHYSICALDRIVE2 — VMware Virtual disk [26G]
:::

:::scenario{id="task-2" level="beginner"}
title: "Task 2 — Create a Physical Forensic Image"
goal: "Image the entire evidence drive. On Linux use dcfldd with hashing. On Windows use FTK Imager with E01 format."
hint: "Physical images capture every sector — including deleted files, unallocated space, and the partition table. Always verify after creating. On Linux, dcfldd writes the hash log automatically. On Windows, check the 'Verify images after they are created' checkbox before clicking Start."
command: "sudo dcfldd if=/dev/sdb of=/mnt/evidence/image.dd bs=512 hash=md5,sha1 hashlog=/mnt/evidence/hashes.txt conv=noerror,sync"
expected_output: |
  dcfldd output:
    256 blocks (128Mb) written.
    512 blocks (256Mb) written.
    ...
    2048 blocks (1024Mb) written.
    Total: 2097152 blocks (1024Mb) written.

  hashes.txt contents:
    /mnt/evidence/image.dd:
    MD5:  8dbd697cfba8a907b1d212a35a8cb705
    SHA1: 35071408942480l736bb6452cd82281e1783cf

  Windows FTK Imager — Drive/Image Verify Results:
    MD5  Verify result:  Match
    SHA1 Verify result:  Match
    Bad Blocks:          No bad blocks found in image
:::

:::scenario{id="task-3" level="beginner"}
title: "Task 3 — Create a Logical (Partition) Image"
goal: "Image a single partition rather than the whole disk. On Linux target the partition device node. On Windows choose Logical Drive."
hint: "A logical image skips the partition table and unallocated space between partitions — it only captures the selected file system. Use this when you only have access to a mounted share, a single volume on a multi-partition drive, or when a full physical image is not possible. On Linux, target /dev/sdb1 (the partition) instead of /dev/sdb (the whole disk)."
command: "sudo dcfldd if=/dev/sdb1 of=/mnt/evidence/partition.dd bs=512 hash=md5,sha1 hashlog=/mnt/evidence/partition_hashes.txt conv=noerror,sync"
expected_output: |
  dcfldd output:
    Imaging partition /dev/sdb1 → partition.dd

  After completion, verify:
    md5sum /mnt/evidence/partition.dd
    sha1sum /mnt/evidence/partition.dd
    (values should match the hashlog entries)

  Windows FTK Imager:
    File > Create Disk Image > Logical Drive > select G:\ USB 001 [NTFS]
    Evidence Item: Case FOR_LAB_001, Evidence 001A
    Status: Image created successfully
:::

:::scenario{id="task-4" level="beginner"}
title: "Task 4 — Verify Image Integrity"
goal: "Confirm the image hash matches the source. On Linux recompute the hash and compare. On Windows review the image report .txt file."
hint: "Hash verification is the forensic proof that your image is an exact copy. If even one bit changed during acquisition or storage, the hash will be completely different. On Linux, recompute and diff. On Windows, FTK Imager writes a .txt report alongside the .E01 file — open it in Notepad and compare the Computed Hashes section against the Image Verification Results section."
command: "md5sum /mnt/evidence/image.dd && sha1sum /mnt/evidence/image.dd"
expected_output: |
  Linux hash verification:
    # Recompute hash of the image file
    md5sum /mnt/evidence/image.dd
    8dbd697cfba8a907b1d212a35a8cb705  /mnt/evidence/image.dd

    sha1sum /mnt/evidence/image.dd
    35071408942480l736bb6452cd82281e1783cf  /mnt/evidence/image.dd

    # Compare against hashes.txt from dcfldd — values must be identical.
    # Any difference = image is corrupted or tampered.

  Windows FTK Imager .txt report sections:
    [Computed Hashes]
      MD5 checksum:  41cf98f622791425f6aa8beddb714bd4
      SHA1 checksum: a4e5e4f68176b103c025d6a91dd9ebe4e30fefe2

    [Image Verification Results]
      MD5 checksum:  41cf98f622791425f6aa8beddb714bd4 : verified
      SHA1 checksum: a4e5e4f68176b103c025d6a91dd9ebe4e30fefe2 : verified
:::

:::scenario{id="task-5" level="beginner"}
title: "Task 5 — Mount and Browse the Image (Read-Only)"
goal: "Open the image and browse its file system without modifying it. Confirms the capture was successful and the file structure is intact."
hint: "Mount with read-only flag to guarantee you cannot accidentally write to the image. On Linux, use a loop device with the ro flag. If the image contains multiple partitions, use the offset option to target a specific partition (offset = partition start sector x 512). On Windows, load the image into FTK Imager via Add Evidence Item and expand the Evidence Tree."
command: "sudo mount -o ro,loop /mnt/evidence/image.dd /mnt/browse"
expected_output: |
  Linux — mount and browse:
    sudo mkdir /mnt/browse
    sudo mount -o ro,loop /mnt/evidence/image.dd /mnt/browse
    ls /mnt/browse

    Example output:
      lost+found  Documents  Downloads  Pictures  Desktop

    Unmount when done:
      sudo umount /mnt/browse

  For a specific partition (use fdisk -l to find start sector):
    sudo mount -o ro,loop,offset=$((2048 * 512)) /mnt/evidence/image.dd /mnt/browse

  Windows FTK Imager — Evidence Tree after loading .E01:
    1GB_Seagate_SN954321.E01
    ├── Microsoft reserved partition [1]
    └── Basic data partition [2]
          └── Data [NTFS]
                ├── [root]           ← files appear in File List pane
                ├── [orphan]         ← deleted/orphaned files
                └── [unallocated space]
:::

---

## Chaining the Workflow on Linux

Full end-to-end example on Kali:

```bash
# 1. Identify the evidence drive
lsblk
# Assume evidence is /dev/sdb (1GB drive)

# 2. Write-protect the source
sudo blockdev --setro /dev/sdb

# 3. Create output directory
sudo mkdir -p /mnt/evidence/case001

# 4. Image with dcfldd (physical, full disk)
sudo dcfldd if=/dev/sdb \
     of=/mnt/evidence/case001/drive_image.dd \
     bs=512 \
     hash=md5,sha1 \
     hashlog=/mnt/evidence/case001/hashes.txt \
     conv=noerror,sync \
     status=on

# 5. Verify — recompute and compare
md5sum /mnt/evidence/case001/drive_image.dd
sha1sum /mnt/evidence/case001/drive_image.dd
# Values must match hashes.txt

# 6. Browse (read-only)
sudo mkdir /mnt/browse
sudo mount -o ro,loop /mnt/evidence/case001/drive_image.dd /mnt/browse
ls /mnt/browse
sudo umount /mnt/browse
```

---

## Key Forensic Concepts

### Physical vs Logical Images

| | Physical Image | Logical Image |
|--|--------------|--------------|
| Linux source | `/dev/sdb` (whole disk) | `/dev/sdb1` (partition) |
| FTK source type | Physical Drive | Logical Drive |
| Captures | Deleted files, unallocated space, MBR | Active file system only |
| Use when | Full forensic exam | Mounted shares, single-volume triage |

### Why Not Just `cp` or `xcopy`?

A file copy only captures what the OS exposes. A forensic image captures **every sector**, including:
- Unallocated space (where deleted files live)
- File system journal and metadata
- Slack space (the gap between file end and sector end)

### Hash Verification

Both MD5 and SHA1 are computed to provide double verification:
- **MD5** (128-bit) — fast, widely recognized in legal proceedings
- **SHA1** (160-bit) — stronger; used alongside MD5

If `computed hash == stored/expected hash` → the image is forensically sound and has not been altered since acquisition.

---

:::quiz{id="quiz-1"}
Q: What is the primary reason to create a forensic image rather than copying files with a file manager?
- [ ] It is faster than a regular file copy
- [x] It captures deleted files, unallocated space, and file system metadata that a file copy misses
- [ ] It compresses the data to save storage space
- [ ] It encrypts the evidence for secure transport
:::

:::quiz{id="quiz-2"}
Q: On Linux, which command images /dev/sdb and generates MD5 and SHA1 hashes simultaneously?
- [ ] dd if=/dev/sdb of=image.dd bs=512
- [ ] cp /dev/sdb image.dd
- [x] dcfldd if=/dev/sdb of=image.dd hash=md5,sha1 hashlog=hashes.txt
- [ ] rsync /dev/sdb image.dd
:::

:::quiz{id="quiz-3"}
Q: What is the purpose of the conv=noerror,sync flag in a dd/dcfldd command?
- [ ] It speeds up imaging by skipping checksums
- [ ] It compresses the output image
- [x] It continues past bad sectors and pads them with zeros, preserving the sector alignment
- [ ] It encrypts the image during acquisition
:::

:::quiz{id="quiz-4"}
Q: Which Linux command confirms a block device has been set to read-only before imaging?
- [x] sudo blockdev --getro /dev/sdb
- [ ] sudo chmod 444 /dev/sdb
- [ ] sudo hdparm -r /dev/sdb
- [ ] sudo lsblk --ro /dev/sdb
:::

:::quiz{id="quiz-5"}
Q: A physical image differs from a logical image in that a physical image:
- [ ] Only captures files the operating system can currently see
- [ ] Is faster to create
- [x] Captures the entire disk including deleted files, unallocated space, and the partition table
- [ ] Cannot be opened in FTK Imager after creation
:::

:::quiz{id="quiz-6"}
Q: After imaging with dcfldd, you recompute the hash with md5sum and the value does NOT match the hashlog. What does this mean?
- [ ] The drive was write-protected correctly
- [ ] The image is complete and ready for analysis
- [x] The image was corrupted or modified after acquisition and cannot be trusted as forensic evidence
- [ ] The hash algorithm is not supported by the tool
:::

---

## Quick Reference

| Task | Linux (Kali) | Windows (FTK Imager) |
|------|-------------|---------------------|
| Identify device | `lsblk` / `sudo fdisk -l` | File > Create Disk Image > Select Drive |
| Write-protect | `sudo blockdev --setro /dev/sdX` | Hardware write blocker |
| Physical image | `dcfldd if=/dev/sdX of=image.dd ...` | File > Create Disk Image > Physical Drive |
| Logical image | `dcfldd if=/dev/sdX1 of=part.dd ...` | File > Create Disk Image > Logical Drive |
| Verify hash | `md5sum image.dd` / `sha1sum image.dd` | Review .E01.txt report |
| Browse image | `mount -o ro,loop image.dd /mnt/...` | File > Add Evidence Item > Image File |
| Unmount | `sudo umount /mnt/browse` | Remove Evidence Item |
