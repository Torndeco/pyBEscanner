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
			if self.config.get("Default", "Version") != "1":
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
		
		## Scan Settings -- Default 
		self.interval = int(self.config.get("Default", "interval", "60"))
		
		if self.config.has_option("Default", "Debug File"):
			self.debug_file = self.config.get("Default", "Debug File")
		else:
			self.debug_file = os.path.join(self.main_dir, "debug.log")
			
		if self.config.has_option("Default", "Debug Level"):
			self.debug_level = self.config.get("Default", "Debug Level")
		else:
			self.debug_level = "WARNING"
			
		default["Ban Message"] = self.config.get("Default", "Ban Message")

		default["addbackpackcargo"] = self.config.get("Default", "Scan Addbackpackcargo")		
		default["addmagazinecargo"] = self.config.get("Default", "Scan Addmagazinecargo")		
		default["createvehicle"] = self.config.get("Default", "Scan Createvehicle")
		default["deletevehicle"] = self.config.get("Default", "Scan Deletevehicle")
		default["mpeventhandler"] = self.config.get("Default", "Scan Mpeventhandler")
		default["publicvariable"] = self.config.get("Default", "Scan Publicvariable")
		default["remoteexec"] = self.config.get("Default", "Scan Remoteexec")
		default["scripts"] = self.config.get("Default", "Scan Scripts")
		default["setdamage"] = self.config.get("Default", "Scan Setdamage")
		default["setpos"] = self.config.get("Default", "Scan Setpos")
		default["setvariable"] = self.config.get("Default", "Scan Setvariable")
		default["server_log"] = self.config.get("Default", "Scan Server Log")
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
			if self.config.has_option(self.server_settings[x], "Scan Addbackpackcargo") == True:
				temp["addbackpackcargo"] = self.config.get(self.server_settings[x], "Scan Addbackpackcargo")

			if self.config.has_option(self.server_settings[x], "Scan Addmagazinecargo") == True:
				temp["addmagazinecargo"] = self.config.get(self.server_settings[x], "Scan Addmagazinecargo")
				
			if self.config.has_option(self.server_settings[x], "Scan Createvehicle") == True:
				temp["createvehicle"] = self.config.get(self.server_settings[x], "Scan Createvehicle")
				
			if self.config.has_option(self.server_settings[x], "Scan Deletevehicle") == True:
				temp["deletevehicle"] = self.config.get(self.server_settings[x], "Scan Deletevehicle")

			if self.config.has_option(self.server_settings[x], "Scan Mpeventhandler") == True:
				temp["mpeventhandler"] = self.config.get(self.server_settings[x], "Scan Mpeventhandler")

			if self.config.has_option(self.server_settings[x], "Scan Publicvariable") == True:
				temp["publicvariable"] = self.config.get(self.server_settings[x], "Scan Publicvariable")

			if self.config.has_option(self.server_settings[x], "Scan Remoteexec") == True:
				temp["remoteexec"] = self.config.get(self.server_settings[x], "Scan Remoteexec")

			if self.config.has_option(self.server_settings[x], "Scan Scripts") == True:
				temp["scripts"] = self.config.get(self.server_settings[x], "Scan Scripts")
		
			if self.config.has_option(self.server_settings[x], "Scan Setdamage") == True:
				temp["setdamage"] = self.config.get(self.server_settings[x], "Scan Setdamage")
				
			if self.config.has_option(self.server_settings[x], "Scan Setpos") == True:
				temp["setpos"] = self.config.get(self.server_settings[x], "Scan Setpos")
				
			if self.config.has_option(self.server_settings[x], "Scan Setvariable") == True:
				temp["setvariable"] = self.config.get(self.server_settings[x], "Scan Setvariable")

			if self.config.has_option(self.server_settings[x], "Scan Server_log") == True:
				temp["server_log"] = self.config.get(self.server_settings[x], "Scan Server Log")

			if self.config.has_option(self.server_settings[x], "Temp Directory") == True:
				temp["temp_directory"] = self.config.get(self.server_settings[x], "Temp Directory")
			else:
				temp["temp_directory"] = os.path.join(temp["BattlEye Directory"], "pyBEscanner", "Temp")

			if self.config.has_option(self.server_settings[x], "Ban Message") == True:
				temp["temp_directory"] = self.config.get(self.server_settings[x], "Ban Message")
				
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
				if os.path.isfile(bans_file) != True:
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
				if os.path.isfile(bans_file) != True:
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