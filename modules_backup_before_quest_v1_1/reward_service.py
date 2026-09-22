import time


class RewardService:
    """Redis-backed daily reward/promo helper.

    This helper intentionally does not invent a SWF command. It can be called by
    web/admin/server code safely and wired to the client once the exact packet is known.
    """

    DAILY_REWARDS = [
        {"slvr": 500},
        {"gld": 1},
        {"slvr": 1000},
        {"enrg": 10},
        {"gld": 2},
        {"slvr": 2500},
        {"gld": 5},
    ]

    PROMOS = {
        "YENIDEN2017": {"gld": 10, "slvr": 5000},
        "AVATARLIFE": {"gld": 5, "enrg": 25},
    }

    def __init__(self, server):
        self.server = server

    def _add_resources(self, uid, reward):
        pipe = self.server.redis.pipeline()
        for field in ("gld", "slvr", "enrg", "emd"):
            amount = int(reward.get(field, 0) or 0)
            if amount > 0:
                pipe.incrby(f"uid:{uid}:{field}", amount)
        pipe.execute()

    def claim_daily(self, uid):
        now = int(time.time())
        day = now // 86400
        last = int(self.server.redis.get(f"uid:{uid}:daily:last") or -1)
        if last == day:
            return {"ok": False, "reason": "already_claimed"}

        previous = int(self.server.redis.get(f"uid:{uid}:daily:day") or -2)
        streak = int(self.server.redis.get(f"uid:{uid}:daily:streak") or 0)
        streak = streak + 1 if previous == day - 1 else 1
        reward = self.DAILY_REWARDS[(streak - 1) % len(self.DAILY_REWARDS)]

        self._add_resources(uid, reward)
        pipe = self.server.redis.pipeline()
        pipe.set(f"uid:{uid}:daily:last", day)
        pipe.set(f"uid:{uid}:daily:day", day)
        pipe.set(f"uid:{uid}:daily:streak", streak)
        pipe.execute()
        return {"ok": True, "streak": streak, "reward": reward}

    def redeem_promo(self, uid, code):
        code = (code or "").strip().upper()
        reward = self.PROMOS.get(code)
        if not reward:
            return {"ok": False, "reason": "invalid_code"}
        used_key = f"promo:{code}:used"
        if self.server.redis.sismember(used_key, uid):
            return {"ok": False, "reason": "already_used"}
        self._add_resources(uid, reward)
        self.server.redis.sadd(used_key, uid)
        return {"ok": True, "reward": reward}
