import time
import hashlib
from datetime import datetime, timezone

from modules.base_module import Module
from modules import economy

class_name = "QuestSystem"


class QuestSystem(Module):
    prefix = "qs"

    QUESTS = {
        # One-time starter chain
        "starter_create_avatar": {
            "type": "starter", "event": "create_avatar", "target": 1,
            "reward": economy.STARTER_QUEST_REWARDS["create_avatar"],
            "title": "Avatarını oluştur"
        },
        "starter_first_purchase": {
            "type": "starter", "event": "purchase", "target": 1,
            "reward": economy.STARTER_QUEST_REWARDS["first_purchase"],
            "title": "İlk alışverişini yap"
        },
        "starter_first_social": {
            "type": "starter", "event": "social", "target": 1,
            "reward": economy.STARTER_QUEST_REWARDS["first_social_action"],
            "title": "İlk sosyal etkileşimini yap"
        },

        # Daily
        "daily_login": {
            "type": "daily", "event": "login", "target": 1,
            "reward": economy.DAILY_QUEST_REWARDS["login"],
            "title": "Bugün oyuna giriş yap"
        },
        "daily_social": {
            "type": "daily", "event": "social", "target": 3,
            "reward": economy.DAILY_QUEST_REWARDS["social"],
            "title": "3 sosyal etkileşim yap"
        },
        "daily_shopping": {
            "type": "daily", "event": "purchase", "target": 2,
            "reward": economy.DAILY_QUEST_REWARDS["shopping"],
            "title": "2 alışveriş yap"
        },

        # Weekly
        "weekly_social": {
            "type": "weekly", "event": "social", "target": 15,
            "reward": economy.WEEKLY_QUEST_REWARDS["social_player"],
            "title": "15 sosyal etkileşim yap"
        },
        "weekly_shopper": {
            "type": "weekly", "event": "purchase", "target": 10,
            "reward": economy.WEEKLY_QUEST_REWARDS["shopper"],
            "title": "10 alışveriş yap"
        },

        # Endless activity reward. Progress is handled separately below.
        "activity_play_time": {
            "type": "activity", "event": "play_minute",
            "target": economy.ACTIVITY_QUEST_MINUTES,
            "reward": economy.ACTIVITY_QUEST_REWARD,
            "title": "Aktiflik ödülü"
        },
    }

    def __init__(self, server):
        self.server = server
        self.commands = {
            "get": self.get_quests,
            "claim": self.claim,
        }

    @staticmethod
    def _daily_period():
        return datetime.now(timezone.utc).strftime("%Y%m%d")

    @staticmethod
    def _weekly_period():
        now = datetime.now(timezone.utc)
        iso = now.isocalendar()
        return f"{iso[0]}W{iso[1]:02d}"

    def _base_period(self, quest_type):
        if quest_type == "daily":
            return self._daily_period()
        if quest_type == "weekly":
            return self._weekly_period()
        return "once"

    def _cycle_key(self, uid, quest_id, quest_type):
        return f"uid:{uid}:questcycle:{self._base_period(quest_type)}:{quest_id}"

    def _cycle(self, uid, quest_id, quest_type):
        return int(self.server.redis.get(
            self._cycle_key(uid, quest_id, quest_type)
        ) or 1)

    def _period(self, quest_type, uid=None, quest_id=None):
        base = self._base_period(quest_type)
        if uid is None or quest_id is None:
            return base
        return f"{base}:c{self._cycle(uid, quest_id, quest_type)}"

    def _progress_key(self, uid, quest_id, quest_type):
        return f"uid:{uid}:quest:{self._period(quest_type, uid, quest_id)}:{quest_id}:progress"

    def _claimed_key(self, uid, quest_id, quest_type):
        return f"uid:{uid}:quest:{self._period(quest_type, uid, quest_id)}:{quest_id}:claimed"

    def _activity_total_key(self, uid):
        return f"uid:{uid}:quest:activity:total_minutes"

    def _activity_claimed_cycles_key(self, uid):
        return f"uid:{uid}:quest:activity:claimed_cycles"

    def _activity_cycle_claim_key(self, uid, cycle):
        return f"uid:{uid}:quest:activity:cycle:{cycle}:claimed"

    def _validate_reward(self, reward):
        gold = int(reward.get("gld", 0) or 0)
        silver = int(reward.get("slvr", 0) or 0)
        energy = int(reward.get("enrg", 0) or 0)
        if gold < 0 or gold > economy.MAX_SINGLE_GOLD_REWARD:
            return False
        if silver < 0 or silver > economy.MAX_SINGLE_SILVER_REWARD:
            return False
        if energy < 0 or energy > economy.MAX_SINGLE_ENERGY_REWARD:
            return False
        return True

    def _event_for_cycle(self, quest_id, quest, cycle):
        """Keep normal quest families consistent; convert one-time actions after cycle 1."""
        cycle = max(1, int(cycle))
        if cycle == 1:
            return quest["event"]

        # These actions cannot sensibly repeat forever, so after the first
        # completion they become normal gameplay tasks.
        if quest_id == "starter_create_avatar":
            return ("purchase", "social", "play_minute")[(cycle - 2) % 3]
        if quest_id == "daily_login":
            return ("play_minute", "social", "purchase")[(cycle - 2) % 3]

        return quest["event"]

    @staticmethod
    def _event_base_target(event, quest):
        if event == "purchase":
            return max(2, int(quest.get("target", 2)))
        if event == "social":
            return max(3, int(quest.get("target", 3)))
        if event == "play_minute":
            return max(15, int(quest.get("target", 15)))
        if event == "login":
            return 1
        if event == "create_avatar":
            return 1
        return max(1, int(quest.get("target", 1)))

    def _target_for_cycle(self, quest_id, quest, cycle):
        """
        Strictly increasing, deterministic pseudo-random targets.
        Example shape: 2 -> 5 -> 8 -> 10 -> 14 ...
        A restart never changes the current cycle's target.
        """
        cycle = max(1, int(cycle))
        event = self._event_for_cycle(quest_id, quest, cycle)
        if cycle == 1:
            return int(quest["target"])

        base = self._event_base_target(event, quest)

        if event == "purchase":
            low, high = 2, 4
        elif event == "social":
            low, high = 2, 6
        elif event == "play_minute":
            low, high = 10, 20
        else:
            return 1

        target = base
        for step in range(2, cycle + 1):
            digest = hashlib.sha256(
                f"{quest_id}:{event}:{step}".encode("utf-8")
            ).digest()
            increment = low + (digest[0] % (high - low + 1))
            target += increment

        if event == "play_minute":
            target = int(round(target / 5.0) * 5)

        return max(base, target)

    def _activity_required_total(self, quest_id, quest, cycle):
        return sum(self._target_for_cycle(quest_id, quest, n)
                   for n in range(1, max(1, int(cycle)) + 1))

    def _quest_title(self, event, target, cycle):
        if event == "purchase":
            return f"Marketten {target} kıyafet/eşya al"
        if event == "social":
            return f"{target} sosyal etkileşim yap"
        if event == "play_minute":
            return f"{target} dakika aktif kal"
        if event == "login":
            return "Oyuna giriş yap"
        if event == "create_avatar":
            return "Avatarını oluştur"
        return f"Görevi {target} kez tamamla"

    def _quest_description(self, event, target, cycle):
        if event == "create_avatar":
            return "Karakterini oluştur. Tamamlandığında sonraki turda farklı bir görev açılır."
        if event == "purchase":
            return f"Marketten toplam {target} başarılı kıyafet/eşya satın al. Her satın alma otomatik sayılır."
        if event == "social":
            return f"Diğer oyuncularla toplam {target} geçerli sosyal etkileşim gerçekleştir. İlerleme otomatik kaydedilir."
        if event == "login":
            return "Oyuna giriş yap. Başarılı giriş otomatik sayılır; ödülü alınca sonraki tur farklılaşır."
        if event == "play_minute":
            return f"Oyunda toplam {target} dakika aktif kal. Süre otomatik sayılır."
        return f"Bu turdaki hedefi {target} kez tamamla."

    def record_event(self, uid, event, amount=1):
        """Trusted server-side progress entry point."""
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return
        if amount <= 0:
            return

        redis = self.server.redis

        # Activity keeps cumulative authenticated minutes so changing targets
        # never loses already-earned play time.
        if event == "play_minute":
            redis.incrby(self._activity_total_key(uid), amount)

        for quest_id, quest in self.QUESTS.items():
            if quest["type"] == "activity":
                continue

            cycle = self._cycle(uid, quest_id, quest["type"])
            cycle_event = self._event_for_cycle(quest_id, quest, cycle)
            if cycle_event != event:
                continue

            target = self._target_for_cycle(quest_id, quest, cycle)
            progress_key = self._progress_key(uid, quest_id, quest["type"])
            claimed_key = self._claimed_key(uid, quest_id, quest["type"])
            if redis.get(claimed_key):
                continue

            current = int(redis.get(progress_key) or 0)
            if current >= target:
                continue
            redis.set(progress_key, min(target, current + amount))

    def get_state(self, uid):
        result = []
        redis = self.server.redis

        for quest_id, quest in self.QUESTS.items():
            if quest["type"] == "activity":
                claimed_cycles = int(redis.get(
                    self._activity_claimed_cycles_key(uid)) or 0)
                cycle = claimed_cycles + 1
                target = self._target_for_cycle(quest_id, quest, cycle)
                total = int(redis.get(self._activity_total_key(uid)) or 0)
                previous_required = self._activity_required_total(
                    quest_id, quest, cycle - 1) if cycle > 1 else 0
                required_total = previous_required + target
                progress = max(0, min(target, total - previous_required))
                completed = total >= required_total
                event = "play_minute"

                result.append({
                    "id": quest_id,
                    "type": "activity",
                    "title": self._quest_title(event, target, cycle),
                    "event": event,
                    "progress": progress,
                    "target": target,
                    "completed": completed,
                    "claimed": False,
                    "reward": quest["reward"],
                    "cycle": cycle,
                    "total_minutes": total,
                    "description": self._quest_description(event, target, cycle),
                })
                continue

            cycle = self._cycle(uid, quest_id, quest["type"])
            event = self._event_for_cycle(quest_id, quest, cycle)
            target = self._target_for_cycle(quest_id, quest, cycle)
            progress = int(redis.get(
                self._progress_key(uid, quest_id, quest["type"])) or 0)
            claimed = bool(redis.get(
                self._claimed_key(uid, quest_id, quest["type"])))

            result.append({
                "id": quest_id,
                "type": quest["type"],
                "title": self._quest_title(event, target, cycle),
                "event": event,
                "progress": min(progress, target),
                "target": target,
                "completed": progress >= target,
                "claimed": claimed,
                "reward": quest["reward"],
                "cycle": cycle,
                "description": self._quest_description(event, target, cycle),
            })

        return result

    def get_quests(self, msg, client):
        # Opening the quest screen also counts as today's authenticated login.
        self.record_event(client.uid, "login", 1)
        client.send(["qs.get", {"quests": self.get_state(client.uid)}])

    def claim(self, msg, client):
        payload = msg[2] if len(msg) > 2 and isinstance(msg[2], dict) else {}
        quest_id = str(payload.get("id", ""))
        result = self.claim_reward(client.uid, quest_id)

        if result.get("ok"):
            user_data = self.server.get_user_data(client.uid)
            client.send(["ntf.res", {"res": {
                "gld": user_data["gld"], "slvr": user_data["slvr"],
                "enrg": user_data["enrg"], "emd": user_data["emd"]
            }}])
        client.send(["qs.claim", result])

    def claim_reward(self, uid, quest_id):
        quest = self.QUESTS.get(quest_id)
        if not quest:
            return {"ok": False, "reason": "quest_not_found"}

        reward = quest["reward"]
        if not self._validate_reward(reward):
            return {"ok": False, "reason": "invalid_reward"}

        redis = self.server.redis

        if quest["type"] == "activity":
            total = int(redis.get(self._activity_total_key(uid)) or 0)
            claimed_cycles = int(redis.get(self._activity_claimed_cycles_key(uid)) or 0)
            cycle = claimed_cycles + 1
            target = self._target_for_cycle(quest_id, quest, cycle)
            required_total = self._activity_required_total(quest_id, quest, cycle)

            if total < required_total:
                return {"ok": False, "reason": "not_completed"}

            cycle_lock = self._activity_cycle_claim_key(uid, cycle)
            if not redis.set(cycle_lock, int(time.time()), nx=True):
                return {"ok": False, "reason": "already_claimed"}

            try:
                pipe = redis.pipeline()
                gold = int(reward.get("gld", 0) or 0)
                silver = int(reward.get("slvr", 0) or 0)
                energy = int(reward.get("enrg", 0) or 0)
                if gold:
                    pipe.incrby(f"uid:{uid}:gld", gold)
                if silver:
                    pipe.incrby(f"uid:{uid}:slvr", silver)
                if energy:
                    pipe.incrby(f"uid:{uid}:enrg", energy)
                pipe.incrby(self._activity_claimed_cycles_key(uid), 1)
                pipe.execute()
            except Exception:
                redis.delete(cycle_lock)
                raise

            return {
                "ok": True, "id": quest_id, "reward": reward,
                "activity_cycle": cycle
            }
        progress_key = self._progress_key(uid, quest_id, quest["type"])
        claimed_key = self._claimed_key(uid, quest_id, quest["type"])

        cycle = self._cycle(uid, quest_id, quest["type"])
        target = self._target_for_cycle(quest_id, quest, cycle)
        if int(redis.get(progress_key) or 0) < target:
            return {"ok": False, "reason": "not_completed"}

        # Redis SET NX is the anti-double-claim lock.
        lock = redis.set(claimed_key, int(time.time()), nx=True)
        if not lock:
            return {"ok": False, "reason": "already_claimed"}

        try:
            pipe = redis.pipeline()
            gold = int(reward.get("gld", 0) or 0)
            silver = int(reward.get("slvr", 0) or 0)
            energy = int(reward.get("enrg", 0) or 0)
            if gold:
                pipe.incrby(f"uid:{uid}:gld", gold)
            if silver:
                pipe.incrby(f"uid:{uid}:slvr", silver)
            if energy:
                pipe.incrby(f"uid:{uid}:enrg", energy)
            pipe.execute()
        except Exception:
            # Allow retry if the balance update itself failed.
            redis.delete(claimed_key)
            raise

        redis.incr(self._cycle_key(uid, quest_id, quest["type"]))

        return {
            "ok": True,
            "id": quest_id,
            "reward": reward,
            "next_cycle": self._cycle(uid, quest_id, quest["type"])
        }

    def record_play_minutes(self, uid, minutes):
        """Call this from a trusted server timer/heartbeat."""
        self.record_event(uid, "play_minute", minutes)
