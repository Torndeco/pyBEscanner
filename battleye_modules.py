import datetime
import re
import os
import shutil
import pickle
import time

import rcon_modules

class Scanner:
	def __init__(self, server_settings):

		self.server_settings = server_settings				
		
		self.bans = Bans(os.path.join(self.server_settings["BattlEye Directory"], "bans.txt"))
		self.rcon = rcon_modules.Rcon(self.server_settings["ServerIP"], self.server_settings["ServerPort"], self.server_settings["RconPassword"])	
		
		self.ban_list = []
		self.ban_reason = []
		self.kick_list = []
		self.kick_reason = []
	
		self.backuplog_dir = os.path.join(self.server_settings["BattlEye Directory"], datetime.datetime.now().strftime("BattlEye Logs - %Y-%m-%d"))
		
		
		self.battleye_logs = {
			"addmagazinecargo": os.path.join(self.server_settings["BattlEye Directory"], "addmagazinecargo.log"),
			"createvehicle": os.path.join(self.server_settings["BattlEye Directory"], "createvehicle.log"),
			"deletevehicle": os.path.join(self.server_settings["BattlEye Directory"], "deletevehicle.log"),
			"mpeventhandler": os.path.join(self.server_settings["BattlEye Directory"], "mpeventhandler.log"),
			"publicvariable": os.path.join(self.server_settings["BattlEye Directory"], "publicvariable.log"),
			"remoteexec": os.path.join(self.server_settings["BattlEye Directory"], "remoteexec.log"),
			"scripts": os.path.join(self.server_settings["BattlEye Directory"], "scripts.log"),
			"setdamage": os.path.join(self.server_settings["BattlEye Directory"], "setdamage.log"),
			"setpos": os.path.join(self.server_settings["BattlEye Directory"], "setpos.log"),
			"setvariable": os.path.join(self.server_settings["BattlEye Directory"], "setvariable.log")
			}
		
		self.temp_logs = {
			"addmagazinecargo": os.path.join(self.server_settings["temp_directory"], "addmagazinecargo.log"),
			"createvehicle": os.path.join(self.server_settings["temp_directory"], "createvehicle.log"),
			"deletevehicle": os.path.join(self.server_settings["temp_directory"], "deletevehicle.log"),
			"mpeventhandler": os.path.join(self.server_settings["temp_directory"], "mpeventhandler.log"),
			"publicvariable": os.path.join(self.server_settings["temp_directory"], "publicvariable.log"),
			"remoteexec": os.path.join(self.server_settings["temp_directory"], "remoteexec.log"),
			"scripts": os.path.join(self.server_settings["temp_directory"], "scripts.log"),
			"setdamage": os.path.join(self.server_settings["temp_directory"], "setdamage.log"),
			"setpos": os.path.join(self.server_settings["temp_directory"], "setpos.log"),
			"setvariable": os.path.join(self.server_settings["temp_directory"], "setvariable.log")
			}

		self.backup_logs = {
			"addmagazinecargo": os.path.join(self.backuplog_dir, "addmagazinecargo.log"),
			"createvehicle": os.path.join(self.backuplog_dir, "createvehicle.log"),
			"deletevehicle": os.path.join(self.backuplog_dir, "deletevehicle.log"),
			"mpeventhandler": os.path.join(self.backuplog_dir, "mpeventhandler.log"),
			"publicvariable": os.path.join(self.backuplog_dir, "publicvariable.log"),
			"remoteexec": os.path.join(self.backuplog_dir, "remoteexec.log"),
			"scripts": os.path.join(self.backuplog_dir, "scripts.log"),
			"setdamage": os.path.join(self.backuplog_dir, "setdamage.log"),
			"setpos": os.path.join(self.backuplog_dir, "setpos.log"),
			"setvariable": os.path.join(self.backuplog_dir, "setvariable.log")
			}			

		self.banlist_filters = {
			"addmagazinecargo": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "addmagazinecargo.banlist"),
			"createvehicle": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "createvehicle.banlist"),
			"deletevehicle": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "deletevehicle.banlist"),
			"mpeventhandler": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "mpeventhandler.banlist"),
			"publicvariable": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "publicvariable.banlist"),
			"remoteexec": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "remoteexec.banlist"),
			"scripts": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "scripts.banlist"),
			"setdamage": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setdamage.banlist"),
			"setpos": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setpos.banlist"),
			"setvariable": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setvariable.banlist")
			}
			
		self.kicklist_filters = {
			"addmagazinecargo": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "addmagazinecargo.kicklist"),
			"createvehicle": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "createvehicle.kicklist"),
			"deletevehicle": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "deletevehicle.kicklist"),
			"mpeventhandler": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "mpeventhandler.kicklist"),
			"publicvariable": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "publicvariable.kicklist"),
			"remoteexec": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "remoteexec.kicklist"),
			"scripts": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "scripts.kicklist"),
			"setdamage": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setdamage.kicklist"),
			"setpos": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setpos.kicklist"),
			"setvariable": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setvariable.kicklist")
			}

		self.whitelist_filters = {
			"addmagazinecargo": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "addmagazinecargo.whitelist"),
			"createvehicle": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "createvehicle.whitelist"),
			"deletevehicle": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "deletevehicle.whitelist"),
			"mpeventhandler": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "mpeventhandler.whitelist"),
			"publicvariable": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "publicvariable.whitelist"),
			"remoteexec": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "remoteexec.whitelist"),
			"scripts": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "scripts.whitelist"),
			"setdamage": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setdamage.whitelist"),
			"setpos": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setpos.whitelist"),
			"setvariable": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setvariable.whitelist")
			}
			
		# Create Backup Folder if it doesnt exist
		if not os.path.exists(self.backuplog_dir):
			os.mkdir(self.backuplog_dir)

		if not os.path.exists(os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner")):
			os.mkdir(os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner"))
			
		if not os.path.exists(self.server_settings["temp_directory"]):
			os.mkdir(self.server_settings["temp_directory"])
		

	def scan_battleye_logs(self, x, time="-1"):

		self.log_scanner.scan_log(self.temp_logs[x], self.backup_logs[x], self.whitelist_filters[x], self.banlist_filters[x], self.kicklist_filters[x])
		if self.server_settings[x] == "off":
			print "No actions taken " + x + ".log, scan option = off"
		else:
			if self.server_settings[x] == "strict":
				# Strict Scanning
				print x + " (strict)"
				self.update_bans(x, self.log_scanner.banlist)
				self.update_bans(x, self.log_scanner.kicklist)
				self.update_bans(x, self.log_scanner.unknownlist, update=True) 
				
				# Logging
				self.log(x, "bans", self.log_scanner.banlist)
				self.log(x, "kicks", self.log_scanner.kicklist)
				self.log(x, "unknown", self.log_scanner.unknownlist)

			elif self.server_settings[x] == "standard+kick":
				# Standard Scanning + Kicking
				print x + " (standard+kick)"
				self.update_bans(x, self.log_scanner.banlist, update=True)
				self.update_kicks(x, self.log_scanner.kicklist)
				self.update_kicks(x, self.log_scanner.unknownlist)
				
				# Logging
				self.log(x, "bans", self.log_scanner.banlist)
				self.log(x, "kicks", self.log_scanner.kicklist)
				self.log(x, "unknown", self.log_scanner.unknownlist)
				
			elif self.server_settings[x] == "standard":
				# Standard Scanning
				print x + " (standard)"
				self.update_bans(x, self.log_scanner.banlist, update=True)
				self.update_kicks(x, self.log_scanner.kicklist)

				# Logging
				self.log(x, "bans", self.log_scanner.banlist)
				self.log(x, "kicks", self.log_scanner.kicklist)
				self.log(x, "unknown", self.log_scanner.unknownlist)

			else:
				print x + " (unknown option)"
						
						
	def update_bans(self, x, data, time="-1", update=False):
		for x in range(len(data["guid"])):
			if self.ban_list.count(data["guid"][x]) == 0:
				self.ban_list.append(data["guid"][x])
				self.ban_reason.append("pyBEscanner: " + str(data["name"][x]) + " detected hacking on Server " + str(self.server_settings["ServerName"]) + " @ " + str(data["date"][x]))
				print "       Banning Player " + str(data["name"][x])
			
		if update == True:
			if self.ban_list != []:
				self.bans.openfile()
				for x in range(len(self.ban_list)):
					self.bans.addban(self.ban_list[x], time, self.ban_reason[x])
				self.bans.closefile()
		print
	
	
	def update_kicks(self, x, data):
		for x in range(len(data["name"])):
			if self.kick_list.count(data["name"]) == 0:
				self.kick_list.append(data["name"])
				self.kick_reason.append("pyBEscanner: " + str(data["name"][x]) + " detected unknown @ " + str(data["date"][x]))
			
		for x in range(len(self.kick_list)):
			self.rcon.kickplayer(self.kick_list[x])
			
			
	def log(self, x, action, data):
		if data["date"] != []:
			f_log = open((os.path.join(self.backuplog_dir, x + "-" + action + ".txt")), "a")
			for x in range(len(data["date"])):
				f_log.write(str(data["date"][x]) + str(data["name"][x]) + "(" + str(data["ip"][x]) + ") " + str(data["guid"][x]) + " - " + str(data["code"][x]) + "\n")
			f_log.close()
				
				
	def scan(self):
		battleye_logs = ["addmagazinecargo", "createvehicle", "deletevehicle", "mpeventhandler", "publicvariable", "remoteexec", "scripts", "setdamage", "setpos", "setvariable"]
		
		self.log_scanner = Parser(time.time(), float(self.server_settings["OffSet"]))
		
		for log in battleye_logs:
			if os.path.isfile(self.battleye_logs[log]) == True:
				shutil.move(self.battleye_logs[log], self.temp_logs[log])

		for log in battleye_logs:
			if os.path.isfile(self.temp_logs[log]) == True:
				self.scan_battleye_logs(log)

		
class Parser:		
	def __init__(self, scan_time, offset):
		self.scan_time = scan_time
		self.offset = offset

		
	def scan_log(self, logfile, backupfile, whitelist_filters, banlist_filters, kicklist_filters):
	
		# Entries
		entries_date = []
		entries_guid = []
		entries_ip = []
		entries_code = []
		entries_name = []

		# Ban Entries
		ban_entries_date = []
		ban_entries_guid = []
		ban_entries_ip = []
		ban_entries_code = []
		ban_entries_name = []
		
		# Kick Entries
		kick_entries_date = []
		kick_entries_guid = []
		kick_entries_ip = []
		kick_entries_code = []
		kick_entries_name = []
		

		# Check for Offset BattlEye Logs + Load File
		offset_data_file = logfile + ".pickle"
		if os.path.isfile(offset_data_file) == True:
			f_offset_data_file = open(offset_data_file, 'rb')
			offset_data = pickle.load(f_offset_data_file)
			#print "Retreiving " + str(offset_data)
			if offset_data != []:
				entries_date.append(offset_data[0])
				entries_guid.append(offset_data[1])
				entries_ip.append(offset_data[2])
				entries_code.append(offset_data[3])
				entries_name.append(offset_data[4])
			f_offset_data_file.close()
			
		# Initialize New OffSet Data
		offset_data = []
		
		# Scan BattlEye Logs
		f_backup = open(backupfile, "a")
		with open(logfile) as f_log:
			for line in f_log:
				## Append Lines to Backup Files
				f_backup.write(line)

				temp = line.strip()
				date = re.match('\A[0-3][0-9]\.[0-1][0-9]\.[0-9][0-9][0-9][0-9][ ][0-2][0-9][:][0-6][0-9][:][0-6][0-9][:]\s', temp)
				temp = re.split('\A[0-3][0-9]\.[0-1][0-9]\.[0-9][0-9][0-9][0-9][ ][0-2][0-9][:][0-6][0-9][:][0-6][0-9][:]\s', temp)
				if date == None:
					x = len(entries_code) - 1
					if x > 0:
						entries_code[x] = entries_code[x] + line.strip()
				else:
					name = re.split(".\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}[0-9].",temp[1])
					temp = re.split(".\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}[0-9].",line.strip())
					ip = re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}[0-9]",line.strip())
					code = re.split("\s-\s",temp[1])
					entries_date.append(date.group())
					entries_guid.append(code[0].strip(' '))
					entries_ip.append(ip.group())
					entries_code.append(code[1])
					entries_name.append(name[0])	
		f_backup.close()
		
		#print "DEBUG : length of entries code " + str(len(entries_code))

		os.remove(logfile)
		
		# Check for battleye offset condition
		if len(entries_date) > 0:
			x = time.mktime(time.localtime(self.scan_time))
			x2 = time.mktime((time.strptime(entries_date[-1], "%d.%m.%Y %H:%M:%S: ")))
			#print x - x2
			
			if ((x - x2) < self.offset) == True:
				offset_data.append(entries_date.pop())
				offset_data.append(entries_guid.pop())
				offset_data.append(entries_ip.pop())
				offset_data.append(entries_code.pop())
				offset_data.append(entries_name.pop())
				#print "Adding " + str(offset_data)
			#else:
				#print "Resetting Offset Data " + str(time.mktime(time.localtime(self.scan_time)) - time.mktime((time.strptime(entries_date[-1], "%d.%m.%Y %H:%M:%S: "))))
				#print self.offset
			
		# Update offset_data_file
		f_offset_data_file = open(offset_data_file, 'wb')
		pickle.dump(offset_data, f_offset_data_file)
		f_offset_data_file.close()
		
		if os.path.isfile(whitelist_filters) == True:		
			# Remove whitelisted entries
			with open(whitelist_filters) as f:
				for line in f:
					temp = line.strip()
					x = 0
					while x != len(entries_code):
						if re.search(temp, entries_code[x]) != None:
							entries_date.pop(x)
							entries_guid.pop(x)
							entries_ip.pop(x)
							entries_code.pop(x)
							entries_name.pop(x)
						else:
							x = x + 1
		else:
			# If file = missing, create an empty file
			open(whitelist_filters, 'w').close()

		#print "DEBUG 2: length of entries code " + str(len(entries_code))

		if banlist_filters != None:
			if os.path.isfile(banlist_filters) == True:			
				# Search for BlackListed Entries
				with open(banlist_filters) as f:
					for line in f:
						temp = line.strip()
						x = 0
						while x != len(entries_code):
							if re.search(temp, entries_code[x]):
								ban_entries_date.append(entries_date.pop(x))
								ban_entries_guid.append(entries_guid.pop(x))
								ban_entries_ip.append(entries_ip.pop(x))
								ban_entries_code.append(entries_code.pop(x))
								ban_entries_name.append(entries_name.pop(x))
							else:
								x = x + 1
			else:
				# If file = missing, create an empty file
				open(banlist_filters, 'w').close()

		#print "DEBUG 3: length of entries code " + str(len(entries_code))
		
		if kicklist_filters != None:
			if os.path.isfile(kicklist_filters) == True:			
				# Search for KickList Entries
				with open(kicklist_filters) as f:
					for line in f:
						temp = line.strip()
						x = 0
						while x != len(entries_code):
							if re.search(temp, entries_code[x]):
								kick_entries_date.append(entries_date.pop(x))
								kick_entries_guid.append(entries_guid.pop(x))
								kick_entries_ip.append(entries_ip.pop(x))
								kick_entries_code.append(entries_code.pop(x))
								kick_entries_name.append(entries_name.pop(x))
							else:
								x = x + 1
			else:
				# If file = missing, create an empty file
				open(kicklist_filters, 'w').close()

		#print "DEBUG 4: length of entries code " + str(len(entries_code))

		self.banlist = {
					"date":ban_entries_date,
					"guid":ban_entries_guid,
					"ip":ban_entries_ip,
					"code":ban_entries_code,
					"name":ban_entries_name
					}

		self.kicklist = {
					"date":kick_entries_date,
					"guid":kick_entries_guid,
					"ip":kick_entries_ip,
					"code":kick_entries_code,
					"name":kick_entries_name
					}

		self.unknownlist = {
					"date":entries_date,
					"guid":entries_guid,
					"ip":entries_ip,
					"code":entries_code,
					"name":entries_name
					}
		


		
class Bans:
	def __init__(self, bans_file):
		self.bans_file = bans_file
		
	def openfile(self):
		self.f_bans = open(self.bans_file, "a")		

	def closefile(self):
		self.f_bans.close()

	def addban(self, guid, time, reason):
		self.f_bans.write(guid + " " + time + " " + reason + "\n")

	def removeban(self, guid, time, reason):
		pass
		
