import datetime
import re
import os
import shutil
import time
import string
import logging
import cPickle as pickle

import rcon_modules

class Scanner:
	def __init__(self, server_settings):

		self.logger = logging.getLogger("Battleye Scanner ")
		self.logger.debug("Filters --> " + str(server_settings["Filters Location"]))

		self.server_settings = server_settings

		self.bans = Bans(os.path.join(self.server_settings["BattlEye Directory"], "bans.txt"))
		self.rcon = rcon_modules.Rcon(self.server_settings["ServerIP"], self.server_settings["ServerPort"], self.server_settings["RconPassword"])

		self.ban_list = []
		self.ban_reason = []
		self.kick_list = []
		self.kick_reason = []

		self.backuplog_dir = os.path.join(self.server_settings["BattlEye Directory"], "Logs", datetime.datetime.now().strftime("BattlEye Logs - %Y-%m-%d"))

		self.battleye_logs = {"addbackpackcargo": os.path.join(self.server_settings["BattlEye Directory"], "addbackpackcargo.log"),
							"addmagazinecargo": os.path.join(self.server_settings["BattlEye Directory"], "addmagazinecargo.log"),
							"createvehicle": os.path.join(self.server_settings["BattlEye Directory"], "createvehicle.log"),
							"deletevehicle": os.path.join(self.server_settings["BattlEye Directory"], "deletevehicle.log"),
							"mpeventhandler": os.path.join(self.server_settings["BattlEye Directory"], "mpeventhandler.log"),
							"publicvariable": os.path.join(self.server_settings["BattlEye Directory"], "publicvariable.log"),
							"remoteexec": os.path.join(self.server_settings["BattlEye Directory"], "remoteexec.log"),
							"scripts": os.path.join(self.server_settings["BattlEye Directory"], "scripts.log"),
							"setdamage": os.path.join(self.server_settings["BattlEye Directory"], "setdamage.log"),
							"setpos": os.path.join(self.server_settings["BattlEye Directory"], "setpos.log"),
							"setvariable": os.path.join(self.server_settings["BattlEye Directory"], "setvariable.log")}

		self.temp_logs = {"addbackpackcargo": os.path.join(self.server_settings["Temp Directory"], "addbackpackcargo.log"),
						"addmagazinecargo": os.path.join(self.server_settings["Temp Directory"], "addmagazinecargo.log"),
						"createvehicle": os.path.join(self.server_settings["Temp Directory"], "createvehicle.log"),
						"deletevehicle": os.path.join(self.server_settings["Temp Directory"], "deletevehicle.log"),
						"mpeventhandler": os.path.join(self.server_settings["Temp Directory"], "mpeventhandler.log"),
						"publicvariable": os.path.join(self.server_settings["Temp Directory"], "publicvariable.log"),
						"remoteexec": os.path.join(self.server_settings["Temp Directory"], "remoteexec.log"),
						"scripts": os.path.join(self.server_settings["Temp Directory"], "scripts.log"),
						"setdamage": os.path.join(self.server_settings["Temp Directory"], "setdamage.log"),
						"setpos": os.path.join(self.server_settings["Temp Directory"], "setpos.log"),
						"setvariable": os.path.join(self.server_settings["Temp Directory"], "setvariable.log")}

		self.backup_logs = {"addbackpackcargo": os.path.join(self.backuplog_dir, "addbackpackcargo.log"),
							"addmagazinecargo": os.path.join(self.backuplog_dir, "addmagazinecargo.log"),
							"createvehicle": os.path.join(self.backuplog_dir, "createvehicle.log"),
							"deletevehicle": os.path.join(self.backuplog_dir, "deletevehicle.log"),
							"mpeventhandler": os.path.join(self.backuplog_dir, "mpeventhandler.log"),
							"publicvariable": os.path.join(self.backuplog_dir, "publicvariable.log"),
							"remoteexec": os.path.join(self.backuplog_dir, "remoteexec.log"),
							"scripts": os.path.join(self.backuplog_dir, "scripts.log"),
							"setdamage": os.path.join(self.backuplog_dir, "setdamage.log"),
							"setpos": os.path.join(self.backuplog_dir, "setpos.log"),
							"setvariable": os.path.join(self.backuplog_dir, "setvariable.log")}

		self.banlist_filters = {"addbackpackcargo": os.path.join(self.server_settings["Filters Location"], "addbackpackcargo.banlist"),
								"addmagazinecargo": os.path.join(self.server_settings["Filters Location"], "addmagazinecargo.banlist"),
								"createvehicle": os.path.join(self.server_settings["Filters Location"], "createvehicle.banlist"),
								"deletevehicle": os.path.join(self.server_settings["Filters Location"], "deletevehicle.banlist"),
								"mpeventhandler": os.path.join(self.server_settings["Filters Location"], "mpeventhandler.banlist"),
								"publicvariable": os.path.join(self.server_settings["Filters Location"], "publicvariable.banlist"),
								"remoteexec": os.path.join(self.server_settings["Filters Location"], "remoteexec.banlist"),
								"scripts": os.path.join(self.server_settings["Filters Location"], "scripts.banlist"),
								"setdamage": os.path.join(self.server_settings["Filters Location"], "setdamage.banlist"),
								"setpos": os.path.join(self.server_settings["Filters Location"], "setpos.banlist"),
								"setvariable": os.path.join(self.server_settings["Filters Location"], "setvariable.banlist")}

		self.kicklist_filters = {"addbackpackcargo": os.path.join(self.server_settings["Filters Location"], "addbackpackcargo.kicklist"),
								"addmagazinecargo": os.path.join(self.server_settings["Filters Location"], "addmagazinecargo.kicklist"),
								"createvehicle": os.path.join(self.server_settings["Filters Location"], "createvehicle.kicklist"),
								"deletevehicle": os.path.join(self.server_settings["Filters Location"], "deletevehicle.kicklist"),
								"mpeventhandler": os.path.join(self.server_settings["Filters Location"], "mpeventhandler.kicklist"),
								"publicvariable": os.path.join(self.server_settings["Filters Location"], "publicvariable.kicklist"),
								"remoteexec": os.path.join(self.server_settings["Filters Location"], "remoteexec.kicklist"),
								"scripts": os.path.join(self.server_settings["Filters Location"], "scripts.kicklist"),
								"setdamage": os.path.join(self.server_settings["Filters Location"], "setdamage.kicklist"),
								"setpos": os.path.join(self.server_settings["Filters Location"], "setpos.kicklist"),
								"setvariable": os.path.join(self.server_settings["Filters Location"], "setvariable.kicklist")}

		self.whitelist_filters = {"addbackpackcargo": os.path.join(self.server_settings["Filters Location"], "addbackpackcargo.whitelist"),
								"addmagazinecargo": os.path.join(self.server_settings["Filters Location"], "addmagazinecargo.whitelist"),
								"createvehicle": os.path.join(self.server_settings["Filters Location"], "createvehicle.whitelist"),
								"deletevehicle": os.path.join(self.server_settings["Filters Location"], "deletevehicle.whitelist"),
								"mpeventhandler": os.path.join(self.server_settings["Filters Location"], "mpeventhandler.whitelist"),
								"publicvariable": os.path.join(self.server_settings["Filters Location"], "publicvariable.whitelist"),
								"remoteexec": os.path.join(self.server_settings["Filters Location"], "remoteexec.whitelist"),
								"scripts": os.path.join(self.server_settings["Filters Location"], "scripts.whitelist"),
								"setdamage": os.path.join(self.server_settings["Filters Location"], "setdamage.whitelist"),
								"setpos": os.path.join(self.server_settings["Filters Location"], "setpos.whitelist"),
								"setvariable": os.path.join(self.server_settings["Filters Location"], "setvariable.whitelist")}

		self.banlist_spam_filters = {"addbackpackcargo": os.path.join(self.server_settings["Filters Location"], "addbackpackcargo.spam-rules"),
									"addmagazinecargo": os.path.join(self.server_settings["Filters Location"], "addmagazinecargo.spam-rules"),
									"createvehicle": os.path.join(self.server_settings["Filters Location"], "createvehicle.spam-rules"),
									"deletevehicle": os.path.join(self.server_settings["Filters Location"], "deletevehicle.spam-rules"),
									"mpeventhandler": os.path.join(self.server_settings["Filters Location"], "mpeventhandler.spam-rules"),
									"publicvariable": os.path.join(self.server_settings["Filters Location"], "publicvariable.spam-rules"),
									"remoteexec": os.path.join(self.server_settings["Filters Location"], "remoteexec.spam-rules"),
									"scripts": os.path.join(self.server_settings["Filters Location"], "scripts.spam-rules"),
									"setdamage": os.path.join(self.server_settings["Filters Location"], "setdamage.spam-rules"),
									"setpos": os.path.join(self.server_settings["Filters Location"], "setpos.spam-rules"),
									"setvariable": os.path.join(self.server_settings["Filters Location"], "setvariable.spam-rules")}

		# Create Backup Folder if it doesnt exist
		if not os.path.exists(self.backuplog_dir):
			os.makedirs(self.backuplog_dir)

		if not os.path.exists(os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner")):
			os.mkdir(os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner"))

		if not os.path.exists(self.server_settings["Filters Location"]):
			os.mkdir(self.server_settings["Filters Location"])

		if not os.path.exists(self.server_settings["Temp Directory"]):
			os.mkdir(self.server_settings["Temp Directory"])


	def scan_battleye_logs(self, x):

		if self.server_settings["Spam Filters"] == "on":
			self.log_scanner.scan_log(self.temp_logs[x],
								self.backup_logs[x],
								self.whitelist_filters[x],
								self.banlist_filters[x],
								self.kicklist_filters[x],
								self.banlist_spam_filters[x])
		else:
			self.log_scanner.scan_log(self.temp_logs[x],
								self.backup_logs[x],
								self.whitelist_filters[x],
								self.banlist_filters[x],
								self.kicklist_filters[x],
								None)
		if self.server_settings[x] == "off":
			print x + " (off)"
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
				self.logger.warning(x + " (unknown option)")
				print x + " (unknown option)"

	def kick_ban_msg(self, template, player_name, server_name, log_file, date_time):
		tmp = string.replace(template, "PLAYER_NAME", player_name)
		tmp = string.replace(tmp, "SERVER_NAME", server_name)
		tmp = string.replace(tmp, "LOG_FILE", log_file)
		tmp = string.replace(tmp, "DATE_TIME", date_time)
		return tmp

	def update_bans(self, log_file, data, time="-1", update=False):

		for x in range(len(data["guid"])):
			if self.ban_list.count(data["guid"][x]) == 0:
				self.ban_list.append(data["guid"][x])
				ban_message = self.kick_ban_msg(self.server_settings["Ban Message"], str(data["name"][x]), str(self.server_settings["ServerName"]), log_file, str(data["date"][x]))
				self.ban_reason.append(ban_message)
				self.logger.info("Banning Player " + str(data["name"][x]))
				print ("Banning Player " + str(data["name"][x]))

		if update is True:
			if self.ban_list != []:
				self.bans.openfile()
				for x in range(len(self.ban_list)):
					self.bans.addban(self.ban_list[x], time, self.ban_reason[x])
				self.bans.closefile()
				self.ban_list = []
				self.ban_reason = []

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
		battleye_logs = ["addbackpackcargo", "addmagazinecargo", "createvehicle", "deletevehicle", "mpeventhandler", "publicvariable", "remoteexec", "scripts", "setdamage", "setpos", "setvariable"]

		self.log_scanner = Parser(time.time(), float(self.server_settings["OffSet"]))

		for log in battleye_logs:
			if os.path.isfile(self.battleye_logs[log]) is True:
				if os.path.isfile(self.temp_logs[log]) is True:
					os.remove(self.temp_logs[log])
					self.logger.info("Removing Old Temp File - " + self.temp_logs[log])
				error_loop = 0
				while True:
					try:
						shutil.move(self.battleye_logs[log], self.temp_logs[log])
						break
					except WindowsError:
						if error_loop >= 5:
							print "Error file " + log + " in usage by a process, skipping..."
							self.logger.critical("Error file " + log + " in usage by a process, skipping...")
							break
						else:
							error_loop = error_loop + 1
							time.sleep(1)

		for log in battleye_logs:
			self.scan_battleye_logs(log)



class Parser:
	def __init__(self, scan_time, offset):
		self.logger = logging.getLogger("Parser ")

		self.scan_time = scan_time
		self.offset = offset
		self.decoder = Decoder()

	def scan_log(self, logfile, backupfile, whitelist_filters, banlist_filters, kicklist_filters, spam_filters):

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

		# Check for Offset pickle file / Initialize OffSet Data
		offset_data_file = logfile + ".offset"
		spam_data_file = logfile + ".spam"

		self.logger.debug('')
		self.logger.debug('Parsing ' + str(logfile))
		self.logger.debug('Checking of Offset Data File')
		if os.path.isfile(offset_data_file) is True:
			self.logger.debug('Offset Data File Found')
			f_offset_data_file = open(offset_data_file, 'rb')
			offset_data = pickle.load(f_offset_data_file)
			self.logger.debug('Loading Offset Data = ' + str(offset_data))
			if offset_data != []:
				entries_date.append(offset_data[0])
				entries_guid.append(offset_data[1])
				entries_ip.append(offset_data[2])
				entries_code.append(offset_data[3])
				entries_name.append(offset_data[4])
			f_offset_data_file.close()
			self.logger.debug('Entries Data = ' + str(offset_data))
		else:
			self.logger.debug('No Offset Data File Found')

		# Scan BattlEye Logs
		if os.path.isfile(logfile) is True:
			f_backup = open(backupfile, "a")
			with open(logfile) as f_log:
				for line in f_log:
					## Append Lines to Backup Files
					f_backup.write(line)

					temp = line.strip()
					date = re.match('\A[0-3][0-9]\.[0-1][0-9]\.[0-9][0-9][0-9][0-9][ ][0-2][0-9][:][0-6][0-9][:][0-6][0-9][:]\s', temp)
					temp = re.split('\A[0-3][0-9]\.[0-1][0-9]\.[0-9][0-9][0-9][0-9][ ][0-2][0-9][:][0-6][0-9][:][0-6][0-9][:]\s', temp, 1)
					if date is None:
						x = len(entries_date) - 1
						if x >= 0:
							self.logger.debug('Detected Multiple lines = ' + str(entries_code[x]))
							entries_code[x] = entries_code[x] + line.strip()
							self.logger.debug('Updated line = ' + str(entries_code[x]))
					else:
						name = re.split(".\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}[0-9].", temp[1], 1)
						temp = re.split(".\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}[0-9].", line.strip(), 1)
						ip = re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}[0-9]", line.strip())
						code = re.split("\s-\s", temp[1], 1)
						entries_date.append(date.group())
						entries_guid.append(code[0].strip(' '))
						entries_ip.append(ip.group())
						entries_code.append(code[1])
						entries_name.append(name[0])
			f_backup.close()

			os.remove(logfile)

		# Check for battleye offset condition
		offset_data = []
		if len(entries_date) > 0:
			x = time.mktime(time.localtime(self.scan_time))
			x2 = time.mktime((time.strptime(entries_date[-1], "%d.%m.%Y %H:%M:%S: ")))

			if ((x - x2) < self.offset) is True:
				offset_data.append(entries_date.pop())
				offset_data.append(entries_guid.pop())
				offset_data.append(entries_ip.pop())
				offset_data.append(entries_code.pop())
				offset_data.append(entries_name.pop())
				self.logger.debug("Saving  " + str(offset_data))

		# Update offset_data_file
		f_offset_data_file = open(offset_data_file, 'wb')
		pickle.dump(offset_data, f_offset_data_file)
		f_offset_data_file.close()

		if (len(entries_code) > 0) is True:

			# Spam Detection
			# THIS IS NOT FUNCTIONAL YET IN ANYWAY WAY DONT UNCOMMENT!!!!!!!!!!
			if spam_filters is not None:
				self.spam_detection = Spam(spam_data_file, spam_filters)
				self.spam_detection.load()
				self.spam_detection.scan(x)
				self.spam_detection.save()

			if os.path.isfile(whitelist_filters) is True:
				# Remove whitelisted entries
				with open(whitelist_filters) as f:
					for line in f:
						temp = line.strip()
						x = 0
						while x != len(entries_code):
							if re.search(temp, entries_code[x]) is not None:
								entries_date.pop(x)
								entries_guid.pop(x)
								entries_ip.pop(x)
								entries_code.pop(x)
								entries_name.pop(x)
							else:
								x = x + 1
			else:
				# If file = missing, create an empty file
				self.logger.info("Create missing filter " + str(whitelist_filters))
				print "Create missing filter " + str(whitelist_filters)
				open(whitelist_filters, 'w').close()


			if banlist_filters is not None:
				if os.path.isfile(banlist_filters) is True:
					# Search for BlackListed Entries
					with open(banlist_filters) as f:
						for line in f:
							temp = line.strip()
							x = 0
							while x != len(entries_code):
								if re.search(temp, entries_code[x]) or re.search(temp, self.decoder.decode_string(entries_code[x])):
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

			if kicklist_filters is not None:
				if os.path.isfile(kicklist_filters) is True:
					# Search for KickList Entries
					with open(kicklist_filters) as f:
						for line in f:
							temp = line.strip()
							x = 0
							while x != len(entries_code):
								if re.search(temp, entries_code[x]) or re.search(temp, self.decoder.decode_string(entries_code[x])):
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


		self.banlist = {"date": ban_entries_date,
						"guid": ban_entries_guid,
						"ip": ban_entries_ip,
						"code": ban_entries_code,
						"name": ban_entries_name}

		self.kicklist = {"date": kick_entries_date,
						"guid": kick_entries_guid,
						"ip": kick_entries_ip,
						"code": kick_entries_code,
						"name": kick_entries_name}

		self.unknownlist = {"date": entries_date,
							"guid": entries_guid,
							"ip": entries_ip,
							"code": entries_code,
							"name": entries_name}


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


class Decoder:


	def __init__(self):
		self.pattern = ["[\"][\s\+,\"][\"]]", "[\"][\s+,\"]*[\+,]+[\s+,\"]*[\"]]"]

	def decode_string(self, txt):
		temp_txt = txt
		for x in range(len(self.pattern)):
			temp_txt = re.sub(self.pattern[x], "", temp_txt)

		return temp_txt


class Spam:


	def __init__(self, spam_data_file, spam_rules_file):
		self.logger = logging.getLogger("Spam ")

		self.spam_data_file = spam_data_file
		self.spam_rules_file = spam_rules_file

		self.players = {}
		self.rules = {} # {Regrex rule:[[triggers][actions], [triggers2][actions2]]}

		self.hackers = {}

	def add_data(self, entries_date, entries_guid, entries_ip, entries_code, entries_name):
		# Loop through entries
		for x in range(len(entries_date)):
			if entries_guid[x] not in self.players: # Check if Player GUID exists in data
				self.players[entries_guid[x]] = {"Name": entries_name[x], "IP":entries_ip}  # Add GUID + Player Name

			# Loop through self.filters & check if entries_code[x] is a match
			for rule in self.rules.keys():
				if re.search(rule, entries_code[x]) or re.search(rule, self.decoder.decode_string(entries_code[x])):   # TODO: Find regrex filter alternative than hardcoded this in everywhere....
					time_stamp = time.mktime((time.strptime(entries_date[x], "%d.%m.%Y %H:%M:%S: ")))
					self.players[entries_guid[x]]["Rules"][rule] = [time_stamp][entries_code[x]]


	def scan(self, scan_time):
		# Loop through Players (unique id = GUID)
		for guid in self.players: # Loop through PLAYERS
			for rule in self.players[guid]["Rules"]: # Loop Logged Rules Detection
				if rule not in self.filters.keys(): # Check if old rule logged
					del self.players[guid]["Rules"][rule] # Remove Old Rule
				else:
					#[[Timestamp][Code]] = self.players[entries_guid[x]][Rules][filter]
					data = self.players[guid]["Rules"][rule] # Current logged rule data = [[Timestamp, Code], [T2,C2]]

					x = 0
					while x <= len(data):
						code_time = data[x][0] # Timestamp
						max_count = self.rules[rule][0]
						max_time =  self.rules[rule][1]
						action = self.rules[rule][2]
						if max_count <= len(data):
							if (data[x][0] - code_time) <= self.rules[rule][0]:
								self.addhacker(action)
								break
						if scan_time - code_time > max_time:
							self.players[guid]["Rules"][rule].pop[0]   # Remove old entry
						else:
							x = x + 1

	def load(self):
			# GUID : Player Info Dict{}
				#{GUID: PlayerInfo{}}
					#{Name: Player Name}
					#{IP: Player IP}
					#{Rules: Regrex Filters{}}
						# regrex-filter1: [Timestamp][Code]
						# regrex-filter2: [Timestamp][Code]
						# regrex-filter3: [Timestamp][Code]
		self.logger.debug(" ")
		self.logger.debug("Checking for " + self.spam_data_file)
		if os.path.isfile(self.spam_data_file) is True:
			self.logger.debug("Spam File Detected")
			f_spam_data_file = open(self.spam_data_file, 'rb')
			self.players = pickle.load(f_spam_data_file)
			self.logger.debug("Loaded Spam Data")
			f_spam_data_file.close()
		else:
			self.players = {}


			# self.rules = {}
				# Regrex Rule: [[count, time elapsed, action], [2x]]
		self.logger.debug("Checking for " + self.spam_rules_file)
		if os.path.isfile(self.spam_rules_file) is True:
			with open(self.spam_rules_file) as f:
				for line in f:
					# data = [0-max_count, 1-time elapsed, 2-action, 3-regrex rule]
					data = re.split(" ", line, 4)
					self.rules[data[3]] = [data[0], data[1], data[2]]
		else:
			open(self.spam_rules_file, 'w').close()
			self.rules = {}

	def save(self):
		# Update players data
		self.logger.debug("Saving Spam Info")
		self.logger.debug(self.spam_data_file)
		self.logger.debug(str(self.players))
		f_spam_data_file = open(self.spam_data_file, 'wb')
		pickle.dump(self.players, f_spam_data_file)
		f_spam_data_file.close()

	def addHacker(self, action):
		pass

	def getHackersLog(self):
		pass

	def clean(self):
		# Remove Hackers From self.players
		# Reset hackers variables
		# Remove Hackers from self.players
		pass