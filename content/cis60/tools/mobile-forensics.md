# Mobile Forensic Analysis

Android phones are one of the richest evidence sources in digital forensics. A physical image can reveal device identifiers, account data, email fragments, maps history, Wi-Fi credentials, SIM details, installed apps, call logs, and text messages. This lab mirrors the Autopsy workflow used in CSI-Linux and adds explicit Kali-side methods for mounting partitions, opening SQLite databases, and reviewing Android configuration files directly.

## Overview

This lab uses a **physical image** of a Samsung Galaxy S2. A physical extraction is the mobile equivalent of a full forensic disk image:

- **Live files** — user-accessible app data and configuration
- **System artifacts** — device settings, account files, network data
- **SQLite databases** — app content, message fragments, navigation history
- **Deleted space** — potentially recoverable items not visible in a logical extraction
- **Multiple partitions** — Android images typically contain many partitions, but the main evidence lives in the `data` partition

Whenever possible, choose a **physical image** over a logical one. Physical images preserve more artifacts and may include deleted content that never appears in a standard backup.

---

## Tool Comparison

| Task | Autopsy GUI (CSI-Linux) | Linux / Kali |
|------|--------------------------|--------------|
| Open phone image | Autopsy > New Case > Add Data Source | `mmls`, `mount`, `losetup`, `kpartx` |
| Focus on Android data partition | Expand `vol15` in Data Sources | Mount/extract the `data` partition read-only |
| Browse Android files | Tree + File List + Text/Application tabs | `find`, `ls -la`, `less`, `cat` |
| Open SQLite DBs | Application tab | `sqlite3`, DB Browser for SQLite |
| Convert epoch times | Right-click column > Display as > Date | `datetime(...,'unixepoch')` or `datetime(.../1000,'unixepoch')` |
| Parse XML / config files | Text tab | `grep`, `cat`, `xmllint`, `jq` |
| Review extracted calls/SMS/apps | Results > Extracted Content | Query source DBs directly with `sqlite3` |

---

## High-Value Android Artifacts

| Artifact | Example Path | Forensic Value |
|---------|--------------|----------------|
| Settings database | `data/com.android.providers.settings/databases/settings.db` | Security, network, lock-screen, backup state |
| Device check-in XML | `data/com.google.android.gms/shared_prefs/checkin.xml` | IMEI, Gmail account, device-linked metadata |
| Gmail database | `data/com.google.android.gm/databases/mailstore.<account>.db` | Email fragments, thread IDs, send/receive times, attachments |
| Maps destination history | `data/com.google.android.apps.maps/databases/da_destination_history` | Navigation start time, source and destination coordinates, address |
| Wi-Fi config | `misc/wifi/wpa_supplicant.conf` | SSIDs, passphrases, device model/manufacturer, adapter info |
| SIM info | `System/SimCard.dat` | ICCID, phone number, operator, SIM change/removal time |
| Call log DB | `data/com.sec.android.provider.logsprovider/databases/logs.db` | Calls, direction, start/end time, names, numbers |
| SMS/MMS DB | Commonly `mmssms.db` / messages source DB | Message body, direction, timestamps, thread IDs |
| Package / app data | Android package DBs and extracted content | Installed programs, social media apps, install times |

---

:::command-builder{id="android-sqlite-builder"}
tool_name: sqlite3
target_placeholder: "settings.db"
scan_types:
  - name: "List tables"
    flag: "settings.db '.tables'"
    desc: "See which tables are available in the database"
  - name: "System settings"
    flag: "settings.db \"SELECT * FROM system;\""
    desc: "Review phone behavior settings and system-state options"
  - name: "Secure settings"
    flag: "settings.db \"SELECT * FROM secure;\""
    desc: "Review lockscreen, Bluetooth, backups, and security settings"
  - name: "Gmail messages"
    flag: "mailstore.account.db \"SELECT messageId,conversation,fromAddress,toAddress,subject,snippet FROM messages LIMIT 20;\""
    desc: "Show email fragments, IDs, subjects, and sender/recipient data"
  - name: "Gmail attachments"
    flag: "mailstore.account.db \"SELECT messageId,conversation,filename FROM attachments LIMIT 20;\""
    desc: "Show attachment names and associated message/thread IDs"
  - name: "Maps destinations"
    flag: "da_destination_history \"SELECT time,dest_lat,dest_lng,dest_address,source_lat,source_lng FROM destination_history;\""
    desc: "Show navigation history with coordinates and address"
