# logs_battleye.py
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

import cPickle as pickle
import datetime
import os
import re
import shutil
import string
import sys
import time

#from modules import rcon_cscript

pickleVersion = 3

		# rules {}
		# Regrex Rule: Extra Info {}
		#	Exception:[x,y], Time:x, Max Count:x

def load_rules(rule_files):
	rules = {}
	for rule_file in rule_files:
		if os.path.isfile(rule_file) is True:
			with open(rule_file) as f:
				for line in f:
					line = line.strip()
					if (line[:1] != "#") and (line != ""):
						temp = re.split("\s=\s", line, 1)
						if temp[0] == "Rule":
							current_rule = temp[0]
							rules[current_rule] = {"Exception":[]}
						elif temp[0] == "Exception":
							rules[current_rule]["Exception"].append(temp[1])
						elif temp[0] == "Time":
							rules[current_rule]["Time"] = int(temp[1])
						elif temp[0] == "Count":
							rules[current_rule]["Max Count"] = int(temp[1])
						elif temp[0] == "Action":
							if temp[1] == "DELETE":
								del rules[current_rule]
							else:
								rules[current_rule]["Action"] = temp[1]
						else:
							print 
							print "Error rule file " + rule_file
							print line
							print "-----"
							sys.exit()
		else:
			open(rule_file, 'w').close()
	return rules


