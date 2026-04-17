# Log Capturing and Interpretation

Windows keeps multiple layers of logs that help reconstruct what happened, when it happened, and what object was affected. This lab focuses on two of the most useful sources: **Windows Event Logs** (`.evtx`) and the **NTFS USN Change Journal** (`$Extend\$UsnJrnl:$J`). The workflow below mirrors the Autopsy lab and adds Kali-side methods for locating, exporting, and parsing the same data.

## Overview

These two logs answer different kinds of questions:

- **Windows Event Logs** — user logons/logoffs, password resets, service activity, update downloads and installs
- **USN Journal** — file-system changes on NTFS volumes such as create, delete, rename, append, and close

Together they are powerful in timelines:

- Event Logs tell you **what the OS or a service reported**
- USN Journal tells you **what the NTFS file system changed**
- Comparing both can tie user activity to specific files or folders at precise times

---

## Key Log Locations

| Artifact | Path | Notes |
|---------|------|-------|
| USN Journal | `C:\$Extend\$UsnJrnl:$J` | NTFS alternate data stream containing change records |
| USN Journal metadata | `C:\$Extend\$UsnJrnl:$Max` | Max size / journal settings |
| Modern Windows Event Logs | `C:\Windows\System32\winevt\Logs\*.evtx` | Vista+ systems |
| Legacy Event Logs | `C:\Windows\System32\config\*.evt` | XP-era systems |
| Main EVTX files | `Application.evtx`, `System.evtx`, `Security.evtx` | Highest-value logs in many investigations |

> The USN Journal exists on **any NTFS volume**, not just operating-system drives.

---

## Tool Comparison

| Task | Windows / Autopsy | Linux / Kali |
|------|-------------------|--------------|
| Locate EVTX logs | Browse `Windows > System32 > winevt > Logs` | Mount NTFS image and `find` / `ls` |
| Locate USN Journal | Browse `$Extend` and identify `$UsnJrnl:$J` | Enumerate NTFS metadata/ADS-aware paths, export `$J` |
| Parse Event Logs | ParseEvtx ingest module | `evtx_dump.py`, `evtx_dump_json.py`, `python-evtx` |
| Search by Event ID | Autopsy table sort/filter | `grep`, `jq`, `rg` on dumped XML/JSON |
| Parse USN Journal | USN Parser ingest module | `usn.py` from `usnparser` on exported `$J` |
| Review file rename/delete activity | NTFS UsrJrnl Entries | CSV/TLN output from `usn.py`, then `grep` / sort |

---

## Important Event IDs in This Lab

| Event ID | Meaning | Why it matters |
|---------|---------|----------------|
| `4624` | Successful logon | Shows account, time, and logon method |
| `4634` | Logoff | Helps bracket session activity |
| `4724` | Password reset attempt | High-value account-management activity |
| `44` | Windows Update download | Shows which update was retrieved |
| `43` | Windows Update install attempt | Confirms install activity after download |
| `19` | Update installation result | Often used to confirm success/failure |

---

## Important USN Change Types

| Change Type | Meaning |
|------------|---------|
| `file_created; file_closed` | A file or directory was created, then closed |
| `file_deleted; file_closed` | A file or directory was deleted |
| `file_new_name; file_closed` | The item received a new name |
| `file_old_name` | The prior/original name during a rename |
| `data_appended` | Data was added to the file |

Recycle Bin activity often appears as:

- `$I...` — metadata record for the deleted item
- `$R...` — renamed file/folder representing the recycled content

---

:::command-builder{id="logs-builder"}
tool_name: evtx_dump.py
target_placeholder: "Security.evtx"
scan_types:
  - name: "Dump EVTX to XML"
    flag: "Security.evtx > security.xml"
    desc: "Convert binary EVTX into XML for searching"
  - name: "Dump EVTX to JSON"
    flag: "Security.evtx > security.json"
    desc: "Convert EVTX to JSON for structured filtering"
  - name: "Parse USN Journal"
    flag: "-f '$J' -c -o usn.csv"
    desc: "Convert exported USN $J stream to CSV using `usn.py`"
  - name: "Parse USN to timeline"
    flag: "-f '$J' -t usn.tln -s HOSTNAME"
    desc: "Create TLN-style output for timeline work"
options:
  - name: "Verbose USN output"
    flag: "-v"
    desc: "Show all record properties in JSON-style detail"
  - name: "Quick parse"
    flag: "-q"
    desc: "Faster parsing for very large USN journals"
  - name: "Filter filename"
    flag: "-g temp"
    desc: "Only return USN records matching a target filename"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Locate the USN Journal and Windows Event Logs"
