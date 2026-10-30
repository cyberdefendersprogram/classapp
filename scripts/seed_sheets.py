#!/usr/bin/env python3
"""
Seed Google Sheets with initial data structure and test data.

Usage:
    python scripts/seed_sheets.py --create-structure
    python scripts/seed_sheets.py --seed-test-data
    python scripts/seed_sheets.py --all

Requires:
    - GOOGLE_SHEETS_ID environment variable
    - GOOGLE_SERVICE_ACCOUNT_PATH environment variable
"""

import argparse
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Sheet structures: name -> headers
SHEET_STRUCTURES = {
    "Roster": [
        "student_id",
        "full_name",
        "preferred_email",
        "preferred_name",
        "preferred_name_phonetic",
        "preferred_pronoun",
        "linkedin",
        "program_plan",
        "student_level",
        "cs_experience",
        "computer_system",
        "hobbies",
        "used_netlabs",
        "used_tryhackme",
        "class_goals",
        "support_request",
        "claimed_at",
        "onboarding_completed_at",
        "last_login_at",
    ],
    "Onboarding_Responses": [
        "timestamp",
        "student_id",
        "email",
        "form_version",
        "question_key",
        "question_label",
        "answer",
        "answer_type",
        "source",
    ],
    "MagicLink_Requests": [
        "requested_at",
        "email",
        "result",
        "note",
    ],
    "Quizzes": [
        "quiz_id",
        "title",
        "content_path",
        "open_at",
        "close_at",
        "attempts_allowed",
        "status",
        "total_points",
    ],
    "Quiz_Submissions": [
        "submitted_at",
        "quiz_id",
        "attempt",
        "student_id",
        "email",
        "answers_json",
        "score",
        "max_score",
        "autograde_json",
        "source",
    ],
    "Schedule": [
        "session",
        "desc",
        "desc_link",
        "notes",
        "slides_link",
        "recording_link",
    ],
    "Config": [
        "key",
        "value",
    ],
    "Book_Reading": [
        "chapter",
        "class",
        "primary_reader",
        "secondary_reader",
        "chapter_presentation_link",
    ],
    "Reading": [
        "class",
        "title",
        "author",
        "link",
        "required_or_optional",
        "estimated_time",
        "reading_question",
    ],
    "Final_Projects": [
        "student_id",
        "full_name",
        "topic",
        "timing_pref",
        "order",
        "grade",
        "submitted_at",
    ],
}

# Default config values, keyed by course. Selected with --course (default: cis53).
DEFAULT_CONFIG_BY_COURSE = {
    "cis55": {
        "course_title": "CIS 55",
        "term": "Spring 2025",
        "magic_link_ttl_minutes": "15",
        "rate_limit_per_email_15m": "3",
        "onboarding_form_version": "v1",
        "admin_email": "",  # Set manually in sheet
    },
    "cis52": {
        "course_title": "CIS 52",
        "term": "Fall 2026",
        "magic_link_ttl_minutes": "15",
        "rate_limit_per_email_15m": "3",
        "onboarding_form_version": "v1",
        "admin_email": "",  # Set manually in sheet
        # CIS52 uses the simple read-only Reading list, not the Book_Reading
        # chapter-claim system. See nav_reading_link() in app/dependencies.py.
        "reading_mode": "list",
        # CIS52 finals are one student reviewing one cloud breach, not team
        # case studies — sign-up/order/grade live in the Final_Projects tab.
        # See final_project_mode handling in app/routers/pages.py.
        "final_project_mode": "individual",
        # Gate on the student-facing sign-up form; flip to "true" when ready.
        "final_project_open": "false",
    },
    "cis53": {
        "course_title": "CIS 53",
        "term": "Fall 2026",
        "magic_link_ttl_minutes": "15",
        "rate_limit_per_email_15m": "3",
        "onboarding_form_version": "v1",
        "admin_email": "",  # Set manually in sheet
        # CIS53 uses the read-only Reading list (like CIS52): selected chapters
        # plus a reading question each week, assigned in class.
        "reading_mode": "list",
    },
}

# Test quiz data, keyed by course.
TEST_QUIZZES_BY_COURSE = {
    "cis55": [
        {
            "quiz_id": "q001",
            "title": "Introduction Quiz",
            "content_path": "content/cis55/quizzes/001-intro.md",
            "open_at": "",
            "close_at": "",
            "attempts_allowed": "2",
            "status": "published",
            "total_points": "10",
        },
    ],
    "cis52": [
        {
            "quiz_id": "q001",
            "title": "Introduction to Cloud Security",
            "content_path": "content/cis52/quizzes/001-intro.md",
            "open_at": "",
            "close_at": "",
            "attempts_allowed": "2",
            "status": "published",
            "total_points": "12",
        },
    ],
    "cis53": [
        {
            "quiz_id": "q001",
            "title": "Introduction to Intrusion Detection",
            "content_path": "content/cis53/quizzes/001-intro.md",
            "open_at": "",
            "close_at": "",
            "attempts_allowed": "2",
            "status": "published",
            "total_points": "11",
        },
        {
            "quiz_id": "q002",
            "title": "Class 2 In-Class Check (Reading Traffic)",
            "content_path": "content/cis53/quizzes/002-class2-inclass.md",
            "open_at": "",
            "close_at": "",
            "attempts_allowed": "1",
            "status": "published",
            "total_points": "21",
        },
    ],
}

