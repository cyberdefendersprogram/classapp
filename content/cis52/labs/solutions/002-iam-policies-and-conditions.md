# Lab 2 Solution — IAM Policies, Conditions, and KMS

**Admin-only reference.** This is a worked example showing one valid path through the lab. Student submissions will vary in naming and specific choices — grade for whether the concept was demonstrated, not for matching this exactly.

## Part 1 — S3 Bucket Policy: Allow Everyone in Your Account Except One User

1. **Create Eve:**
   IAM → Users → Create user → name `Eve` → skip console access (access keys only, or console access if you'd rather test via sign-in) → no policies attached directly to Eve; her access is governed entirely by the bucket policy.
2. **Create the bucket:**
   S3 → Create bucket → globally unique name (e.g. `cis52-lab2-<yourname>`) → leave all four **Block Public Access** settings checked/enabled → create. Upload one small test file (e.g. `test.txt`).
3. **Bucket policy** (Permissions tab → Bucket policy → edit):

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "AllowAccountExceptEve",
         "Effect": "Allow",
         "Principal": { "AWS": "arn:aws:iam::<ACCOUNT_ID>:root" },
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::cis52-lab2-<yourname>/*"
       },
       {
         "Sid": "DenyEve",
         "Effect": "Deny",
         "Principal": { "AWS": "arn:aws:iam::<ACCOUNT_ID>:user/Eve" },
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::cis52-lab2-<yourname>/*"
       }
     ]
   }
   ```

   Note: `Principal: {"AWS": "arn:aws:iam::<ACCOUNT_ID>:root"}` in an *Allow* statement means "every identity in this account," not just the root user — this is a common point of confusion worth calling out if a student asks. It is **not** the same as `Principal: "*"`, which would mean the entire internet.

4. **Screenshots expected:** the policy JSON above (account ID visible or redacted), and Block Public Access still showing all four boxes checked.
5. **Prove it works:**
   - As `Eve` (switch role/sign in with her credentials, or use the CLI with her access keys: `aws s3api get-object --bucket cis52-lab2-<yourname> --key test.txt out.txt --profile eve`), the call returns `AccessDenied`. Screenshot this.
   - As the admin user (or a second test IAM user with no explicit deny), the same `GetObject` call succeeds. Screenshot this.
6. **Expected answer (deny precedence):** AWS evaluates all applicable statements across all attached policies and if *any* statement explicitly denies the action, that overrides any `Allow` — regardless of statement order or how specific/broad each statement's principal is. Eve matches both the `Allow` (she's part of the account) and the `Deny` (she's named explicitly); the `Deny` wins.
7. **Cleanup:** delete the test object, empty and delete the bucket, delete `Eve` (and her access keys, if created). Screenshot the confirmation (e.g. IAM Users list without `Eve`, or S3 bucket list without the test bucket).

**Grading check:** policy correctly uses account-root `Allow` + user-specific `Deny` (or an equivalent construction using `NotPrincipal` — accept either), Block Public Access screenshot present, both the denied and allowed `GetObject` attempts are demonstrated, cleanup confirmed. Full public (`Principal: "*"`) policies should be flagged and discussed, not just marked wrong — the point is they understood why it's the less appropriate choice here.

## Part 2 — IAM Role with a Multi-Factor Condition

1. **Create the role:**
   IAM → Roles → Create role → trusted entity type: depends on how the role will be used in your Academy sandbox — "AWS account" (this account) is the simplest choice for a lab, allowing IAM users in the account to assume it.
2. **Attach managed policies:** search and attach `SecurityHubFullAccess`, `AmazonInspector2FullAccess`, `SecretsManagerReadWrite`.
3. **Add the condition.** The condition can live in the role's **trust policy** (governs who can assume the role) or in a **permissions policy** attached to the role (governs what the role can do once assumed) — either placement is a valid answer; the trust policy is the more common real-world choice for "who can assume this and under what conditions." Example trust policy:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": { "AWS": "arn:aws:iam::<ACCOUNT_ID>:root" },
         "Action": "sts:AssumeRole",
         "Condition": {
           "IpAddress": { "aws:SourceIp": "10.20.30.40/32" },
           "Bool": { "aws:MultiFactorAuthPresent": "true" }
         }
       }
     ]
   }
   ```

4. **Screenshots expected:** role summary page showing all three managed policies attached, and the trust policy (or permissions policy) JSON showing both condition keys.
5. **Expected answer (why MFA matters beyond IP):** a source-IP condition only proves *where* the request came from, not *who* is making it. If an attacker steals a user's long-lived credentials and is also on/routing through the trusted network (e.g. a compromised VPN client, a corporate laptop with malware, or a NAT'd office network), the IP condition is satisfied with a stolen identity. Requiring `aws:MultiFactorAuthPresent` means the credentials alone aren't enough — the attacker would also need the legitimate user's second factor, which is a much higher bar. This is the same point Week 2's BeyondCorp reading makes: location is one signal, not proof of identity.

**Grading check:** both managed-policy attachment and the two-condition block are visible in screenshots; written answer identifies that IP alone only proves network position, not identity.

## Part 3 — KMS Customer Managed Key

1. KMS → Customer managed keys → Create key → Key type: **Symmetric** → Key usage: **Encrypt and decrypt** → Origin: **KMS** (this is the default — AWS generates and stores the key material, which is the "AWS-generated key material" the lab asks for; this is different from an "AWS managed key" like `aws/s3`, which students cannot create themselves).
2. Add an alias (e.g. `alias/lab2-general-purpose`), optionally add tags, then define key administrators/usage permissions (default admin account is fine for a lab), and create.
3. **Screenshots expected:**
   - Key details page showing alias, Key ID, "Customer managed" under Key type, and Origin = KMS.
   - The key policy (Key policy tab) showing the JSON that controls who can administer/use the key.
   - Key rotation tab or setting showing **automatic rotation enabled** (default for new symmetric KMS keys is now on; if a student explicitly disabled it, the one-sentence explanation should reference cost or an intentional manual-rotation workflow — otherwise flag it as a miss, since Week 2's reading explicitly calls out credential/key rotation as a best practice).

**Grading check:** key is a **customer managed** key (not an attempt to "create" an AWS managed key, which isn't possible), origin is KMS-generated, key policy screenshot present, rotation status addressed either way.

## General Grading Notes

- This lab is graded for attempt and demonstrated understanding, not exact configuration matches — naming, exact ARNs, and minor JSON formatting differences are all fine.
- The most common student error will likely be Part 1: watch for `Principal: "*"` (fully public) instead of the account-root pattern. If a student did this, it's a good moment to point back to the Week 1 CampusCart incident and Week 2's least-privilege material rather than just deducting points silently.
- Part 2's condition can reasonably live in either the trust policy or a permissions policy — don't require one specific placement.
- Part 3's most common miss is confusing "customer managed key with AWS-generated material" for "AWS managed key" — this is explicitly why the lab prompt was reworded from the original phrasing, so use it as a teaching moment if it comes up.
