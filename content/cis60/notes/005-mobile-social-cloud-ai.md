# CIS 60 – Lecture 5 Notes
**Mobile, Social Media, Cloud & AI Forensics**

---

## Today's Topics

- Guest Speaker: Sherman Kwok
- Mobile Device Forensics
- Reading Assignments & Group Discussion
- Social Media Forensics
- Cloud Forensics
- AI Forensics
- Final Project Review

---

## Guest Speaker: Sherman Kwok

**Professional development advocate** with a passion for content development and delivery in Digital Forensics and Cybersecurity.

- Experienced instructor and coordinator for classroom and scenario-based trainings
- Developed and delivered highly customized courses for Law Enforcement agencies worldwide
- Creator of a popular YouTube channel providing free training on digital forensics, networking, Linux, and more
- LinkedIn: https://www.linkedin.com/in/sherman-kwok-0522/
- X/Twitter: https://www.x.com/BlueMonkey4n6

**What do Forensic Scientists do?**
- Collect evidence
- Preserve evidence
- Analyze evidence
- Testify as expert witness

---

## Mobile Device Forensics

### Overview

- Forensic methodologies remain the same
- Device architectures differ significantly
- Preservation of evidence requires special mobile considerations
- Tools are categorized by level of data acquisition
- Analyzing mobile device evidence requires multiple approaches

### Forensic Methodology

The same core cycle applies to mobile as to all digital forensics:

**Collect → Analyze → Report**

---

### Device Architectures

**Mobile Devices** split into two categories:

| Non-Cellular | Cellular |
|---|---|
| Windows Mobile | Non-GSM |
| PalmOS | GSM |
| Non-cellular Tablets | — |
| iOS, Android | iOS, Android (via SIM / Handset) |

**GSM network components:**
- **PSTN** — Public Switch Telephone Network
- **RNC** — Radio Network Controller
- **GMSC** — Gateway Mobile Switching Center
- **MSC** — Mobile Switching Center
- **HLR** — Home Location Register
- **VLR** — Visitor Location Register
- **GGSN** — Gateway GPRS Support Node
- **SGSN** — Serving GPRS Support Node

**Complicating factors:**
- Prevalence of WiFi, cellular devices, and Internet of Things
- Difficult to capture consistent images — mobile devices actively and continuously write data
- Constantly evolving protocols: CDMA, 2G, 3G, 4G, LTE, WiFi, Bluetooth, IR

---

### Preserving Mobile Device Evidence

**Inactive devices:**
- Leave off until in a protected laboratory setting
- Seize all associated cables and media (SIMs, SD cards, CF cards, etc.)

**Active devices:**
- **Power off?** — May trigger authentication or lockout mechanisms; may change current device state
- **Faraday bag?** — Not proven 100% effective; must use a portable battery or shielded power supply
- **Perform evidence collection on scene?** — Weigh against risks below

**Caveats — improper shielding may result in:**
- Overwritten data that is unrecoverable
- Remote lockout
- Remote observation
- Updated LOCI data

---

### Mobile Forensics Tools

The **NIST Computer Forensics Tool Testing catalog** lists 23 mobile device forensics data collection and analysis tools, categorized by level of data acquisition.

**Mobile Device Tool Classification System (5 levels):**

| Level | Method | Example Tool |
|---|---|---|
| 1 | Manual Extraction | ART (Android Ripping Tool) |
| 2 | Logical Extraction | BlackLight |
| 3 | Hex Dumping / JTAG | CDMA Workshop |
| 4 | Chip-Off | SalvationData Flash Doctor |
| 5 | Micro Read | *(no commercial tools)* |

**Level 1 — ART (Android Ripping Tool):**
- Simple, standalone tool
- Requires Android debugging tools on forensic workstation
- No software required on the Android device itself
- *Can* be used to push software to the Android device
- Connects via serial, USB, or USB-to-COM cabling
- Resulting evidence is similar in nature to a raw disk image

**Level 2 — BlackLight (BlackBag Technologies):**
- Device type, OS version, serial number, UDID, and IMEI
- Artifact summary statistics for documents, emails, movies, calls, voicemail, and more
- Device user account information and common Internet account info (Twitter, iCloud)
- Recent usage history: dialed numbers (with contact info), last running apps, most recent web-based location searches

**Level 3 — CDMA Workshop:**
- Compatible with CDMA 450/800/1900/1xEVDO/WCDMA/GSM/UMTS/HSDPA/LTE phones, smartphones, tablets, fixed terminals, data cards, modems, and chipsets

**Level 4 — SalvationData Flash Doctor:**
- Low-level tool to recover data from Flash devices directly