# Test schedule data, keyed by course.
TEST_SCHEDULE_BY_COURSE = {
    "cis55": [
        {
            "session": "1/23/2026",
            "desc": "1 - Introduction",
            "desc_link": "content/cis55/notes/001-intro.md",
            "notes": "Quiz 1",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "1/30/2026",
            "desc": "2 - Cryptography & Incident Response",
            "desc_link": "content/cis55/notes/002-ethics-ir-and-crypto.md",
            "notes": "Lab 1\nQuiz 2",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "2/6/2026",
            "desc": "3 - Pentesting Tools (Nmap, Nessus, Metasploit, SQLMap)",
            "desc_link": "",
            "notes": "Lab 1\nCase Study 2\nQuiz 1",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "2/13/2026",
            "desc": "Holiday (President's Day)",
            "desc_link": "",
            "notes": "",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "2/20/2026",
            "desc": "4 - Threat Modeling, OSINT, OWASP",
            "desc_link": "",
            "notes": "Lab 3\nQuiz 3",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "2/27/2026",
            "desc": "5 - Cloud Security, LLM Security",
            "desc_link": "",
            "notes": "Lab 4\nQuiz 4",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "3/6/2026",
            "desc": "6 - Security Careers and Presentations",
            "desc_link": "",
            "notes": "Lab 5, Quiz 5",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "3/13/2026",
            "desc": "BONUS - Bug Bounty Session",
            "desc_link": "",
            "notes": "",
            "slides_link": "",
            "recording_link": "",
        },
    ],
    "cis52": [
        {
            "session": "08/28/2026",
            "desc": "1 - Cloud Security Foundations",
            "desc_link": "content/cis52/notes/001-intro.md",
            "notes": "Nothing is due\nQuiz 1",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "09/04/2026",
            "desc": "2 - Identity Is the Perimeter",
            "desc_link": "",
            "notes": "Lab 1 due at 9am\nQuiz 1 from 1pm-2:30pm",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "09/11/2026",
            "desc": "3 - Secure the Cloud Stack",
            "desc_link": "",
            "notes": "Lab 2 due at 9am\nQuiz 2 from 1pm-2:30pm",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "09/18/2026",
            "desc": "4 - Cloud-Native Security",
            "desc_link": "",
            "notes": "Lab 3 due at 9am\nQuiz 3 from 1pm-2:30pm",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "09/25/2026",
            "desc": "5 - Detect the Attack",
            "desc_link": "",
            "notes": "Lab 4 due at 9am\nQuiz 4 from 1pm-2:30pm",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "10/02/2026",
            "desc": "6 - Respond, Recover, Improve",
            "desc_link": "",
            "notes": "Lab 5 due at 9am\nQuiz 5 from 1pm-2:30pm",
            "slides_link": "",
            "recording_link": "",
        },
    ],
    "cis53": [
        {
            "session": "10/23/2026",
            "desc": "1 - Network Traffic Analysis, Part 1",
            "desc_link": "content/cis53/notes/001-intro-and-packets.md",
            "notes": "Lab 1\nCase Study 1",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "10/30/2026",
            "desc": "2 - Network Traffic Analysis, Part 2",
            "desc_link": "content/cis53/notes/002-reading-traffic.md",
            "notes": "Lab 2\nQuiz 2",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "11/6/2026",
            "desc": "3 - Application Protocols and Encrypted Traffic",
            "desc_link": "content/cis53/notes/003-application-protocols.md",
            "notes": "Lab 2\nCase Study 3\nQuiz 2",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "11/13/2026",
            "desc": "4 - IDS/IPS, SIEM and Monitoring Architecture",
            "desc_link": "content/cis53/notes/004-detection-architecture.md",
            "notes": "Lab 3\nCase Study 4\nQuiz 3",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "11/20/2026",
            "desc": "5 - Threat Intelligence, Hunting and AI-Assisted Triage",
            "desc_link": "content/cis53/notes/005-intel-hunting-ai.md",
            "notes": "Presentation\nFinal (released 12:00 pm)",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "11/27/2026",
            "desc": "Holiday (Thanksgiving)",
            "desc_link": "",
            "notes": "",
            "slides_link": "",
            "recording_link": "",
        },
        {
            "session": "12/4/2026",
            "desc": "6 - Student Presentations and Guest Lecture",
            "desc_link": "content/cis53/notes/006-presentations-and-wrap-up.md",
            "notes": "Presentation\nFinal (closes Sun 12/6 11:59 pm)",
            "slides_link": "",
            "recording_link": "",
        },
    ],
}

