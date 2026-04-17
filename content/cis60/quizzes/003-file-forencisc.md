---
title: CIS 60 – File Systems, Windows and Methodology Quiz
---

## Q1 [mcq_single, 5pts]
Why is a forensic clone preferred over examining the original drive directly?

- [ ] It automatically recovers passwords from the system
- [x] It allows the examiner to work on a copy while preserving the original evidence
- [ ] It removes the need for hashing
- [ ] It guarantees encrypted files will be readable

## Q2 [mcq_single, 5pts]
Which of the following best describes unallocated space on a storage device?

- [ ] Space reserved only for the operating system kernel
- [x] Space not currently assigned to active files and where deleted file data may remain
- [ ] The area that stores only metadata such as permissions
- [ ] A hidden partition used only for backups

## Q3 [mcq_single, 5pts]
What happens during Windows hibernation?

- [ ] Open documents are deleted and the system powers off
- [ ] The system stays powered on and keeps all state only in RAM
- [x] RAM contents are written to `hiberfil.sys` and the system powers off
- [ ] The Registry is copied to the recycle bin before shutdown

## Q4 [mcq_single, 5pts]
Which Registry key is a live link to the current user’s SID under `HKEY_USERS`?

- [ ] `HKEY_LOCAL_MACHINE`
- [ ] `HKEY_CLASSES_ROOT`
- [x] `HKEY_CURRENT_USER`
- [ ] `HKEY_CURRENT_CONFIG`

## Q5 [mcq_single, 5pts]
Why does an acquired Registry hive image not contain `CurrentControlSet` as a stored key?

- [ ] It is deleted whenever Windows shuts down
- [x] It is ephemeral and derived at runtime rather than stored directly in the hive file
- [ ] It only exists on FAT32 systems
- [ ] It is stored only in the pagefile

## Q6 [mcq_single, 5pts]
Which Registry artifact is commonly used to show objects or programs a user accessed?

- [ ] `USBSTOR`
- [ ] `TimeZoneInformation`
- [x] `UserAssist`
- [ ] `HiveList`

## Q7 [mcq_single, 5pts]
What type of evidence can the `USBSTOR` Registry key help establish?

- [ ] Which browser bookmarks were synced to the machine
- [ ] Which user changed the system time zone
- [x] Which USB storage devices were connected to the computer
- [ ] Which restore points were deleted

## Q8 [mcq_single, 5pts]
Which action will typically bypass the Recycle Bin?

- [ ] Deleting a file from Windows Explorer normally
- [x] Pressing `Shift+Delete`
- [ ] Moving a file to another folder on the same drive
- [ ] Renaming a file and then closing Explorer

## Q9 [mcq_single, 5pts]
Which set of timestamps is commonly used in file-system forensics to describe file activity?

- [ ] PID, SID, RID, GUID
- [x] Created, Modified, Accessed, and Record/metadata change times
- [ ] Source, Destination, Port, Protocol
- [ ] Encrypt, Compress, Archive, Hidden

## Q10 [mcq_single, 5pts]
What is the correct order-of-volatility principle during evidence collection?

- [ ] Collect hard disks first because they are easiest to hash
- [x] Collect the most volatile evidence first, such as CPU state, routing data, and RAM
- [ ] Collect only powered-off devices first
- [ ] Collect archival media before live systems

## Q11 [mcq_single, 5pts]
Why is live acquisition sometimes necessary?

- [ ] It is always faster than imaging a powered-off system
- [ ] It avoids the need for documentation
- [x] It may capture volatile data in RAM such as processes, passwords, and network state
- [ ] It guarantees the suspect cannot claim malware was involved

## Q12 [mcq_single, 5pts]
What is the primary purpose of computing hashes such as MD5 or SHA-1 on forensic images?

- [ ] To compress evidence files for storage
- [ ] To identify the operating system automatically
- [x] To verify that copied evidence remains identical to the original
- [ ] To determine whether a file is deleted or allocated

## Q13 [mcq_single, 5pts]
Which of the following is the best documentation practice at a digital crime scene?

- [ ] Write only conclusions, not observations
- [ ] Avoid photos if you are already taking notes
- [x] Record precise observations chronologically and photograph the scene before disturbing it
- [ ] Rely on memory for minor details to save time

## Q14 [mcq_single, 5pts]
What is the best description of chain of custody?

- [ ] A list of all files found in the Recycle Bin
- [ ] The order in which Registry hives load into memory
- [x] The documented history of who handled evidence, when, and what was done to it
- [ ] A timeline of every user login on the system

## Q15 [mcq_single, 5pts]
What should a good final forensic report include in addition to tool-generated output?

- [ ] Only screenshots of suspicious files
- [x] A clear narrative of actions taken and a plain-English summary for the audience
- [ ] Only raw hashes and no explanation
- [ ] Speculation about what probably happened even if unsupported
