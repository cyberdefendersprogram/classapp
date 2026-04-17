# IoT Forensics

IoT devices often store fragments of personal activity that never appear on a traditional desktop: synced photos, health data, notification text, Wi-Fi credentials, voice assistant settings, and cloud-linked account identifiers. This lab mirrors the FTK Imager + DB Browser workflow from the Windows exercise and adds explicit Kali-side methods for mounting Linux-style images, exporting SQLite databases, and parsing plain-text IoT configuration files.

## Overview

This lab focuses on two device families:

- **Samsung smartwatch** — Android-style `ext4` file system with synced media, thumbnails, health databases, email notifications, and recent app usage
- **Amazon Echo Dot** — `ext4` userdata partition with Wi-Fi configuration, connection history, wake-word settings, and account-linked SQLite data

IoT artifacts can answer questions such as:

- **Who used the device** — profile names, account IDs, display names
- **What they did** — steps, heart rate, recent apps, viewed notifications
- **Where they were** — Wi-Fi SSIDs, router identifiers, synced data tied to location
- **When it happened** — epoch timestamps in config files and databases
- **Which device it was** — serial number, model, codename, OS version

---

## Tool Comparison

| Task | Windows / GUI | Linux / Kali |
|------|---------------|--------------|
| Open forensic image | FTK Imager > Add Evidence Item | `mount -o ro,loop`, `ewfmount`, `mmls`, `kpartx` |
| Browse `ext4` file system | FTK Imager Evidence Tree | `mount -o ro`, `find`, `ls -la` |
| Export files from image | FTK Imager > right-click > Export Files | `cp`, `icat`, `tsk_recover` |
| View media and thumbnails | FTK Imager View pane | Any image viewer, `file`, `find` |
| Open SQLite databases | DB Browser for SQLite | `sqlite3`, `DB Browser for SQLite` |
| Convert epoch timestamps | DB Browser display format | `datetime(..., 'unixepoch')` in `sqlite3` |
| Read config / text artifacts | FTK text or hex view | `cat`, `less`, `grep`, `jq` |

---

## IoT Artifact Types

| Artifact | Example Path | Forensic Value |
|---------|---------------|----------------|
| Synced media | `media/Images/` | Photos copied from a paired phone |
| Thumbnail cache | `media/.thumb/phone/` | Evidence of viewed or deleted media |
| Health DB | `apps/com.samsung.shealth/data/.shealth.db` | Profile, steps, heart rate, fitness metrics |
| Email notification DB | `apps/com.samsung.wemail/data/dbspace/.wemail.db` | Sender, subject, partial message text |
| Recent apps DB | `apps/com.samsung.w-launcher-app/data/.favorite_apps.db` | Most recently used app order |
| Wi-Fi config | `misc/wifi/wpa_supplicant.conf` | SSID, passphrase, device codename, last connect time |
| Network history | `misc/wifi/networkHistory.txt` | BSSID, auth type, gateway MAC, radio details |
| Wake-word config | `davs/wakeword/.../op.cfg.json` | Wake word, stop command, sleep duration |
| Echo account DB | `data/com.amazon.imp/databases/map_data_storage_v2.db` | Display name / cloud-linked user account |

---

:::command-builder{id="sqlite-iot-builder"}
tool_name: sqlite3
target_placeholder: ".shealth.db"
scan_types:
  - name: "List tables"
    flag: ".shealth.db '.tables'"
    desc: "See which tables exist in the database"
  - name: "Health profile"
    flag: ".shealth.db \"SELECT * FROM shealth_profile;\""
    desc: "Show user profile data such as age, height, weight, goals"
  - name: "Pedometer history"
    flag: ".shealth.db \"SELECT * FROM shealth_pedometer_history LIMIT 20;\""
    desc: "Show step counts, distance, and calories"
  - name: "Heart-rate log"
    flag: ".shealth.db \"SELECT * FROM shealth_heartrate_log LIMIT 20;\""
    desc: "Show average/min/max heart rate and time ranges"
  - name: "Email notifications"
    flag: ".wemail.db \"SELECT mDateTime,mTitle,mTextMessage,mEmailAddr,mDisplayName FROM EmailNotiInfo LIMIT 20;\""
    desc: "Show notification timestamps, subjects, message text, and sender data"
  - name: "Echo accounts"
    flag: "map_data_storage_v2.db \"SELECT * FROM accounts;\""
    desc: "Show account identifiers linked to the Echo device"