goal: "Identify where both log sources live in the filesystem before relying on parsed results."
hint: "Autopsy already parsed both logs in the pre-processed case, but the lab explicitly wants you to know where they live. In Autopsy, the USN Journal appears under `$Extend` as `$UsnJrnl:$J` and `$UsnJrnl:$Max`. Event logs live in `Windows > System32 > winevt > Logs`. On Kali, mount the NTFS image read-only and browse to the EVTX path; for the USN journal, remember it is an NTFS metadata file with alternate data streams, not a normal user file."
command: "find /mnt/windows/Windows/System32/winevt/Logs -maxdepth 1 -name '*.evtx' | head"
expected_output: |
  Kali EVTX path:
    /mnt/windows/Windows/System32/winevt/Logs/Application.evtx
    /mnt/windows/Windows/System32/winevt/Logs/Security.evtx
    /mnt/windows/Windows/System32/winevt/Logs/System.evtx

  Windows / Autopsy path:
    Data Sources > Lab17.E01 > $Extend > $UsnJrnl:$J
    Data Sources > Lab17.E01 > Windows > System32 > winevt > Logs

  Notes:
    `$UsnJrnl:$J` is the change-record stream.
    `$UsnJrnl:$Max` stores journal settings and size information.
:::

:::scenario{id="task-2" level="beginner"}
title: "Task 2 — Parse Event Logs and Search by Event ID"
goal: "Convert EVTX files into searchable text/JSON and find the same high-value event IDs reviewed in the lab."
hint: "Autopsy sorts the parsed table by `Event Identifier` and then `Event Time`. On Kali, do the same by dumping EVTX to XML or JSON and searching for specific IDs. `Security.evtx` is where the logon/logoff and password-reset events usually live, while update-related events may live in other Windows Update operational logs depending on the source."
command: "evtx_dump.py Security.evtx > security.xml && rg 'EventID>4624<|EventID>4634<|EventID>4724<' security.xml"
expected_output: |
  Example hits:
    <EventID>4624</EventID>
    <TimeCreated SystemTime="2020-08-27 04:32:10.650324" />
    ...
    <EventID>4634</EventID>
    <TimeCreated SystemTime="2020-08-27 04:32:45.162733" />
    ...
    <EventID>4724</EventID>
    <TimeCreated SystemTime="2020-08-27 04:38:58.736717" />

  Windows / Autopsy:
    Results > Extracted Content > Windows Event Logs
    Sort by: Event Identifier, then Event Time

  Key point:
    Event ID is the fastest way to pivot into a specific class of activity.
:::

:::scenario{id="task-3" level="intermediate"}
title: "Task 3 — Interpret Logon, Logoff, and Password Reset Events"
goal: "Extract the same details the lab highlights from event IDs 4624, 4634, and 4724."
hint: "The important fields inside each event are often in the detailed XML payload: username, workstation/computer name, SID, and logon type. In this lab, `Logon Type = 2` is the field the exercise calls out. On Kali, dump to XML/JSON, then search around the matching Event ID and timestamp."
command: "rg -n '4624|4634|4724|LogonType|TargetUserName|TargetDomainName|WorkstationName' security.xml"
expected_output: |
  Example 4624 interpretation:
    EventID: 4624
    TimeCreated: 2020-08-27 04:32:10.650324
    TargetUserName: IEUser
    WorkstationName: WINOS
    LogonType: 2

  Example 4634 interpretation:
    EventID: 4634
    TimeCreated: 2020-08-27 04:32:45.162733
    TargetUserName: IEUser
    LogonType: 2

  Example 4724 interpretation:
    EventID: 4724
    TimeCreated: 2020-08-27 04:38:58.736717
    TargetUserName: IEUser

  Investigative value:
    4624 + 4634 can bracket a session.
    4724 shows account-management activity that may matter in compromise or admin-abuse cases.
:::