class Scanner:
	def __init__(self, server_settings):

		self.server_settings = server_settings

		self.bans = self.server_settings["Bans"]
		self.kicks = Kicks(os.path.join(self.server_settings["Temp Directory"], "kicks.txt"))

		self.bans_guid_list = []
		self.bans_ip_list = []
		self.bans_info_list = []
		self.kick_list = []
		self.kick_reason = []

		self.backuplog_dir = os.path.join(self.server_settings["Logs Directory"], datetime.datetime.now().strftime("%Y-%m-%d"), "BattlEye Logs")

		self.backup_logs = {"addbackpackcargo": os.path.join(self.backuplog_dir, "addbackpackcargo.log"),
						"addmagazinecargo": os.path.join(self.backuplog_dir, "addmagazinecargo.log"),
						"addweaponcargo": os.path.join(self.backuplog_dir, "addweaponcargo.log"),
						"attachto": os.path.join(self.backuplog_dir, "attachto.log"),
						"createvehicle": os.path.join(self.backuplog_dir, "createvehicle.log"),
						"deletevehicle": os.path.join(self.backuplog_dir, "deletevehicle.log"),
						"mpeventhandler": os.path.join(self.backuplog_dir, "mpeventhandler.log"),
						"publicvariable": os.path.join(self.backuplog_dir, "publicvariable.log"),
						"remotecontrol": os.path.join(self.backuplog_dir, "remotecontrol.log"),
						"remoteexec": os.path.join(self.backuplog_dir, "remoteexec.log"),
						"scripts": os.path.join(self.backuplog_dir, "scripts.log"),
						"selectplayer": os.path.join(self.backuplog_dir, "selectplayer.log"),
						"setdamage": os.path.join(self.backuplog_dir, "setdamage.log"),
						"setpos": os.path.join(self.backuplog_dir, "setpos.log"),
						"setvariable": os.path.join(self.backuplog_dir, "setvariable.log"),
						"teamswitch": os.path.join(self.backuplog_dir, "teamswitch.log")}


		# Create Backup Folder if it doesnt exist
		if not os.path.exists(self.backuplog_dir):
			os.makedirs(self.backuplog_dir)

		for filter_location in self.server_settings["Rules"]:
			if not os.path.exists(filter_location):
				os.mkdir(filter_location)

		if not os.path.exists(self.server_settings["Temp Directory"]):
			os.makedirs(self.server_settings["Temp Directory"])


	def scan_battleye_logs(self, x):


		if self.server_settings[x] == "off":
			if os.path.isfile(self.server_settings["Battleye Temp Logs"][x]) is True:
				with open(self.backup_logs[x], "a") as f_backup, open(self.server_settings["Battleye Temp Logs"][x]) as f_log:
					for line in f_log:
						## Append Lines to Backup Files
						f_backup.write(line)
				os.remove(self.backup_logs[x])
		else:
			self.log_scanner.scan_log(self.server_settings["Battleye Temp Logs"][x],
						self.backup_logs[x],
						self.server_settings["Whitelist Rules"][x],
						self.server_settings["Banlist Rules"][x],
						self.server_settings["Kicklist Rules"][x],
						self.server_settings["Spamlist Rules"][x],
						x)
			if self.server_settings[x] == "strict":
				# Strict Scanning
				self.update_bans(x, self.log_scanner.banlist)
				self.update_bans(x, self.log_scanner.kicklist)
				self.update_bans(x, self.log_scanner.unknownlist, update=True)

				# Logging
				self.log(x, "bans", self.log_scanner.banlist)
				self.log(x, "kicks", self.log_scanner.kicklist)
				self.log(x, "unknown-bans", self.log_scanner.unknownlist)

			elif self.server_settings[x] == "standard+kick":
				# Standard Scanning + Kicking
				self.update_bans(x, self.log_scanner.banlist, update=True)
				self.update_kicks(x, self.log_scanner.kicklist)
				self.update_kicks(x, self.log_scanner.unknownlist, update=True)

				# Logging
				self.log(x, "bans", self.log_scanner.banlist)
				self.log(x, "kicks", self.log_scanner.kicklist)
				self.log(x, "unknown-kicks", self.log_scanner.unknownlist)

			elif self.server_settings[x] == "standard":
				# Standard Scanning
				self.update_bans(x, self.log_scanner.banlist, update=True)
				self.update_kicks(x, self.log_scanner.kicklist, update=True)

				# Logging
				self.log(x, "bans", self.log_scanner.banlist)
				self.log(x, "kicks", self.log_scanner.kicklist)
				self.log(x, "unknown", self.log_scanner.unknownlist)

			else:
				print
				print self.server_settings[x]["ServerName"]
				print x + " (unknown option)"
				sys.exit()

	def kick_ban_msg(self, template, player_name, server_name, log_file, date_time):
		tmp = string.replace(template, "PLAYER_NAME", player_name)
		tmp = string.replace(tmp, "SERVER_NAME", server_name)
		tmp = string.replace(tmp, "LOG_FILE", log_file)
		tmp = string.replace(tmp, "DATE_TIME", date_time)
		return tmp

	def update_bans(self, logname, data, time="-1", update=False):

		for x in range(len(data["Guid"])):
			guid = data["Guid"][x]
			ip = data["IP"][x]
			player_name = data["Name"][x]
			date = data["Date"][x]

			if guid == "-":
				self.bans_guid_list.append(None)
			else:
				self.bans_guid_list.append(guid)
			self.bans_info_list.append({"Name": player_name, "Guid": guid, "IP": ip, "ServerName": self.server_settings["ServerName"], "Date":date})
			self.bans_ip_list.append(ip)

				#def addBan(self, unique_id, info, logname, ban_template, report_template): #{ID,Reason}
		if update:
			for x in range(len(self.bans_guid_list)):
				if (self.server_settings["Ban IP"] == "on") or (self.bans_guid_list[x] == None):
					self.bans.addBan(self.bans_ip_list[x], self.bans_info_list[x], logname, self.server_settings["Ban Message"], self.server_settings["Report Message"], self.server_settings["Ban IP Time"])
				if self.bans_guid_list[x] != None:
					self.bans.addBan(self.bans_guid_list[x], self.bans_info_list[x], logname, self.server_settings["Ban Message"], self.server_settings["Report Message"], "-1")
			if self.bans_guid_list != []:
				self.bans.updateStatus(True)
				self.bans_guid_list = []
				self.bans_ip_list = []
				self.bans_info_list = []

	def update_kicks(self, logname, data, update=False):
		for x in range(len(data["Name"])):
			if self.kick_list.count(data["Name"][x]) == 0:
				self.kick_list.append(data["Name"][x])
				kick_message = self.kick_ban_msg(self.server_settings["Kick Message"], str(data["Name"][x]), str(self.server_settings["ServerName"]), logname, str(data["Date"][x]))
				self.kick_reason.append(kick_message)

		if update is True:
			if self.kick_list != []:
				for player in self.kick_list:
					#self.kicks.addkick(self.kick_list[x], self.kick_reason[x])
					self.kicks.addkick(player, None)
				self.kicks.synckicks()
				self.kick_list = []
				self.kick_reason = []

	def log(self, x, action, data):
		if data["Date"] != []:
			with open((os.path.join(self.backuplog_dir, x + "-" + action + ".txt")), "a") as f_log:
				for x in range(len(data["Date"])):
					f_log.write(str(data["Date"][x]) + ": " + str(data["Name"][x]) + ": (" + str(data["IP"][x]) + ":" + str(data["Port"][x]) + ") " + str(data["Guid"][x]) + " - " + str(data["Code"][x]) + "\n")

	def scan(self):

		self.log_scanner = Parser(self, time.time(), float(self.server_settings["OffSet"]))

		for log in self.server_settings["Battleye Logs"]:
			if os.path.isfile(self.server_settings["Battleye Logs Location"][log]) is True:
				if os.path.isfile(self.server_settings["Battleye Temp Logs"][log]) is True:
					os.remove(self.server_settings["Battleye Temp Logs"][log])
				error_loop = 0
				while True:
					try:
						shutil.move(self.server_settings["Battleye Logs Location"][log], self.server_settings["Battleye Temp Logs"][log])
						break
					except WindowsError:
						if error_loop >= 5:
							print "Error file " + log + " in usage by a process, skipping..."
							break
						else:
							error_loop = error_loop + 1
							time.sleep(1)

		for log in self.server_settings["Battleye Logs"]:
			self.scan_battleye_logs(log)