options:
  - name: "Column mode"
    flag: "-column -header"
    desc: "Print readable tabular output"
  - name: "Convert Unix epoch"
    flag: "datetime(column_name, 'unixepoch')"
    desc: "Convert seconds-since-epoch to readable date/time"
  - name: "Convert Java epoch ms"
    flag: "datetime(column_name/1000, 'unixepoch')"
    desc: "Convert milliseconds-since-epoch to readable date/time"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Mount the Smartwatch Image and Confirm It Uses ext4"
goal: "Open the smartwatch image and verify that the device uses an Android/Linux-style file system."
hint: "In FTK Imager, the smartwatch image expands to `NONAME [ext4]`, which is an immediate clue that the device is Linux/Android-based. On Kali, mount the raw image read-only with a loop device and inspect the top-level folders. Names like `media` and `apps` reinforce that you are looking at a mobile/embedded file system rather than a Windows volume."
command: "sudo mkdir -p /mnt/lab15_watch && sudo mount -o ro,loop Lab15-1.img /mnt/lab15_watch && ls -la /mnt/lab15_watch"
expected_output: |
  Kali:
    sudo mkdir -p /mnt/lab15_watch
    sudo mount -o ro,loop Lab15-1.img /mnt/lab15_watch
    ls -la /mnt/lab15_watch

    drwxr-xr-x root root .
    drwxr-xr-x root root ..
    drwxr-xr-x root root apps
    drwxr-xr-x root root media
    drwxr-xr-x root root system
    drwxr-xr-x root root data

  Windows FTK Imager:
    Evidence Tree > Lab15-1.img > NONAME [ext4] > [root]

  Forensic meaning:
    ext4 strongly suggests a Linux/Android-family device.
:::

:::scenario{id="task-2" level="beginner"}
title: "Task 2 — Find Synced Media and Hidden Thumbnails on the Smartwatch"
goal: "Locate user-visible images and the hidden thumbnail cache that may preserve evidence of deleted or synced media."
hint: "The lab shows pictures in `media/Images` and thumbnail artifacts in `media/.thumb/phone`. Hidden folders matter because they often survive after the original file is deleted. On Kali, use `find` to enumerate image files in both places and compare names. Thumbnails with `.jpg`, `.mp4`, or `.mp3` prefixes can reveal what kinds of content were once synced."
command: "find /mnt/lab15_watch/media -maxdepth 3 \\( -iname '*.jpg' -o -iname '*.png' -o -iname '*.mp4*' -o -iname '*.mp3*' \\) | sort"
expected_output: |
  Smartwatch media examples:
    /mnt/lab15_watch/media/Images/photo1.jpg
    /mnt/lab15_watch/media/Images/photo2.jpg
    /mnt/lab15_watch/media/.thumb/phone/.jpg_001
    /mnt/lab15_watch/media/.thumb/phone/.jpg_002
    /mnt/lab15_watch/media/.thumb/phone/.mp4_001

  Windows FTK Imager path:
    Lab15-1.img > NONAME [ext4] > [root] > media > Images
    Lab15-1.img > NONAME [ext4] > [root] > media > .thumb > phone

  Why this matters:
    Thumbnails can outlive the source media and show content that was synced or later removed.
:::