:::scenario{id="task-4" level="intermediate"}
title: "Task 4 — Track Windows Update Downloads and Installs"
goal: "Compare update download events with install events to see whether an update was only retrieved or actually installed."
hint: "The lab reviews Event ID `44` for downloads and `43` for installs. A good practice is to pivot from the update name in the download event to the corresponding install event, then optionally look for Event ID `19` to confirm success or failure."
command: "rg -n 'EventID>44<|EventID>43<|EventID>19<' update.xml"
expected_output: |
  Example update sequence:
    EventID 44  TimeCreated: 2020-08-27 04:43:07.825611
      Update Title: Security Intelligence Update for Microsoft Defender Antivirus ...

    EventID 44  TimeCreated: 2020-08-27 04:43:22.064549
      Update Title: Microsoft Defender Antivirus update ...

    EventID 43  TimeCreated: 2020-08-28 05:35:03.486477
      Update Title: Security Intelligence Update for Microsoft Defender Antivirus ...

  Interpretation:
    Event 44 = download observed
    Event 43 = install attempt observed
    Event 19 = usually used to confirm final success/failure
:::

:::scenario{id="task-5" level="intermediate"}
title: "Task 5 — Parse the USN Journal and Find File Create/Delete/Rename Activity"
goal: "Convert the exported `$J` stream into readable records and identify create, delete, and rename activity."
hint: "Autopsy exposes parsed USN rows under `Results > Extracted Content > NTFS UsrJrnl Entries`. On Kali, use a USN parser such as `usn.py` from `usnparser` against an exported copy of `$J`. Once parsed to CSV, search the `Change_Type` and `Filename` fields for create/delete/rename patterns."
command: "usn.py -f '$J' -c -o usn.csv && rg 'file_created|file_deleted|file_new_name|file_old_name' usn.csv"
expected_output: |
  Example USN CSV rows:
    2020-08-29 20:14:01.516344,$I3L7INC,ARCHIVE,data_appended; file_created; file_closed
    2020-08-29 20:14:01.600000,$R3L7INC,DIRECTORY,file_new_name; file_closed
    2020-08-29 20:14:01.500000,Temp,DIRECTORY,file_old_name

  Windows / Autopsy:
    Results > Extracted Content > NTFS UsrJrnl Entries

  Key interpretation:
    `$I...` often marks Recycle Bin metadata.
    `$R...` often marks the recycled file/folder body.
    `file_old_name` + `file_new_name` together describe a rename.
:::

:::scenario{id="task-6" level="intermediate"}
title: "Task 6 — Reconstruct a Recycle Bin Rename Sequence from USN Records"
goal: "Use the same pattern as the lab to infer that a folder was renamed into a Recycle Bin-style name."
hint: "The lab’s example shows a folder named `Temp` becoming `$R3L7INC`, with a matching `$I3L7INC` record created around the same time. On Kali, grep for `Temp` and nearby `$I` / `$R` names in the parsed USN CSV, then compare timestamps and change types."
command: "rg -n 'Temp|\\$I3L7INC|\\$R3L7INC' usn.csv"
expected_output: |
  Example sequence:
    2020-08-29 20:14:01.500000,Temp,DIRECTORY,file_old_name
    2020-08-29 20:14:01.516344,$I3L7INC,ARCHIVE,data_appended; file_created; file_closed
    2020-08-29 20:14:01.530000,$R3L7INC,DIRECTORY,file_new_name; file_closed

  Inference:
    The original folder `Temp` was renamed into a Recycle Bin-style `$R...` name.
    A matching `$I...` metadata record was created immediately before/around the rename.
:::

---

## Full Kali Workflow

End-to-end log review from a Windows image:

```bash
# 1. Mount the E01 or raw image and locate Windows logs
# For E01:
# sudo ewfmount Lab17.E01 /mnt/ewf
# sudo mount -o ro /mnt/ewf/ewf1 /mnt/windows

# 2. Confirm EVTX log location
find /mnt/windows/Windows/System32/winevt/Logs -name '*.evtx' | head -20

# 3. Dump Security.evtx to XML for searching
evtx_dump.py /mnt/windows/Windows/System32/winevt/Logs/Security.evtx > security.xml

# 4. Search key event IDs
rg 'EventID>4624<|EventID>4634<|EventID>4724<' security.xml

# 5. Dump update-related EVTX and search for download/install/result events
evtx_dump.py /mnt/windows/Windows/System32/winevt/Logs/System.evtx > system.xml
rg 'EventID>44<|EventID>43<|EventID>19<' system.xml

# 6. Export the USN $J stream with your preferred ADS-aware workflow/tooling
# Resulting file assumed to be named $J

# 7. Parse the USN Journal to CSV
usn.py -f '$J' -c -o usn.csv

# 8. Search for creates, deletes, and renames
rg 'file_created|file_deleted|file_new_name|file_old_name' usn.csv

# 9. Reconstruct specific filename activity
rg 'Temp|\\$I|\\$R' usn.csv
```

---

## Key Concepts

### Event Logs vs USN Journal

