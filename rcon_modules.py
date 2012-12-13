# rcon_modules.py
#    This file is part of pyBEscanner.
#
#    pyBEscanner is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pyBEscanner is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pyBEscanner.  If not, see <http://www.gnu.org/licenses/>.


## Workaround & Placeholder until get around to writing python code to connect to servers via rcon...
import subprocess
import os

class Rcon:
	def __init__(self, ip, port, password):

		# Initialize Variables
		self.ip = ip
		self.port = port
		self.password = password


	def kickplayers(self, kickfile):
		temp = os.path.join("rcon", ("rcon_kick.exe"))
		subprocess.call([temp, "--ip=" + self.ip, "--port=" + self.port, "--password=" + self.password, "--file=" + kickfile])

	def reloadbans(self):
		temp = os.path.join(os.getcwd(), "rcon", ("rcon_reloadbans.exe"))
		subprocess.call([temp, self.ip, str(self.port), self.password])