options:
  - name: "Readable columns"
    flag: "-column -header"
    desc: "Print output in aligned columns with headers"
  - name: "Unix epoch conversion"
    flag: "datetime(column_name,'unixepoch')"
    desc: "Convert epoch seconds into human-readable timestamps"
  - name: "Java epoch ms conversion"
    flag: "datetime(column_name/1000,'unixepoch')"
    desc: "Convert epoch milliseconds into human-readable timestamps"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Open the Physical Image and Identify the Android Data Partition"
goal: "Recognize that Android physical images contain many partitions and isolate the one that holds the user data."
hint: "In Autopsy, the evidence tree reveals many partitions, but the lab focuses on `vol15`, the data partition. On Kali, use `mmls` on the image to list partitions, then mount the target partition read-only. This mirrors what Autopsy is doing behind the scenes."
command: "mmls Lab16.0011"
expected_output: |
  Kali:
    mmls Lab16.0011

    DOS Partition Table
    Units are in 512-byte sectors
      Slot      Start        End          Length       Description
      ...
      015:000   0041943040   0073408511   0031465472   Linux (0x83)   ← data partition candidate
      ...

    # Example mount once the correct start sector is known
    sudo mkdir -p /mnt/lab16_data
    sudo mount -o ro,loop,offset=$((41943040*512)) Lab16.0011 /mnt/lab16_data

  Autopsy GUI:
    Data Sources > Lab16.001 > vol15

  Key point:
    Android images often contain many partitions. The main app/user evidence usually lives in the `data` partition.
:::

:::scenario{id="task-2" level="beginner"}
title: "Task 2 — Review Device Security and Network State in settings.db"
goal: "Use the Android settings database to determine how the phone was configured."
hint: "The `system` and `secure` tables in `settings.db` are excellent for quick triage. They can show behavior settings, backup state, Bluetooth, roaming, and lock-screen configuration. On Kali, query the database directly with `sqlite3`; in Autopsy, use the Application tab and switch tables from the dropdown."
command: "sqlite3 -column -header settings.db \"SELECT name,value FROM secure WHERE name IN ('bluetooth_on','data_roaming','backup_enabled','lockscreen.disabled','lockscreen.options');\""
expected_output: |
  Kali:
    name                  value
    bluetooth_on          1
    data_roaming          0
    backup_enabled        1
    lockscreen.disabled   0
    lockscreen.options    enable_facelock

  Autopsy GUI:
    settings.db > Application tab > secure table

  Interpretation:
    `lockscreen.disabled = 0` means the lock screen was enabled.
    `enable_facelock` indicates face unlock was configured.
    Backup, Bluetooth, and roaming settings provide context about device state.
:::

:::scenario{id="task-3" level="intermediate"}
title: "Task 3 — Extract Device Identifiers and the Linked Gmail Account"
goal: "Pull unique device and account information from checkin.xml."
hint: "The `checkin.xml` file stores high-value identification data. In the lab, it exposes the IMEI and a Gmail account associated with the phone. On Kali, use `grep` or `xmllint` to extract those values directly from the XML."
command: "grep -E 'imei|android_id|gmail|account|email' checkin.xml"
expected_output: |
  Example XML hits:
    <string name=\"imei\">359207041234567</string>
    <string name=\"android_id\">4f8c2a1b7d9e1234</string>
    <string name=\"account\">cfttmobile1@gmail.com</string>

  Autopsy GUI:
    data > com.google.android.gms > shared_prefs > checkin.xml > Text tab

  Investigative value:
    IMEI uniquely identifies the handset.
    The Gmail account helps tie the phone to a specific user and cloud ecosystem.
