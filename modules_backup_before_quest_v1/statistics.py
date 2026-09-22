from modules.base_module import Module
import time

class_name = "Statistics"


class Statistics(Module):
    prefix = "stat"

    def __init__(self, server):
        self.server = server
        self.commands = {"urlnv": self.log_url_navigate}

    def log_url_navigate(self, msg, client):
        payload = msg[2] if len(msg) > 2 and isinstance(msg[2], dict) else {}
        url = str(payload.get("url") or payload.get("u") or payload.get("lnk") or "")[:1000]
        if not url:
            return
        key = f"uid:{client.uid}:urlnav"
        self.server.redis.lpush(key, f"{int(time.time())}|{url}")
        self.server.redis.ltrim(key, 0, 99)
