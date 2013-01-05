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
import ConfigParser
import time
import copy
import re
import sys

from modules import bans, logs_battleye, rcon_cscript



class Main:
	def __init__(self, args):
		print
		self.main_dir = os.getcwd()
		conf_dir = os.path.join(self.main_dir, 'conf')
		logs_dir = os.path.join(self.main_dir, "logs")
		temp_dir = os.path.join(self.main_dir, "temp")

		self.lockfile = os.path.join(temp_dir, "pyBEscanner.lockfile")
		self.conf_file = os.path.join(self.main_dir, 'conf', 'servers.ini')
		
		if not os.path.isfile(os.path.join(self.main_dir, 'pyBEscanner.py')):
			print "Wrong working Directory"
			sys.exit()
		else:
			if not os.path.exists(conf_dir):
				print "Missing Conf Directory @ " + self.conf_dir
				sys.exit()
			else:
				if not os.path.isfile(self.conf_file):
					print "Missing Server Configs @ " + self.conf_file
					sys.exit()

		if not os.path.exists(temp_dir):
			os.mkdir(temp_dir)
			
		if not os.path.exists(logs_dir):
			os.mkdir(logs_dir)

		if (os.path.isfile(self.lockfile) == True) and (args.force_start == False):
			print("LockFile Detected")
			print("This means another pyBEscanner is either running or the previous instance of pyBEscanner crashed")
			print("To start pyBEscanner, Use -f switch to ignore the lockfile")
			sys.exit()
		else:
			open(self.lockfile, 'w').close()

		config = ConfigParser.ConfigParser()
		config.read(self.conf_file)
		if config.has_option("Default", "Version"):
			if config.get("Default", "Version") != "15":
				print "-------------------------------------------------"
				print "ERROR: Bad conf/servers.ini version"
				print "-------------------------------------------------"
				print "Read Changes.txt for more info"
				print "Old version = " + config.get("Default", "Version")
				sys.exit()
		else:
			print "-------------------------------------------------"
			print "ERROR: No servers.ini version found"
			print "-------------------------------------------------"
			print "This either means a mistake in your servers.ini file,"
			print "Look @ servers-example.ini"
			print
			print "Or if u haven't updated in awhile"
			print "Recommend u delete pyBEscanner temp folders & read Changes.txt for update changes"
			sys.exit()

	def loadconfig(self):

		config = ConfigParser.ConfigParser()
		config.read(self.conf_file)
		config_sections= config.sections()
		config_sections.remove("Default")

		default = {"pyBEscanner Directory": self.main_dir}
		self.server_settings = []
		# Ban.txt  File Location
		if config.has_option("Default", "Bans Directory"):
			default["Bans Directory"] = config.get("Default", "Bans Directory")
			default["Bans"] = None
			# Doesnt initializes bans, until encounters a server with symlink setting turned on

		options = [["Scan Addbackpackcargo", "addbackpackcargo"],
					["Scan Addmagazinecargo", "addmagazinecargo"],
					["Scan Addweaponcargo", "addweaponcargo"],
					["Scan Attachto", "attachto"],
					["Scan Createvehicle", "createvehicle"],
					["Scan Deletevehicle", "deletevehicle"],
					["Scan Mpeventhandler", "mpeventhandler"],
					["Scan Publicvariable", "publicvariable"],
					["Scan Remotecontrol", "remotecontrol"],
					["Scan Remoteexec", "remoteexec"],
					["Scan Scripts", "scripts"],
					["Scan Setdamage", "setdamage"],
					["Scan Selectplayer", "selectplayer"],
					["Scan Setpos", "setpos"],
					["Scan Setvariable", "setvariable"],
					["Scan Teamswitch", "teamswitch"],
					["OffSet", "OffSet"],
					["Ban Message", "Ban Message"],
					["Kick Message", "Kick Message"],
					["Report Message", "Report Message"],
					["Ban IP", "Ban IP"],
					["Filters", "Filters"],
					["Bans Symlinked", "Bans Symlinked"]]

		## Scan Settings -- Default
		self.interval = int(config.get("Default", "interval", "60"))

		for x in range(len(options)):
			default[options[x][1]] = config.get("Default", options[x][0])

		## Debug Settings
		if config.has_option("Default", "Debug File"):
			self.debug_file = config.get("Default", "Debug File")
		else:
			self.debug_file = os.path.join(self.main_dir, "debug.log")

		if config.has_option("Default", "Debug Level"):
			self.debug_level = config.get("Default", "Debug Level")
		else:
			self.debug_level = "WARNING"

		for section in config_sections:
			server = copy.copy(default)

			## Server Info
			server["ServerName"] = config.get(section, "ServerName")
			server["ServerIP"] = config.get(section, "ServerIP")
			server["ServerPort"] = config.get(section, "ServerPort")
			server["RconPassword"] = config.get(section, "RconPassword")
			server["BattlEye Directory"] = config.get(section, "BattlEye Directory")
			server["Server Console Log"] = config.get(section, "Server Console Log")
			server["Server RPT Log"] = config.get(section, "Server RPT Log")
			server["Temp Directory"] = os.path.join(self.main_dir, "temp", section)
			server["Logs Directory"] = os.path.join(self.main_dir, "logs", section)
			server["LockFile"] = os.path.join(server["Temp Directory"], "scan-stopped.lockfile")
			server["LockFile-Ask"] = os.path.join(server["Temp Directory"], "scan-stop-ask.lockfile")

			for y in range(len(options)):
				if config.has_option(section, options[y][0]):
					server[options[y][1]] = config.get(section, options[y][0])

			server["Filters"] = re.sub(",\s*", ",", server["Filters"])
			temp_filters = server["Filters"].split(",")
			server["Filters"] = []
			for filters in temp_filters:
				if filters == "Custom":
					server["Filters"].append(os.path.join(server["BattlEye Directory"], "pyBEscanner", "filters"))
				else:
					server["Filters"].append(os.path.join(self.main_dir, "filters", filters))

			if server["Bans Symlinked"] == "on":
				if default["Bans"] == None:
					default["Bans"] = bans.Bans(default["Bans Directory"])
				server["Bans"] = default["Bans"]
			else:
				default["Bans"] = bans.Bans(server["BattlEye Directory"])

			# Generated Settings
			server["Battleye Logs"] = ["addbackpackcargo",
											"addmagazinecargo",
											"addweaponcargo",
											"attachto",
											"createvehicle",
											"deletevehicle",
											"mpeventhandler",
											"publicvariable",
											"remotecontrol",
											"remoteexec",
											"selectplayer",
											"scripts",
											"setdamage",
											"setpos",
											"setvariable",
											"teamswitch"]

			server["Battleye Logs Location"] = {}
			server["Battleye Temp Logs"] = {}
			server["Battleye Backup Logs"] = {}  # TODO

			server["Banlist Filters"] = {}
			server["Kicklist Filters"] = {}
			server["Whitelist Filters"] = {}
			server["Spamlist Filters"] = {}


			for be_log in server["Battleye Logs"]:
				server["Battleye Logs Location"][be_log] = os.path.join(server["BattlEye Directory"], (be_log + ".log"))
				server["Battleye Temp Logs"][be_log] = os.path.join(server["Temp Directory"], (be_log + ".log"))

				server["Banlist Filters"][be_log] = []
				server["Kicklist Filters"][be_log] = []
				server["Whitelist Filters"][be_log] = []
				server["Spamlist Filters"][be_log] = []

				for filters in server["Filters"]:
					server["Banlist Filters"][be_log].append(os.path.join(filters, be_log + ".banlist"))
					server["Kicklist Filters"][be_log].append(os.path.join(filters, be_log + ".kicklist"))
					server["Whitelist Filters"][be_log].append(os.path.join(filters, be_log + ".whitelist"))
					server["Spamlist Filters"][be_log].append(os.path.join(filters, be_log + ".spamlist"))
			self.server_settings.append(server)


	def start(self):
		old_config_timestamp = None
		scan_count = 60
		while True:
			try:
				new_config_timestamp = os.path.getmtime(self.conf_file)
				if old_config_timestamp != new_config_timestamp:
					print "---------------------------------------------------------"
					print "       Loading Config File"
					print "---------------------------------------------------------"
					self.loadconfig()
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

				for server in self.server_settings:
					if os.path.isfile(server["LockFile"]):
						print
						print("LockFile Detected - Skipping " + server["ServerName"])
						scan_count = 60
					else:
						bans_file = os.path.join(server["BattlEye Directory"], "bans.txt")
						if os.path.isfile(bans_file) is False:
							open(bans_file, 'w').close()
						server["Bans.txt Timestamp"] = os.path.getmtime(bans_file)
						logs_battleye.Scanner(server).scan()
						if os.path.isfile(server["LockFile-Ask"]):
							print()
							print("LockFile Detected, Finished Scanning Logs for Server " + server["ServerName"])
							#logs_server.ConsoleScanner(server).scan_log(0)
							#logs_server.RPTScanner(server).scan_log(0)
							open(server["LockFile"], 'w').close()
						else:
							pass
							#logs_server.ConsoleScanner(server).scan_log()
							#logs_server.RPTScanner(server).scan_log()

				for server in self.server_settings:
					kicks_file = os.path.join(server["BattlEye Directory"], "kicks.txt")
					if os.path.isfile(kicks_file) is True:
						rcon = rcon_cscript.Rcon(server["ServerIP"], server["ServerPort"], server["RconPassword"])
						rcon.kickplayers(kicks_file)
						os.remove(kicks_file)
						scan_count = 60

				for server in list(self.server_settings):
					server["Bans"].checkBans()
					if server["Bans"].getStatus() == True:
						print
						print ("Reloading Bans: " + server["ServerName"])
						logging.info("Reloading Bans")
						server["Bans"].writeBans()
						rcon = rcon_cscript.Rcon(server["ServerIP"], server["ServerPort"], server["RconPassword"])
						rcon.reloadbans()
						scan_count = 60
				for server in list(self.server_settings):
					server["Bans"].updateStatus(False)

				time.sleep(self.interval)
			except KeyboardInterrupt:
				print()
				print("Removing LockFile....")
				os.remove(self.lockfile)
				sys.exit()

parser = argparse.ArgumentParser(description='pyBEscanner Options...')
parser.add_argument('--force-start', '-f', action='store_true')
args = parser.parse_args()
main = Main(args)
main.start()
