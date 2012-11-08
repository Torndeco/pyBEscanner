## Workaround & Placeholder until get around to writing python code to connect to servers via rcon...
import subprocess
import os

class Rcon:
	def __init__(self, ip, port, password):
	
		# Initialize Variables
		self.ip = ip
		self.port = port
		
		self.password = password
		
	def connect(self):
		pass
		
	def kickplayer(self, playername):
		temp = os.path.join("rcon", ("rcon_kickplayer_" + str(self.port) + ".exe"))
		#subprocess.call([temp, playername])
		
	def reloadbans(self):
		temp = os.path.join(os.getcwd(), "rcon", ("rcon_reloadbans_" + str(self.port) + ".exe"))
		print str(temp)
		subprocess.call([temp, self.ip, str(self.port), self.password])

	
	def reloadfilters(self):
		pass
		
	def disconnect(self):
		pass
