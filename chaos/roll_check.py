import hashlib


def roll(key: str) -> int:
    return int(hashlib.sha256(key.encode()).hexdigest(), 16) % 100


def expected(r: int) -> str:
    if r < 60:
        return "200"
    if r < 75:
        return "429"
    if r < 85:
        return "500"
    if r < 95:
        return "HANG (30s)"
    return "200 slow (1.5s)"


for attempt in range(10):
    r = roll(f"a:{attempt}")
    print(f"attempt {attempt}: roll={r:2d}  expect={expected(r)}")