**Level 5 — Micro Read:**
- No commercial tools are available
- Per NIST: involves recording the physical observation of gates on a NAND or NOR chip using an electron microscope
- Should only be attempted for high-profile cases equivalent to a national security crisis after all other techniques have been exhausted
- Requires a team of experts, proper equipment, time, and in-depth knowledge of proprietary information
- No known U.S. Law Enforcement agencies currently perform acquisitions at this level

---

### Analyzing Mobile Device Evidence

- Diversity of devices requires a variety of tools and procedures
- **OS diversity:** iOS, Android, Symbian, Windows Mobile, et al.
- **Network type diversity:** CDMA, GSM, iDENT/TDMA
- Obstructed devices require careful application of forensic methodology

**Kinds of data available on mobile devices:**

**SIM:**
- Card reader required
- Data objects defined by the GSM 11.11 standard

**Memory:**
- *Physical* — bit-wise copy of physical memory; allows analysis of in-memory and deleted objects
- *Logical* — bit-wise copy of logical objects; easier extraction and analysis

**Application data:**
- Phonebook, calendar, to-do list, email, IM, web history
- Documents, photos, videos, audio
- Subscriber identifiers, equipment identifiers, service provider
- Call data records, subscriber data records
- SMS, MMR
- Location data

**Other sources:**
- Internet and cloud service data
- Social media data

---

### Mobile Forensics Tips

- **Practice, practice, practice** — due to diversity of devices, collection methods, and service providers
- Conduct mock collection and analysis exercises
- Quality control and tool validation are essential to ensure repeatable, valid results
- Multiple tools required to ensure thorough collection and analysis of evidence

---

### Mobile Forensics References

- Mobile Device Forensics, GCFA Gold Certification, Andrew Martin, 2008
- NIST Mobile Device Forensics presentation, Richard Ayers, circa 2008 — http://www.cftt.nist.gov/AAFS-MobileDeviceForensics.pdf
- NIST Special Publication 800-101r1: Guidelines on Mobile Device Forensics, 2014 — http://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-101r1.pdf
- NIST Computer Forensics Tool Testing program & catalog — http://www.cftt.nist.gov/mobile_devices.htm

---

## Reading Assignments

| Module | Topic | Primary Reader |
|---|---|---|
| Module 1 | Understanding the Digital Forensics Profession and Investigations | Frozenda |
| Module 2 | Report Writing and Testimony for Digital Investigations | Peter (Peas) |
| Module 3 | The Investigator's Laboratory and Digital Forensics Tools | Charnnel |
| Module 4 | Data Acquisition | Tina |
| Module 14 | e-Discovery | Emil |
| Module 15 | Ethics and Professional Responsibilities | Davina |
| Module 5 | Processing Crime and Incident Scenes | Rengsey |
| Module 13 | Email and Social Media Investigations | Amal |

### Group Discussion Format

- **5–7 min** — Lead reader presents the chapter
- **4–5 min** — Group discussion and questions
- **5 min** — Group comes up with questions for the class

---

## Class 5 Labs

| Lab | Topic |
|---|---|
| Lab 13 | Browser Forensics |
| Lab 14 | Timeline Analysis |
| Lab 18 | Pagefile Analysis |
| Lab 19 | Password Cracking |

---

## Social Media Forensics

### Overview

- Traditional forensic methods vs. social network evidence
- Social media forensics techniques
- Threats to validity

---

### Traditional Methods vs. Social Networks

**Challenges with forensically sound images of social media:**
- Data is **distributed** across many servers
- At **scale** — enormous data volumes
- Hashes and timelines are difficult to pin down
- Requires **operator cooperation** (e.g., Facebook Law Enforcement Guidelines)
- Even with cooperation, difficult to meet standards like RFC 3227

**Best evidence sources on local devices:**
- Cached data on the local device (e.g., iPhone `consolidated.db`)
- Browser history and cache
- Multimedia — photo geo-location data, `thumbs.db`

---

### Social Media Forensics: Collection Methods

**Network forensics with social media data collection:**
- Passive sniffing
- With ARP spoofing
- Requires an active user session to gather information

**Friend-in-the-Middle attack:**
- Sniffer + fake login page
- Friend with lax privacy settings
- More analogous to undercover work than traditional forensics

**Statistical data analytics:**
- Timeline analysis to detect malevolent behaviors: bullying, stalking, escalation to violent crimes
- Few users fully understand social media privacy settings; even fewer adjust them

---

### Social Media APIs

**What can a forensic examiner retrieve from social media APIs?**
- Social graph
- Communications patterns
- Pictures and videos
- Times of activity
- Apps used