# Reading list rows, keyed by course. Only used by courses with reading_mode
# "list" (see nav_reading_link() in app/dependencies.py). Sourced from the
# Fall 2026 CIS52 reading-list CSV (author, required/optional, estimated time,
# and the per-reading question — omitted for optional readings, which don't
# carry one in the source CSV).
TEST_READING_BY_COURSE = {
    "cis52": [
        {
            "class": "1",
            "title": "Practical Cloud Security, 2nd Ed. — Ch. 1: Principles and Concepts",
            "author": "Chris Dotson / O'Reilly Media",
            "link": "https://www.repository.gctu.edu.gh/files/original/58109f0c11ade205dc3deb567a9d1525.pdf",
            "required_or_optional": "Required",
            "estimated_time": "25–35 minutes",
            "reading_question": "Which traditional security principles remain important in the cloud, and which assumptions must change?",
        },
        {
            "class": "1",
            "title": "NIST SP 800-145 — The NIST Definition of Cloud Computing",
            "author": "National Institute of Standards and Technology",
            "link": "https://csrc.nist.gov/pubs/sp/800/145/final",
            "required_or_optional": "Required",
            "estimated_time": "15–20 minutes",
            "reading_question": "How does the customer's technical control over a system change as the organization moves from IaaS to PaaS to SaaS?",
        },
        {
            "class": "1",
            "title": "AWS — Shared Responsibility Model",
            "author": "Amazon Web Services",
            "link": "https://aws.amazon.com/compliance/shared-responsibility-model/",
            "required_or_optional": "Required",
            "estimated_time": "10–15 minutes",
            "reading_question": "Give one security control owned by the provider and one owned by the customer for an IaaS workload. How would the answer change for SaaS?",
        },
        {
            "class": "1",
            "title": "Above the Clouds: A Berkeley View of Cloud Computing",
            "author": "Michael Armbrust et al. / UC Berkeley",
            "link": "https://www.cs.princeton.edu/courses/archive/spring13/cos448/web/docs/berkeley_cloud.pdf",
            "required_or_optional": "Optional",
            "estimated_time": "30–45 minutes",
            "reading_question": "",
        },
        {
            "class": "1",
            "title": "Above the Clouds — USENIX LISA '09 presentation",
            "author": "Michael Armbrust et al. / UC Berkeley",
            "link": "https://www.usenix.org/conference/lisa-09/above-clouds-berkeley-view-cloud-computing",
            "required_or_optional": "Optional",
            "estimated_time": "20–30 minutes",
            "reading_question": "",
        },
        {
            "class": "2",
            "title": "Practical Cloud Security, 2nd Ed. — Ch. 4: Identity and Access Management",
            "author": "Chris Dotson / O'Reilly Media",
            "link": "https://www.repository.gctu.edu.gh/files/original/58109f0c11ade205dc3deb567a9d1525.pdf",
            "required_or_optional": "Required",
            "estimated_time": "35–45 minutes",
            "reading_question": "Why are temporary roles and workload identities generally safer than distributing long-lived cloud credentials?",
        },
        {
            "class": "2",
            "title": "BeyondCorp: A New Approach to Enterprise Security",
            "author": "Rory Ward and Betsy Beyer / Google",
            "link": "https://research.google/pubs/beyondcorp-a-new-approach-to-enterprise-security/",
            "required_or_optional": "Required",
            "estimated_time": "20–25 minutes",
            "reading_question": "If being inside the corporate network no longer establishes trust, what evidence should determine whether access is granted?",
        },
        {
            "class": "2",
            "title": "NIST SP 800-207 — Zero Trust Architecture",
            "author": "National Institute of Standards and Technology",
            "link": "https://csrc.nist.gov/pubs/sp/800/207/final",
            "required_or_optional": "Required",
            "estimated_time": "20–30 minutes",
            "reading_question": "What information should a Zero Trust policy engine evaluate before allowing access to a cloud resource?",
        },
        {
            "class": "2",
            "title": "MITRE ATT&CK — Valid Accounts: Cloud Accounts (T1078.004)",
            "author": "MITRE ATT&CK",
            "link": "https://attack.mitre.org/techniques/T1078/004/",
            "required_or_optional": "Optional",
            "estimated_time": "10 minutes",
            "reading_question": "",
        },
        {
            "class": "3",
            "title": "Practical Cloud Security, 2nd Ed. — Selected Ch. 2, 5 & 6",
            "author": "Chris Dotson / O'Reilly Media",
            "link": "https://www.repository.gctu.edu.gh/files/original/58109f0c11ade205dc3deb567a9d1525.pdf",
            "required_or_optional": "Required",
            "estimated_time": "35–45 minutes",
            "reading_question": "Which cloud security weakness becomes most dangerous when combined with excessive IAM permissions, and why?",
        },
        {
            "class": "3",
            "title": "OWASP API Security Top 10 — 2023",
            "author": "OWASP",
            "link": "https://owasp.org/API-Security/editions/2023/en/0x11-t10/",
            "required_or_optional": "Required",
            "estimated_time": "20–30 minutes",
            "reading_question": "Which API vulnerabilities can allow an attacker to cross an application trust boundary and gain access to cloud resources or data?",
        },
        {
            "class": "3",
            "title": "A Technical Analysis of the Capital One Cloud Misconfiguration Breach",
            "author": "Cloud Security Alliance",
            "link": "https://cloudsecurityalliance.org/blog/2019/08/09/a-technical-analysis-of-the-capital-one-cloud-misconfiguration-breach",
            "required_or_optional": "Required",
            "estimated_time": "15–20 minutes",
            "reading_question": "Identify at least three points where the attack path could have been interrupted. Which control would you prioritize?",
        },
        {
            "class": "3",
            "title": "A Systematic Analysis of the Capital One Data Breach: Critical Lessons Learned",
            "author": "Khan et al.",
            "link": "https://doi.org/10.1145/3546068",
            "required_or_optional": "Optional",
            "estimated_time": "45–60 minutes",
            "reading_question": "",
        },
        {
            "class": "4",
            "title": "Practical Cloud Security, 2nd Ed. — Ch. 5: Cloud-Native Vulnerability Management",
            "author": "Chris Dotson / O'Reilly Media",
            "link": "https://www.repository.gctu.edu.gh/files/original/58109f0c11ade205dc3deb567a9d1525.pdf",
            "required_or_optional": "Required",
            "estimated_time": "20–30 minutes",
            "reading_question": "Which security problems should be detected before deployment, and which can only be detected effectively at runtime?",
        },
        {
            "class": "4",
            "title": "NIST SP 800-190 — Application Container Security Guide",
            "author": "National Institute of Standards and Technology",
            "link": "https://csrc.nist.gov/pubs/sp/800/190/final",
            "required_or_optional": "Required",
            "estimated_time": "25–35 minutes",
            "reading_question": "What new attack surfaces appear when an application moves from a virtual machine to containers managed by an orchestrator?",
        },
        {
            "class": "4",
            "title": "NIST SP 800-204C — DevSecOps for a Microservices-Based Application with Service Mesh",
            "author": "National Institute of Standards and Technology",
            "link": "https://csrc.nist.gov/pubs/sp/800/204/c/final",
            "required_or_optional": "Required",
            "estimated_time": "20–30 minutes",
            "reading_question": "Which controls can be automated before deployment, and what class of incidents does this help prevent?",
        },
        {
            "class": "4",
            "title": "Securing DevOps",
            "author": "Julien Vehent / Manning",
            "link": "https://www.manning.com/books/securing-devops",
            "required_or_optional": "Optional",
            "estimated_time": "30–60 minutes",
            "reading_question": "",
        },
        {
            "class": "5",
            "title": "Practical Cloud Security, 2nd Ed. — Ch. 7: Detection Sections",
            "author": "Chris Dotson / O'Reilly Media",
            "link": "https://www.repository.gctu.edu.gh/files/original/58109f0c11ade205dc3deb567a9d1525.pdf",
            "required_or_optional": "Required",
            "estimated_time": "30–40 minutes",
            "reading_question": "What makes a cloud log useful for security detection rather than merely operational troubleshooting?",
        },
        {
            "class": "5",
            "title": "MITRE ATT&CK — Enterprise Cloud Matrix",
            "author": "MITRE ATT&CK",
            "link": "https://attack.mitre.org/matrices/enterprise/cloud/",
            "required_or_optional": "Required",
            "estimated_time": "30–40 minutes",
            "reading_question": "Choose three ATT&CK techniques and identify the telemetry you would use to detect or investigate each one.",
        },
        {
            "class": "6",
            "title": "Practical Cloud Security, 2nd Ed. — Ch. 7: Response and Recovery Sections",
            "author": "Chris Dotson / O'Reilly Media",
            "link": "https://www.repository.gctu.edu.gh/files/original/58109f0c11ade205dc3deb567a9d1525.pdf",
            "required_or_optional": "Required",
            "estimated_time": "25–35 minutes",
            "reading_question": "Which cloud characteristics make incident response easier than traditional infrastructure, and which make it harder?",
        },
        {
            "class": "6",
            "title": "NIST SP 800-61 Rev. 3 — Incident Response Recommendations and Considerations",
            "author": "National Institute of Standards and Technology",
            "link": "https://csrc.nist.gov/pubs/sp/800/61/r3/final",
            "required_or_optional": "Required",
            "estimated_time": "25–35 minutes",
            "reading_question": "Why should a security incident lead to changes in architecture and controls rather than ending when normal service is restored?",
        },
        {
            "class": "6",
            "title": "Cloud Security Alliance — Cloud Controls Matrix and Introductory Guidance",
            "author": "Cloud Security Alliance",
            "link": "https://cloudsecurityalliance.org/research/cloud-controls-matrix",
            "required_or_optional": "Required",
            "estimated_time": "20–25 minutes",
            "reading_question": "Choose one technical security control used during the course. What evidence would demonstrate that the control is operating effectively?",
        },
        {
            "class": "6",
            "title": "AWS Security Incident Response Guide",
            "author": "Amazon Web Services",
            "link": "https://docs.aws.amazon.com/whitepapers/latest/aws-security-incident-response-guide/aws-security-incident-response-guide.html",
            "required_or_optional": "Optional",
            "estimated_time": "30–45 minutes",
            "reading_question": "",
        },
    ],
    # CIS53 Fall 2026. Chapter titles come from the O'Reilly tables of contents;
    # estimated times are rough. Book links go to the O'Reilly landing page
    # (students sign in through the free O'Reilly access); the rest are free.
    "cis53": [
        {
            "class": "1",
            "title": "The Practice of Network Security Monitoring — Ch. 1: Network Security Monitoring Rationale",
            "author": "Richard Bejtlich / No Starch Press",
            "link": "https://www.oreilly.com/library/view/the-practice-of/9781457185175/",
            "required_or_optional": "Required",
            "estimated_time": "30–40 minutes",
            "reading_question": "Why is prevention alone not enough to protect a network, and what does monitoring add?",
        },
        {
            "class": "1",
            "title": "The Practice of Network Security Monitoring — Ch. 2: Collecting Network Traffic: Access, Storage, and Management",
            "author": "Richard Bejtlich / No Starch Press",
            "link": "https://www.oreilly.com/library/view/the-practice-of/9781457185175/",
            "required_or_optional": "Required",
            "estimated_time": "30–40 minutes",
            "reading_question": "Where can you place a sensor to see traffic, and what can you not see from each position?",
        },
        {
            "class": "2",
            "title": "The Practice of Network Security Monitoring — Ch. 6: Command Line Packet Analysis Tools and Ch. 7: Graphical Packet Analysis Tools",
            "author": "Richard Bejtlich / No Starch Press",
            "link": "https://www.oreilly.com/library/view/the-practice-of/9781457185175/",
            "required_or_optional": "Required",
            "estimated_time": "40–50 minutes",
            "reading_question": "What does each tool (command line vs. graphical) let you do faster, and when would you reach for each?",
        },
        {
            "class": "2",
            "title": "Wireshark User's Guide — Filtering Packets (Display Filters)",
            "author": "The Wireshark Project",
            "link": "https://www.wireshark.org/docs/wsug_html_chunked/ChWorkBuildDisplayFilterSection.html",
            "required_or_optional": "Required",
            "estimated_time": "20–25 minutes",
            "reading_question": "When do you use a capture filter and when a display filter, and what does each one change?",
        },
        {
            "class": "3",
            "title": "The Practice of Network Security Monitoring — Ch. 10: Server-side Compromise and Ch. 11: Client-side Compromise",
            "author": "Richard Bejtlich / No Starch Press",
            "link": "https://www.oreilly.com/library/view/the-practice-of/9781457185175/",
            "required_or_optional": "Required",
            "estimated_time": "40–50 minutes",
            "reading_question": "Follow one investigation: which evidence led the analyst from the first alert to a conclusion?",
        },
        {
            "class": "3",
            "title": "OWASP Top 10 for LLM Applications",
            "author": "OWASP GenAI Security Project",
            "link": "https://genai.owasp.org/llm-top-10/",
            "required_or_optional": "Required",
            "estimated_time": "25–30 minutes",
            "reading_question": "What network or log evidence would show data leaving through an AI service or an LLM-powered application?",
        },
        {
            "class": "4",
            "title": "The Practice of Network Security Monitoring — Ch. 9: NSM Operations",
            "author": "Richard Bejtlich / No Starch Press",
            "link": "https://www.oreilly.com/library/view/the-practice-of/9781457185175/",
            "required_or_optional": "Required",
            "estimated_time": "30–40 minutes",
            "reading_question": "How does an analyst decide whether an alert is worth escalating, and what should be recorded?",
        },
        {
            "class": "4",
            "title": "Practical Threat Detection Engineering — Ch. 1: Fundamentals of Detection Engineering",
            "author": "Megan Roddie, Jason Deyalsingh, Gary J. Katz / Packt",
            "link": "https://www.oreilly.com/library/view/practical-threat-detection/9781801076715/",
            "required_or_optional": "Required",
            "estimated_time": "25–30 minutes",
            "reading_question": "When does a signature-based detection beat a behavioral one, and when does it fail?",
        },
        {
            "class": "4",
            "title": "Suricata Documentation — Rules: Introduction",
            "author": "Open Information Security Foundation",
            "link": "https://docs.suricata.io/en/latest/rules/intro.html",
            "required_or_optional": "Required",
            "estimated_time": "15–20 minutes",
            "reading_question": "Name the parts of a rule header and rule options, and say what a rule needs to avoid false positives.",
        },
        {
            "class": "4",
            "title": "The Practice of Network Security Monitoring — Ch. 4: Distributed Deployment",
            "author": "Richard Bejtlich / No Starch Press",
            "link": "https://www.oreilly.com/library/view/the-practice-of/9781457185175/",
            "required_or_optional": "Optional",
            "estimated_time": "30–40 minutes",
            "reading_question": "",
        },
        {
            "class": "4",
            "title": "Sigma Rules — Basics",
            "author": "SigmaHQ",
            "link": "https://sigmahq.io/docs/basics/rules.html",
            "required_or_optional": "Optional",
            "estimated_time": "15–20 minutes",
            "reading_question": "",
        },
        {
            "class": "5",
            "title": "Intelligence-Driven Incident Response, 2nd Ed. — Ch. 2: Basics of Intelligence",
            "author": "Rebekah Brown, Scott J. Roberts / O'Reilly Media",
            "link": "https://www.oreilly.com/library/view/intelligence-driven-incident-response/9781098120672/",
            "required_or_optional": "Required",
            "estimated_time": "30–40 minutes",
            "reading_question": "What turns raw indicators into intelligence an analyst can act on?",
        },
        {
            "class": "5",
            "title": "Practical Threat Detection Engineering — Ch. 7: Developing Detections Using Behavioral Indicators",
            "author": "Megan Roddie, Jason Deyalsingh, Gary J. Katz / Packt",
            "link": "https://www.oreilly.com/library/view/practical-threat-detection/9781801076715/",
            "required_or_optional": "Required",
            "estimated_time": "30–40 minutes",
            "reading_question": "Why do behavioral detections age better than indicator-based ones, and how would you test one?",
        },
        {
            "class": "5",
            "title": "MITRE ATLAS — Adversarial Threat Landscape for AI Systems (matrix overview)",
            "author": "MITRE",
            "link": "https://atlas.mitre.org/",
            "required_or_optional": "Required",
            "estimated_time": "15–20 minutes",
            "reading_question": "Pick one ATLAS technique. What evidence of it could a defender collect from network traffic or application logs?",
        },
        {
            "class": "5",
            "title": "NIST AI 100-2 — Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations",
            "author": "National Institute of Standards and Technology",
            "link": "https://csrc.nist.gov/pubs/ai/100/2/e2025/final",
            "required_or_optional": "Optional",
            "estimated_time": "30–45 minutes",
            "reading_question": "",
        },
        {
            "class": "5",
            "title": "Practical Threat Detection Engineering — Ch. 9: Detection Validation",
            "author": "Megan Roddie, Jason Deyalsingh, Gary J. Katz / Packt",
            "link": "https://www.oreilly.com/library/view/practical-threat-detection/9781801076715/",
            "required_or_optional": "Optional",
            "estimated_time": "30–40 minutes",
            "reading_question": "",
        },
        {
            "class": "6",
            "title": "Google Secure AI Framework (SAIF)",
            "author": "Google",
            "link": "https://safety.google/cybersecurity-advancements/saif/",
            "required_or_optional": "Optional",
            "estimated_time": "15–20 minutes",
            "reading_question": "",
        },
        {
            "class": "6",
            "title": "Intelligence-Driven Incident Response, 2nd Ed. — Ch. 10: Strategic Intelligence",
            "author": "Rebekah Brown, Scott J. Roberts / O'Reilly Media",
            "link": "https://www.oreilly.com/library/view/intelligence-driven-incident-response/9781098120672/",
            "required_or_optional": "Optional",
            "estimated_time": "30–40 minutes",
            "reading_question": "",
        },
    ],
}

