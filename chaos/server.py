import asyncio
import hashlib
from collections import defaultdict

from fastapi import FastAPI, Response

app = FastAPI()
attempts: dict[str, int] = defaultdict(int)


def roll(key: str) -> int:
    """Deterministic 0-99 value derived from the key."""
    return int(hashlib.sha256(key.encode()).hexdigest(), 16) % 100


@app.get("/r/{rid}")
async def resource(rid: str):
    attempt = attempts[rid]
    attempts[rid] += 1  # no await before this line, so it is atomic on the event loop
    r = roll(f"{rid}:{attempt}")

    if r < 60:                       # 60%: success
        return {"id": rid, "attempt": attempt}
    if r < 75:                       # 15%: rate limited
        return Response(status_code=429, headers={"Retry-After": "1"})
    if r < 85:                       # 10%: server error
        return Response(status_code=500)
    if r < 95:                       # 10%: hang past any sane timeout
        await asyncio.sleep(30)
        return {"id": rid}
    await asyncio.sleep(1.5)         # 5%: slow but successful
    return {"id": rid, "slow": True}


@app.post("/reset")
def reset():
    attempts.clear()
    return {"ok": True}