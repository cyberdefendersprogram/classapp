# Steganography & Alternate Data Streams

Steganography and Alternate Data Streams (ADS) are data-hiding techniques used to conceal evidence in plain sight. A file can look completely normal — open in any viewer, pass a casual inspection — while carrying hidden text, embedded files, or whole secondary payloads. Forensic examiners must know how these techniques work in order to detect them.

## Overview

Two distinct hiding methods covered here:

| Technique | How It Works | Where It Lives | Detectable By |
|-----------|-------------|---------------|---------------|
| **Steganography (appended text)** | Plaintext written after a file's EOF marker | Inside the carrier file's bytes | Hex editor, `strings`, size anomaly |
| **Steganography (embedded file)** | Second file appended after host file's EOF | Inside the carrier file's bytes | Magic byte search, `binwalk`, `foremost` |
| **Alternate Data Streams (ADS)** | Hidden data stream attached to a file | NTFS metadata (not visible in `dir`) | `dir /r` (Windows), `icat` / TSK (Kali) |

> **Important:** Creating steganography modifies the carrier file — it changes the hash and file size. Never practice stego techniques on evidence files. The exercises below are for understanding detection, not operational use.

---

## File Signatures Used in Stego Detection

When searching for embedded files, you look for their magic bytes appearing at an unexpected offset inside another file type.

| File Type | Header (hex) | Footer (hex) | Notes |
|-----------|-------------|-------------|-------|
| JPEG | `FF D8 FF` | `FF D9` | Any data after `FF D9` is appended stego content |
| PNG | `89 50 4E 47 0D 0A 1A 0A` | `49 45 4E 44 AE 42 60 82` | Full 8-byte header; 8-byte IEND footer |
| ZIP / DOCX | `50 4B 03 04` | `50 4B 05 06` | Searching for PK header inside images is common |
| PDF | `25 50 44 46` | `25 25 45 4F 46` | `%PDF` in ASCII |
| EXE / DLL | `4D 5A` | — | `MZ` header; no fixed footer |

---

## Tool Comparison

| Task | Windows (GUI/CMD) | Linux / Kali (CLI) |
|------|------------------|-------------------|
| View raw file bytes | HxD hex editor | `xxd file.jpg \| less` or `hexdump -C file.jpg` |
| Search for magic bytes in file | HxD > Search > Find > Hex-values | `binwalk file.jpg` or `grep -c` hex via `xxd` |
| Find EOF marker and appended data | HxD > Go to > End (backwards) | `xxd file.jpg \| tail -20` |
| Extract embedded file by offset | HxD > Edit > Select block > File > Save selection | `dd if=file.jpg bs=1 skip=$((0x191F9)) count=$((0x1A025-0x191F9+1)) of=hidden.png` |
| Auto-extract all embedded files | — | `binwalk -e file.jpg` |
| Search strings in binary file | HxD decoded text pane | `strings file.jpg` |
| Create ADS | `type src > host.exe:stream.txt` (cmd.exe) | `setfattr` on mounted NTFS; or `echo > host:stream` |
| List ADS on file | `dir /r` | `getfattr -d file` (mounted NTFS) or `icat image.dd 42-128-4` (TSK) |
| Find all ADS in directory | `dir /r` or Streams.exe (Sysinternals) | `find . -name "*" \| xargs getfattr 2>/dev/null` or `fls -r image.dd \| grep ":"` |
| Detect stego in image (LSB) | OpenStego (GUI) | `steghide info file.jpg`, `stegosuite`, `zsteg file.png` |

---

