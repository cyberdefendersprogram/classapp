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

Students are beginners with no AWS CLI or terminal setup — this entire exercise is done through the web console. Don't ask for CLI output; it's not required.

1. **Create the IAM user with console access:**
   IAM → Users → Create user → name `lab1-user` → check **Provide user access to the AWS Management Console** → choose "I want to create an IAM user" → set a custom password and check **Require password reset** (or leave unchecked for a one-shot lab) → next.
2. **Attach a restrictive policy:**
   Attach policy directly → `AmazonS3ReadOnlyAccess` (AWS managed policy). This grants read/list on S3 but nothing else — not EC2, not IAM, nothing.
3. **Get the console sign-in link:**
   After creating the user, AWS shows a sign-in URL like `https://<account-id>.signin.aws.amazon.com/console` along with the username and password. Copy this down (don't screenshot the password).
4. **Sign in as the test user:**
   Sign out of the root/main account, open the sign-in URL in a new browser window (or an incognito/private window, so both sessions can coexist), and log in as `lab1-user`.
5. **Test the allowed operation:**
   As `lab1-user`, go to the S3 console and view/list the bucket(s). This should load normally — no error banner. Screenshot the S3 console showing you're signed in as `lab1-user` (visible in the top-right account menu) with the bucket list loading successfully.
6. **Test the denied operation:**
   As `lab1-user`, go to the EC2 console. Since the policy only grants S3 permissions, the console shows a red error banner like *"You are not authorized to perform this action"* (referencing `ec2:DescribeInstances`). Screenshot this banner.
7. **Find the CloudTrail event:**
   Sign back in as root/admin. CloudTrail → Event history → filter by "User name" = `lab1-user` → find the `DescribeInstances` (denied) or `ListBuckets`/`ListObjects` (allowed) event → open it and screenshot the event detail panel. The denied call's JSON shows `"errorCode": "Client.UnauthorizedOperation"` (or similar) — point this out in the screenshot or a caption.
8. **Long-lived vs. temporary credentials explanation (expected answer shape):**
   This IAM user's console password is long-lived — it doesn't expire until manually rotated or the user is deleted, so if it leaked, it would work indefinitely. Temporary credentials (via IAM Identity Center federated sign-in, or an IAM role assumed with STS) expire automatically, typically within an hour, which limits how long a leaked credential is useful. Students should conclude temporary credentials are safer for anything beyond a one-off manual test like this one.
9. **Cleanup:**
   Sign back in as root/admin. IAM → Users → `lab1-user` → Delete. Screenshot the IAM Users list with `lab1-user` no longer present, or the "User deleted successfully" confirmation.

**Grading check:** all four screenshots present (allowed action, denied action with the error banner, CloudTrail event, cleanup), explanation shows understanding of expiry as the safety differentiator — exact wording will vary. No CLI/terminal output should be expected or required.

## Part 4 — Written Reflection

No single correct answer — this is a synthesis question. Look for:
- Concrete AWS services named appropriately for a website (e.g. S3 + CloudFront for static hosting, or EC2/ECS + RDS + ALB for a dynamic app; Route 53 for DNS; ACM for TLS).
- At least 2–3 specific security concerns tied to those services (e.g. public S3 bucket misconfiguration, missing WAF on a public-facing ALB, database security groups too permissive, IAM roles for the app tier being over-privileged, secrets hardcoded instead of using Secrets Manager).
- Evidence the student verified any AI-sourced claims (e.g. citing AWS docs, or explicitly noting they checked something against the console).
- At least 600 words, own words (not a verbatim AI paste — watch for generic, unspecific paragraphs that don't reference anything from lecture or this lab).

**Grading check:** reflection engages with *this specific* Week 1 material (shared responsibility, service models) rather than being a generic "AWS security tips" list.