# Dev-only test roster rows, keyed by course. Only written with --seed-test-roster.
TEST_ROSTER_BY_COURSE = {
    "cis52": [
        {
            "student_id": "10110234",
            "full_name": "Student, Test",
            "preferred_email": "",
            "preferred_name": "",
            "preferred_name_phonetic": "",
            "preferred_pronoun": "",
            "linkedin": "",
            "program_plan": "",
            "student_level": "",
            "cs_experience": "",
            "computer_system": "",
            "hobbies": "",
            "used_netlabs": "",
            "used_tryhackme": "",
            "class_goals": "",
            "support_request": "",
            "claimed_at": "",
            "onboarding_completed_at": "",
            "last_login_at": "",
        },
    ],
    "cis53": [
        {
            "student_id": "10110234",
            "full_name": "Student, Test",
            "preferred_email": "",
            "preferred_name": "",
            "preferred_name_phonetic": "",
            "preferred_pronoun": "",
            "linkedin": "",
            "program_plan": "",
            "student_level": "",
            "cs_experience": "",
            "computer_system": "",
            "hobbies": "",
            "used_netlabs": "",
            "used_tryhackme": "",
            "class_goals": "",
            "support_request": "",
            "claimed_at": "",
            "onboarding_completed_at": "",
            "last_login_at": "",
        },
    ],
}


