# Lab 1: AWS Account Setup and IAM Fundamentals

**CIS 52 — Cloud Security Fundamentals**

**Due:** Friday, September 4, 2026, 9:00 a.m.
**Canvas:** [Lab 1 assignment](https://peralta.instructure.com/courses/92216/assignments/1757696)

Complete all four parts below and submit everything as a single PDF.

**Before you take any screenshots:** black out or crop your AWS Access Key ID, Secret Access Key, and root account password if they ever appear on screen. Never submit a screenshot containing real credentials.

## Part 1 — Register for an AWS Free Tier Account

- Create an AWS Free Tier account (if you don't already have one).
- Enable MFA (multi-factor authentication) on your root account — this is a security requirement, not optional.
- Screenshot: show that you are logged in, with your account name/alias visible.

## Part 2 — Explore Core Services

- Look around the AWS Console and review the core services discussed in class: EC2 and S3.
- Screenshot each service's console page (EC2 dashboard, S3 dashboard).

## Part 3 — Hands-On IAM Exercise

- Create a new IAM user (not root) — e.g. `lab1-user` — with a policy granting only limited permissions (for example, read-only S3 access).
- Test an **allowed** operation as that user (e.g. listing S3 buckets). Screenshot the successful result.
- Test a **denied** operation outside that policy (e.g. launching an EC2 instance, deleting a bucket). Screenshot the "Access Denied" error.
- Find the corresponding CloudTrail audit log event for one of the actions above. Screenshot it.
- In a couple of sentences, explain the difference between this IAM user's long-lived access keys and temporary (STS) credentials — which is safer, and why?
- Clean up: delete the test IAM user and any access keys you created. Screenshot the confirmation.

## Part 4 — Written Reflection (at least 600 words)

In your own words: if you were to build a website on AWS, which services would you use, and how? What security issues would you need to watch out for?

You're welcome to research this using Google, ChatGPT, or other AI tools — but treat anything an AI tool tells you about IAM, permissions, or security controls as **unverified** until you've checked it against AWS's own documentation. Don't just paste AI output; write it in your own words and be ready to explain any claim you make.

## Submission

- One PDF combining all screenshots and your written reflection.
- Written portion must be at least 600 words.
- Due Friday, September 4, 2026, 9:00 a.m. — late submissions follow the syllabus's 10% deduction policy.

**Student template:** a Word template with placeholder sections for each part is available on Canvas — use it if you want a starting structure.
