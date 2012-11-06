import datetime
import re
import os

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
		
		self.logs = {
			"createvehicle": os.path.join(self.server_settings["BattlEye Directory"], "createvehicle.log"),
			"mpeventhandler": os.path.join(self.server_settings["BattlEye Directory"], "mpeventhandler.log"),
			"publicvariable": os.path.join(self.server_settings["BattlEye Directory"], "publicvariable.log"),
			"scripts": os.path.join(self.server_settings["BattlEye Directory"], "scripts.log"),
			"setdamage": os.path.join(self.server_settings["BattlEye Directory"], "setdamage.log"),
			"setpos": os.path.join(self.server_settings["BattlEye Directory"], "setpos.log")
			}

		self.backup_logs = {
			"createvehicle": os.path.join(self.backuplog_dir, "createvehicle.log"),
			"mpeventhandler": os.path.join(self.backuplog_dir, "mpeventhandler.log"),
			"publicvariable": os.path.join(self.backuplog_dir, "publicvariable.log"),
			"scripts": os.path.join(self.backuplog_dir, "scripts.log"),
			"setdamage": os.path.join(self.backuplog_dir, "setdamage.log"),
			"setpos": os.path.join(self.backuplog_dir, "setpos.log")
			}			

		self.banlist_filters = {
			"createvehicle": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "createvehicle.banlist"),
			"mpeventhandler": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "mpeventhandler.banlist"),
			"publicvariable": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "publicvariable.banlist"),
			"scripts": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "scripts.banlist"),
			"setdamage": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setdamage.banlist"),
			"setpos": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setpos.banlist")
			}
			
		self.kicklist_filters = {
			"createvehicle": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "createvehicle.kicklist"),
			"mpeventhandler": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "mpeventhandler.kicklist"),
			"publicvariable": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "publicvariable.kicklist"),
			"scripts": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "scripts.kicklist"),
			"setdamage": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setdamage.kicklist"),
			"setpos": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setpos.kicklist")
			}

		self.whitelist_filters = {
			"createvehicle": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "createvehicle.whitelist"),
			"mpeventhandler": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "mpeventhandler.whitelist"),
			"publicvariable": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "publicvariable.whitelist"),
			"scripts": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "scripts.whitelist"),
			"setdamage": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setdamage.whitelist"),
			"setpos": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setpos.whitelist")
			}
			
		# Create Backup Folder if it doesnt exist
		if not os.path.exists(self.backuplog_dir):
			os.mkdir(self.backuplog_dir)

		if not os.path.exists(os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner")):
			os.mkdir(os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner"))


	def scan_battleye_logs(self, x, time="-1"):

		if os.path.isfile(self.logs[x]) == True:
			if self.server_settings[x] == "off":
				print "Skipping " + x + ".log, scan option = off"
			else:
				log_scanner = Parser()
				log_scanner.scan_log(self.logs[x], self.backup_logs[x], self.whitelist_filters[x], self.banlist_filters[x], self.kicklist_filters[x])
				if self.server_settings[x] == "strict":
					# Strict Scanning
					print x + " (strict)"
					self.update_bans(x, log_scanner.banlist)
					self.update_bans(x, log_scanner.kicklist)
					self.update_bans(x, log_scanner.unknownlist, update=True) 
					
					# Logging
					self.log(x, "bans", log_scanner.banlist)
					self.log(x, "kicks", log_scanner.kicklist)
					self.log(x, "unknown", log_scanner.unknownlist)

				elif self.server_settings[x] == "standard+kick":
					# Standard Scanning + Kicking
					print x + " (standard+kick)"
					self.update_bans(x, log_scanner.banlist, update=True)
					self.update_kicks(x, log_scanner.kicklist)
					self.update_kicks(x, log_scanner.unknownlist)
					
					# Logging
					self.log(x, "bans", log_scanner.banlist)
					self.log(x, "kicks", log_scanner.kicklist)
					self.log(x, "unknown", log_scanner.unknownlist)
					
				elif self.server_settings[x] == "standard":
					# Standard Scanning
					print x + " (standard)"
					log_scanner.scan_log(self.logs[x], self.backup_logs[x], self.whitelist_filters[x], self.banlist_filters[x], self.kicklist_filters[x])
					self.update_bans(x, log_scanner.banlist, update=True)
					self.update_kicks(x, log_scanner.kicklist)

					# Logging
					self.log(x, "bans", log_scanner.banlist)
					self.log(x, "kicks", log_scanner.kicklist)
					self.log(x, "unknown", log_scanner.unknownlist)

				else:
					print x + " (unknown option)"
						
						
	def update_bans(self, x, data, time="-1", update=False):
		for x in range(len(data["guid"])):
			if self.ban_list.count(data["guid"][x]) == 0:
				self.ban_list.append(data["guid"][x])
				self.ban_reason.append("pyBEscanner: " + str(data["name"][x]) + " detected hacking on Server " + str(self.server_settings["ServerName"]) + " @ " + str(data["date"][x]))
				print "       Banning Player " + str(data["name"][x])
			
		if update == True:
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
				
				
	def start(self):
		
		# Check for Log Files to Scan
		self.scan_battleye_logs("createvehicle")
		self.scan_battleye_logs("mpeventhandler")
		self.scan_battleye_logs("publicvariable")
		self.scan_battleye_logs("scripts")
		self.scan_battleye_logs("setdamage")
		self.scan_battleye_logs("setpos")



		if os.path.isfile(self.server_settings["Server Console Log"]) == True:
			# TODO: Server Log Scan
			pass

		if os.path.isfile(self.server_settings["Server RPT Log"]) == True:
			# TODO: Server Log Scan
			pass
				
		
class Parser:		
	def __init__(self):
		pass

		

	def scan_log(self, logfile, backupfile, whitelist_filters, banlist_filters, kicklist_filters):
	
#log_scanner.scan_log(self.logs[x], self.backup_logs[x], self.whitelist_filters[x], self.banlist_filters[x], self.kicklist_filters[x])

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

		# Empty Logfile after reading it
			# Possible race condition between parsing file & emptying file. If battleye updates it, lost entries...
			# TODO: Replace with code that wipes entries based on line number ???
		self.purge(logfile)
		
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

		
	def purge(self, logfile):
		#open(logfile, 'w').close()
		pass


		
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
		
