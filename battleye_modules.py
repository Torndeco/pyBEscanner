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
			
		self.whitelisted_filters = {
			"createvehicle": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "createvehicle.whitelist"),
			"mpeventhandler": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "mpeventhandler.whitelist"),
			"publicvariable": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "publicvariable.whitelist"),
			"scripts": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "scripts.whitelist"),
			"setdamage": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setdamage.whitelist"),
			"setpos": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setpos.whitelist")
			}
			
		self.blacklisted_filters = {
			"createvehicle": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "createvehicle.blacklist"),
			"mpeventhandler": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "mpeventhandler.blacklist"),
			"publicvariable": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "publicvariable.blacklist"),
			"scripts": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "scripts.blacklist"),
			"setdamage": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setdamage.blacklist"),
			"setpos": os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner", "setpos.blacklist")
			}

			
		# Create Backup Folder if it doesnt exist
		if not os.path.exists(self.backuplog_dir):
			os.mkdir(self.backuplog_dir)

		if not os.path.exists(os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner")):
			os.mkdir(os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner"))


	def scan_battleye_logs(self, x, time="-1"):

		if os.path.isfile(self.logs[x]) == True:

			if self.server_settings[x] == "disable":
				print "Skipping " + x + ".log, scan option = disable"
			else:
				log_scanner = Parser()
				if self.server_settings[x] == "whitelist":
					print x + " = whitelist"
					log_scanner.scan_log(self.logs[x], self.backup_logs[x], self.whitelisted_filters[x], None)
					self.update_bans(x, log_scanner.blacklist)
					self.update_bans(x, log_scanner.unknownlist, time, True) 
					self.log_unknown(x, log_scanner.unknownlist)
					# TODO: Update bans.txt
				elif self.server_settings[x] == "blacklist":
					print x + " = blacklist"
					log_scanner.scan_log(self.logs[x], self.backup_logs[x], self.whitelisted_filters[x], self.blacklisted_filters[x])
					self.update_bans(x, log_scanner.blacklist, time, True)
					self.log_unknown(x, log_scanner.unknownlist)
					# TODO: Update bans.txt
				elif self.server_settings[x] == "blacklist+kick":
					print x + " = blacklist+kick"
					log_scanner.scan_log(self.logs[x], self.backup_logs[x], self.whitelisted_filters[x], self.blacklisted_filters[x])
					self.update_bans(x, log_scanner.blacklist, time, True)
					self.update_kicks(x, log_scanner.unknownlist)
					self.log_unknown(x, log_scanner.unknownlist)
						
						
	def update_bans(self, x, data, time="-1", update=False):
		ban_logger = Logger(os.path.join(self.backuplog_dir, x + "-bans.txt"))				
		for x in range(len(data["guid"])):
			if self.ban_list.count(data["guid"][x]) == 0:
				self.ban_list.append(data["guid"][x])
				self.ban_reason.append("pyBEscanner: " + str(data["name"][x]) + " detected hacking on Server " + str(self.server_settings["ServerName"]) + " @ " + str(data["date"][x]))
			ban_logger.add(str(data["date"][x]) + str(data["name"][x]) + "(" + str(data["ip"][x]) + ") " + str(data["guid"][x]) + " - " + str(data["code"][x]) + "\n")
			
		if update == True:
			f_bans = open(os.path.join(self.server_settings["BattlEye Directory"], "bans.txt"), "a")
			for x in range(len(self.ban_list)):
				print str(self.ban_list)
				f_bans.write("\n" + str(self.ban_list[x]) + " " + str(time) + " " + str(self.ban_reason[x]))
			f_bans.close()
	
	
	def update_kicks(self, x, data):
		kicks_logger = Logger(os.path.join(self.backuplog_dir, x + "-kicks.txt"))				
		for x in range(len(data["name"])):
			if self.kick_list.count(data["name"]) == 0:
				self.kick_list.append(data["name"])
				self.kick_reason.append("pyBEscanner: " + str(data["name"][x]) + " detected unknown @ " + str(data["date"][x]))
			kicks_logger.add(str(data["date"][x]) + str(data["name"][x]) + "(" + str(data["ip"][x]) + ") " + str(data["guid"][x]) + " - " + str(data["code"][x]) + "\n")
			
		for x in range(len(self.kick_list)):
			self.rcon.kickplayer(self.kick_list[x])
			
			
	def log_unknown(self, x, data):
		unknown_logger = Logger(os.path.join(self.backuplog_dir, x + "-unknown.txt"))				
		for x in range(len(data["guid"])):
			unknown_logger.add(str(data["date"][x]) + str(data["name"][x]) + "(" + str(data["ip"][x]) + ") " + str(data["guid"][x]) + " - " + str(data["code"][x]) + "\n")
				
				
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

		

	def scan_log(self, logfile, backupfile, whitelisted_filters, blacklisted_filters):

		entries_date = []
		entries_guid = []
		entries_ip = []
		entries_code = []
		entries_name = []

		# Scan BattlEye Logs
			# Append BattlEye Backup Logs
			# Empty BattlEye Logs

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
		
		print "DEBUG : length of entries code " + str(len(entries_code))

		# Empty Logfile after reading it
			# Possible race condition between parsing file & emptying file. If battleye updates it, lost entries...
			# TODO: Replace with code that wipes entries based on line number ???
		self.purge(logfile)
		
		if os.path.isfile(whitelisted_filters) == True:		
			# Remove whitelisted entries
			with open(whitelisted_filters) as f:
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
			open(whitelisted_filters, 'w').close()

		print "DEBUG 2: length of entries code " + str(len(entries_code))
				
		# Split up into unknown / blacklisted entries
		blackentries_date = []
		blackentries_guid = []
		blackentries_ip = []
		blackentries_code = []
		blackentries_name = []

		if blacklisted_filters != None:
			if os.path.isfile(blacklisted_filters) == True:			
				# Search for BlackListed Entries
				with open(blacklisted_filters) as f:
					for line in f:
						temp = line.strip()
						x = 0
						while x != len(entries_code):
							if re.search(temp, entries_code[x]):
								blackentries_date.append(entries_date.pop(x))
								blackentries_guid.append(entries_guid.pop(x))
								blackentries_ip.append(entries_ip.pop(x))
								blackentries_code.append(entries_code.pop(x))
								blackentries_name.append(entries_name.pop(x))
							else:
								x = x + 1
			else:
				# If file = missing, create an empty file
				open(blacklisted_filters, 'w').close()

		print "DEBUG 3: length of entries code " + str(len(entries_code))

		self.blacklist = {
					"date":blackentries_date,
					"guid":blackentries_guid,
					"ip":blackentries_ip,
					"code":blackentries_code,
					"name":blackentries_name
					}

		self.unknownlist = {
					"date":entries_date,
					"guid":entries_guid,
					"ip":entries_ip,
					"code":entries_code,
					"name":entries_name
					}

		

			
	def purge(self, logfile):
		# Emptys logfile
		open(logfile, 'w').close()


class Logger:
	def __init__(self, logfile):
		self.logfile = logfile

	def add(self, txt):
		f_bans = open(self.logfile, "a")
		f_bans.write(txt)
		f_bans.close()

class Bans:
	def __init__(self, bans_file):
		self.bans_file = bans_file


		
	def addban(self, guid, time, reason):
		temp = guid + " " + time + " " + reason + "\n"
		f_bans = open(self.bans_file, "a")
		f_bans.write(temp)
		f_bans.close()
	

	def removeban(self, guid, time, reason):
		pass