# Placeholder book chapters — update chapter names and presentation links directly in the sheet
TEST_BOOK_CHAPTERS = [
    {
        "chapter": "Chapter 1",
        "class": "1",
        "primary_reader": "",
        "secondary_reader": "",
        "chapter_presentation_link": "",
    },
    {
        "chapter": "Chapter 2",
        "class": "2",
        "primary_reader": "",
        "secondary_reader": "",
        "chapter_presentation_link": "",
    },
    {
        "chapter": "Chapter 3",
        "class": "3",
        "primary_reader": "",
        "secondary_reader": "",
        "chapter_presentation_link": "",
    },
    {
        "chapter": "Chapter 4",
        "class": "4",
        "primary_reader": "",
        "secondary_reader": "",
        "chapter_presentation_link": "",
    },
    {
        "chapter": "Chapter 5",
        "class": "5",
        "primary_reader": "",
        "secondary_reader": "",
        "chapter_presentation_link": "",
    },
]


def get_client() -> gspread.Client:
    """Get authenticated gspread client."""
    sa_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH")
    if not sa_path:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_PATH environment variable not set")

    creds = Credentials.from_service_account_file(sa_path, scopes=SCOPES)
    return gspread.authorize(creds)


def get_spreadsheet(client: gspread.Client) -> gspread.Spreadsheet:
    """Open the spreadsheet."""
    sheets_id = os.environ.get("GOOGLE_SHEETS_ID")
    if not sheets_id:
        raise ValueError("GOOGLE_SHEETS_ID environment variable not set")

    return client.open_by_key(sheets_id)


