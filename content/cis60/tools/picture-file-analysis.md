# Picture File Analysis

Digital photos carry hidden metadata beyond the visible image — camera make and model, exact timestamp, and often GPS coordinates. Windows also maintains a hidden `Thumbs.db` thumbnail cache that can retain copies of pictures even after the originals are deleted. This lab covers both: extracting **EXIF metadata** with `exiftool`, and **carving embedded images** from `Thumbs.db` using a hex editor.

## Overview

Picture file analysis reveals:

- **Device attribution** — the make and model of the camera or smartphone that took the photo
- **Accurate timestamps** — Date/Time Original embedded in the file, which is more reliable than the file system timestamp
- **GPS coordinates** — latitude, longitude, and altitude pinpointing where the photo was taken
- **Camera settings** — ISO, exposure, aperture, focal length, flash status
- **Thumbnail evidence** — `Thumbs.db` may retain thumbnail copies of deleted images

---

## EXIF Data Structure

Every JPEG from a modern camera or smartphone embeds EXIF (Exchangeable Image File Format) data in the file header:

| EXIF Field | Forensic Value |
|------------|---------------|
| Make / Camera Model Name | Identifies the specific device |
| Date/Time Original | When the shutter was pressed — more reliable than file system mtime |
| GPS Latitude / Longitude | Physical location the photo was taken |
| GPS Altitude | Elevation above sea level |
| Software | Firmware or app version (e.g., HDR+ on Google Pixel) |
| Image Size | Resolution — can confirm if image was cropped or resized |
| Flash | Whether flash fired — useful for indoor/outdoor context |

---

:::command-builder{id="exiftool-builder"}
tool_name: exiftool
target_placeholder: "image.jpg"
scan_types:
  - name: "All metadata (terminal)"
    flag: "image.jpg"
    desc: "Dump all EXIF fields to the terminal"
  - name: "Export to text file"
    flag: "-w txt image.jpg"
    desc: "Write metadata to image.txt for review in a text editor"
  - name: "GPS coordinates only"
    flag: "-gps:all image.jpg"
    desc: "Show only GPS-related tags (location, altitude, timestamp)"
  - name: "Key forensic fields"
    flag: "-Make -Model -DateTimeOriginal -GPSPosition image.jpg"
    desc: "Show the four most forensically relevant fields"
  - name: "Batch process all JPGs"
    flag: "-w txt *.jpg"
    desc: "Export metadata for every JPG in the current directory"
options:
  - name: "CSV output"
    flag: "-csv"
    desc: "Format output as comma-separated values (good for spreadsheets)"
  - name: "Compact / short tags"
    flag: "-s"
    desc: "Show short tag names instead of verbose descriptions"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Extract EXIF Metadata from a Photo"
goal: "Run exiftool against a JPEG to see all embedded metadata — identify the camera make and model, timestamps, and any GPS data."
hint: "Run exiftool with just the filename to print all tags to the terminal. The output is long, so pipe it to less for scrolling. Key fields to find: Make, Camera Model Name, Date/Time Original, and any GPS fields near the bottom of the output. On Windows, you can right-click a JPG in Explorer > Properties > Details tab for a subset of EXIF, but exiftool gives the full picture."
command: 'exiftool IMG_001.jpg | less'
expected_output: |
  ExifTool Version Number         : 8.60
  File Name                       : IMG_001.jpg
  File Size                       : 5.8 MB
  File Modification Date/Time     : 2020:08:01 14:21:26-04:00
  File Type                       : JPEG
  MIME Type                       : image/jpeg
  Exif Byte Order                 : Little-endian (Intel, II)
  Make                            : Google
  Camera Model Name               : Pixel 3 XL
  Orientation                     : Horizontal (normal)
  X Resolution                    : 72
  Y Resolution                    : 72
  Software                        : HDR+ 1.0.322479891zdr
  Modify Date                     : 2020:08:01 14:21:24
  Exposure Time                   : 1/23
  F Number                        : 1.8
  ISO                             : 181
  Exif Version                    : 0231
  Date/Time Original              : 2020:08:01 14:21:24
  Flash                           : Auto, Did not fire
  Focal Length                    : 4.4 mm
  Image Size                      : 4032x3024
