# Filename: pyBEScanner.py
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

#!/usr/bin/python

import argparse
import os
import platform
import sys
import time

from modules import settings, logs_battleye, logs_server, rcon_cscript


class Main:
	def __init__(self, args):
		self.config = settings.Settings()
		

	def start(self):
		old_config_timestamp = None
		scan_count = 60
		os_name = platform.system()
		print "---------------------------------------------------------"
		print "System Platform = " + os_name
		print "---------------------------------------------------------"
		while True:
			try:
				new_config_timestamp = os.path.getmtime(self.config.get_config_file())
				if old_config_timestamp != new_config_timestamp:
					print "---------------------------------------------------------"
					print "       Loading Config File"
					print "---------------------------------------------------------"
					interval, server_ban_deamon, server_settings = self.config.load_config()
					old_config_timestamp = new_config_timestamp
					scan_count = 60
					
				if scan_count == 60:
					print
					sys.stdout.write('Scanning .')
					sys.stdout.flush()
					scan_count = 0
				else:
					sys.stdout.write('.')
					sys.stdout.flush()
					scan_count = scan_count + 1

				for server in server_settings:
					if os.path.isfile(server["LockFile"]):
						print
						print("LockFile Detected - Skipping " + server["ServerName"])
						scan_count = 60
					else:
						logs_battleye.Scanner(server, server_ban_deamon).scan()
						if server["Scan Server Logs"] == "on":
							#player_tracker_data_file = os.path.join(server["Temp Directory"], "server_player_tracker.offset")
							#player_tracker = logs_server.PlayerTracker(server, player_tracker_data_file, server_ban_deamon)
							#logs_server.ConsoleScanner(server, player_tracker).scan_log(0)
							#logs_server.RPTScanner(server, player_tracker).scan_log(0)
							pass
						if os.path.isfile(server["LockFile-Ask"]):
							print
							print("LockFile Detected, Finished Scanning Logs for Server " + server["ServerName"])
							open(server["LockFile"], 'w').close()

				for server in server_settings:
					kicks_file = os.path.join(server["BattlEye Directory"], "kicks.txt")
					if os.path.isfile(kicks_file) is True:
						print
						rcon = rcon_cscript.Rcon(os_name, server["ServerIP"], server["ServerPort"], server["RconPassword"])
						rcon.kickplayers(kicks_file)
						os.remove(kicks_file)
						scan_count = 60

				for server in server_settings:
					server_ban_deamon.checkBans(server["Server ID"])					
					if server_ban_deamon.getStatus(server["Server ID"]) == True:
						print
						print ("Reloading Bans: " + server["ServerName"])
						server_ban_deamon.writeBans(server["Server ID"])
						rcon = rcon_cscript.Rcon(os_name, server["ServerIP"], server["ServerPort"], server["RconPassword"])
						rcon.reloadbans()
						scan_count = 60
				for server in server_settings:
					server_ban_deamon.updateStatus(server["Server ID"], False)

				time.sleep(interval)
			except KeyboardInterrupt:
				print
				print("Stopping pyBEscanner....")
				print
				sys.exit()

parser = argparse.ArgumentParser(description='pyBEscanner Options...')
args = parser.parse_args()
main = Main(args)
main.start()