def create_structure(spreadsheet: gspread.Spreadsheet, course: str) -> None:
    """Create all required worksheets with headers, skipping the reading tab this course doesn't use."""
    existing_sheets = [ws.title for ws in spreadsheet.worksheets()]

    # Only one of these two is ever needed — see nav_reading_link() in app/dependencies.py.
    reading_mode = DEFAULT_CONFIG_BY_COURSE.get(course, {}).get("reading_mode", "signup")
    skip_sheets = {{"list": "Book_Reading", "signup": "Reading"}.get(reading_mode, "")}

    # Final_Projects only applies to courses using the individual (one student,
    # one topic) final project model — see final_project_mode in app/routers/pages.py.
    final_project_mode = DEFAULT_CONFIG_BY_COURSE.get(course, {}).get("final_project_mode", "teams")
    if final_project_mode != "individual":
        skip_sheets.add("Final_Projects")

    for sheet_name, headers in SHEET_STRUCTURES.items():
        if sheet_name in skip_sheets:
            print(f"  Skipping '{sheet_name}' (not used by this course's config)...")
            continue

        if sheet_name in existing_sheets:
            print(f"  Sheet '{sheet_name}' already exists, skipping...")
            continue

        print(f"  Creating sheet '{sheet_name}'...")
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=len(headers))
        worksheet.update("A1", [headers])

        # Format header row (bold)
        worksheet.format("A1:Z1", {"textFormat": {"bold": True}})

    # Remove default Sheet1 if it exists and is empty
    try:
        sheet1 = spreadsheet.worksheet("Sheet1")
        if sheet1.get_all_values() == []:
            spreadsheet.del_worksheet(sheet1)
            print("  Removed empty 'Sheet1'")
    except gspread.WorksheetNotFound:
        pass

    print("Structure creation complete!")


