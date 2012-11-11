#!/usr/bin/python
# Filename: pyBEScanner.py


import os
import ConfigParser
import time
import copy

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


	def loadconfig(self):
		self.config = ConfigParser.ConfigParser()
		self.config.read(self.conf_file)
		self.server_settings = self.config.sections()
		self.server_settings.remove("Default")

		default = {}
		
		## Scan Settings -- Default 
		self.interval = int(self.config.get("Default", "interval", "60"))

		default["addmagazinecargo"] = self.config.get("Default", "scan_addmagazinecargo")		
		default["createvehicle"] = self.config.get("Default", "scan_createvehicle")
		default["mpeventhandler"] = self.config.get("Default", "scan_mpeventhandler")
		default["publicvariable"] = self.config.get("Default", "scan_publicvariable")
		default["remoteexec"] = self.config.get("Default", "scan_remoteexec")
		default["scripts"] = self.config.get("Default", "scan_scripts")
		default["setdamage"] = self.config.get("Default", "scan_setdamage")
		default["setpos"] = self.config.get("Default", "scan_setpos")
		default["server_log"] = self.config.get("Default", "scan_server_log")
		default["OffSet"] = self.config.get("Default", "OffSet")

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

			## Scan Settings -- Server Specfic
			if self.config.has_option(self.server_settings[x], "scan_addmagazinecargo") == True:
				temp["addmagazinecargo"] = self.config.get(self.server_settings[x], "scan_addmagazinecargo")
				
			if self.config.has_option(self.server_settings[x], "scan_createvehicle") == True:
				temp["createvehicle"] = self.config.get(self.server_settings[x], "scan_createvehicle")

			if self.config.has_option(self.server_settings[x], "scan_mpeventhandler") == True:
				temp["mpeventhandler"] = self.config.get(self.server_settings[x], "scan_mpeventhandler")

			if self.config.has_option(self.server_settings[x], "scan_publicvariable") == True:
				temp["publicvariable"] = self.config.get(self.server_settings[x], "scan_publicvariable")

			if self.config.has_option(self.server_settings[x], "scan_remoteexec") == True:
				temp["remoteexec"] = self.config.get(self.server_settings[x], "scan_remoteexec")

			if self.config.has_option(self.server_settings[x], "scan_scripts") == True:
				temp["scripts"] = self.config.get(self.server_settings[x], "scan_scripts")
		
			if self.config.has_option(self.server_settings[x], "scan_setdamage") == True:
				temp["setdamage"] = self.config.get(self.server_settings[x], "scan_setdamage")
				
			if self.config.has_option(self.server_settings[x], "scan_setpos") == True:
				temp["setpos"] = self.config.get(self.server_settings[x], "scan_setpos")

			if self.config.has_option(self.server_settings[x], "scan_server_log") == True:
				temp["server_log"] = self.config.get(self.server_settings[x], "scan_server_log")

			if self.config.has_option(self.server_settings[x], "temp_directory") == True:
				temp["temp_directory"] = self.config.get(self.server_settings[x], "temp_directory")
			else:
				temp["temp_directory"] = os.path.join(temp["BattlEye Directory"], self.config.get("Default", "temp_directory"))

				
			self.server_settings[x] = temp
			x = x + 1

		
	def start(self):
		while True:
			print
			print "Reloading Config"
			self.loadconfig()


			kick_list = []
			ban_list = []
			
			x = 0
			while x < len(self.server_settings):
				print
				print
				print "---------------------------------------------------------"
				print "       Scanning " + str(self.server_settings[x]["ServerName"])
				print "---------------------------------------------------------"
				bans_file = os.path.join(self.server_settings[x]["BattlEye Directory"], "bans.txt")
				if os.path.isfile(bans_file) != True:
					open(bans_file, 'w').close()
				self.server_settings[x]["Bans.txt Timestamp"] = os.path.getmtime(bans_file)
				server_scan = battleye_modules.Scanner(self.server_settings[x])
				server_scan.scan()
				x = x + 1
			
			
			x = 0
			print "---------------------------------------------------------"
			while x < len(self.server_settings):
				print "Checking for bans.txt changes -- " + str(self.server_settings[x]["ServerName"])
				bans_file = os.path.join(self.server_settings[x]["BattlEye Directory"], "bans.txt")
				if os.path.isfile(bans_file) != True:
					open(bans_file, 'w').close()
				if self.server_settings[x]["Bans.txt Timestamp"] != os.path.getmtime(bans_file):
					print "Reload Bans"
					rcon = rcon_modules.Rcon(self.server_settings[x]["ServerIP"], self.server_settings[x]["ServerPort"], self.server_settings[x]["RconPassword"])
					rcon.reloadbans()
				
				x = x + 1
			print "---------------------------------------------------------"

			time.sleep(self.interval)
		

pyBE = Main()
pyBE.start()
