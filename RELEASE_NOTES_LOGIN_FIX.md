# Release Notes — Login & OTP Bug Fixes

**Release Date:** February 8, 2026  
**Branch:** `sathishdev_fixes`  
**Severity:** Critical  

---

## Summary

This release resolves critical authentication issues affecting both the **Patient Mobile App (OTP Login)** and the **Admin Portal (Email/Password Login)**. Users were experiencing:

1. **"Account Locked"** errors after multiple login attempts, with no clear recovery path.
2. **"Invalid OTP"** errors even when entering the correct OTP received via SMS.

---

## Issues Fixed

### 1. Patient App — Correct OTP Rejected as "Invalid OTP"

**Problem:** After a user entered a wrong OTP (or faced a network issue during verification), subsequent attempts — even with the correct OTP — returned "Invalid OTP". The system was not distinguishing between a wrong OTP, an expired OTP, and an account lockout.

**Root Cause:** Missing configuration values (`WRONG_OTP_ATTEMPT_ERROR`, `MAX_WRONG_OTP_ATTEMPT_ERROR`, `HARDCODED_MOBILE_NO_OTP`) caused internal server errors that were silently caught and displayed as "Invalid OTP" to the user.

**Fix:** Added the missing configuration values and updated error handling to return specific, actionable messages based on the actual failure reason.

---

### 2. Patient App — Account Locked After Failed OTP Attempts

**Problem:** After 3 incorrect OTP entries, the account was locked. Even after the 1-minute cooloff period, when the user requested a **new OTP** and entered it correctly, the system still reported "Invalid OTP" or "Account Locked".

**Root Cause:** When a new OTP was requested, the previous lockout records were not cleared. The authentication system still treated the user as locked based on stale records.

**Fix:** When a new OTP is requested (via Login or Resend OTP), any previous lockout records are now automatically cleared, allowing fresh authentication.

---

### 3. Admin Portal — Account Locked with No Recovery

**Problem:** After 3 incorrect password attempts on the Admin Portal login, the system locked the account and returned an unhandled error. There was no clear error message, and in some cases the server returned a 500 error.

**Root Cause:** The admin login endpoint (`admin/login/`) uses Django's `authenticate()` function, which is protected by a rate-limiting library (django-axes). When the account was locked, the library raised an exception that was not handled, causing an uncontrolled error response.

**Fix:** Added proper error handling that catches the lockout condition and returns a clear message: *"Account locked due to too many failed attempts. Please try again after 1 minute."* Successful logins now also clear any stale lockout records.

---

### 4. Admin Portal — Server Crash on Invalid Email

**Problem:** If an admin entered an email address that didn't exist in the system, the server crashed with an internal error instead of returning "Invalid credentials".

**Root Cause:** The code attempted to check the password against a `None` user object without first verifying the user exists.

**Fix:** Added a null check that returns "Invalid credentials" when the email is not found.

---

### 5. Timezone-Related OTP Expiry Issues

**Problem:** In some cases, OTPs appeared expired immediately after being generated, or remained valid beyond their intended 5-minute window.

**Root Cause:** The OTP expiry time was calculated using the system's local clock without timezone information, while the database stores timezone-aware timestamps. This mismatch caused incorrect expiry comparisons.

**Fix:** All OTP expiry calculations and comparisons now use timezone-aware timestamps consistent with the server's configured timezone (Asia/Kolkata).

---

## Error Messages — Before vs After

| Scenario | Before | After |
|---|---|---|
| Wrong OTP (1st or 2nd attempt) | "Invalid OTP" | "Invalid OTP. Attempt 1 of 3." |
| Wrong OTP (3rd attempt) | "Invalid OTP" | "Account locked due to too many failed attempts. Please try again after 1 minute." |
| Correct OTP after lockout + new OTP request | "Invalid OTP" | Login succeeds ✅ |
| OTP expired (after 5 minutes) | "Invalid OTP" | "OTP expired" |
| Admin wrong password (3+ times) | 500 Internal Server Error | "Account locked due to too many failed attempts. Please try again after 1 minute." |
| Admin invalid email | 500 Internal Server Error | "Invalid credentials" |

---

## Lockout Policy

| Setting | Value |
|---|---|
| Maximum failed attempts before lockout | **3** |
| Lockout duration | **1 minute** |
| OTP validity period | **5 minutes** |
| Lockout resets on | New OTP request or successful login |

---

## Affected Endpoints

| Endpoint | Type | Fix Applied |
|---|---|---|
| `POST api/users/login/` | Patient OTP Request | Clears lockout on new OTP, timezone fix |
| `POST api/users/verify_login_otp/` | Patient OTP Verify | Specific error messages, timezone fix |
| `POST api/users/resend-otp/` | Patient OTP Resend | Clears lockout on resend, timezone fix |
| `POST admin/login/` | Admin Login | Lockout handling, clear message |
| `POST api/admin/user/login/` | Admin Login (alt) | Null check for missing user |

---

## Files Changed

| File | Change Summary |
|---|---|
| `KALAKSHETRA/settings.py` | Added 3 missing configuration constants for error messages |
| `utils/utils.py` | Fixed OTP verification to handle lockout exceptions and return proper error messages |
| `apps/users/views.py` | Fixed OTP login/verify/resend: timezone handling, lockout reset, specific error responses |
| `user_details/views.py` | Fixed admin login: lockout exception handling, stale record cleanup, safety fallback |

---

## Testing Recommendations

Please verify the following scenarios after deployment:

### Patient App
- [ ] Request OTP → Enter correct OTP → Login succeeds
- [ ] Request OTP → Enter wrong OTP 3 times → See "Account locked" message
- [ ] After lockout → Wait 1 minute → Request new OTP → Enter correct OTP → Login succeeds
- [ ] Request OTP → Wait 6 minutes → Enter OTP → See "OTP expired" message
- [ ] Request OTP → Enter wrong OTP once → See attempt count message → Enter correct OTP → Login succeeds

### Admin Portal
- [ ] Enter correct email/password → Login succeeds
- [ ] Enter wrong password 3 times → See "Account locked" message (not server error)
- [ ] After lockout → Wait 1 minute → Enter correct password → Login succeeds
- [ ] Enter non-existent email → See "Invalid credentials" (not server error)

---

## Emergency: Unlocking Accounts Manually

If needed, accounts can be unlocked immediately via the Django management shell:

```bash
python manage.py shell
```

```python
# Unlock a specific user
from axes.models import AccessAttempt
AccessAttempt.objects.filter(username='<mobile_or_email>').delete()

# Unlock all locked accounts
AccessAttempt.objects.all().delete()
```

Or via the Django admin panel at `/admin/axes/accessattempt/`.

---

*For questions or issues, contact the development team.*