def fix_config_headers(spreadsheet: gspread.Spreadsheet) -> None:
    """Fix Config sheet by adding header row if missing."""
    print("  Checking Config sheet headers...")
    worksheet = spreadsheet.worksheet("Config")

    # Get the first row
    first_row = worksheet.row_values(1)

    # Check if headers are correct
    if first_row and first_row[0] == "key" and len(first_row) > 1 and first_row[1] == "value":
        print("    Config headers are correct")
        return

    # Headers are missing or wrong - need to insert header row
    print("    Config headers missing, adding header row...")

    # Get all current data
    all_data = worksheet.get_all_values()

    # Clear and rewrite with headers
    worksheet.clear()
    worksheet.update("A1", [["key", "value"]] + all_data)

    # Format header row (bold)
    worksheet.format("A1:B1", {"textFormat": {"bold": True}})

    print("    Added header row to Config sheet")


def seed_config(spreadsheet: gspread.Spreadsheet, course: str) -> None:
    """Seed the Config sheet with default values for the given course."""
    print("  Seeding Config...")

    # First fix headers if needed
    fix_config_headers(spreadsheet)

    worksheet = spreadsheet.worksheet("Config")

    # Check if already has data
    existing = worksheet.get_all_records()
    existing_keys = {r.get("key") for r in existing}

    default_config = DEFAULT_CONFIG_BY_COURSE[course]
    rows_to_add = []
    for key, value in default_config.items():
        if key not in existing_keys:
            rows_to_add.append([key, value])

    if rows_to_add:
        worksheet.append_rows(rows_to_add, value_input_option="RAW")
        print(f"    Added {len(rows_to_add)} config entries")
    else:
        print("    Config already seeded")


def seed_quizzes(spreadsheet: gspread.Spreadsheet, course: str) -> None:
    """Seed the Quizzes sheet with test data for the given course."""
    print("  Seeding Quizzes...")
    worksheet = spreadsheet.worksheet("Quizzes")

    # Check if already has data
    existing = worksheet.get_all_records()
    existing_ids = {r.get("quiz_id") for r in existing}

    headers = SHEET_STRUCTURES["Quizzes"]
    rows_to_add = []

    for quiz in TEST_QUIZZES_BY_COURSE.get(course, []):
        if quiz["quiz_id"] in existing_ids:
            continue

        rows_to_add.append([quiz.get(h, "") for h in headers])

    if rows_to_add:
        worksheet.append_rows(rows_to_add, value_input_option="RAW")
        print(f"    Added {len(rows_to_add)} quizzes")
    else:
        print("    Quizzes already seeded")


def seed_schedule(spreadsheet: gspread.Spreadsheet, course: str) -> None:
    """Seed the Schedule sheet with test data for the given course."""
    print("  Seeding Schedule...")
    worksheet = spreadsheet.worksheet("Schedule")

    # Check if already has data
    existing = worksheet.get_all_records()
    existing_sessions = {r.get("session") for r in existing}

    headers = SHEET_STRUCTURES["Schedule"]
    rows_to_add = []

    for entry in TEST_SCHEDULE_BY_COURSE.get(course, []):
        if entry["session"] in existing_sessions:
            continue

        rows_to_add.append([entry.get(h, "") for h in headers])

    if rows_to_add:
        worksheet.append_rows(rows_to_add, value_input_option="RAW")
        print(f"    Added {len(rows_to_add)} schedule entries")
    else:
        print("    Schedule already seeded")