:::scenario{id="task-3" level="intermediate"}
title: "Task 3 — Export the Smartwatch SQLite Databases"
goal: "Collect the smartwatch databases and their journal files for offline review."
hint: "The lab exports three pairs of files: `.shealth.db`, `.wemail.db`, and `.favorite_apps.db`, each with its matching journal file. On Kali, copy both the database and journal file because uncommitted or recently changed transactions may still be stored there. Keep exports in a separate case folder rather than modifying the mounted image."
command: "mkdir -p ~/cases/FOR_LAB_015/Exports/Lab15_1 && cp /mnt/lab15_watch/apps/com.samsung.shealth/data/.shealth.db* ~/cases/FOR_LAB_015/Exports/Lab15_1/ && cp /mnt/lab15_watch/apps/com.samsung.wemail/data/dbspace/.wemail.db* ~/cases/FOR_LAB_015/Exports/Lab15_1/ && cp /mnt/lab15_watch/apps/com.samsung.w-launcher-app/data/.favorite_apps.db* ~/cases/FOR_LAB_015/Exports/Lab15_1/"
expected_output: |
  Kali export folder:
    ~/cases/FOR_LAB_015/Exports/Lab15_1/
      .shealth.db
      .shealth.db-journal
      .wemail.db
      .wemail.db-journal
      .favorite_apps.db
      .favorite_apps.db-journal

  Windows FTK Imager:
    Highlight target files > right-click > Export Files
    Save to: E:\FOR_LAB_015\Exports\Lab15_1

  Best practice:
    Export the journal file with the main `.db` every time.
:::

:::scenario{id="task-4" level="intermediate"}
title: "Task 4 — Query Health, Email, and Recent-App Data on the Smartwatch"
goal: "Use SQLite queries to extract user profile, pedometer, heart-rate, email notification, and recent-app evidence."
hint: "DB Browser does this through the Browse Data tab and display-format conversions. On Kali, `sqlite3` gives you the same result directly. The health database uses Java epoch timestamps in milliseconds, while some notification data is Unix epoch in seconds. Convert them explicitly inside your SQL queries so the output is immediately readable."
command: "sqlite3 -column -header ~/cases/FOR_LAB_015/Exports/Lab15_1/.shealth.db \"SELECT birthday, datetime(birthday/1000,'unixepoch') AS birthday_readable, timestamp, datetime(timestamp/1000,'unixepoch') AS profile_created FROM shealth_profile;\""
expected_output: |
  Smartwatch profile query:
    birthday       birthday_readable      timestamp      profile_created
    315532800000   1980-01-01 00:00:00    1604275200000  2020-11-02 00:00:00

  Pedometer example:
    sqlite3 -column -header .shealth.db \
      "SELECT datetime(start_time/1000,'unixepoch') AS start_time,
              walk_step_count, run_step_count, distance, calorie
       FROM shealth_pedometer_history LIMIT 10;"

  Heart-rate example:
    sqlite3 -column -header .shealth.db \
      "SELECT datetime(start_time/1000,'unixepoch') AS start_time,
              avg_heart_rate, min_heart_rate, max_heart_rate
       FROM shealth_heartrate_log LIMIT 10;"

  Email notification example:
    sqlite3 -column -header .wemail.db \
      "SELECT datetime(mDateTime,'unixepoch') AS seen_at,
              mTitle, mTextMessage, mEmailAddr, mDisplayName
       FROM EmailNotiInfo LIMIT 10;"

  Favorite apps example:
    sqlite3 -column -header .favorite_apps.db \
      "SELECT app_id, position FROM app_item ORDER BY position ASC;"

  Key interpretation:
    `position = 0` in `app_item` means most recently used app.
:::