:::command-builder{id="binwalk-builder"}
tool_name: binwalk
target_placeholder: "suspect.jpg"
scan_types:
  - name: "Signature Scan"
    flag: "suspect.jpg"
    desc: "Scan for embedded file signatures and magic bytes — the default mode"
  - name: "Extract All"
    flag: "-e suspect.jpg"
    desc: "Scan and automatically extract all detected embedded files"
  - name: "Extract with Matryoshka"
    flag: "-Me suspect.jpg"
    desc: "Recursively extract files-within-files (handles nested archives)"
  - name: "Entropy Analysis"
    flag: "-E suspect.jpg"
    desc: "Plot entropy — high entropy after an EOF marker suggests hidden encrypted data"
  - name: "Strings Search"
    flag: "-S suspect.jpg"
    desc: "Extract printable strings from the file (similar to strings command)"
  - name: "Raw Search (hex)"
    flag: "-R '\\x89\\x50\\x4E\\x47' suspect.jpg"
    desc: "Search for a specific hex byte sequence — useful for finding PNG header inside JPEG"
options:
  - name: "Output directory"
    flag: "-C /mnt/evidence/extracted/"
    desc: "Save extracted files to a specific directory"
  - name: "Verbose"
    flag: "-v"
    desc: "Show verbose output including all signatures checked"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Identify Appended Data After a JPEG EOF"
goal: "Open a JPEG in a hex editor and navigate to its end-of-file marker (FF D9). Determine whether any data has been appended after it — the simplest form of steganography."
hint: "JPEG files always end with the two bytes FF D9. Any legitimate image viewer will stop rendering at FF D9 and ignore everything after. On Kali, use xxd and tail to quickly check the last bytes. If you see readable text or additional magic bytes after FF D9, something was appended. The file size will also be larger than expected — compare against the original if you have it. On Windows, HxD's Go to > End (backwards) jumps directly to the last byte."
command: xxd /mnt/evidence/WhatsApp-Encryption.jpg | tail -20
expected_output: |
  Kali — check end of JPEG for appended content:
    xxd /mnt/evidence/WhatsApp-Encryption.jpg | tail -20
    000112a0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
    000112b0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
    000112c0: 0000 0000 0000 0000 0000 0000 03ff d973  ...............s
    000112d0: 7465 6761 6e6f 6772 6170 6879 2069 7320  teganography is
    000112e0: 6120 6772 6561 7420 7761 7920 746f 2068  a great way to h
    000112f0: 6964 6520 7365 6372 6574 73         ide secrets

  Explanation:
    FF D9  = JPEG end-of-file marker (at 0x000112CE)
    Everything after FF D9 = appended hidden message

  Quick check — does anything come after FF D9?
    python3 -c "
    data = open('/mnt/evidence/WhatsApp-Encryption.jpg','rb').read()
    eof = data.rfind(b'\\xff\\xd9')
    tail = data[eof+2:]
    print(f'EOF at offset: {hex(eof)}')
    print(f'Bytes after EOF: {len(tail)}')
    if tail: print(f'Content: {tail[:80]}')
    "

  Windows HxD equivalent:
    Search > Go to > select "end (backwards)" > OK
    Cursor lands on last byte; scroll up to find FF D9
    Any decoded text visible after FF D9 in the text pane = appended content
:::

