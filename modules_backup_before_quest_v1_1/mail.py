from modules.base_module import Module
import json
import time

class_name = "Mail"


class Mail(Module):
    prefix = "mail"

    def __init__(self, server):
        self.server = server
        self.commands = {"gc": self.get_collection}

    def get_collection(self, msg, client):
        inbox = []
        key = f"uid:{client.uid}:mail:in"
        for raw in self.server.redis.lrange(key, 0, 49):
            try:
                item = json.loads(raw)
                if isinstance(item, dict):
                    inbox.append(item)
            except (TypeError, ValueError):
                continue
        client.send(["mail.gc", {"in": inbox, "out": []}])

    def add_system_mail(self, uid, subject, text, sender="Avatar Life"):
        """Server-side helper for future rewards/events/admin tools."""
        mail_id = self.server.redis.incr("mail:ids")
        item = {
            "id": int(mail_id),
            "sid": "0",
            "sn": sender,
            "sbj": str(subject)[:120],
            "txt": str(text)[:2000],
            "tm": int(time.time()),
            "rd": False
        }
        self.server.redis.lpush(f"uid:{uid}:mail:in", json.dumps(item, ensure_ascii=False))
        self.server.redis.ltrim(f"uid:{uid}:mail:in", 0, 49)
        return item
