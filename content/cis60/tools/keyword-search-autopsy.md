# Keyword Search & Analysis with Autopsy

Finding relevant data inside large forensic images requires systematic search techniques. Keyword searching dramatically reduces examination time and surfaces evidence that would otherwise be buried in gigabytes of data. This lab covers how to create a case in Autopsy, configure the Keyword Search ingest module, run all three search types, and interpret the results — alongside equivalent command-line methods for Linux.

## Overview

**Autopsy** is a free, open-source digital forensics platform built on top of **The Sleuth Kit (TSK)**. It performs analysis, reports findings, and preserves results in a forensically sound format. The key advantages over raw command-line tools:

- **Cases** isolate evidence and prevent cross-contamination across investigations
- **Ingest Modules** automate extraction of file types, hashes, email, keywords, and more
- **Keyword Search Index** pre-indexes all text in the image so searches run in seconds
- **Ingest Messages** display live hits as analysis runs
- **Tree-table pane** lets you drill from result → source file → highlighted context

The evidence file used in this lab: `FOR_LAB_006.E01` (an EnCase-format FEF)

---

## Tool Comparison

| Task | Autopsy (GUI) | Linux CLI |
|------|--------------|-----------|
| Create a case | Case > New Case | Create a directory; note case number manually |
| Add a FEF | Case > Add Data Source > Disk Image or VM file | `mmls image.E01` to inspect |
| Run keyword search at ingest | Keyword Search Ingest Module | `bulk_extractor -o output/ image.E01` |
| Exact match search | Keyword Search > Exact Match | `grep -r --include="*" 'term' /mnt/evidence/` |
| Substring search | Keyword Search > Substring Match | `grep -ri 'partial' /mnt/evidence/` |
| Regular expression search | Keyword Search > Regular Expression | `grep -rE 'pattern.*' /mnt/evidence/` |
| Index search (post-ingest) | Keyword Search toolbar > type term | `grep -rF 'term' /mnt/evidence/` |
| Extract all strings | Keyword Search > String Extraction | `strings -a image.E01 > strings.txt` |
| View keyword hits in context | Click hit → Indexed Text tab | `grep -C 5 'term' file.txt` |
| Filter known-good files | NSRL Hash Lookup module | `hashdeep -r -k nsrl.txt /mnt/evidence/` |
| Save results | Save Table as CSV | Redirect `grep` output to a file |

---

## Autopsy Interface Reference

| Element | Location | Purpose |
|---------|----------|---------|
| Case menu | Top menu bar | New/open/close cases, add data sources |
| Add Data Source | Toolbar button | Add FEF, local disk, or logical files to the case |
| Keyword Lists | Toolbar button | Manage saved keyword lists; configure ingest-time search |
| Keyword Search | Toolbar button (right) | Ad-hoc index search on an already-ingested image |
| Data Sources tree | Left pane | Browse the ingested image by volume/directory |
| Views > File Types | Left pane | Filter files by extension or MIME type |
| Views > Deleted Files | Left pane | Show files marked deleted but still recoverable |
| Results > Keyword Hits | Left pane | All hits from ingest-time keyword searches |
| Results > Extracted Content | Left pane | Emails, accounts, installed programs, etc. |
| Listing pane | Center | File list for selected tree node |
| View pane (bottom) | Hex / Text / Application / File Metadata / Results tabs | Content and metadata for selected file |
| Ingest Messages (envelope icon) | Toolbar | Live stream of hits as ingest runs |

---

## Keyword Search Types

| Type | Behavior | Use When | Example |
|------|----------|----------|---------|
| **Exact Match** | Case-insensitive, matches the term with no extra characters attached | You know the precise string you're looking for | `hackersteam` → 1 hit |
| **Substring Match** | Case-insensitive, matches anywhere the term appears inside a larger string | You want any word containing the term | `hack` → 1959 hits |
| **Regular Expression** | Matches a pattern with wildcards and character classes | You need flexible pattern matching across variants | `hackerst.*` → 4 hits across multiple files |

> **`*` in Autopsy regex** means "match the preceding character zero or more times" — so `hack*` matches `hac`, `hack`, `hackk`, etc. Use `hack.*` to match "hack" followed by anything.

All search types are **case-insensitive** by default.

---

## Default Keyword Lists (Built-in)