**Information available from API analysis:**
- Social interconnections graph
- Social interaction graph
- Timeline
- Location visualization
- Photo and video tags

**Advanced analyses:**
- **Event tracking** — determining the beginning of shared events; insight into dissemination and propagation
- **Timeline matching** — match timelines of multiple users; cluster analysis
- **Differential snapshots** — repeated capture and analysis of social data; helps determine data dynamism and counter threats to validity

---

### Social Media Forensics Tools

| Tool | Notes |
|---|---|
| Xplico | Included in many security distros, including Kali Linux |
| Maltego | Link analysis and data mining |
| Gephi | Graph visualization |
| TouchGraph | Social network visualization |
| Browser plugins | Various |

**Law enforcement-only tools (Facebook):**
- **Neoprint & Photoprint** — expanded metadata including endpoint IP address, location, and photo tags (law enforcement only; see the Facebook guide for law enforcement)

---

### Threats to Validity in Social Media Forensics

- **Reproducibility** — timelines and social graphs are dynamic and easily changed; results are not reproducible
- **Covert channels** — may complicate forensic validation
- **Some data restricted to operator** — access requires legal process
- **Difficult to guarantee completeness** — user deletion is often irreversible; undelete requires operator assistance

---

### Social Media References

- Mulazzani, Huber, and Weippl. *Social Network Forensics: Tapping the Data Pool of Social Networks.* Pre-print.
- M. Huber et al. *Social snapshots: Digital forensics for online social networks.* ACSAC, 2011.
- Facebook Forensics guide: https://www.fbiic.gov/public/2011/jul/facebook_forensics-finalized.pdf

---

## Cloud Forensics

### Accessing Evidence in the Cloud

The **Electronic Communications Privacy Act (ECPA)** describes five mechanisms the government can use to obtain electronic information from a provider:

1. Search warrants
2. Subpoenas
3. Subpoenas with prior notice to the subscriber or customer
4. Court orders
5. Court orders with prior notice to the subscriber or customer

**Search Warrants:**
- Can be used only in criminal cases
- Must be requested by a law enforcement officer with probable cause evidence
- Must contain specific descriptions of what is to be seized
- In cloud environments, the property to be seized usually describes **data** rather than physical hardware (unless the CSP is the suspect)
- Must describe the **location** of items — difficult when servers are dispersed across state or national borders
- Must establish how and when it will be carried out (timing minimizes disruption to business operations)

**Subpoenas and Court Orders:**
- *Government agency subpoenas* — customer communications and records cannot be knowingly divulged; used in cases involving danger of death or serious physical injury
- *Non-government and civil litigation subpoenas* — used to produce information from private parties for litigation
- *Court orders* — written by judges to compel someone to do or not do something

---

### Tools for Cloud Forensics

Few dedicated cloud forensics tools exist. Investigators typically combine digital, network, and e-discovery tools.

**Vendors with integrated tools:**
- Guidance Software EnCase eDiscovery
- AccessData Digital Forensics Incident Response (DFIR)
- F-Response

---

## AI Forensics

### AI Usage in Forensics

AI is increasingly applied to forensic investigation tasks:

- **Facial categorization** and **image categorization** — automated classification of images at scale
- **Character and word recognition within images** — OCR applied to evidence images
- **Targeted image and facial collection** — identifying specific individuals or objects across large datasets

**Resource:** https://aiforensics.org/

---

## Final Project

### Final Case Study Components

| Assignment | Points |
|---|---|
| Forensics Case Study | 200 pts |
| AI-Enhanced Digital Forensics Investigation | 100 pts |
| Digital Forensics Tool Research Assignment | 100 pts |
| Live Presentation — Forensics Case Study & Tool | 100 pts |

**All components due: May 2 at 11:59pm**

### Team Presentation Order

| Order | Team Members |
|---|---|
| 1 | Roosevelt, Tega, Angel |
| 2 | Eyobe, Cynthia, Chime |
| 3 | Israel, Garrett, Sally |
| 4 | Donald, Jaela, Kelvin |
| 5 | Mohamed, Chase, ... |

---

## Key Takeaways

1. Mobile forensic methodology (Collect → Analyze → Report) is unchanged — the device complexity is what changes
2. Mobile evidence preservation requires deciding early: power off risk vs. remote-wipe risk
3. Tool level matters — choose the least invasive method that recovers the needed evidence
4. Social media evidence lives primarily on local devices; server-side data requires legal process and operator cooperation
5. Cloud evidence requires ECPA legal mechanisms — search warrants describe data, not hardware
6. AI is an emerging force multiplier in forensics for image analysis, facial recognition, and pattern detection
