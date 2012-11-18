#!/usr/bin/python
# Filename: pyBEScanner.py


import os
import ConfigParser
import time
import copy
import logging

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
			if self.config.get("Default", "Version") != "2":
				print "-------------------------------------------------"
				print "ERROR: Bad conf/servers.ini version"
				print "-------------------------------------------------"
				print "Check conf/servers-examples.ini for changes"
				exit()
		else:
			print "-------------------------------------------------"
			print "ERROR: Bad conf/servers.ini version"
			print "-------------------------------------------------"
			print "Check conf/servers-examples.ini for changes"
			exit()

	def loadconfig(self):

		self.config.read(self.conf_file)
		self.server_settings = self.config.sections()
		self.server_settings.remove("Default")

		default = {}

		options = [["Scan Addbackpackcargo", "addbackpackcargo"],
					["Scan Addmagazinecargo", "addmagazinecargo"],
					["Scan Createvehicle", "createvehicle"],
					["Scan Deletevehicle", "deletevehicle"],
					["Scan Mpeventhandler", "mpeventhandler"],
					["Scan Publicvariable", "publicvariable"],
					["Scan Remoteexec", "remoteexec"],
					["Scan Scripts", "scripts"],
					["Scan Setdamage", "setdamage"],
					["Scan Setpos", "setpos"],
					["Scan Setvariable", "setvariable"],
					["Scan Server Log", "server_log"],
					["OffSet", "OffSet"],
					["Ban Message", "Ban Message"],
					["Filters Location", "Filters Location"]]

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
			temp["Server Console Log"] = self.config.get(self.server_settings[x], "Server Console Log")
			temp["Server RPT Log"] = self.config.get(self.server_settings[x], "Server RPT Log")
			temp["Temp Directory"] = os.path.join(temp["BattlEye Directory"], "pyBEscanner", "Temp")

			for y in range(len(options)):
				if self.config.has_option(self.server_settings[x], options[y][0]):
					temp[options[y][1]] = self.config.get("Default", options[y][0])

			if temp["Filters Location"] == "Custom":
				temp["Filters Location"] = os.path.join(temp["BattlEye Directory"], "pyBEscanner", "filters")
			else:
				temp["Filters Location"] = os.path.join(self.main_dir, "filters", temp["Filters Location"])

			self.server_settings[x] = temp
			x = x + 1

	def start(self):
		while True:
			print
			print "Reloading Config"
			self.loadconfig()
			logging.basicConfig(filename=self.debug_file, level=self.debug_level)

			kick_list = []
			ban_list = []

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
				x = x + 1

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