class Parser:
	def __init__(self, parent, scan_time, offset):
		self.parent = parent

		self.scan_time = scan_time
		self.offset = offset
		self.decoder = Decoder()


	def scan_log(self, logfile, backupfile, whitelist_rules, banlist_rules, kicklist_rules, spam_rules, logname):

		# Entries
		entries_date = []
		entries_guid = []
		entries_ip = []
		entries_port = []
		entries_code = []
		entries_name = []

		# Ban Entries
		ban_entries_date = []
		ban_entries_guid = []
		ban_entries_ip = []
		ban_entries_port = []
		ban_entries_code = []
		ban_entries_name = []

		# Kick Entries
		kick_entries_date = []
		kick_entries_guid = []
		kick_entries_ip = []
		kick_entries_port = []
		kick_entries_code = []
		kick_entries_name = []

		# Check for Offset pickle file / Initialize OffSet Data
		offset_data_file = logfile + ".offset"

		if os.path.isfile(offset_data_file) is True:
			with open(offset_data_file, 'rb') as f_offset_data_file:
				offset_data = pickle.load(f_offset_data_file)
			if offset_data["Version"] == pickleVersion:
				if offset_data["Data"] != []:
					entries_date.append(offset_data["Data"][0])
					entries_guid.append(offset_data["Data"][1])
					entries_ip.append(offset_data["Data"][2])
					entries_port.append(offset_data["Data"][3])
					entries_code.append(offset_data["Data"][4])
					entries_name.append(offset_data["Data"][5])
		# Scan BattlEye Logs
		if os.path.isfile(logfile) is True:
			with open(backupfile, "a") as f_backup, open(logfile) as f_log:
				for line in f_log:
					## Append Lines to Backup Files
					f_backup.write(line)

					line_stripped = line.strip()
					date = re.match('\A[0-3][0-9]\.[0-1][0-9]\.[0-9][0-9][0-9][0-9][ ][0-2][0-9][:][0-6][0-9][:][0-6][0-9][:]\s', line_stripped)
					temp = re.split('\A[0-3][0-9]\.[0-1][0-9]\.[0-9][0-9][0-9][0-9][ ][0-2][0-9][:][0-6][0-9][:][0-6][0-9][:]\s', line_stripped, 1)
					if date is None:
						x = len(entries_date) - 1
						if x >= 0:
							entries_code[x] = entries_code[x] + line.strip()
					else:
						name = re.split("\s.\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}[0-9].\s", temp[1], 1)
						ip_port = re.split(':', re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}[0-9]", line_stripped).group(0))
						code = re.split("\s-\s", name[1], 1)
						entries_date.append(date.group()[:-2])
						entries_guid.append(code[0])
						entries_ip.append(ip_port[0])
						entries_port.append(ip_port[1])
						entries_code.append(code[1])
						entries_name.append(name[0])
			os.remove(logfile)

		# Check for battleye offset condition
		offset_data = {"Version": pickleVersion, "Data": []}
		if len(entries_date) > 0:
			x = time.mktime(time.localtime(self.scan_time))
			x2 = time.mktime((time.strptime(entries_date[-1], "%d.%m.%Y %H:%M:%S")))

			if ((x - x2) < self.offset) is True:
				offset_data["Data"].append(entries_date.pop())
				offset_data["Data"].append(entries_guid.pop())
				offset_data["Data"].append(entries_ip.pop())
				offset_data["Data"].append(entries_port.pop())
				offset_data["Data"].append(entries_code.pop())
				offset_data["Data"].append(entries_name.pop())

		# Update offset_data_file
		with open(offset_data_file, 'wb') as f_offset_data_file:
			pickle.dump(offset_data, f_offset_data_file)

		if (len(entries_code) > 0) is True:
			spam_data_file = logfile + ".spam"
			self.spam_detection = Spam(self, spam_data_file, spam_rules, logname)
			self.spam_detection.load()
			self.spam_detection.add_data(entries_date, entries_guid, entries_ip, entries_port, entries_code, entries_name)
			self.spam_detection.scan(x)
			self.spam_detection.sync()
			self.spam_detection.save()

			# rules {}
			# Regrex Rule: Extra Info {}
			#	Exception:[x,y], Time:x, Max Count:x
			wl_rules = load_rules(whitelist_rules)
			for rule in wl_rules.keys():
				x = 0
				while x != len(entries_code):
					if re.search(rule, entries_code[x]) is not None:
						exception_flag = False
						for exception_rule in wl_rules[rule]["Exception"]:
							if re.search(exception_rule, entries_code[x]):
								exception_flag = True	
								break								
						if exception_flag is False:
							entries_date.pop(x)
							entries_guid.pop(x)
							entries_ip.pop(x)
							entries_port.pop(x)
							entries_code.pop(x)
							entries_name.pop(x)
					else:
						x = x + 1


			kl_rules = load_rules(kicklist_rules)
			for rule in kl_rules.keys():
				x = 0
				while x != len(entries_code):
					if re.search(rule, entries_code[x]) or re.search(rule, self.decoder.decode_string(entries_code[x])):
						exception_flag = False
						for exception_rule in kl_rules[rule]["Exception"]:
							if re.search(exception_rule, entries_code[x]):
								exception_flag = True	
								break	
						if exception_flag is False:
							kick_entries_date.append(entries_date.pop(x))
							kick_entries_guid.append(entries_guid.pop(x))
							kick_entries_ip.append(entries_ip.pop(x))
							kick_entries_port.append(entries_port.pop(x))
							kick_entries_code.append(entries_code.pop(x))
							kick_entries_name.append(entries_name.pop(x))
					else:
						x = x + 1



			bl_rules = load_rules(banlist_rules)
			for rule in bl_rules.keys():
				x = 0
				while x != len(entries_code):
					if re.search(rule, entries_code[x]) or re.search(rule, self.decoder.decode_string(entries_code[x])):
						exception_flag = False
						for exception_rule in bl_rules[rule]["Exception"]:
							if re.search(exception_rule, entries_code[x]):
								exception_flag = True	
								break	
						if exception_flag is False:
							ban_entries_date.append(entries_date.pop(x))
							ban_entries_guid.append(entries_guid.pop(x))
							ban_entries_ip.append(entries_ip.pop(x))
							ban_entries_port.append(entries_port.pop(x))
							ban_entries_code.append(entries_code.pop(x))
							ban_entries_name.append(entries_name.pop(x))
					else:
						x = x + 1


		self.banlist = {"Date": ban_entries_date,
						"Guid": ban_entries_guid,
						"IP": ban_entries_ip,
						"Port": ban_entries_port,
						"Code": ban_entries_code,
						"Name": ban_entries_name}

		self.kicklist = {"Date": kick_entries_date,
						"Guid": kick_entries_guid,
						"IP": kick_entries_ip,
						"Port": kick_entries_port,
						"Code": kick_entries_code,
						"Name": kick_entries_name}

		self.unknownlist = {"Date": entries_date,
							"Guid": entries_guid,
							"IP": entries_ip,
							"Port": entries_port,
							"Code": entries_code,
							"Name": entries_name}