| Source | Best for |
|-------|----------|
| Event Logs | User/session, service, update, and OS-reported events |
| USN Journal | File-system metadata changes on NTFS volumes |

Event Logs are semantic and human-meaningful.
USN is low-level and file-centric.

### Why the USN Journal Is So Valuable

The USN Journal is:

- **Persistent** on NTFS volumes until older entries roll off
- **Granular** about file changes
- **Independent** of whether the file still exists under its original name
- **Useful for rename/deletion reconstruction**, especially around Recycle Bin activity

Microsoft describes the change journal as a persistent per-volume NTFS log of changes to files and directories. Source: [Microsoft Learn](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-usn), [Change Journal Records](https://learn.microsoft.com/en-us/windows/win32/fileio/change-journal-records)

### Why EVTX Parsing Is Needed

`.evtx` files are not plain text. They store records in a binary XML-based format.

The `python-evtx` project provides `evtx_dump.py` and `evtx_dump_json.py` to convert EVTX into searchable XML/JSON. Source: [python-evtx PyPI](https://pypi.org/project/python-evtx/)

### Why USN Parsing Is Needed

`$UsnJrnl:$J` is a binary NTFS alternate data stream. You need a parser to make it readable.

The `usnparser`/`usn.py` tool is specifically built to parse the NTFS USN Change Journal into text, CSV, timeline, or verbose formats. Source: [usnparser PyPI](https://pypi.org/project/usnparser/), [USN-Journal-Parser GitHub](https://github.com/PoorBillionaire/USN-Journal-Parser)

---

:::quiz{id="quiz-1"}
Q: Where is the Windows USN Journal change stream stored on an NTFS volume?
- [ ] `C:\Windows\System32\config\$UsnJrnl`
- [x] `C:\$Extend\$UsnJrnl:$J`
- [ ] `C:\Recycle.Bin\$UsnJrnl`
- [ ] `C:\Windows\Logs\$UsnJrnl`
:::

:::quiz{id="quiz-2"}
Q: Which three EVTX files are the most commonly reviewed first in Windows investigations?
- [ ] `Boot.evtx`, `Kernel.evtx`, `DNS.evtx`
- [x] `Application.evtx`, `System.evtx`, `Security.evtx`
- [ ] `Audit.evtx`, `Power.evtx`, `Users.evtx`
- [ ] `Logon.evtx`, `Logoff.evtx`, `Update.evtx`
:::

:::quiz{id="quiz-3"}
Q: Which Event ID in this lab corresponds to a successful logon?
- [ ] `4634`
- [ ] `4724`
- [x] `4624`
- [ ] `44`
:::

:::quiz{id="quiz-4"}
Q: What does a USN change type of `file_old_name` usually indicate?
- [ ] The file was encrypted
- [ ] The file was downloaded
- [x] The record is part of a rename sequence and shows the previous name
- [ ] The file was copied to a USB drive
:::

:::quiz{id="quiz-5"}
Q: In the lab, which Event ID is used to look for password reset attempts?
- [ ] `19`
- [ ] `43`
- [x] `4724`
- [ ] `4624`
:::

:::quiz{id="quiz-6"}
Q: Why do you need a parser for `.evtx` and `$J`?
- [ ] Because both files are always encrypted with BitLocker
- [ ] Because both files are compressed ZIP archives
- [x] Because both store binary structured data that is not directly readable as plain text
- [ ] Because Autopsy deletes the raw files after parsing
:::

---

## Quick Reference

| Task | Linux / Kali | Windows / Autopsy |
|------|--------------|-------------------|
| Locate EVTX logs | `find /mnt/windows/Windows/System32/winevt/Logs -name '*.evtx'` | Browse `Windows > System32 > winevt > Logs` |
| Locate USN Journal | Export/find `$Extend\$UsnJrnl:$J` | Browse `$Extend > $UsnJrnl:$J` |
| Dump EVTX to XML | `evtx_dump.py Security.evtx > security.xml` | ParseEvtx ingest module |
| Search Event IDs | `rg 'EventID>4624<' security.xml` | Sort/filter Windows Event Logs table |
| Parse USN to CSV | `usn.py -f '$J' -c -o usn.csv` | USN Parser ingest module |
| Search rename/delete activity | `rg 'file_old_name|file_new_name|file_deleted' usn.csv` | NTFS UsrJrnl Entries |
| Investigate Recycle Bin rename | `rg 'Temp|\\$I|\\$R' usn.csv` | Sort/filter Filename + Change_Type |