:::

:::scenario{id="task-4" level="intermediate"}
title: "Task 4 — Query Gmail Fragments and Attachments"
goal: "Review the Gmail database for message fragments, timestamps, thread IDs, and attachment names."
hint: "The `messages` table gives you partial message content through the `snippet` field, plus sender/recipient information and send/receive times. The `attachments` table links filenames back to the message and conversation IDs. Convert the timestamp fields so they are readable before making conclusions."
command: "sqlite3 -column -header mailstore.cfttmobile1@gmail.com.db \"SELECT messageId, conversation, fromAddress, toAddress, datetime(dateSentMs/1000,'unixepoch') AS sent_at, datetime(dateReceivedMs/1000,'unixepoch') AS received_at, subject, snippet FROM messages LIMIT 10;\""
expected_output: |
  Gmail messages:
    messageId   conversation   fromAddress             toAddress                sent_at              received_at          subject            snippet
    1123        9001           boss@example.com        cfttmobile1@gmail.com    2011-09-14 09:12:01  2011-09-14 09:12:08  Meeting Update     Please review...
    1124        9001           cfttmobile1@gmail.com   boss@example.com         2011-09-14 09:14:55  2011-09-14 09:14:55  Re: Meeting Update Thanks...

  Attachment query:
    sqlite3 -column -header mailstore.cfttmobile1@gmail.com.db \
      "SELECT messageId, conversation, filename FROM attachments LIMIT 10;"

    messageId   conversation   filename
    1123        9001           /attachments/agenda.pdf

  Autopsy GUI:
    mailstore...db > Application tab > `messages` and `attachments` tables

  Key interpretation:
    `messageId` identifies the message.
    `conversation` groups messages into a thread.
    `filename` helps trace where a recovered file came from.
:::

:::scenario{id="task-5" level="intermediate"}
title: "Task 5 — Recover Google Maps Navigation History"
goal: "Use the Maps destination history database to identify where the user navigated and when."
hint: "The `destination_history` table records route start time, destination coordinates, destination address, and the source coordinates where navigation began. Convert the time field and map the coordinates if needed."
command: "sqlite3 -column -header da_destination_history \"SELECT datetime(time/1000,'unixepoch') AS nav_start, dest_lat, dest_lng, dest_address, source_lat, source_lng FROM destination_history;\""
expected_output: |
  Maps destination history:
    nav_start             dest_lat    dest_lng      dest_address                         source_lat   source_lng
    2011-09-13 18:42:11   28.538336   -81.379234    Orlando, FL 32801, United States    28.545000    -81.381000

  Autopsy GUI:
    da_destination_history > Application tab > destination_history table

  Investigative value:
    Destination coordinates show where the user intended to go.
    Source coordinates show where the trip started.
    The timestamp anchors the trip in a timeline.
:::

:::scenario{id="task-6" level="intermediate"}
title: "Task 6 — Read Saved Wi-Fi Networks and SIM Card Details"
goal: "Extract network and subscriber evidence from plain-text Android configuration files."
hint: "Both `wpa_supplicant.conf` and `SimCard.dat` are high-value text artifacts. The Wi-Fi config can reveal the handset model, manufacturer, saved SSIDs, and passphrases. `SimCard.dat` can expose the ICCID, phone number, operator, and SIM change/removal time."
command: "grep -E 'model|manufacturer|serial|ssid=|psk=|key_mgmt' wpa_supplicant.conf && grep -Ei 'iccid|phone|operator|country|time' SimCard.dat"
expected_output: |
  Wi-Fi config:
    model=GT-I9100
    manufacturer=samsung
    serial=0x4e4f12345678
    ssid=\"HomeWiFi\"
    psk=\"supersecretpassphrase\"
    key_mgmt=WPA-PSK

  SIM card data:
    ICCID=89014103211118510720
    phoneNumber=5551234567
    operator=AT&T
    country=us
    simChangedTime=1315938451

  Convert SIM change time:
    date -d @1315938451
    Tue Sep 13 18:27:31 UTC 2011

  Autopsy GUI:
    misc > wifi > wpa_supplicant.conf > Text tab
    System > SimCard.dat > Text tab