:::scenario{id="task-2" level="beginner"}
title: "Task 2 — Find and Extract a File Embedded Inside a JPEG"
goal: "A JPEG file contains a completely separate PNG embedded after its EOF marker. Locate the PNG by searching for its magic bytes, note the start and end offsets, then extract the hidden file using dd."
hint: "PNG files start with the 8-byte magic sequence 89 50 4E 47 0D 0A 1A 0A and end with the 8-byte IEND chunk 49 45 4E 44 AE 42 60 82. Use binwalk to find these offsets automatically, or xxd + grep for a manual approach. Once you have the start offset and end offset, use dd with skip= and count= to carve the embedded PNG out. The file will be fully intact and openable. In HxD on Windows, use Search > Find > Hex-values to locate 89504E470D0A1A0A, note the offset, then find the footer, use Edit > Select block with both offsets, and File > Save selection."
command: binwalk /mnt/evidence/PlanC.jpg
expected_output: |
  Kali — binwalk signature scan:
    binwalk /mnt/evidence/PlanC.jpg

    DECIMAL       HEXADECIMAL     DESCRIPTION
    -------       -----------     -----------
    0             0x0             JPEG image data, JFIF standard 1.01
    102905        0x191F9         PNG image, 711 x 184, 24-bit/color RGB, non-interlaced
    106533        0x1A025         PNG image end

  Auto-extract the hidden PNG:
    binwalk -e /mnt/evidence/PlanC.jpg
    ls _PlanC.jpg.extracted/
    191F9.png   ← this is the hidden file

  Manual extraction using dd (if you have start/end offsets from binwalk):
    START=0x191F9    # decimal: 102905
    END=0x1A025      # decimal: 106533
    COUNT=$((END - START + 8))   # +8 for the 8-byte PNG footer

    dd if=/mnt/evidence/PlanC.jpg \
       bs=1 \
       skip=$((START)) \
       count=$((COUNT)) \
       of=/mnt/evidence/hidden.png

    file /mnt/evidence/hidden.png
    # hidden.png: PNG image data, 711 x 184, 8-bit/color RGB

  Verify by opening:
    eog /mnt/evidence/hidden.png    # Eye of GNOME image viewer
    # or: xdg-open /mnt/evidence/hidden.png
:::