:::

:::scenario{id="task-2" level="beginner"}
title: "Task 2 — Export EXIF to a Text File and Find GPS Coordinates"
goal: "Write the EXIF output to a text file for easier review, then locate the GPS coordinates that reveal where the photo was taken."
hint: "Use exiftool -w txt to create a .txt file alongside the image. Open it with any text editor (gedit, less, cat). Scroll to the bottom to find GPS fields. The GPS Position field combines latitude and longitude into one line. GPS coordinates from a photo can be plotted on a map to confirm the location claimed by a subject. Note that GPS Date/Time is often stored in UTC, while Date/Time Original is in local time."
command: 'exiftool -w txt IMG_001.jpg && grep -i gps IMG_001.txt'
expected_output: |
  Terminal after running exiftool -w txt:
    1 output files created

  grep -i gps IMG_001.txt output:
    GPS Altitude                    : 7.5 m Above Sea Level
    GPS Date/Time                   : 2020:08:01 21:21:18Z
    GPS Latitude                    : 49 deg 19' 29.56" N
    GPS Longitude                   : 122 deg 56' 42.89" W
    GPS Position                    : 49 deg 19' 29.56" N, 122 deg 56' 42.89" W

  Forensic note:
    GPS Date/Time is in UTC (Z suffix): 2020:08:01 21:21:18Z
    Date/Time Original is local time:   2020:08:01 14:21:24
    Difference = 7 hours → Pacific Daylight Time (UTC-7) confirmed

  Plot coordinates on Google Maps or OpenStreetMap:
    49.324878, -122.945247  →  Maple Ridge, British Columbia, Canada
:::

:::scenario{id="task-3" level="beginner"}
title: "Task 3 — Batch Extract Metadata from Multiple Images"
goal: "Process all JPEG files in a directory at once and compare timestamps and GPS coordinates across images to build a timeline."
hint: "exiftool accepts wildcards, so *.jpg processes every JPEG in the current folder. Use -w txt to create individual text files, or -csv to get all metadata in a single spreadsheet. Comparing Date/Time Original and GPS Position across multiple photos can confirm a subject was at a location at a specific time, or reveal inconsistencies if images were edited or copied."
command: 'exiftool -csv -DateTimeOriginal -GPSPosition -Make -Model *.jpg'
expected_output: |
  CSV output (one row per image):
  SourceFile,DateTimeOriginal,GPSPosition,Make,Model
  IMG_001.jpg,2020:08:01 14:21:24,"49 deg 19' 29.56"" N, 122 deg 56' 42.89"" W",Google,Pixel 3 XL
  IMG_002.jpg,2020:08:01 14:23:11,"49 deg 19' 31.02"" N, 122 deg 56' 40.14"" W",Google,Pixel 3 XL
  IMG_003.jpg,2020:08:01 14:25:44,"49 deg 19' 28.87"" N, 122 deg 56' 43.55"" W",Google,Pixel 3 XL
  IMG_004.jpg,2020:08:01 14:27:03,"49 deg 19' 30.11"" N, 122 deg 56' 41.78"" W",Google,Pixel 3 XL

  All four images:
    - Same device (Google Pixel 3 XL)
    - Taken within 6 minutes (14:21 to 14:27)
    - GPS coordinates cluster within ~100 meters of each other
    - Consistent with a single person walking in a small area
:::

