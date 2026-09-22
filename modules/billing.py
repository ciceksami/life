from modules.base_module import Module

class_name = "Billing"


class Billing(Module):
    prefix = "b"

    # Economy setting: 1 gold -> 100 silver.
    GOLD_TO_SILVER_RATE = 100

    def __init__(self, server):
        self.server = server
        self.commands = {"chkprchs": self.check_purchase,
                         "bs": self.buy_silver}

    def _send_resources(self, client, user_data):
        client.send(["ntf.res", {"res": {
            "gld": int(user_data["gld"]),
            "slvr": int(user_data["slvr"]),
            "enrg": int(user_data["enrg"]),
            "emd": int(user_data["emd"])
        }}])

    def check_purchase(self, msg, client):
        # Classic Avatar Life gold shop:
        # whichever original package is clicked is credited directly.
        # No payment, cooldown, or staff-role requirement.
        try:
            product_id = str(msg[2]["prid"])
            if "pack" not in product_id:
                return
            amount = int(product_id.rsplit("pack", 1)[1])
        except (KeyError, TypeError, ValueError, IndexError):
            return

        # Only allow the package values present in the classic shop.
        allowed_packages = {10, 30, 50, 100, 200, 500, 1000, 1500}
        if amount not in allowed_packages:
            return

        user_data = self.server.get_user_data(client.uid)
        if not user_data:
            return

        gold = int(user_data["gld"]) + amount
        self.server.redis.set(f"uid:{client.uid}:gld", gold)

        updated = self.server.get_user_data(client.uid)
        self._send_resources(client, updated)
        client.send(["b.ingld", {"ingld": amount}])

    def buy_silver(self, msg, client):
        # Gold -> silver exchange remains available to normal players,
        # but the amount is validated server-side.
        try:
            amount = int(msg[2]["gld"])
        except (KeyError, TypeError, ValueError):
            return

        if amount <= 0 or amount > 1000000:
            return

        user_data = self.server.get_user_data(client.uid)
        if not user_data:
            return

        current_gold = int(user_data["gld"])
        current_silver = int(user_data["slvr"])
        if current_gold < amount:
            return

        new_gold = current_gold - amount
        silver_reward = amount * self.GOLD_TO_SILVER_RATE
        new_silver = current_silver + silver_reward

        # Atomic balance update.
        pipe = self.server.redis.pipeline()
        pipe.set(f"uid:{client.uid}:gld", new_gold)
        pipe.set(f"uid:{client.uid}:slvr", new_silver)
        pipe.execute()

        updated = self.server.get_user_data(client.uid)
        self._send_resources(client, updated)
        client.send(["b.inslv", {"inslv": silver_reward}])