:::scenario{id="task-3" level="beginner"}
title: "Task 3 — Detect Steganography with binwalk and strings"
goal: "Run a triage sweep on a directory of suspect images using binwalk and strings to quickly flag files that contain embedded content or suspicious appended text."
hint: "binwalk prints nothing unusual for clean files — any extra entries beyond the expected format header mean something is embedded. strings is faster for catching plaintext hidden messages; pipe through grep to filter noise. A file whose size is significantly larger than visually similar files of the same format is a red flag worth examining in a hex editor. Check the file hash against known-good baselines if available."
command: binwalk /mnt/evidence/*.jpg
expected_output: |
  Kali — sweep all JPEGs in a directory:
    for f in /mnt/evidence/*.jpg; do
      echo "=== $f ==="
      binwalk "$f"
      echo ""
    done

    === /mnt/evidence/WhatsApp-Encryption.jpg ===
    DECIMAL       HEXADECIMAL     DESCRIPTION
    0             0x0             JPEG image data, JFIF standard 1.01
    # Only one entry = nothing embedded (message was appended as raw text, not a file)

    === /mnt/evidence/PlanC.jpg ===
    DECIMAL       HEXADECIMAL     DESCRIPTION
    0             0x0             JPEG image data, JFIF standard 1.01
    102905        0x191F9         PNG image, 711 x 184, 24-bit/color RGB
    # Two entries = embedded file detected!

  Strings sweep for hidden text:
    strings /mnt/evidence/WhatsApp-Encryption.jpg | grep -v "^.\{1,3\}$" | tail -20
    # Shows readable text near end of file — the appended message

  File size anomaly check:
    ls -lh /mnt/evidence/*.jpg
    -rw-r--r-- 1 user user 105K PlanC.jpg        ← larger than dimensions suggest
    -rw-r--r-- 1 user user  70K WhatsApp-Encryption.jpg

  Entropy check (high entropy after EOF = encrypted hidden content):
    binwalk -E /mnt/evidence/PlanC.jpg
    # Entropy spike at offset 0x191F9 confirms embedded data
:::

:::scenario{id="task-4" level="intermediate"}
title: "Task 4 — Create and Detect an NTFS Alternate Data Stream"
goal: "Create an ADS on an NTFS file, verify it is invisible to a normal directory listing, then detect it using dir /r (Windows) or Sleuth Kit tools on a mounted NTFS image (Kali)."
hint: "ADS only work on NTFS file systems — they do not survive being copied to FAT32, emailed, or zipped (the stream is silently dropped). The syntax to create an ADS in Windows CMD is: type sourcefile > hostfile:streamname. The colon separates the host filename from the stream name. A plain 'dir' shows only the host file at its original size; 'dir /r' reveals the hidden stream with its own byte count and the $DATA attribute tag. On Kali analyzing an NTFS disk image, use fls to list streams and icat to extract them by inode:stream."
command: fls -r /mnt/evidence/ntfs.img | grep ":"
expected_output: |
  Windows CMD — create and verify ADS:
    cd E:\FOR_LAB_010\ADS\Exercise1

    # Create the ADS (hides secret.txt inside Legitimate_Program.exe's stream)
    type Legitimate_Program.exe > Legitimate_Program.exe:secret.txt
    notepad Legitimate_Program.exe:secret.txt
    # Type message, save, close

    # Normal listing — ADS is invisible
    dir
    08/11/2020  11:00 PM    24 Legitimate_Program.exe   ← only host file shown

    # Reveal ADS
    dir /r
    08/11/2020  11:00 PM    24 Legitimate_Program.exe
                           169 Legitimate_Program.exe:secret.txt:$DATA  ← ADS revealed

    # Read the ADS
    more < Legitimate_Program.exe:secret.txt

  Kali — detect ADS in a mounted NTFS image:
    # Mount the NTFS image
    sudo mount -o loop,ro /mnt/evidence/ntfs.img /mnt/ntfs

    # List files with ADS using The Sleuth Kit
    fls -r /mnt/evidence/ntfs.img | grep ":"
    r/r 42-128-4:  Legitimate_Program.exe:secret.txt

    # Extract the ADS stream content
    icat /mnt/evidence/ntfs.img 42-128-4 > /mnt/evidence/secret_stream.txt
    cat /mnt/evidence/secret_stream.txt

  Kali — detect ADS on a live mounted NTFS volume:
    # List extended attributes (streams appear as user.* attributes)
    getfattr -d /mnt/ntfs/FOR_LAB_010/ADS/Exercise1/Legitimate_Program.exe
    # user.secret.txt = "This is an example of how to hide data..."
:::

:::scenario{id="task-5" level="intermediate"}
title: "Task 5 — LSB Steganography Detection with steghide"
goal: "Use steghide to detect and extract content hidden using Least Significant Bit (LSB) steganography — a more sophisticated method that hides data by modifying individual pixel bits, leaving no EOF anomaly and no size change visible to basic inspection."
hint: "LSB steganography does not append bytes after the EOF or embed a second file — it alters the carrier image's pixel data at the bit level. The file size stays the same, binwalk finds nothing, and the image looks visually identical. steghide can detect and extract LSB-hidden content from JPEG and BMP files. stegosuite and zsteg cover PNG and other formats. If no password is known, stegcracker can brute-force common wordlists against steghide-protected files."
command: steghide info suspect.jpg
expected_output: |
  Kali — probe file for hidden steghide content:
    steghide info suspect.jpg
    "suspect.jpg":
      format: jpeg
      capacity: 14.5 KB
    Try to get information about embedded data? (y/n) y
    Enter passphrase:
      embedded file "secret_message.txt":
        size: 312.0 Byte
        encrypted: rijndael-128, cbc
        compressed: yes

  Extract if passphrase is known:
    steghide extract -sf suspect.jpg -p "password123"
    wrote extracted data to "secret_message.txt"

  No passphrase? Try brute-force:
    stegcracker suspect.jpg /usr/share/wordlists/rockyou.txt

  PNG files — use zsteg instead:
    zsteg suspect.png
    b1,r,lsb,xy    .. text: "hidden message here"
    b1,rgb,lsb,xy  .. text: "SECRET"

  Check image metadata for stego clues:
    exiftool suspect.jpg | grep -i "comment\|description\|software\|warning"
    # Unexpected software tags or comment fields can indicate stego tools were used
:::

---

## Full Kali Workflow

End-to-end triage: sweep a directory of suspect images for both types of hidden content.

```bash
# --- SETUP ---
mkdir -p /mnt/evidence/extracted

# --- BINWALK SWEEP ---

# Quick scan — flag any file with embedded content
for f in /mnt/evidence/images/*; do
  count=$(binwalk "$f" | grep -c "DECIMAL" )
  if [ "$count" -gt 1 ]; then
    echo "[EMBEDDED CONTENT] $f"
    binwalk "$f"
  fi
done

# Auto-extract from all flagged files
binwalk -Me /mnt/evidence/images/PlanC.jpg -C /mnt/evidence/extracted/

# --- APPENDED DATA CHECK ---

# Check every JPEG for bytes after FF D9
python3 << 'EOF'
import os, glob

for path in glob.glob('/mnt/evidence/images/*.jpg'):
    data = open(path, 'rb').read()
    eof = data.rfind(b'\xff\xd9')
    if eof == -1:
        print(f"[NO EOF] {path}")
        continue
    tail = data[eof+2:]
    if tail.strip(b'\x00'):
        print(f"[APPENDED {len(tail)} bytes] {path}")
        print(f"  Preview: {tail[:60]}")
    else:
        print(f"[CLEAN] {path}")
EOF

# --- STRINGS SWEEP ---
for f in /mnt/evidence/images/*; do
  echo "=== $f ==="
  strings "$f" | grep -iE "password|secret|key|flag|hidden|message" | head -5
done

# --- LSB STEGANOGRAPHY ---

# Check all JPEGs with steghide (no password attempt)
for f in /mnt/evidence/images/*.jpg; do
  echo "=== $f ==="
  steghide info "$f" 2>&1 | grep -E "capacity|embedded"
done

# --- NTFS ADS (from disk image) ---

# List all files with ADS streams
fls -r /mnt/evidence/ntfs.img | grep ":"

# Extract a specific stream (replace inode number)
icat /mnt/evidence/ntfs.img 42-128-4 > /mnt/evidence/ads_content.txt
cat /mnt/evidence/ads_content.txt

# --- MANUAL HEX EXTRACTION ---

# If binwalk auto-extract fails, carve manually with dd
# (adjust START and COUNT from binwalk output)
START=102905   # 0x191F9
END=106533     # 0x1A025
dd if=/mnt/evidence/PlanC.jpg bs=1 skip=$START count=$((END-START+8)) \
   of=/mnt/evidence/carved_hidden.png 2>/dev/null
file /mnt/evidence/carved_hidden.png
```

---

## Key Concepts

### Why Steganography Survives File Format Viewers

Image viewers (IrfanView, Preview, Windows Photos) parse the file format spec — they read the JPEG data, hit `FF D9`, and stop. They never see what comes after. The OS does not warn you. The file opens normally. Only a hex editor or forensic tool that reads the full raw byte stream will reveal the appended content.

### ADS and NTFS-Only Restriction

Alternate Data Streams are a feature of the **NTFS file system** only. If a file with an ADS is:
- Copied to a FAT32 or exFAT drive → stream is **silently dropped**
- Emailed as an attachment → stream **not transmitted**
- Added to a ZIP archive → stream **not included**

This means ADS cannot be used for off-system exfiltration but is effective for hiding data on a local NTFS volume. The `$DATA` suffix shown by `dir /r` is the NTFS attribute type — every regular file has a default unnamed `$DATA` stream; ADS add named streams alongside it.

### Hash Impact of Steganography

Appending data to a file changes both its **size** and its **hash**. An investigator comparing a suspect file against a known-good hash database (e.g., NSRL) will immediately see a mismatch — which is itself evidence of tampering. LSB steganography also changes the hash (pixel values are altered) but keeps the file size identical, making it harder to detect without dedicated tools.

### LSB vs Appended-File Steganography

| | Appended / Embedded File | LSB Steganography |
|--|--------------------------|------------------|
| File size | Increases | Unchanged |
| Visual appearance | Identical | Identical |
| Detectable by binwalk | Yes (magic bytes) | No |
| Detectable by strings | Yes (if plaintext) | No |
| Detectable by tool | `binwalk`, `foremost`, `xxd` | `steghide`, `zsteg`, `stegosuite` |
| Carrier formats | Any (JPEG, PNG, EXE…) | JPEG, BMP, PNG (varies by tool) |

---

:::quiz{id="quiz-1"}
Q: A JPEG file opens normally in an image viewer but contains extra bytes after its FF D9 end-of-file marker. Why does the image viewer not show an error?
- [ ] Image viewers automatically decrypt hidden content
- [x] Image viewers stop reading at the EOF marker and ignore everything after it
- [ ] The extra bytes are compressed and invisible to the OS
- [ ] The file system hides data appended after the EOF
:::

:::quiz{id="quiz-2"}
Q: What is the 8-byte hex magic sequence that marks the beginning of a PNG file?
- [ ] FF D8 FF E0 00 10 4A 46
- [ ] 50 4B 03 04 14 00 00 00
- [x] 89 50 4E 47 0D 0A 1A 0A
- [ ] 25 50 44 46 2D 31 2E 34
:::

:::quiz{id="quiz-3"}
Q: You run `dir` in a Windows folder and see only one file, Legitimate_Program.exe (24 bytes). You then run `dir /r` and see an additional entry: Legitimate_Program.exe:secret.txt:$DATA (169 bytes). What does this tell you?
- [ ] The file system is corrupted and showing ghost entries
- [ ] secret.txt is a regular file that Windows Explorer is hiding
- [x] An Alternate Data Stream named secret.txt is hidden inside Legitimate_Program.exe's NTFS metadata
- [ ] The 169-byte entry is a backup created automatically by Windows
:::

:::quiz{id="quiz-4"}
Q: An investigator copies a file containing an Alternate Data Stream from an NTFS drive to a USB drive formatted as FAT32. What happens to the ADS?
- [ ] The ADS is preserved inside the file
- [ ] The copy operation fails with an error
- [x] The ADS is silently dropped — FAT32 does not support alternate data streams
- [ ] The ADS is converted to a hidden file in the same folder
:::

:::quiz{id="quiz-5"}
Q: binwalk scans a JPEG and returns only one entry at offset 0 (the JPEG header itself). Does this mean the file contains no hidden content?
- [ ] Yes — binwalk detects all forms of steganography
- [x] No — binwalk detects embedded files by magic bytes, but appended plaintext and LSB steganography will not appear as additional entries
- [ ] Yes — a single entry means the file hash is clean
- [ ] No — binwalk only works on PNG files
:::

:::quiz{id="quiz-6"}
Q: Appending a secret message to a JPEG file after its FF D9 marker will change which of the following?
- [ ] The image's visual appearance when opened in a viewer
- [x] The file's size and hash value
- [ ] The JPEG's embedded EXIF metadata
- [ ] The file's creation timestamp
:::

---

## Quick Reference

| Goal | Kali Command | Windows Tool |
|------|-------------|-------------|
| View hex bytes of file | `xxd file.jpg \| less` | HxD > File > Open |
| Jump to end of file | `xxd file.jpg \| tail -20` | HxD > Search > Go to > End (backwards) |
| Find magic bytes in file | `binwalk file.jpg` | HxD > Search > Find > Hex-values |
| Auto-extract embedded files | `binwalk -e file.jpg` | HxD > Edit > Select block > File > Save selection |
| Recursive extract | `binwalk -Me file.jpg` | Manual per-file in HxD |
| Find strings in binary | `strings file.jpg \| tail -20` | HxD decoded text pane |
| Check for LSB stego (JPEG) | `steghide info file.jpg` | OpenStego (GUI) |
| Check for LSB stego (PNG) | `zsteg file.png` | OpenStego (GUI) |
| Create ADS | N/A on ext4; needs NTFS mount | `type src > host.exe:stream` in cmd.exe |
| List ADS on file | `getfattr -d file` (NTFS mount) | `dir /r` |
| List all ADS in image | `fls -r image.dd \| grep ":"` | Streams.exe (Sysinternals) |
| Extract ADS from image | `icat image.dd <inode-stream>` | `more < host.exe:stream` |