:::scenario{id="task-5" level="intermediate"}
title: "Task 5 — Mount the Echo Dot E01 and Extract Wi-Fi / Wake-Word Artifacts"
goal: "Open the Echo Dot image, locate its userdata partition, and read Wi-Fi and wake-word configuration files."
hint: "FTK Imager opens the E01 directly and shows a `userdata` partition with `NONAME [ext4]`. On Kali, first mount the E01 with `ewfmount`, then inspect partitions with `mmls`, and mount the userdata ext4 partition read-only using an offset or a mapped partition device. Once mounted, plain-text files like `wpa_supplicant.conf`, `networkHistory.txt`, and `op.cfg.json` can be read directly."
command: "sudo mkdir -p /mnt/ewf /mnt/lab15_echo && sudo ewfmount Lab15-2.E01 /mnt/ewf && mmls /mnt/ewf/ewf1"
expected_output: |
  Kali — E01 workflow:
    sudo mkdir -p /mnt/ewf /mnt/lab15_echo
    sudo ewfmount Lab15-2.E01 /mnt/ewf
    mmls /mnt/ewf/ewf1

    DOS Partition Table
    Offset Sector: 0
    Units are in 512-byte sectors
      Slot      Start        End          Length       Description
      000:000   0000002048   0002506751   0002504704   Linux (0x83)   ← userdata candidate

    # Example mount with offset
    sudo mount -o ro,loop,offset=$((2048*512)) /mnt/ewf/ewf1 /mnt/lab15_echo

  Windows FTK Imager:
    Lab15-2.E01 > userdata (16) [1263MB] > NONAME [ext4] > [root]

  After mount, inspect these paths:
    /mnt/lab15_echo/misc/wifi/wpa_supplicant.conf
    /mnt/lab15_echo/misc/wifi/networkHistory.txt
    /mnt/lab15_echo/davs/wakeword/.../op.cfg.json
:::

:::scenario{id="task-6" level="intermediate"}
title: "Task 6 — Parse Echo Wi-Fi, Wake-Word, and Account Evidence"
goal: "Extract identifying Wi-Fi details, wake-word settings, and the linked account display name from the Echo image."
hint: "The lab highlights three high-value Echo artifacts: `wpa_supplicant.conf` for SSID/passphrase/serial/model info, `networkHistory.txt` for BSSID/auth/gateway history, and `op.cfg.json` for the wake word. Export `map_data_storage_v2.db` and query the `accounts` table with `sqlite3` to recover the account-linked display name."
command: "grep -E 'ssid=|psk=|serial|model|last_connected|full_biscuit' /mnt/lab15_echo/misc/wifi/wpa_supplicant.conf && sqlite3 -column -header ~/cases/FOR_LAB_015/Exports/Lab15_2/map_data_storage_v2.db \"SELECT * FROM accounts;\""
expected_output: |
  Wi-Fi config:
    device_name=full_biscuit
    serial=G090LF118173117U
    model=Echo Dot
    ssid=\"HomeNet\"
    psk=\"CorrectHorseBatteryStaple\"
    last_connected=1608192487

  Convert last_connected:
    date -d @1608192487
    Wed Dec 16 15:28:07 UTC 2020

  Network history highlights:
    BSSID=aa:bb:cc:dd:ee:ff
    ValidatedInternetAccess=true
    KeyMgmt=WPA-PSK
    GatewayMAC=11:22:33:44:55:66
    BSSID_2G=aa:bb:cc:dd:ee:ff
    BSSID_5G=aa:bb:cc:dd:ee:00

  Wake-word config:
    jq '.wakeWord, .stopWord, .sleepAfterMinutes' /mnt/lab15_echo/davs/wakeword/.../op.cfg.json
    "COMPUTER"
    "STOP"
    5

  Echo account data:
    sqlite3 -column -header map_data_storage_v2.db "SELECT display_name FROM accounts;"
    display_name
    hera13

  Investigative value:
    Wi-Fi details can place the device near a known router.
    The wake word can help attribute familiarity with the device.
    The account name ties the hardware to a cloud-backed user profile.
:::

---

## Full Kali Workflow

End-to-end example for both IoT images:

```bash
# --- SMARTWATCH IMAGE ---

# 1. Mount raw ext4 image read-only
sudo mkdir -p /mnt/lab15_watch
sudo mount -o ro,loop Lab15-1.img /mnt/lab15_watch

# 2. Review synced media and thumbnail cache
find /mnt/lab15_watch/media -maxdepth 3 -type f | sort

# 3. Export SQLite artifacts
mkdir -p ~/cases/FOR_LAB_015/Exports/Lab15_1
cp /mnt/lab15_watch/apps/com.samsung.shealth/data/.shealth.db* \
   ~/cases/FOR_LAB_015/Exports/Lab15_1/
cp /mnt/lab15_watch/apps/com.samsung.wemail/data/dbspace/.wemail.db* \
   ~/cases/FOR_LAB_015/Exports/Lab15_1/
cp /mnt/lab15_watch/apps/com.samsung.w-launcher-app/data/.favorite_apps.db* \
   ~/cases/FOR_LAB_015/Exports/Lab15_1/

# 4. Query profile and health data
sqlite3 -column -header ~/cases/FOR_LAB_015/Exports/Lab15_1/.shealth.db \
  "SELECT datetime(timestamp/1000,'unixepoch') AS created_at,* FROM shealth_profile;"

sqlite3 -column -header ~/cases/FOR_LAB_015/Exports/Lab15_1/.shealth.db \
  "SELECT datetime(start_time/1000,'unixepoch') AS start_time,
          walk_step_count, run_step_count, distance, calorie
   FROM shealth_pedometer_history LIMIT 20;"

# 5. Query email notification and app recency data
sqlite3 -column -header ~/cases/FOR_LAB_015/Exports/Lab15_1/.wemail.db \
  "SELECT datetime(mDateTime,'unixepoch') AS seen_at,
          mTitle,mTextMessage,mEmailAddr,mDisplayName
   FROM EmailNotiInfo LIMIT 20;"

sqlite3 -column -header ~/cases/FOR_LAB_015/Exports/Lab15_1/.favorite_apps.db \
  "SELECT app_id,position FROM app_item ORDER BY position ASC;"

# --- ECHO DOT IMAGE ---

# 6. Mount the E01 container and inspect partitions
sudo mkdir -p /mnt/ewf /mnt/lab15_echo
sudo ewfmount Lab15-2.E01 /mnt/ewf
mmls /mnt/ewf/ewf1

# 7. Mount the userdata ext4 partition (replace OFFSET with the real start sector * 512)
sudo mount -o ro,loop,offset=$((OFFSET*512)) /mnt/ewf/ewf1 /mnt/lab15_echo

# 8. Export account database
mkdir -p ~/cases/FOR_LAB_015/Exports/Lab15_2
cp /mnt/lab15_echo/data/com.amazon.imp/databases/map_data_storage_v2.db* \
   ~/cases/FOR_LAB_015/Exports/Lab15_2/

# 9. Review Wi-Fi and wake-word artifacts
less /mnt/lab15_echo/misc/wifi/wpa_supplicant.conf
less /mnt/lab15_echo/misc/wifi/networkHistory.txt
jq . /mnt/lab15_echo/davs/wakeword/*/op.cfg.json

# 10. Query linked account
sqlite3 -column -header ~/cases/FOR_LAB_015/Exports/Lab15_2/map_data_storage_v2.db \
  "SELECT * FROM accounts;"
```

---

## Key Concepts

### ext4 on IoT Devices

Many embedded and Android-based devices use `ext4`, not NTFS or FAT. That means:

- The image is often Linux-style and can be mounted directly on Kali
- Folder names like `apps`, `media`, `data`, and `misc` matter
- Text configuration files and SQLite databases are common evidence sources

### SQLite Journals Matter

IoT apps often store data in SQLite with a journal file beside it:

| Main File | Journal File | Why it matters |
|----------|--------------|----------------|
| `.shealth.db` | `.shealth.db-journal` | Recent transactions may live here |
| `.wemail.db` | `.wemail.db-journal` | Notification changes may not be fully committed |
| `map_data_storage_v2.db` | `map_data_storage_v2.db-journal` | Account changes may persist in journal data |