def seed_test_roster(spreadsheet: gspread.Spreadsheet, course: str) -> None:
    """Seed dev-only test roster rows for the given course (unclaimed students for local testing)."""
    print("  Seeding test Roster rows...")
    worksheet = spreadsheet.worksheet("Roster")

    existing = worksheet.get_all_records()
    existing_ids = {str(r.get("student_id")) for r in existing}

    headers = SHEET_STRUCTURES["Roster"]
    rows_to_add = []

    for student in TEST_ROSTER_BY_COURSE.get(course, []):
        if student["student_id"] in existing_ids:
            continue
        rows_to_add.append([student.get(h, "") for h in headers])

    if rows_to_add:
        worksheet.append_rows(rows_to_add, value_input_option="RAW")
        print(f"    Added {len(rows_to_add)} test roster rows")
    else:
        print("    Test roster already seeded")


def seed_reading(spreadsheet: gspread.Spreadsheet, course: str) -> None:
    """Seed the Reading sheet with reading-list rows for the given course."""
    print("  Seeding Reading...")
    worksheet = spreadsheet.worksheet("Reading")

    existing = worksheet.get_all_records()
    existing_titles = {r.get("title") for r in existing}

    headers = SHEET_STRUCTURES["Reading"]
    rows_to_add = []

    for item in TEST_READING_BY_COURSE.get(course, []):
        if item["title"] in existing_titles:
            continue
        rows_to_add.append([item.get(h, "") for h in headers])

    if rows_to_add:
        worksheet.append_rows(rows_to_add, value_input_option="RAW")
        print(f"    Added {len(rows_to_add)} reading rows")
    else:
        print("    Reading already seeded")


def seed_book_reading(spreadsheet: gspread.Spreadsheet) -> None:
    """Seed the Book_Reading sheet with placeholder chapter rows."""
    print("  Seeding Book_Reading...")
    worksheet = spreadsheet.worksheet("Book_Reading")

    existing = worksheet.get_all_records()
    existing_chapters = {r.get("chapter") for r in existing}

    headers = SHEET_STRUCTURES["Book_Reading"]
    rows_to_add = []

    for chapter in TEST_BOOK_CHAPTERS:
        if chapter["chapter"] in existing_chapters:
            continue
        rows_to_add.append([chapter.get(h, "") for h in headers])

    if rows_to_add:
        worksheet.append_rows(rows_to_add, value_input_option="RAW")
        print(f"    Added {len(rows_to_add)} chapter rows")
    else:
        print("    Book_Reading already seeded")


def main():
    parser = argparse.ArgumentParser(description="Seed Google Sheets with data")
    parser.add_argument(
        "--course",
        default="cis53",
        choices=sorted(DEFAULT_CONFIG_BY_COURSE.keys()),
        help="Which course's default Config/Schedule/Quizzes to seed (default: cis53)",
    )
    parser.add_argument("--create-structure", action="store_true", help="Create sheet structure")
    parser.add_argument("--seed-test-data", action="store_true", help="Seed test data")
    parser.add_argument(
        "--seed-meta",
        action="store_true",
        help=(
            "Seed structure + Config + Quizzes only (real metadata, safe to run against a "
            "hand-curated sheet like production) — skips Schedule and Book_Reading, which "
            "carry example/test rows this won't reliably deduplicate against real ones."
        ),
    )
    parser.add_argument(
        "--seed-test-roster",
        action="store_true",
        help="Seed dev-only unclaimed test roster rows (e.g. student_id 10110234 for local /claim testing)",
    )
    parser.add_argument("--all", action="store_true", help="Create structure and seed data")

    args = parser.parse_args()

    if not any(
        [
            args.create_structure,
            args.seed_test_data,
            args.seed_meta,
            args.seed_test_roster,
            args.all,
        ]
    ):
        parser.print_help()
        return

    print("Connecting to Google Sheets...")
    client = get_client()
    spreadsheet = get_spreadsheet(client)
    print(f"Opened: {spreadsheet.title} (course: {args.course})")

    if args.create_structure or args.all or args.seed_meta:
        print("\nCreating structure...")
        create_structure(spreadsheet, args.course)

    if args.seed_test_data or args.all:
        print("\nSeeding test data...")
        seed_config(spreadsheet, args.course)
        seed_quizzes(spreadsheet, args.course)
        seed_schedule(spreadsheet, args.course)
        reading_mode = DEFAULT_CONFIG_BY_COURSE.get(args.course, {}).get("reading_mode", "signup")
        if reading_mode == "list":
            seed_reading(spreadsheet, args.course)
        else:
            seed_book_reading(spreadsheet)

    if args.seed_meta:
        print("\nSeeding metadata only (Config + Quizzes, no Schedule/Book_Reading)...")
        seed_config(spreadsheet, args.course)
        seed_quizzes(spreadsheet, args.course)

    if args.seed_test_roster:
        print("\nSeeding test roster (dev only)...")
        seed_test_roster(spreadsheet, args.course)

    print("\nDone!")


if __name__ == "__main__":
    main()
