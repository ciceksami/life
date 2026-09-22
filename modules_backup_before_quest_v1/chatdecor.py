from modules.base_module import Module
from modules.location import refresh_avatar
import time
import logging

class_name = "Chatdecor"


class Chatdecor(Module):
	prefix = "chtdc"

	def __init__(self, server):
		self.server = server
		self.commands = {"schtm": self.satinal  }


	def satinal(self, msg, client): 
		 tcl = msg[2]["chtdc"]["tcl"]
		 bdc = msg[2]["chtdc"]["bdc"]
		 redis = self.server.redis
		 redis.set(f"uid:{client.uid}:tcl", f"{tcl}")
		 redis.set(f"uid:{client.uid}:bdc", f"{bdc}")
		 refresh_avatar(client, self.server)
		 client.send(["cp.ms.rsm", {"txt": f"Sohbet dekorunuz başarılı bir şekilde değiştirildi."}])
		 
