# Lab 1 Solution — AWS Account Setup and IAM Fundamentals

**Admin-only reference.** This is a worked example showing one valid path through the lab. Student submissions will vary in naming and specific choices — grade for whether the concept was demonstrated, not for matching this exactly.

## Part 1 — AWS Free Tier Account

1. Sign up at [aws.amazon.com/free](https://aws.amazon.com/free) with a personal email (not a work/school account tied to an existing organization).
2. After signup, go to **IAM → My security credentials** (top-right account menu) and enable **MFA** on the root user — either a virtual MFA app (Google Authenticator, Authy) or a hardware key.
3. Confirm success: the account menu (top-right) shows the account alias/ID, and the IAM dashboard's security status no longer flags "Root user MFA" as a warning.

**Grading check:** screenshot should show the account name/ID in the console header. No access keys or passwords visible.

## Part 2 — Explore Core Services

1. Console search bar → "EC2" → land on the EC2 dashboard. Note the "Instances", "Launch Instance" area, and the region selector (top-right) — a good discussion point is that resources are region-scoped.
2. Console search bar → "S3" → land on the S3 dashboard, showing the (likely empty) bucket list.

**Grading check:** two distinct screenshots, EC2 and S3, both clearly showing the service name in the page.

## Part 3 — Hands-On IAM Exercise

1. **Create the IAM user:**
   IAM → Users → Create user → name `lab1-user` → do *not* grant console access unless testing interactively → next.
2. **Attach a restrictive policy:**
   Attach policy directly → `AmazonS3ReadOnlyAccess` (AWS managed policy). This grants read/list on S3 but nothing else.
3. **Get credentials for the test user:**
   Security credentials tab → Create access key → choose "Command Line Interface (CLI)" use case → download the key pair (do **not** screenshot this step with the key visible).
4. **Test the allowed operation:**
   Using the AWS CLI configured with `lab1-user`'s keys (`aws configure --profile lab1-user`):
   ```
   aws s3 ls --profile lab1-user
   ```
   Expected: a list of bucket names (or an empty list) — a successful, non-error response. Screenshot the terminal output.
5. **Test the denied operation:**
   ```
   aws ec2 describe-instances --profile lab1-user
   ```
   Expected: an `AccessDenied` / `UnauthorizedOperation` error, since the policy only grants S3 read access. Screenshot the error.
6. **Find the CloudTrail event:**
   CloudTrail → Event history → filter by "User name" = `lab1-user` → find the `DescribeInstances` (denied) or `ListBuckets` (allowed) event → open it and screenshot the event detail panel, which shows the `errorCode` field (e.g. `Client.UnauthorizedOperation`) for the denied call.
7. **Long-lived vs. temporary credentials explanation (expected answer shape):**
   The IAM user's access key/secret pair is long-lived — it doesn't expire until manually rotated or deleted, so if leaked, it's valid indefinitely. Temporary credentials (via STS `AssumeRole`, e.g. from an EC2 instance role or federated login) expire automatically (typically in 1 hour), which limits the damage window if they leak. Students should conclude temporary credentials are safer for anything beyond initial manual testing.
8. **Cleanup:**
   IAM → Users → `lab1-user` → Security credentials → delete the access key → then delete the user itself. Screenshot the IAM Users list with `lab1-user` no longer present, or the "User deleted successfully" confirmation.

**Grading check:** all four screenshots present (allowed, denied, CloudTrail event, cleanup), explanation shows understanding of expiry as the safety differentiator — exact wording will vary.

## Part 4 — Written Reflection

No single correct answer — this is a synthesis question. Look for:
- Concrete AWS services named appropriately for a website (e.g. S3 + CloudFront for static hosting, or EC2/ECS + RDS + ALB for a dynamic app; Route 53 for DNS; ACM for TLS).
- At least 2–3 specific security concerns tied to those services (e.g. public S3 bucket misconfiguration, missing WAF on a public-facing ALB, database security groups too permissive, IAM roles for the app tier being over-privileged, secrets hardcoded instead of using Secrets Manager).
- Evidence the student verified any AI-sourced claims (e.g. citing AWS docs, or explicitly noting they checked something against the console).
- At least 600 words, own words (not a verbatim AI paste — watch for generic, unspecific paragraphs that don't reference anything from lecture or this lab).

**Grading check:** reflection engages with *this specific* Week 1 material (shared responsibility, service models) rather than being a generic "AWS security tips" list.