:::scenario{id="task-4" level="beginner"}
title: "Task 4 — Understand What Thumbs.db Is and Why It Matters"
goal: "Learn what Thumbs.db contains and why it can hold evidence of images that no longer exist on the file system."
hint: "Thumbs.db is a hidden OLE Compound Document file created automatically by Windows Explorer when a user views a folder in thumbnail view. It stores small (thumbnail-sized) JPEG copies of every image it has indexed. Even if the original image files are later deleted, the Thumbs.db thumbnail cache may persist, preserving evidence of what images were once in that folder. The file is hidden by default — enable 'Show hidden files' and 'Show protected operating system files' to see it in Explorer."
command: 'file Thumbs.db && xxd Thumbs.db | head -5'
expected_output: |
  file Thumbs.db:
    Thumbs.db: Composite Document File V2 Document (OLE)

  xxd Thumbs.db | head -5:
    00000000: d0cf 11e0 a1b1 1ae1 0000 0000 0000 0000  ................
    00000010: 0000 0000 0000 0000 3e00 0300 feff 0000  ........>.......
    00000020: 0600 0000 0000 0000 0000 0000 0100 0000  ................

  The D0 CF 11 E0 header is the OLE Compound Document signature.
  JPEG thumbnails embedded inside begin at offset 0xA18 (header FF D8 FF E0).

  Linux alternative — list OLE streams:
    sudo apt install python3-oletools
    olefile Thumbs.db

  Windows: Thumbs.db is hidden by default.
  To see it: Explorer > View > Options > Show hidden files AND
  uncheck "Hide protected operating system files"
:::

:::scenario{id="task-5" level="beginner"}
title: "Task 5 — Carve a JPEG from Thumbs.db Using a Hex Editor"
goal: "Manually locate and extract an embedded JPEG thumbnail from a Thumbs.db file using JPEG magic byte signatures."
hint: "Every JPEG starts with FF D8 FF E0 (SOI header) and ends with FF D9 (EOI footer). In HxD on Windows: open Thumbs.db, then Edit > Find > Hex-values > type FF D8 FF E0 to jump to the start of the first embedded JPEG. Note the offset (e.g. 0xA18). Then search for FF D9 to find the end. Note that offset (e.g. 0x6E38). Use Edit > Select block, enter start and end offsets, then File > Save selection as pic1.jpg. On Linux, foremost or binwalk automates this entire process."
command: 'foremost -t jpg -i Thumbs.db -o carved_output/'
expected_output: |
  foremost output:
    Foremost version 1.5.7 by Jesse Kornblum
    Processing: Thumbs.db
    |*|
    Length: 27 KB (27831 bytes)

    File: Thumbs.db
    Start: Thu Aug  1 00:00:00 2020
    Length: 27 KB (27 bytes)

    Num      Name (bs=512)   Size   File Offset   Comment
    0:      00000000.jpg   24 KB   2584           JFIF

  ls carved_output/jpg/
    00000000.jpg   00000001.jpg   00000002.jpg   00000003.jpg

  Manual hex editor method (HxD on Windows):
    1. File > Open → Thumbs.db
    2. Edit > Find > Hex-values: FF D8 FF E0 → OK
       Note start offset: 0xA18
    3. Edit > Find > Hex-values: FF D9 → OK
       Note end offset:   0x6E38
    4. Edit > Select block → Start: A18, End: 6E38 → OK
    5. File > Save selection → pic1.jpg
    Result: viewable 256×192 JPEG thumbnail of original image

  binwalk alternative (Linux):
    binwalk --dd="jpeg:jpg" Thumbs.db
:::

---

## JPEG Magic Bytes

File carving relies on knowing the byte signatures that mark the start and end of each file format:

| File Type | Header (SOI) | Footer (EOI) | Notes |
|-----------|-------------|-------------|-------|
| JPEG | `FF D8 FF E0` or `FF D8 FF E1` | `FF D9` | E0 = JFIF, E1 = EXIF |
| PNG | `89 50 4E 47 0D 0A 1A 0A` | `49 45 4E 44 AE 42 60 82` | Fixed-length footer |
| PDF | `25 50 44 46` (`%PDF`) | `25 25 45 4F 46` (`%%EOF`) | |
| ZIP | `50 4B 03 04` (`PK..`) | `50 4B 05 06` | |

> When carving from Thumbs.db, a single file may contain multiple embedded JPEGs. Continue searching for `FF D8 FF E0` headers sequentially after saving each found image.

---

## Key Forensic Concepts

### EXIF Timestamp Reliability

A file's **file system timestamp** (mtime) changes whenever the file is copied or moved. The **EXIF Date/Time Original** is written by the camera at shutter-press and does not change when the file is copied — making it the authoritative capture timestamp.