Autopsy ships with pre-built keyword lists. **Uncheck these during ingest** unless they are relevant to your case — leaving them enabled generates noise:

| Built-in List | What it finds |
|---------------|--------------|
| Phone Numbers | Common phone number patterns |
| IP Addresses | IPv4 address patterns |
| Email Addresses | Email format matches |
| URLs | Web address patterns |
| Credit Card Numbers | Credit card number patterns |

---

:::command-builder{id="autopsy-keyword-builder"}
tool_name: Autopsy Keyword Search
target_placeholder: "search_term"
scan_types:
  - name: "Exact Match"
    flag: "Exact Match radio button"
    desc: "Finds only the exact string — no extra characters before or after. Best for unique identifiers like MAC addresses, case numbers, or usernames."
  - name: "Substring Match"
    flag: "Substring Match radio button"
    desc: "Finds the term anywhere inside a longer word or string. Use for broad discovery but expect many false positives."
  - name: "Regular Expression"
    flag: "Regular Expression radio button"
    desc: "Matches a pattern. Use .* for 'anything', \\d for digits, [a-z] for character ranges."
options:
  - name: "Save search results"
    flag: "Save search results checkbox"
    desc: "Saves results to the tree pane under Single Regular Expression Search. Uncheck only for throwaway searches."
  - name: "Restrict to selected data sources"
    flag: "Restrict search to the selected data sources checkbox"
    desc: "Limits the search to the currently selected FEF when multiple images are loaded."
:::

---

:::command-builder{id="linux-grep-builder"}
tool_name: grep
target_placeholder: "search_term"
scan_types:
  - name: "Exact match in mounted image"
    flag: "-r --include='*' -w 'term' /mnt/evidence/"
    desc: "Recursively search all files for whole-word exact matches"
  - name: "Substring match"
    flag: "-ri 'partial' /mnt/evidence/"
    desc: "Case-insensitive recursive search for any occurrence of the substring"
  - name: "Regular expression"
    flag: "-rE 'hack.+steam' /mnt/evidence/"
    desc: "Extended regex: find 'hack' followed by one or more chars then 'steam'"
  - name: "Show 5 lines of context"
    flag: "-C 5 'term' file.txt"
    desc: "Display 5 lines before and after each match for context"
  - name: "Count hits per file"
    flag: "-rc 'term' /mnt/evidence/ | grep -v ':0'"
    desc: "Show only files with at least one hit and the count"
  - name: "Search raw image strings"
    flag: "strings -a image.E01 | grep -i 'term'"
    desc: "Extract all printable strings from the raw image then filter"
options:
  - name: "Case insensitive"
    flag: "-i"
    desc: "Ignore uppercase/lowercase distinctions"
  - name: "Recursive"
    flag: "-r"
    desc: "Search all files in directory and subdirectories"
  - name: "Show filename"
    flag: "-H"
    desc: "Always print the filename with each match"
  - name: "Line number"
    flag: "-n"
    desc: "Show the line number of each match"
  - name: "Save output"
    flag: "> results.txt"
    desc: "Redirect all grep output to a file for reporting"
:::

---

:::scenario{id="task-1" level="beginner"}
title: "Task 1 — Create a Case and Load the Evidence File"
goal: "Create a new Autopsy case, fill in required metadata, and add the FEF as a data source."
hint: "Every investigation in Autopsy requires a case. The case stores all analysis results and prevents evidence from different investigations mixing together. The case number and examiner name become part of the final report."
command: "Case > New Case (Ctrl+N)"
expected_output: |
  Case creation wizard:
    Case Name: FOR_LAB_006_KWS
    Base Directory: /home/csi/Cases  (default)
    Case Type: Single-user

  Optional Information:
    Number: NDG006
    Examiner Name: [your name]
    Phone: (555)555-555
    Email: your@email.com

  Add Data Source:
    Source Type: Disk Image or VM file
    Path: /home/csi/Desktop/Evidence Files/FOR_LAB_006/FOR_LAB_006.E01
    Time zone: GMT-5:00 America/New_York  (adjust to match evidence)
    Sector size: Auto Detect

  Key point:
    Set the time zone to match where the evidence was collected.
    If unknown, use the local time zone of the investigating lab.
:::