class Kicks:

	def __init__(self, logfile):
		self.kicks = {}
		self.kicks_file = logfile

	def addkick(self, playername, reason):
		self.kicks[playername] = reason

	def removekick(self, playername):
		if playername in self.kicks:
			del self.kicks[playername]

	def synckicks(self):
		if self.kicks != {}:
			with open(self.kicks_file, "a") as f_kicks:
				for playername in list(self.kicks.keys()):
					f_kicks.write(playername + "\n")

					
class Decoder:


	def __init__(self):
		self.pattern = ["\"[\s\+,\"]\"", "[\"][\s+,\"]*[\+,]+[\s+,\"]*[\"]]"]

	def decode_string(self, txt):
		temp_txt = txt
		for x in range(len(self.pattern)):
			temp_txt = re.sub(self.pattern[x], "", temp_txt)

		return temp_txt


class Spam:


	def __init__(self, parent, spam_data_file, spam_rules_files, logname):
		self.parent = parent

		self.spam_data_file = spam_data_file
		self.spam_rules_files = spam_rules_files
		self.logname = logname

		self.players = {}
		
		# rules {}
		# Regrex Rule: Extra Info {}
		#	Exception:[x,y], Time:x, Max Count:x
		self.rules = {}

		self.hackers = {}
		self.decoder = Decoder()


	def add_data(self, entries_date, entries_guid, entries_ip, entries_port, entries_code, entries_name):
		# Loop through entries
		for x in range(len(entries_date)):
			# Loop through self.rules & check if entries_code[x] is a match
			for rule in self.rules.keys():
				if re.search(rule, entries_code[x]) or re.search(rule, self.decoder.decode_string(entries_code[x])):
					if entries_guid[x] not in self.players: # Check if Player GUID exists in data
						rules_data = {"Exceptions": [], "Data": []}
						self.players[entries_guid[x]] = {"Name": entries_name[x], 
														"IP":    entries_ip[x], 
														"Port":  entries_port[x], 
														"Rules": rules_data}
					time_stamp = time.mktime((time.strptime(entries_date[x], "%d.%m.%Y %H:%M:%S")))
					data = self.players[entries_guid[x]]["Rules"][rule]["Data"]
					data.append([time_stamp, entries_code[x]])
					self.players[entries_guid[x]]["Rules"][rule]["Data"] = data


	def scan(self, scan_time):
		# Loop through Players (unique id = GUID)
		player_guid_list = self.players.keys()
		for guid in player_guid_list: # Loop through PLAYERS
			player_logged_rules = self.players[guid]["Rules"].keys()
			for rule in player_logged_rules: # Loop Logged Rules Detection
				if rule not in self.rules.keys(): # Check if old rule logged
					del self.players[guid]["Rules"][rule] # Remove Old Rule
				elif (self.players[guid]["Rules"][rule]["Exceptions"] != self.rules[rule]["Exceptions"]): # Reset Spam data if Exceptions are Changed
						self.players[guid]["Rules"][rule] = {"Exceptions": [], "Data": []}
				else:
					#[[Timestamp][Code]] = self.players[entries_guid[x]][Rules][filter]
					data = self.players[guid]["Rules"][rule] # Current logged rule data = [[Timestamp, Code], [T2,C2]]
					x = 0
					ignore_count = 0
					while x < len(data):

						if ignore_count != 0:
							ignore_count = ignore_count - 1
						if (x + self.rules[rule]["Max Count"]) < len(data):
							if (data[x + self.rules[rule]["Max Count"] - 1][0] - data[x][0]) <= self.rules[rule]["Time"]:
								for y in range((x + ignore_count), (x + self.rules[rule]["Max Count"])):
									self.addHacker(
													guid, 
													self.rules[rule]["Action"], 
													time.strftime("%d.%m.%Y %H:%M:%S", 
													time.localtime(data[y][0])), 
													data[y][1])
								ignore_count = self.rules[rule]["Max Count"]
						if (scan_time - data[x][0]) > self.rules[rule]["Time"]:
							self.players[guid]["Rules"][rule].pop(0)   # Remove old entry
						else:
							x = x + 1
					if self.players[guid]["Rules"][rule] == []:
						del self.players[guid]["Rules"][rule]  # Remove Rule if no-more logged entries present
			if self.players[guid]["Rules"] == {}:
				del self.players[guid] # Remove Player Info if no-more logged entries present


	def load(self):
			# GUID : Player Info Dict{}
				#{GUID: PlayerInfo{}}
					#{Name: Player Name}
					#{IP: Player IP}
					#{Rules: Regrex Rules{}}
						# regrex-filter1: [Timestamp][Code][Exceptions]
						# regrex-filter2: [Timestamp][Code][Exceptions]
						# regrex-filter3: [Timestamp][Code][Exceptions]
		if os.path.isfile(self.spam_data_file) is True:
			with open(self.spam_data_file, 'rb') as f_spam_data_file:
				spam_data = pickle.load(f_spam_data_file)
			if spam_data["Version"] == pickleVersion:
				self.players = spam_data["Data"]
			else:
				self.players = {}
		else:
			self.players = {}
		self.rules = load_rules(self.spam_rules_files)
	

	def save(self):
		# Update players data
		spam_data = {"Version": pickleVersion, "Data": self.players}
		with open(self.spam_data_file, 'wb') as f_spam_data_file:
			pickle.dump(spam_data, f_spam_data_file)


	def addHacker(self, guid, action, code_time, code_entry):

		if guid not in self.hackers.keys():
			self.hackers[guid] = {"Name": self.players[guid]["Name"],
								"IP": self.players[guid]["IP"],
								"Port": self.players[guid]["Port"],
								"Action": {}}
		if action not in self.hackers[guid]["Action"].keys():
			self.hackers[guid]["Action"][action] = [[code_time, code_entry]]
		else:
			temp = self.hackers[guid]["Action"][action]
			temp.append([code_time, code_entry])
			self.hackers[guid]["Action"][action] = temp


	def sync(self):
		if self.hackers != {}:
			banlist = {"Date": [], "Guid": [], "IP": [], "Port": [], "Code": [], "Name": []}
			kicklist = {"Date": [], "Guid": [], "IP": [], "Port": [], "Code": [], "Name": []}

			with open((os.path.join(self.parent.parent.backuplog_dir, self.logname + "-spam.txt")), "a") as f_log:
				for guid in self.hackers:
					name = self.hackers[guid]["Name"]
					ip = self.hackers[guid]["IP"]
					port = self.hackers[guid]["Port"]
					for action in self.hackers[guid]["Action"]:
						f_log.write("\n")
						f_log.write("Player Name = " + name + "\n")
						f_log.write("\tAction = " + action + "\n")
						data = self.hackers[guid]["Action"][action]
						for x in range(len(data)):
							f_log.write("\t\t" + str(data[x][0]) + ": " + str(name) + " " + str(ip) + ":" + str(port) + " " + str(guid) + " - " + str(data[x][1]) + "\n")
						if action == "BAN":
							banlist["Date"].append(data[x][0])
							banlist["Guid"].append(guid)
							banlist["IP"].append(ip)
							banlist["Port"].append(port)
							banlist["Code"].append(data[x][1])
							banlist["Name"].append(name)
						elif action == "KICK":
							kicklist["Date"].append(data[x][0])
							kicklist["Guid"].append(guid)
							kicklist["IP"].append(ip)
							kicklist["Port"].append(port)
							kicklist["Code"].append(data[x][1])
							kicklist["Name"].append(name)

				self.hackers = {}
				self.parent.parent.update_bans(self.logname, banlist, update=True)
				self.parent.parent.update_kicks(self.logname, kicklist, update=True)