| Timestamp | What it means | Can it be changed? |
|-----------|--------------|-------------------|
| File system mtime | Last write to storage | Yes — any file copy |
| EXIF Modify Date | Last metadata edit | Yes — editing software |
| EXIF Date/Time Original | When camera took the photo | Rarely — requires hex editing |
| EXIF GPS Date/Time | GPS fix timestamp (UTC) | Rarely |

### GPS Coordinates in Evidence

GPS data in EXIF is stored in degrees/minutes/seconds:

```
GPS Latitude  : 49 deg 19' 29.56" N
GPS Longitude : 122 deg 56' 42.89" W
```

Convert to decimal degrees for mapping tools:
- Latitude = 49 + 19/60 + 29.56/3600 = **49.3249°N**
- Longitude = -(122 + 56/60 + 42.89/3600) = **-122.9452°W**

### Why Thumbs.db Survives Deletion

When pictures are deleted from a folder, Windows does not automatically update `Thumbs.db`. The thumbnail copies may persist indefinitely, providing:
- Proof that specific images existed in that folder
- A visual copy of the content (at thumbnail resolution, typically 256×192 px)
- The original filename embedded in the OLE stream metadata

---

:::quiz{id="quiz-1"}
Q: Which EXIF field provides the most reliable timestamp for when a photo was actually taken?
- [ ] File Modification Date/Time
- [ ] Modify Date
- [x] Date/Time Original
- [ ] GPS Date/Time
:::

:::quiz{id="quiz-2"}
Q: An investigator finds that the File Modification Date/Time and the EXIF Date/Time Original differ by three weeks. What is the most likely explanation?
- [ ] The camera's clock was wrong when the photo was taken
- [x] The file was copied or moved after it was originally captured — the EXIF Date/Time Original reflects when it was taken
- [ ] The GPS clock is three weeks ahead of local time
- [ ] exiftool displays timestamps incorrectly for JPEGs
:::

:::quiz{id="quiz-3"}
Q: What Linux command exports EXIF metadata from all JPEGs in the current directory to individual text files?
- [ ] exiftool -all *.jpg
- [x] exiftool -w txt *.jpg
- [ ] exiftool -export txt *.jpg
- [ ] exiftool --dump *.jpg
:::

:::quiz{id="quiz-4"}
Q: What are the JPEG magic bytes used to identify the start of an embedded JPEG during file carving?
- [ ] D0 CF 11 E0
- [ ] 89 50 4E 47
- [x] FF D8 FF E0
- [ ] 25 50 44 46
:::

:::quiz{id="quiz-5"}
Q: Thumbs.db is forensically valuable because:
- [ ] It stores a complete backup of every file in the folder
- [ ] Windows automatically hashes files added to the folder
- [x] It may retain thumbnail copies of images even after the originals have been deleted
- [ ] It records timestamps of every time each file was accessed
:::

:::quiz{id="quiz-6"}
Q: On Linux, which tool automates carving JPEG files from a binary file like Thumbs.db?
- [ ] exiftool
- [ ] lsblk
- [x] foremost
- [ ] dcfldd
:::

---

## Quick Reference

| Task | Linux (DEFT / Kali) | Windows |
|------|---------------------|---------|
| View all EXIF | `exiftool image.jpg` | Right-click > Properties > Details |
| Export to text | `exiftool -w txt image.jpg` | `exiftool -w txt image.jpg` |
| GPS only | `exiftool -gps:all image.jpg` | `exiftool -gps:all image.jpg` |
| Batch process | `exiftool -w txt *.jpg` | `exiftool -w txt *.jpg` |
| CSV summary | `exiftool -csv *.jpg` | `exiftool -csv *.jpg` |
| Identify Thumbs.db | `file Thumbs.db` | File > Open in HxD |
| Carve JPEGs (auto) | `foremost -t jpg -i Thumbs.db -o out/` | HxD: Find FF D8 → Find FF D9 → Select block → Save selection |
| Carve JPEGs (binwalk) | `binwalk --dd="jpeg:jpg" Thumbs.db` | — |