Always export both.

### Unix Epoch vs Java Epoch

This lab uses both time formats:

| Format | Example | Convert With |
|--------|---------|--------------|
| Unix epoch (seconds) | `1608192487` | `datetime(column,'unixepoch')` |
| Java epoch (milliseconds) | `1608192487000` | `datetime(column/1000,'unixepoch')` |

If the converted date looks wildly wrong, you probably used the wrong epoch type.

### Wi-Fi and Wake-Word Artifacts

IoT devices preserve behavioral evidence:

- `SSID` and passphrase tie the device to a known access point
- `BSSID` and gateway MAC tie it to a specific router
- `last_connected` anchors the device near that network at a specific time
- Wake word and stop word show user-specific configuration and familiarity

---

:::quiz{id="quiz-1"}
Q: What does the presence of an `ext4` file system in the smartwatch image most strongly suggest?
- [ ] The device runs Windows CE
- [x] The device is Linux/Android-based
- [ ] The image is corrupted
- [ ] The device only stores cloud data and no local artifacts
:::

:::quiz{id="quiz-2"}
Q: Why is the hidden `.thumb` folder valuable in an IoT investigation?
- [ ] It stores the device password in plain text
- [x] It may retain thumbnails of synced or deleted media files
- [ ] It automatically contains GPS coordinates for every file
- [ ] It only stores firmware updates
:::

:::quiz{id="quiz-3"}
Q: In the smartwatch `app_item` table, what does `position = 0` indicate?
- [ ] The app is disabled
- [ ] The app is deleted
- [x] The app was the most recently used
- [ ] The app is hidden from the launcher
:::

:::quiz{id="quiz-4"}
Q: Which Echo Dot file is most likely to contain the SSID and Wi-Fi passphrase?
- [ ] `map_data_storage_v2.db`
- [x] `wpa_supplicant.conf`
- [ ] `op.cfg.json`
- [ ] `favorite_apps.db`
:::

:::quiz{id="quiz-5"}
Q: Why should you export an SQLite journal file together with the main `.db` file?
- [ ] The journal file is required to identify the file type
- [ ] The main database cannot be opened without it in any tool
- [x] Recent or uncommitted transactions may still be present there
- [ ] The journal file stores only thumbnails
:::

:::quiz{id="quiz-6"}
Q: Which SQL expression correctly converts a Java epoch timestamp in milliseconds to readable time?
- [ ] `datetime(column_name, 'unixepoch')`
- [x] `datetime(column_name/1000, 'unixepoch')`
- [ ] `time(column_name*1000, 'utc')`
- [ ] `strftime('%s', column_name)`
:::

---

## Quick Reference

| Task | Linux / Kali | Windows / GUI |
|------|--------------|---------------|
| Mount raw smartwatch image | `mount -o ro,loop Lab15-1.img /mnt/lab15_watch` | FTK Imager > Add Evidence Item |
| Mount E01 Echo image | `ewfmount Lab15-2.E01 /mnt/ewf` | FTK Imager opens `.E01` directly |
| Inspect partitions | `mmls /mnt/ewf/ewf1` | Evidence Tree partition list |
| Export DB files | `cp source.db* ~/cases/.../Exports/` | Right-click > Export Files |
| View media / thumbnails | `find .../media ...` | Evidence Tree + View pane |
| Open DBs | `sqlite3 -column -header file.db` | DB Browser for SQLite |
| Convert Unix epoch | `datetime(col,'unixepoch')` | DB Browser display format: Unix epoch to date |
| Convert Java epoch ms | `datetime(col/1000,'unixepoch')` | DB Browser display format: Java epoch (milliseconds) |
| Read Wi-Fi config | `less wpa_supplicant.conf` | FTK text view |
| Read wake-word JSON | `jq . op.cfg.json` | FTK text view |
