# Lab 2: IAM Policies, Conditions, and KMS

**CIS 52 — Cloud Security Fundamentals**

**Due:** Friday, September 11, 2026, 9:00 a.m.
**Canvas:** [Lab 2 assignment](https://peralta.instructure.com/courses/92216/assignments/1757697)

Complete all three parts below and submit everything as a single PDF. You'll be graded for attempt and understanding, not for getting every detail perfect — but each part asks you to prove your policy actually works, not just that you configured something.

**Before you take any screenshots:** black out or crop your AWS Access Key ID, Secret Access Key, and any passwords if they ever appear on screen. Never submit a screenshot containing real credentials.

## Part 1 — S3 Bucket Policy: Allow Everyone in Your Account Except One User

This is a classic IAM pattern: granting broad access while explicitly excluding one identity. The mechanism that makes it work is that **an explicit `Deny` always beats an `Allow`**, no matter which statement appears first.

1. Create a new IAM user named `Eve` (no console access needed — access keys or console password, your choice).
2. Create a new S3 bucket. Leave **Block Public Access fully enabled** — this exercise does not require (or want) a publicly accessible bucket.
3. Write a bucket policy that:
   - **Allows** `s3:GetObject` for every principal in your own AWS account (`Principal: {"AWS": "arn:aws:iam::<your-account-id>:root"}` grants this to every identity in the account, not the whole internet).
   - **Denies** `s3:GetObject` specifically for `Eve`.
   - Upload at least one test object to the bucket first, so there's something to fetch.
4. Screenshot the bucket policy (with your account ID visible or lightly redacted — either is fine).
5. Screenshot Block Public Access showing it is still **on**.
6. **Prove it works, don't just configure it:**
   - Sign in (or use the CLI/console) as `Eve` and attempt to `GetObject` on your test file. Screenshot the `Access Denied` result.
   - Attempt the same `GetObject` as a different principal (your admin user, or another IAM user you create). Screenshot the successful result.
7. In 2–3 sentences: why did the explicit `Deny` win even though the `Allow` statement also applies to Eve (since she's part of "everyone in the account")?
8. **Cleanup:** delete the test bucket, `Eve`, and any access keys you created. Screenshot the confirmation.

## Part 2 — IAM Role with a Multi-Factor Condition

A role restricted only by source IP address repeats the mistake BeyondCorp argues against: network location alone doesn't prove trust. This part asks you to layer **two** independent signals on the same role.

1. Create a new IAM role (for example, `SecurityOpsRole`).
2. Attach these AWS-managed policies to it:
   - `SecurityHubFullAccess`
   - `AmazonInspector2FullAccess`
   - `SecretsManagerReadWrite`
3. Edit the role's trust policy or attach an inline permissions policy so that the role's permissions only apply when **both** of these conditions are true:
   - The request's source IP is `10.20.30.40/32` (`aws:SourceIp`)
   - The caller has an active MFA session (`aws:MultiFactorAuthPresent: "true"`)
4. Screenshot the role's summary page (showing the three attached managed policies) and the condition block in the policy JSON.
5. In 2–3 sentences: if you had used the IP condition alone, what's the realistic way an attacker with stolen credentials could still satisfy it? Why does adding the MFA condition close that gap?

## Part 3 — KMS Customer Managed Key

AWS-managed keys (like `aws/s3`) are created automatically by AWS services — you can't create one yourself. What you *can* create is a **customer managed key**, which is what this part asks for.

1. In KMS, create a new key:
   - Key type: **Symmetric**
   - Key usage: **Encrypt and decrypt**
   - Origin: **KMS** (AWS generates the key material — this is what makes it "AWS-generated," not "AWS-managed")
   - Give it an alias, e.g. `alias/lab2-general-purpose`
2. Screenshot the key's details page (showing the alias, key ID, and "Customer managed" origin).
3. Screenshot the key's key policy — this controls **who** can use the key, which is just as important as the key existing at all.
4. Confirm and screenshot that **automatic key rotation** is enabled (or explain in one sentence why you left it off, if you did).

## Submission

- One PDF combining all screenshots and short written answers from Parts 1–3.
- Due Friday, September 11, 2026, 9:00 a.m. — late submissions follow the syllabus's 10% deduction policy.

**Student template:** a Word template with placeholder sections for each part is available on Canvas — use it if you want a starting structure.
