# CIS 60 – Lecture 2 Notes
**Legal Aspects of Forensics and Being an Expert Witness**

---

## Today's Topics

- Guest Speaker: Legal Expert Witness in Practice
- Computer Forensics Overview
- Fact Witness vs. Expert Witness
- Qualifying as an Expert
- Incident Response vs. Computer Forensics

---

## Guest Speaker: Haydee Durand

**Kivu Consulting**
Digital forensics and incident response practitioner with experience testifying as an expert witness.

---

## Part 1 – Legal Expert Witness

### Fact Witness vs. Expert Witness

| Type | Role |
|------|------|
| **Fact Witness** | Testifies only to what they personally observed |
| **Expert Witness** | Offers opinions and analysis based on specialized knowledge |

A fact witness cannot speculate or offer opinions — they can only say what they saw. An expert witness is specifically retained to interpret evidence and explain technical matters to judge and jury.

### Qualifying as an Expert

To testify as an expert, courts evaluate:

- **Education** — relevant degrees, certifications
- **Experience** — years in the field, types of cases worked
- **Publications and Training** — authored work, continuing education
- **Prior Testimony** — previous accepted qualifications

The opposing attorney will challenge your qualifications. Your CV and case documentation must be thorough and accurate.

### What Experts Must Provide

1. **Curriculum Vitae (CV)** — complete professional history
2. **Summary of Findings** — written report of analysis and conclusions
3. **Methodology** — how the analysis was conducted, tools used, steps taken

Courts require that expert opinions be based on:
- Sufficient facts or data
- Reliable methods and principles
- Proper application of those methods to the facts of the case

### Depositions and Court Testimony

- **Deposition** — sworn testimony taken before trial, used by both sides
- **Direct examination** — questioned by the attorney who retained you
- **Cross-examination** — questioned by opposing counsel, often adversarial

### General Advice for Court Testimony

- Know your report cold — opposing counsel will probe inconsistencies
- Answer only what is asked — do not volunteer information
- If you do not know something, say so
- Maintain composure; emotional reactions undermine credibility
- Document everything you did, including dead ends
- Never overstate certainty — "consistent with" is not the same as "proves"

---

## Part 2 – Computer Forensics Overview

### Definition

> Computer forensics is the application of investigative and analytical techniques to collect and preserve evidence from digital devices in a way that is legally admissible.

**Digital artifacts** found during an investigation can include:
- Files (documents, images, executables)
- Metadata (created/modified timestamps, author fields)
- Browser history, cookies, cached data
- Email and messaging records
- Registry entries (Windows)
- Log files
- Deleted file remnants

### What a Computer Forensic Examiner Can Do

- Recover deleted files
- Reconstruct user activity timelines
- Authenticate documents and images
- Identify malware and intrusion artifacts
- Extract data from damaged or encrypted media
- Provide expert testimony

### Career Paths in Digital Forensics

| Role | Context |
|------|---------|
| Expert Witness | Civil/criminal litigation support |
| Incident Responder | Respond to live breaches (IR) |
| DFIR Analyst | Combines IR and forensic analysis |
| Data Recovery Specialist | Recover lost/corrupted data |
| eDiscovery Analyst | Litigation support, legal holds |

### How People Enter the Field

- **Law enforcement** — criminal investigations, trained by agencies (FBI, state/local)
- **Military** — cyber warfare units, intelligence, CYBERCOM
- **University programs** — dedicated forensics/cybersecurity degrees
- **IT/Infosec career pivot** — system admins and security analysts who formalize forensics skills

### Law Enforcement Context

- FBI Cyber Division — priority focus on nation-state intrusions, ransomware, financial fraud
- Local/state agencies handle the majority of cases (child exploitation, financial crimes, homicide)
- Agents and detectives often rely on forensic examiners to process devices

### Military Forensics

- Cyber Mission Force (CYBERCOM)
- Used in battlefield intelligence, counter-terrorism, and infrastructure protection
- Military training pathways: CISA courses, NSA programs, service-branch technical schools

### University Programs

Many community colleges and four-year universities now offer:
- Certificates in digital forensics
- A.S./B.S. in cybersecurity with forensics tracks
- Merritt College CIS 60 is part of this pipeline

---

## Incident Response vs. Computer Forensics

These disciplines overlap but have different objectives:

| | Incident Response (IR) | Computer Forensics (CF) |
|---|------------------------|------------------------|
| **System state** | Live, running system | Static, powered-off disk |
| **Primary goal** | Contain and remediate the threat | Collect and preserve evidence |
| **Evidence type** | Volatile memory, running processes | Forensic disk image |
| **Legal standard** | Not always required | Chain of custody required |
| **Timeline** | Urgent, hours/days | Methodical, days/weeks |

### Forensic Image

A **forensic image** is a **bitwise (bit-for-bit) copy** of a storage device, including:
- All sectors — allocated and unallocated
- Deleted file residue
- File system metadata

A forensic image is **not** a simple file copy (`cp`/`xcopy`). Tools like FTK Imager, `dd`, and Guymager create verified images with cryptographic hashes (MD5/SHA-1) to prove the copy matches the original.

---

## Most Important Trait in Digital Forensics

> **Test yourself. Verify findings with at least two tools.**

Relying on a single tool introduces risk:
- Tools have bugs and blind spots
- Opposing counsel will challenge single-source findings
- Reproducibility is the foundation of scientific credibility

If Tool A says X, confirm with Tool B before including it in your report.

---

## Key Takeaways

1. Expert witnesses must be formally qualified — credentials and methodology matter
2. Document everything, including negative findings
3. Computer forensics and incident response serve different goals with different constraints
4. A forensic image is a bitwise copy, not a file copy
5. Always verify findings with more than one tool