:::

:::scenario{id="task-7" level="intermediate"}
title: "Task 7 — Review Calls, Installed Programs, and Messages from Extracted Content"
goal: "Understand how Autopsy's Android Analyzer results map back to source databases and how to query the same data manually."
hint: "Autopsy surfaces Calls, Installed Programs, and Messages under `Results > Extracted Content`. That is convenient, but the source databases still matter because they contain the original evidence. On Kali, you would query those source databases directly with `sqlite3`."
command: "sqlite3 -column -header logs.db \"SELECT number, name, datetime(date/1000,'unixepoch') AS call_time, duration, type FROM logs LIMIT 10;\""
expected_output: |
  Calls (source DB example):
    number       name        call_time            duration   type
    5551231111   Alice       2011-09-13 20:10:44  125        outgoing
    5551232222   Bob         2011-09-13 21:15:03  63         incoming

  Installed programs (Autopsy Extracted Content):
    Source File         Program Name        Date/Time Installed
    packages.xml        Facebook            2011-09-10 15:11:02
    packages.xml        Twitter             2011-09-10 15:12:41
    packages.xml        Skype               2011-09-10 15:14:22

  Messages (source DB / extracted view):
    Direction   To Phone Number   Date/Time             Read status   Subject   Text
    outgoing    5551239999        2011-09-13 22:03:12   read          —         On my way now
    incoming    5551239999        2011-09-13 22:05:44   unread        —         OK, see you soon

  Autopsy GUI:
    Results > Extracted Content > Call Logs / Installed Programs / Messages

  Key point:
    Extracted content is fast to review, but the source DB is the authoritative evidence.
:::

---

## Full Kali Workflow

End-to-end Android artifact review from a physical image:

```bash
# 1. Identify partitions in the physical image
mmls Lab16.0011

# 2. Mount the Android data partition read-only
sudo mkdir -p /mnt/lab16_data
sudo mount -o ro,loop,offset=$((START_SECTOR*512)) Lab16.0011 /mnt/lab16_data

# 3. Review device settings and security state
sqlite3 -column -header /mnt/lab16_data/data/com.android.providers.settings/databases/settings.db \
  "SELECT name,value FROM secure;"

# 4. Pull handset/account identifiers
grep -E 'imei|account|gmail|email' \
  /mnt/lab16_data/data/com.google.android.gms/shared_prefs/checkin.xml

# 5. Review Gmail fragments and attachments
sqlite3 -column -header /mnt/lab16_data/data/com.google.android.gm/databases/mailstore.cfttmobile1@gmail.com.db \
  "SELECT messageId,conversation,fromAddress,toAddress,
          datetime(dateSentMs/1000,'unixepoch') AS sent_at,
          subject,snippet
   FROM messages LIMIT 20;"

sqlite3 -column -header /mnt/lab16_data/data/com.google.android.gm/databases/mailstore.cfttmobile1@gmail.com.db \
  "SELECT messageId,conversation,filename FROM attachments LIMIT 20;"

# 6. Review Maps history
sqlite3 -column -header /mnt/lab16_data/data/com.google.android.apps.maps/databases/da_destination_history \
  "SELECT datetime(time/1000,'unixepoch') AS nav_start,
          dest_lat,dest_lng,dest_address,source_lat,source_lng
   FROM destination_history;"

# 7. Review Wi-Fi and SIM artifacts
less /mnt/lab16_data/misc/wifi/wpa_supplicant.conf
less /mnt/lab16_data/System/SimCard.dat

# 8. Hunt for other app databases and XML files
find /mnt/lab16_data/data -type f \( -name '*.db' -o -name '*.xml' \) | less
```

---

## Key Concepts

### Physical vs Logical Mobile Extractions

| Type | What you get | Forensic impact |
|------|---------------|----------------|
| Physical extraction | Full raw image of partitions | Best source for deleted space and full app data |
| Logical extraction | Files exposed by OS/API | Faster, but incomplete |
| Advanced logical | More app/system data than simple logical | Better than logical, still not full raw evidence |