:::scenario{id="task-2" level="beginner"}
title: "Task 2 — Configure the Keyword Search Ingest Module"
goal: "Enable only the Keyword Search ingest module, create a custom keyword list, and add exact, substring, and regex search terms."
hint: "Ingest modules extract different artifact types. Enabling too many slows analysis. For keyword-focused investigations, enable only Keyword Search. Disable all built-in keyword lists (Phone Numbers, IP Addresses, Email Addresses, URLs, Credit Card Numbers) to avoid noise."
command: "Keyword Search checkbox > Global Settings > New List"
expected_output: |
  Ingest module selection:
    [✓] Keyword Search  ← enable this only
    [ ] Recent Activity
    [ ] Hash Lookup
    [ ] File Type Identification
    ... (all others unchecked)

  Built-in keyword lists (UNCHECK ALL):
    [ ] Phone Numbers
    [ ] IP Addresses
    [ ] Email Addresses
    [ ] URLs
    [ ] Credit Card Numbers

  New keyword list name: FOR_LAB_006_Keywords

  Keywords added (New Keywords button):
    Lookatlan       → Exact Match
    0010a4933e09    → Exact Match
    yahoo           → Exact Match
    hackersteam     → Exact Match
    hack            → Substring Match
    hack*           → Regular Expression

  String Extraction tab:
    [✓] Enable UTF16LE and UTF16BE string extraction
    [✓] Enable UTF8 text extraction
    [ ] Enable OCR (Windows 64-bit only)

  General tab:
    [✓] Do not add files in NSRL to keyword index
    [✓] Show Keyword Preview in Keyword Search Results
    Results update: 5 minutes (default)
:::

:::scenario{id="task-3" level="intermediate"}
title: "Task 3 — Review Ingest Results and Compare Search Types"
goal: "Examine keyword hits for each search type and understand why Exact Match and Substring Match produce very different result volumes."
hint: "After ingest completes (or above 30%), expand the FOR_LAB_006_Keywords list in Results > Keyword Hits. The number in parentheses after each term is the hit count. Vague substring terms like 'hack' produce thousands of hits; specific exact terms like 'hackersteam' produce one."
command: "Results > Keyword Hits > FOR_LAB_006_Keywords > [click each term]"
expected_output: |
  Hit counts per keyword:
    0010a4933e09   (2)   → Exact Match   — MAC address or ID found in 2 files
    Lookatlan      (2)   → Exact Match   — username found in 2 files
    yahoo          (55)  → Exact Match   — email domain found in 55 files
    hackersteam    (1)   → Exact Match   — specific term found in 1 file (channels.txt)
    hack           (1959)→ Substring     — too broad; includes "backpack", "shack", etc.
    hack*          (573) → Regex         — matches hac, hack, hackk... still broad

  Expanding hack* shows matched variants:
    hac   (322)
    hack  (248)
    hackk (3)

  Investigating hackersteam (1 hit):
    Source file: channels.txt
    Location: /vol2/Program Files/mIRC/...
    Keyword Preview: highlighted "hackersteam" in IRC channel list
    Context: Autopsy shows the term in the Indexed Text tab

  Key takeaway:
    hack         → 1959 hits (most are false positives)
    hackersteam  → 1 hit  (specific, actionable)
    Prefer specific terms; use broad terms only for initial discovery.
:::

:::scenario{id="task-4" level="intermediate"}
title: "Task 4 — Use Ad-Hoc Index Search for a New Regular Expression"
goal: "Run a post-ingest index search using the Keyword Search toolbar to search for a regex without re-running the full ingest."
hint: "The Keyword Search toolbar button (top right) runs against the pre-built index — it is much faster than re-running ingest. 'Save search results' must be checked for results to persist in the tree. The index shows how many files were indexed (e.g. 18,555 files)."
command: "Toolbar > Keyword Search > type hackerst.* > Regular Expression > Search"
expected_output: |
  Search parameters:
    Term: hackerst.*
    Type: Regular Expression
    [✓] Save search results

  Files indexed: 18,555

  Results (4 files):
    channels.txt        → /vol2/Program Files/mIRC/...        → match: hackerstone 1
    NTpasslist.txt      → /vol2/My Documents/EXPLOIT/...
    folders.sts         → /vol2/Documents and Settings/...
    Unalloc_20093_...   → unallocated space

  In channels.txt, matched terms include:
    hackersteam
    hackerstone 1
    (multiple variants across 40 pages)

  Saved to tree pane under:
    Results > Keyword Hits > Single Regular Expression Search

  Key takeaway:
    hackerst.*  finds ALL words starting with "hackerst"
    This is more useful than hack* when you know the first 7 characters
    Unallocated space hits are especially valuable — data was deleted but not overwritten
