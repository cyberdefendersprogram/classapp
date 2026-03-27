# CIS 55 – Bonus Session Notes
**Topics:** Bug Bounty — Getting Started

---

## Session Notes

Small group session focused on getting started with bug bounty hunting. Key message: **start by studying what others have already found**, pick one or two vulnerability types to master, and practice on real programs.

---

## 1. Bug Bounty Platforms

Where to find programs and submit reports:

| Platform | Link | Notes |
|----------|------|-------|
| **BugCrowd** | https://www.bugcrowd.com/ | Large enterprise programs |
| **HackerOne** | https://www.hackerone.com/ | Most popular; Airbnb, Uber, etc. |
| **Intigriti** | https://www.intigriti.com/researcher/programs/overview | European-focused programs |
| **Full List** | https://github.com/disclose/bug-bounty-platforms | Comprehensive list of all platforms |

---

## 2. Where to Start — Recommended Vulnerability Types

> *"XSS is harder to find. Start with IDORs and login payloads."* — Prof. Bhandari

**Start with these two:**

- **IDOR (Insecure Direct Object Reference)** — Many people recommend this as the easiest entry point. Look for API endpoints that expose object IDs (user IDs, order IDs) and test whether you can access other users' data by changing the ID.
- **Login Payloads** — Test login endpoints with common injection payloads (SQLi, default credentials, auth bypass strings).

**Week 1 plan:**
1. Spend at least one week **reading existing public bug reports** before trying to find your own
2. Learn the pattern of how bugs are found and reported
3. Then pick a program and start testing

---

## 3. Live Program Examples

### Airbnb — HackerOne
- `POST /v2/favorite_hotels` — exposes a mobile endpoint worth exploring for IDOR
- `POST /v4/launch_modals` — tried iframe XSS (XSS is harder to find but worth attempting)

### Comcast — BugCrowd
- Program: https://bugcrowd.com/engagements/comcast-mbb
- `POST /login` — tried login payloads (SQL injection, auth bypass)

---

## 4. Practice: Learn Attacks First

Before hunting on real programs, get comfortable with vulnerabilities in a safe environment:

**OWASP Juice Shop** — a deliberately vulnerable web app covering all OWASP Top 10 categories
- https://owasp.org/www-project-juice-shop/
- Run locally with Docker: `docker run -p 3000:3000 bkimminich/juice-shop`
- Complete the full tutorial before hunting live programs

---

## 5. YouTube — Bug Bounty Learning

**NahamSec** — one of the best YouTube channels for beginner bug bounty hunters
- https://www.youtube.com/@NahamSec

> *"They tend to be a time sink — try rather than just watch."* — Prof. Bhandari

Watch to learn patterns, but prioritize hands-on practice over passive viewing.

---

## 6. AI Agents for Bug Bounty

AI agents can assist with the **initial recon and scanning** phase of bug bounty:
- Automated URL discovery and enumeration
- Parsing large amounts of API documentation
- Generating payloads to test

> *"It doesn't make sense to use AI agents until you get comfortable with one or two bug reports. That's the first step."*

Get comfortable manually first — then layer in AI tooling.

---

## Next Steps

1. **Create an account** on HackerOne, BugCrowd, or Intigriti
2. **Pick one program** you want to hack on
3. **Spend week 1** reading public reports for that program — understand what has been found and how
4. **Master one vulnerability type** — start with IDOR or login payloads
5. **Complete OWASP Juice Shop** to build hands-on skills
6. **Email Prof. Bhandari** in 2–3 weeks with your progress — a follow-up session will be scheduled

---

## Resources

| Resource | Link |
|----------|------|
| HackerOne | https://www.hackerone.com/ |
| BugCrowd | https://www.bugcrowd.com/ |
| Intigriti | https://www.intigriti.com/researcher/programs/overview |
| All Bug Bounty Platforms | https://github.com/disclose/bug-bounty-platforms |
| OWASP Juice Shop | https://owasp.org/www-project-juice-shop/ |
| NahamSec (YouTube) | https://www.youtube.com/@NahamSec |
| Comcast MBB Program | https://bugcrowd.com/engagements/comcast-mbb |
