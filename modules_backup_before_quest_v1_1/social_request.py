from modules.base_module import Module
import json
import time

class_name = "SocialRequest"


class SocialRequest(Module):
    prefix = "srqst"

    def __init__(self, server):
        self.server = server
        self.commands = {"gtit": self.get_item,
                         "gtrq": self.get_requests}

    def get_item(self, msg, client):
        items = self._load(client.uid)
        client.send(["srqst.gtit", {"sreqs": items, "sress": [], "mct": len(items)}])

    def get_requests(self, msg, client):
        items = self._load(client.uid)
        client.send(["srqst.gtrq", {"rqlst": {"shwdt": int(time.time()),
                                               "rsprlst": {},
                                               "lapt": {},
                                               "rlst": {str(i): v for i, v in enumerate(items)}}}])

    def _load(self, uid):
        result = []
        for raw in self.server.redis.lrange(f"uid:{uid}:social_requests", 0, 49):
            try:
                item = json.loads(raw)
                if isinstance(item, dict):
                    result.append(item)
            except (TypeError, ValueError):
                continue
        return result

    def add_request(self, uid, data):
        """Server-side helper. Client packet shape can be refined after SWF capture."""
        if not isinstance(data, dict):
            return False
        self.server.redis.lpush(f"uid:{uid}:social_requests",
                                json.dumps(data, ensure_ascii=False))
        self.server.redis.ltrim(f"uid:{uid}:social_requests", 0, 49)
        return True