:::

---

## Full Linux Workflow

End-to-end keyword search on a mounted forensic image:

```bash
# 1. Mount the evidence image read-only (after identifying partition offset)
sudo mkdir -p /mnt/evidence
sudo mount -o ro,loop,offset=$((63*512)) FOR_LAB_006.E01 /mnt/evidence

# 2. Extract all printable strings from the raw image
strings -a FOR_LAB_006.E01 > /tmp/all_strings.txt

# 3. Exact match — find a specific term
grep -r -i -w 'hackersteam' /mnt/evidence/ 2>/dev/null

# 4. Substring match — broader sweep
grep -r -i 'hack' /mnt/evidence/ 2>/dev/null | wc -l
# Count results to gauge whether the term is too broad

# 5. Regular expression — variants of a root word
grep -r -E 'hackerst[a-z]+' /mnt/evidence/ 2>/dev/null

# 6. Search raw strings (catches unallocated space)
grep -i 'hackerst' /tmp/all_strings.txt

# 7. Find a MAC address or hardware ID across all files
grep -r '0010a4933e09' /mnt/evidence/ 2>/dev/null

# 8. Save results with filename and line number for reporting
grep -r -i -n 'hackersteam' /mnt/evidence/ 2>/dev/null > keyword_hits.txt

# 9. Automated pattern extraction with bulk_extractor
bulk_extractor -o bulk_output/ -E email -E url -E find -S find_word=hackersteam \
  FOR_LAB_006.E01

# 10. Use The Sleuth Kit to search within specific files
fls -r FOR_LAB_006.E01 | grep -i 'channels'
icat FOR_LAB_006.E01 <inode_number> | strings | grep -i 'hackerst'
```

---

## Key Concepts

### Why Cases Matter

Autopsy organizes all analysis inside a **case**. Each case has:
- A unique name and number for chain-of-custody documentation
- An examiner record (name, phone, email) for the report
- Isolated storage so results from different investigations never mix
- A portable format that can be archived and reopened later

Never add evidence from different investigations to the same case.

### Ingest Modules

Autopsy's **ingest modules** run automatically when a data source is added. Each module extracts a different artifact class:

| Module | What it extracts |
|--------|-----------------|
| Keyword Search | Indexes all text; runs keyword lists |
| Hash Lookup | Compares file hashes against NSRL and custom databases |
| File Type Identification | Classifies files by content (not just extension) |
| Recent Activity | Windows registry, browser history, prefetch |
| Email Parser | Extracts email messages from PST/MBOX files |
| Exif Parser | Extracts GPS, camera, and timestamp metadata from images |
| Interesting Files Identifier | Flags files matching custom rules |

Enable only what you need — each enabled module adds to total ingest time.

### The Keyword Index

When the Keyword Search module runs, it builds a **text index** of every searchable file in the image. This index is stored in the case folder and enables sub-second ad-hoc searches via the Keyword Search toolbar after ingest completes. The index shows a **Files indexed** count (e.g. 18,555) in the search dropdown.

Files excluded from the index by default when NSRL filtering is enabled: known operating system files, common applications — anything whose hash matches the National Software Reference Library.

### Choosing the Right Search Type

```
                   Specificity →
Broad                                       Narrow
  Substring     Regex            Exact
  "hack"        "hack.*steam"    "hackersteam"
  1959 hits     ~4 hits          1 hit
```

**Start specific, widen if needed** — not the reverse. A broad term like `hack` with 1959 hits will cost hours to review. A specific term like `hackersteam` with 1 hit is immediately actionable.

**Good keyword candidates for investigations:**
- Usernames and handles
- Unique identifiers (MAC addresses, case numbers, serial numbers)
- Specific tool names or IRC channels
- Known email addresses
- Unique phrases from ransom notes or threat communications

### Ambiguous vs. Refined Keywords

| Keyword | Type | Hits | Problem |
|---------|------|------|---------|
| `hack` | Substring | 1959 | Matches "backpack", "shack", "Thacker", system DLLs |
| `hack*` | Regex | 573 | Still matches too many variants |
| `hackersteam` | Exact | 1 | Unique — directly actionable |
| `hackerst.*` | Regex | 4 | Specific root, flexible suffix — good balance |

