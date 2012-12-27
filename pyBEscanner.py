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

import os
import ConfigParser
import time
import copy
import logging
import re

import battleye_modules
import rcon_modules
from sys import exit


class Main:
	def __init__(self):
		print
		self.main_dir = os.getcwd()
		self.conf_dir = os.path.join(self.main_dir, 'conf')

		self.conf_file = os.path.join(self.main_dir, 'conf', 'servers.ini')
		if not os.path.isfile(os.path.join(self.main_dir, 'pyBEscanner.py')):
			print "Wrong working Directory"
			exit()
		else:
			if not os.path.exists(self.conf_dir):
				print "Missing Conf Directory @ " + self.conf_dir
				exit()
			else:
				if not os.path.isfile(self.conf_file):
					print "Missing Server Configs @ " + self.conf_file
					exit()

		self.config = ConfigParser.ConfigParser()
		self.config.read(self.conf_file)
		if self.config.has_option("Default", "Version"):
			if self.config.get("Default", "Version") != "12":
				print "-------------------------------------------------"
				print "ERROR: Bad conf/servers.ini version"
				print "-------------------------------------------------"
				print "Read Changes.txt for more info"
				print "Old version = " + self.config.get("Default", "Version")
				exit()
		else:
			print "-------------------------------------------------"
			print "ERROR: No servers.ini version found"
			print "-------------------------------------------------"
			print "This either means a mistake in your servers.ini file,"
			print "Look @ servers-example.ini"
			print
			print "Or if u haven't updated in awhile"
			print "Recommend u delete pyBEscanner temp folders & read Changes.txt for update changes"
			exit()

	def loadconfig(self):

		self.config.read(self.conf_file)
		self.server_settings = self.config.sections()
		self.server_settings.remove("Default")

		default = {}

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
					["Ban IP", "Ban IP"],
					["Filters", "Filters"]]

		## Scan Settings -- Default
		self.interval = int(self.config.get("Default", "interval", "60"))

		for x in range(len(options)):
			default[options[x][1]] = self.config.get("Default", options[x][0])

		## Debug Settings
		if self.config.has_option("Default", "Debug File"):
			self.debug_file = self.config.get("Default", "Debug File")
		else:
			self.debug_file = os.path.join(self.main_dir, "debug.log")

		if self.config.has_option("Default", "Debug Level"):
			self.debug_level = self.config.get("Default", "Debug Level")
		else:
			self.debug_level = "WARNING"

		x = 0
		while x < (len(self.server_settings)):
			temp = copy.copy(default)

			## Server Info
			temp["ServerName"] = self.config.get(self.server_settings[x], "ServerName")
			temp["ServerIP"] = self.config.get(self.server_settings[x], "ServerIP")
			temp["ServerPort"] = self.config.get(self.server_settings[x], "ServerPort")
			temp["RconPassword"] = self.config.get(self.server_settings[x], "RconPassword")
			temp["BattlEye Directory"] = self.config.get(self.server_settings[x], "BattlEye Directory")
			temp["Temp Directory"] = os.path.join(temp["BattlEye Directory"], "pyBEscanner", "Temp")

			for y in range(len(options)):
				if self.config.has_option(self.server_settings[x], options[y][0]):
					temp[options[y][1]] = self.config.get(self.server_settings[x], options[y][0])

			temp["Filters"] = re.sub(",\s*", ",", temp["Filters"])
			temp_filters = temp["Filters"].split(",")
			temp["Filters"] = []
			for filters in temp_filters:
				if filters == "Custom":
					temp["Filters"].append(os.path.join(temp["BattlEye Directory"], "pyBEscanner", "filters", "Custom"))
				else:
					temp["Filters"].append(os.path.join(self.main_dir, "filters", filters))

			self.server_settings[x] = temp

			# Generated Settings
			self.server_settings[x]["Battleye Logs"] = ["addbackpackcargo",
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

			self.server_settings[x]["Battleye Logs Location"] = {}
			self.server_settings[x]["Battleye Temp Logs"] = {}
			self.server_settings[x]["Battleye Backup Logs"] = {}  # TODO

			self.server_settings[x]["Banlist Filters"] = {}
			self.server_settings[x]["Kicklist Filters"] = {}
			self.server_settings[x]["Whitelist Filters"] = {}
			self.server_settings[x]["Spamlist Filters"] = {}


			for be_log in self.server_settings[x]["Battleye Logs"]:
				self.server_settings[x]["Battleye Logs Location"][be_log] = os.path.join(self.server_settings[x]["BattlEye Directory"], (be_log + ".log"))
				self.server_settings[x]["Battleye Temp Logs"][be_log] = os.path.join(self.server_settings[x]["Temp Directory"], (be_log + ".log"))

				self.server_settings[x]["Banlist Filters"][be_log] = []
				self.server_settings[x]["Kicklist Filters"][be_log] = []
				self.server_settings[x]["Whitelist Filters"][be_log] = []
				self.server_settings[x]["Spamlist Filters"][be_log] = []

				for filters in self.server_settings[x]["Filters"]:
					self.server_settings[x]["Banlist Filters"][be_log].append(os.path.join(filters, be_log + ".banlist"))
					self.server_settings[x]["Kicklist Filters"][be_log].append(os.path.join(filters, be_log + ".kicklist"))
					self.server_settings[x]["Whitelist Filters"][be_log].append(os.path.join(filters, be_log + ".whitelist"))
					self.server_settings[x]["Spamlist Filters"][be_log].append(os.path.join(filters, be_log + ".spamlist"))

			x = x + 1

	def start(self):
		old_config_timestamp = None
		while True:
			new_config_timestamp = os.path.getmtime(self.conf_file)
			if old_config_timestamp != new_config_timestamp:
				print "---------------------------------------------------------"
				print "       Loading Config File"
				print "---------------------------------------------------------"
				self.loadconfig()
				logging.basicConfig(filename=self.debug_file, level=self.debug_level)
				old_config_timestamp = new_config_timestamp
			x = 0
			while x < len(self.server_settings):
				print
				print
				print "---------------------------------------------------------"
				print "       Scanning " + str(self.server_settings[x]["ServerName"])
				print "---------------------------------------------------------"
				logging.info("")
				logging.info("---------------------------------------------------------")
				logging.info("       Scanning " + str(self.server_settings[x]["ServerName"]))
				logging.info("---------------------------------------------------------")
				bans_file = os.path.join(self.server_settings[x]["BattlEye Directory"], "bans.txt")
				if os.path.isfile(bans_file) is False:
					open(bans_file, 'w').close()
				self.server_settings[x]["Bans.txt Timestamp"] = os.path.getmtime(bans_file)
				server_scan = battleye_modules.Scanner(self.server_settings[x])
				server_scan.scan()
				print str(self.server_settings[x]["Filters"])
				x = x + 1


			x = 0
			logging.info("---------------------------------------------------------")
			while x < len(self.server_settings):
				logging.info("Checking for kicks.txt -- " + str(self.server_settings[x]["ServerName"]))
				kicks_file = os.path.join(self.server_settings[x]["BattlEye Directory"], "kicks.txt")
				if os.path.isfile(kicks_file) is True:
					logging.info("Reloading Kicks")
					rcon = rcon_modules.Rcon(self.server_settings[x]["ServerIP"], self.server_settings[x]["ServerPort"], self.server_settings[x]["RconPassword"])
					rcon.kickplayers(kicks_file)
					os.remove(kicks_file)
				x = x + 1
			logging.info("---------------------------------------------------------")

			x = 0
			logging.info("---------------------------------------------------------")
			while x < len(self.server_settings):
				logging.info("Checking for bans.txt changes -- " + str(self.server_settings[x]["ServerName"]))
				bans_file = os.path.join(self.server_settings[x]["BattlEye Directory"], "bans.txt")
				if os.path.isfile(bans_file) is False:
					open(bans_file, 'w').close()
				if self.server_settings[x]["Bans.txt Timestamp"] != os.path.getmtime(bans_file):
					logging.info("Reloading Bans")
					rcon = rcon_modules.Rcon(self.server_settings[x]["ServerIP"], self.server_settings[x]["ServerPort"], self.server_settings[x]["RconPassword"])
					rcon.reloadbans()

				x = x + 1
			logging.info("---------------------------------------------------------")

			time.sleep(self.interval)


pyBE = Main()
pyBE.start()
