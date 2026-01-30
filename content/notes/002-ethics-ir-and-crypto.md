# CIS 55 – Lecture 2 Notes  
**Topics:** Ethics, Incident Response, Introduction to Cryptography  

---

## 1. Cyber Ethics

### Core Principle
- **Do no harm** when using computers or technology.

### Ethical Guidelines
**Do NOT:**
- Use computers to harm others  
- Interfere with other people’s work  
- Snooping in other people’s files  
- Use a computer to steal  
- Use a computer to bear false witness  
- Copy proprietary software without paying  
- Use others’ computer resources without authorization  
- Appropriate other people’s intellectual output  

**Do:**
- Consider the social consequences of the programs or systems you design  
- Use computers in ways that ensure consideration and respect for others  

---

## 2. Incident Response (IR)

### What is CSIRT?
**CSIRT (Computer Security Incident Response Team)**  
An expert group responsible for handling computer security incidents.  

Related roles:
- Incident Response Coordinator  
- CSO (Chief Security Officer)  
- CISO (Chief Information Security Officer)  
- ISSO (Information Systems Security Officer)  

---

### Common IR Challenges
- **Alert Fatigue**: Too many alerts → important threats missed  
- **Mismatching Control to Threat**: Using the wrong defenses for the actual threat  

Example:
- Using firewalls to stop data theft when the application traffic is already allowed  
- Using standard antivirus against zero-day or APT attacks  

---

### Incident Response Playbook Phases

1. **Preparation**  
2. **Detection**  
3. **Analysis**  
4. **Containment**  
5. **Eradication**  
6. **Recovery**  
7. **Post-Incident Activity**

You must **practice** your IR plan:
- Tabletop exercises  
- Pen tests  
- Process reviews  

---

### Investigating Incidents

- Identify **Scope** (what systems/data affected?)  
- Identify **Impact** using CIA triad:
  - Confidentiality  
  - Integrity  
  - Availability  
- Identify **Root Cause**  
- Look for **Indicators of Compromise (IOCs)**  
- Perform **Attribution** (criminals, nation-states, hacktivists, etc.)

---

### Containment Methods

- **Physical**: Disconnect system from network  
- **Network**: Limit subnet traffic  
- **Perimeter**: Firewall rules  
- **Virtual**: SDN / cloud controls  

---

### Eradication

- No way to be 100% sure malware is gone  
- Reimage affected machines  
- Use network segmentation (VLANs)  
- Test in:
  - Air-gapped test  
  - Staging  
  - Then Production  

---

### Recovery

- Patch all systems  
- Update alert profiles  
- Conduct vulnerability scans  
- Review emergency changes  
- Produce **After Action Report**

---

## 3. Digital Forensics Process

1. **Identification** – logs, packet captures, firewall records  
2. **Preservation** – protect evidence from alteration  
3. **Collection** – follow order of volatility  
4. **Examination** – memory images, logs, disk images  
5. **Analysis** – correlate evidence  
6. **Presentation** – clear, unbiased reporting  

**Order of Volatility (high → low):**
- Registers/cache  
- RAM  
- Temporary files  
- Disk  
- Remote logs  
- Archival media  

---

## 4. Introduction to Cryptography

### Purpose
- Keep messages secret  
- Prevent impersonation  

### Key Terms

| Term | Meaning |
|------|---------|
| Cryptography | Science of encryption |
| Cryptanalysis | Breaking encryption |
| Cryptology | Both of the above |

---

### Classical Example: Caesar Cipher
- Shift letters (e.g., +3)  
- A → D  

---

### Steganography
Hiding messages in other content:
- Last word of each line  
- Null cipher (first letters)

---

### Symmetric Key Cryptography
- Alice and Bob share secret key **Kab**  
- Used for encryption and authentication  

---

### Public Key Cryptography (RSA)

Bob generates:
- **Public key (Keb)** – shared  
- **Private key (Kdb)** – secret  

Alice encrypts with **Keb**  
Bob decrypts with **Kdb**

---

### Digital Signatures
Alice signs with **private key**  
Bob verifies with **public key**

---

### Crypto Attack Models
- Ciphertext-only  
- Known plaintext  
- Chosen plaintext  

A secure cipher must resist all.

---

### Kerckhoffs’ Principle
Security depends on **key secrecy**, not algorithm secrecy.

---

### AES (Advanced Encryption Standard)

- Replaced DES  
- 128-bit block size  
- Key sizes: 128, 192, 256 bits  

---

### One-Time Pad
Only **provably secure** encryption:
- Key same length as message  
- Never reused  

---

## 5. SSL / TLS

### Why SSL Certificates?
- Secure login credentials  
- Protect credit card data  
- Verify website authenticity  
- Enable HTTPS  

### SSL Handshake Steps
1. Client connects  
2. Server sends certificate  
3. Client verifies certificate  
4. Encrypted session begins  

---

## 6. Cryptography Reality Check

- Cryptography is hard  
- Security cannot be proven  
- Most attacks don’t break encryption  
- Security strategy = **Prevent, Detect, Recover**  
- Cryptography mainly helps with **prevention**

---