The right keyword is **specific enough to exclude false positives** but **flexible enough to catch variants** (e.g., `Look@lan` would be missed by `Lookatlan` Exact Match — consider Substring for email-style usernames).

### Unallocated Space Hits

When a keyword hit appears in an **unallocated space file** (e.g. `Unalloc_20093_351232_...`), it means:
- The file containing that term was **deleted**
- The sectors were not yet overwritten
- The data is still recoverable and forensically significant

Unallocated hits are often the most valuable — they prove data existed even after deletion attempts.

### NSRL and False-Positive Reduction

The **National Software Reference Library** is a database of hashes for known legitimate software files. Enabling NSRL filtering in the Hash Lookup module prevents the keyword index from including operating system files and common applications — significantly reducing false positives and speeding up index creation.

---

:::quiz{id="quiz-1"}
Q: Why does Autopsy require creating a case before loading evidence?
- [ ] To encrypt the evidence file automatically
- [x] To isolate evidence and prevent cross-contamination between investigations
- [ ] To automatically hash the evidence file
- [ ] To restrict which ingest modules can run
:::

:::quiz{id="quiz-2"}
Q: A search for "hack" returns 1959 hits while "hackersteam" returns 1 hit. What describes the problem with "hack"?
- [ ] It is using the wrong search type
- [x] It is too ambiguous — it matches unrelated words like "backpack", causing many false positives
- [ ] Substring Match is broken in Autopsy
- [ ] The keyword list was not saved properly
:::

:::quiz{id="quiz-3"}
Q: Which Autopsy keyword search type should you use to find all words that begin with "hackerst" regardless of what follows?
- [ ] Exact Match with "hackerst"
- [ ] Substring Match with "hackerst"
- [x] Regular Expression with "hackerst.*"
- [ ] Substring Match with "hackerst*"
:::

:::quiz{id="quiz-4"}
Q: A keyword hit appears in a file named `Unalloc_20093_351232_1683209728`. What does this tell you?
- [ ] The file is currently open by the operating system
- [ ] The file is a system DLL and should be ignored
- [x] The data was found in unallocated space — the original file was deleted but the sectors were not yet overwritten
- [ ] The keyword index failed to parse the file correctly
:::

:::quiz{id="quiz-5"}
Q: What is the purpose of checking "Do not add files in NSRL to keyword index" in the Keyword Search Global Settings?
- [ ] It speeds up the search by skipping encrypted files
- [ ] It prevents Autopsy from indexing deleted files
- [x] It excludes known legitimate OS and application files from the index, reducing false positives
- [ ] It limits searches to documents only
:::

:::quiz{id="quiz-6"}
Q: What is the difference between running a search via the Keyword Lists ingest module versus the Keyword Search toolbar button?
- [ ] The toolbar search is less accurate than the ingest module
- [x] The ingest module indexes the image during loading; the toolbar button searches the pre-built index ad-hoc after ingest — making it much faster for additional searches
- [ ] The toolbar search only works on Exact Match terms
- [ ] The ingest module searches unallocated space while the toolbar does not
:::

---

## Quick Reference

| Task | Autopsy GUI | Linux CLI |
|------|-------------|-----------|
| Create a case | Case > New Case | Create directory; record case number manually |
| Load FEF | Case > Add Data Source | `mmls image.E01` |
| Enable keyword search | Keyword Search ingest module | Enable before analysis step |
| Add keyword list | Global Settings > New List > New Keywords | Write terms to `keywords.txt` |
| Exact match | Exact Match radio | `grep -rw 'term'` |
| Substring match | Substring Match radio | `grep -ri 'partial'` |
| Regex match | Regular Expression radio | `grep -rE 'pattern'` |
| Post-ingest search | Keyword Search toolbar | `grep` on mounted image |
| Search strings | String Extraction settings | `strings image.E01 \| grep` |
| View hit in context | Click hit → Indexed Text tab | `grep -C 5 'term' file` |
| Save results | Save Table as CSV | `grep ... > results.txt` |
| Filter known files | Hash Lookup > NSRL | `hashdeep -k nsrl.txt` |
| Check deleted files | Views > Deleted Files | `fls -r -d image.E01` |