If a physical extraction is available, prefer it.

### SQLite Is the Default Android Evidence Store

Many Android artifacts live in SQLite databases:

- System settings
- Gmail metadata and message fragments
- Maps history
- SMS/MMS data
- Call logs
- App-specific usage and caches

Knowing how to query `sqlite3` directly matters even when Autopsy already parsed part of the evidence.

### Unix Epoch vs Java Epoch

Android artifacts often mix both:

| Format | Example | Convert With |
|--------|---------|--------------|
| Unix epoch (seconds) | `1315938451` | `datetime(column,'unixepoch')` |
| Java epoch (milliseconds) | `1315938451000` | `datetime(column/1000,'unixepoch')` |

If the date converts into the 1970s or far future unexpectedly, you probably used the wrong epoch format.

### Wi-Fi and SIM Artifacts as Attribution Evidence

These files can tie a phone to a person, place, or network:

- **Saved SSID + passphrase** can link the phone to a specific router or location
- **Manufacturer/model/serial** confirms the physical handset identity
- **ICCID + operator + phone number** links the device to a subscriber identity
- **SIM changed/removed time** helps build a device-usage timeline

---

:::quiz{id="quiz-1"}
Q: Why is a physical mobile image preferred over a logical extraction whenever possible?
- [ ] It is always much smaller
- [x] It preserves more complete data, including deleted-space artifacts
- [ ] It contains only user photos and messages
- [ ] It avoids all timestamp conversion work
:::

:::quiz{id="quiz-2"}
Q: Which file in this lab is used to identify handset details like IMEI and the linked Gmail account?
- [ ] `wpa_supplicant.conf`
- [ ] `SimCard.dat`
- [x] `checkin.xml`
- [ ] `logs.db`
:::

:::quiz{id="quiz-3"}
Q: In the Gmail database, which field groups messages into the same thread?
- [ ] `fromAddress`
- [ ] `messageId`
- [x] `conversation`
- [ ] `snippet`
:::

:::quiz{id="quiz-4"}
Q: What does `lockscreen.disabled = 0` indicate in the Android secure settings table?
- [ ] The lock screen was disabled
- [x] The lock screen was enabled
- [ ] The SIM card was removed
- [ ] The phone was in airplane mode
:::

:::quiz{id="quiz-5"}
Q: Which artifact is most useful for recovering a saved Wi-Fi SSID and passphrase from the handset?
- [ ] `mailstore.<account>.db`
- [x] `wpa_supplicant.conf`
- [ ] `da_destination_history`
- [ ] `checkin.xml`
:::

:::quiz{id="quiz-6"}
Q: Which SQL expression correctly converts a millisecond Android timestamp into readable time?
- [ ] `datetime(column_name,'unixepoch')`
- [x] `datetime(column_name/1000,'unixepoch')`
- [ ] `strftime('%s', column_name)`
- [ ] `time(column_name*1000)`
:::

---

## Quick Reference

| Task | Linux / Kali | Autopsy GUI |
|------|--------------|-------------|
| List partitions | `mmls Lab16.0011` | Data Sources tree |
| Mount data partition | `mount -o ro,loop,offset=$((start*512)) ...` | Expand `vol15` |
| Open settings DB | `sqlite3 settings.db` | `settings.db` > Application tab |
| Read XML config | `grep`, `cat`, `xmllint` | Text tab |
| Review Gmail DB | `sqlite3 mailstore...db` | Application tab > `messages` / `attachments` |
| Review Maps history | `sqlite3 da_destination_history` | Application tab > `destination_history` |
| Read Wi-Fi config | `less wpa_supplicant.conf` | Text tab |
| Read SIM artifact | `less SimCard.dat` | Text tab |
| Convert Unix epoch | `datetime(col,'unixepoch')` | Display as > Date |
| Convert Java epoch ms | `datetime(col/1000,'unixepoch')` | Display as > Date |
