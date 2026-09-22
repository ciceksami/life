import operator
from modules.base_module import Module

class_name = "UserRating"


class UserRating(Module):
    prefix = "ur"

    def __init__(self, server):
        self.server = server
        self.commands = {"get": self.get, "gar": self.get_activity}

    def get(self, msg, client):
        users = {}
        max_uid = int(self.server.redis.get("uids") or 0)
        for i in range(1, max_uid+1):
            hrt = self.server.redis.get(f"uid:{i}:hrt")
            if not hrt or not self.server.get_appearance(i):
                continue  # check for not created avatar
            users[i] = int(hrt)
        sorted_users = sorted(users.items(), key=operator.itemgetter(1),
                              reverse=True)
        best_top = []
        i = 1
        for user in sorted_users:
            cr = int(self.server.redis.get(f"uid:{user[0]}:crt") or 0)
            best_top.append({"uid": user[0], "hr": user[1], "cr": cr})
            if i == 10:
                break
            i += 1
        client.send(["ur.get", {"bt": best_top}])

    def get_activity(self, msg, client):
        """Return the top 10 players by server-side activity/report score (rpt)."""
        users = []
        max_uid = int(self.server.redis.get("uids") or 0)
        for uid in range(1, max_uid + 1):
            if not self.server.get_appearance(uid):
                continue
            score = int(self.server.redis.get(f"uid:{uid}:rpt") or 0)
            users.append((uid, score))

        users.sort(key=lambda item: item[1], reverse=True)
        best_top = []
        for uid, score in users[:10]:
            crt = int(self.server.redis.get(f"uid:{uid}:crt") or 0)
            best_top.append({"uid": uid, "hr": score, "cr": crt})
        client.send(["ur.gar", {"bt": best_top}])
