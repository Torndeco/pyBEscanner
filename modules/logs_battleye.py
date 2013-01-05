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

from modules import rcon_cscript

pickleVersion = 1

class Scanner:
	def __init__(self, server_settings):

		self.server_settings = server_settings

		self.bans = Bans(os.path.join(self.server_settings["BattlEye Directory"], "bans.txt"))
		self.kicks = Kicks(os.path.join(self.server_settings["BattlEye Directory"], "kicks.txt"))
		self.rcon = rcon_cscript.Rcon(self.server_settings["ServerIP"], self.server_settings["ServerPort"], self.server_settings["RconPassword"])

		self.ban_guid_list = []
		self.ban_ip_list = []
		self.ban_reason = []
		self.kick_list = []
		self.kick_reason = []

		self.backuplog_dir = os.path.join(self.server_settings["BattlEye Directory"], "Logs", datetime.datetime.now().strftime("BattlEye Logs - %Y-%m-%d"))


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

		if not os.path.exists(os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner")):
			os.mkdir(os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner"))

		for filter_location in self.server_settings["Filters"]:
			if not os.path.exists(filter_location):
				os.mkdir(filter_location)

		if not os.path.exists(self.server_settings["Temp Directory"]):
			os.mkdir(self.server_settings["Temp Directory"])


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
						self.server_settings["Whitelist Filters"][x],
						self.server_settings["Banlist Filters"][x],
						self.server_settings["Kicklist Filters"][x],
						self.server_settings["Spamlist Filters"][x],
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

		for x in range(len(data["guid"])):
			if self.ban_guid_list.count(data["guid"][x]) == 0:
				self.ban_guid_list.append(data["guid"][x])
				self.ban_ip_list.append(data["ip"][x])
				ban_message = self.kick_ban_msg(self.server_settings["Ban Message"], str(data["name"][x]), str(self.server_settings["ServerName"]), logname, str(data["date"][x]))
				self.ban_reason.append(ban_message)
				print ("Banning Player " + str(data["name"][x]))

		if update is True:
			if self.ban_guid_list != []:
				self.bans.openfile()
				for x in range(len(self.ban_guid_list)):
					self.bans.addban(self.ban_guid_list[x], time, self.ban_reason[x])
					if (self.server_settings["Ban IP"] == "on") or (self.ban_guid_list[x] == "-"):
						self.bans.addban(self.ban_ip_list[x], time, self.ban_reason[x])
				self.bans.closefile()
				self.ban_guid_list = []
				self.ban_reason = []

	def update_kicks(self, logname, data, update=False):
		for x in range(len(data["name"])):
			if self.kick_list.count(data["name"][x]) == 0:
				self.kick_list.append(data["name"][x])
				kick_message = self.kick_ban_msg(self.server_settings["Kick Message"], str(data["name"][x]), str(self.server_settings["ServerName"]), logname, str(data["date"][x]))
				self.kick_reason.append(kick_message)

		if update is True:
			if self.kick_list != []:
				self.kicks.openfile()
				for x in range(len(self.kick_list)):
					#self.kicks.addkick(self.kick_list[x], self.kick_reason[x])
					self.kicks.addkick(self.kick_list[x], None)
				self.kicks.closefile()
				self.kick_list = []
				self.kick_reason = []

		for x in range(len(self.kick_list)):
			self.rcon.kickplayer(self.kick_list[x])

	def log(self, x, action, data):
		if data["date"] != []:
			with open((os.path.join(self.backuplog_dir, x + "-" + action + ".txt")), "a") as f_log:
				for x in range(len(data["date"])):
					f_log.write(str(data["date"][x]) + ": " + str(data["name"][x]) + ": (" + str(data["ip"][x]) + ":" + str(data["port"][x]) + ") " + str(data["guid"][x]) + " - " + str(data["code"][x]) + "\n")

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

	def scan_log(self, logfile, backupfile, whitelist_filters, banlist_filters, kicklist_filters, spam_filters, logname):

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
		spam_data_file = logfile + ".spam"

		if os.path.isfile(offset_data_file) is True:
			with open(offset_data_file, 'rb') as f_offset_data_file:
				offset_data = pickle.load(f_offset_data_file)
			if offset_data != []:
				entries_date.append(offset_data[0])
				entries_guid.append(offset_data[1])
				entries_ip.append(offset_data[2])
				entries_port.append(offset_data[3])
				entries_code.append(offset_data[4])
				entries_name.append(offset_data[5])
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
		offset_data = []
		if len(entries_date) > 0:
			x = time.mktime(time.localtime(self.scan_time))
			x2 = time.mktime((time.strptime(entries_date[-1], "%d.%m.%Y %H:%M:%S")))

			if ((x - x2) < self.offset) is True:
				offset_data.append(entries_date.pop())
				offset_data.append(entries_guid.pop())
				offset_data.append(entries_ip.pop())
				offset_data.append(entries_port.pop())
				offset_data.append(entries_code.pop())
				offset_data.append(entries_name.pop())

		# Update offset_data_file
		with open(offset_data_file, 'wb') as f_offset_data_file:
			pickle.dump(offset_data, f_offset_data_file)

		if (len(entries_code) > 0) is True:
			self.spam_detection = Spam(self, spam_data_file, spam_filters, logname)
			self.spam_detection.load()
			self.spam_detection.add_data(entries_date, entries_guid, entries_ip, entries_port, entries_code, entries_name)
			self.spam_detection.scan(x)
			self.spam_detection.sync()
			self.spam_detection.save()

			for wh_filter in whitelist_filters:
				if os.path.isfile(wh_filter) is True:
					# Remove whitelisted entries
					with open(wh_filter) as f:
						for line in f:
							temp = line.strip()
							x = 0
							while x != len(entries_code):
								if re.search(temp, entries_code[x]) is not None:
									entries_date.pop(x)
									entries_guid.pop(x)
									entries_ip.pop(x)
									entries_port.pop(x)
									entries_code.pop(x)
									entries_name.pop(x)
								else:
									x = x + 1
				else:
					open(wh_filter, 'w').close()


			for bl_filter in banlist_filters:
				if bl_filter is not None:
					if os.path.isfile(bl_filter) is True:
						# Search for BlackListed Entries
						with open(bl_filter) as f:
							for line in f:
								temp = line.strip()
								x = 0
								while x != len(entries_code):
									if re.search(temp, entries_code[x]) or re.search(temp, self.decoder.decode_string(entries_code[x])):
										ban_entries_date.append(entries_date.pop(x))
										ban_entries_guid.append(entries_guid.pop(x))
										ban_entries_ip.append(entries_ip.pop(x))
										ban_entries_port.append(entries_port.pop(x))
										ban_entries_code.append(entries_code.pop(x))
										ban_entries_name.append(entries_name.pop(x))
									else:
										x = x + 1
					else:
						open(bl_filter, 'w').close()

			for kl_filter in kicklist_filters:
				if kl_filter is not None:
					if os.path.isfile(kl_filter) is True:
						# Search for KickList Entries
						with open(kl_filter) as f:
							for line in f:
								temp = line.strip()
								x = 0
								while x != len(entries_code):
									if re.search(temp, entries_code[x]) or re.search(temp, self.decoder.decode_string(entries_code[x])):
										kick_entries_date.append(entries_date.pop(x))
										kick_entries_guid.append(entries_guid.pop(x))
										kick_entries_ip.append(entries_ip.pop(x))
										kick_entries_port.append(entries_port.pop(x))
										kick_entries_code.append(entries_code.pop(x))
										kick_entries_name.append(entries_name.pop(x))
									else:
										x = x + 1
					else:
						# If file = missing, create an empty file
						open(kl_filter, 'w').close()


		self.banlist = {"date": ban_entries_date,
						"guid": ban_entries_guid,
						"ip": ban_entries_ip,
						"port": ban_entries_port,
						"code": ban_entries_code,
						"name": ban_entries_name}

		self.kicklist = {"date": kick_entries_date,
						"guid": kick_entries_guid,
						"ip": kick_entries_ip,
						"port": kick_entries_port,
						"code": kick_entries_code,
						"name": kick_entries_name}

		self.unknownlist = {"date": entries_date,
							"guid": entries_guid,
							"ip": entries_ip,
							"port": entries_port,
							"code": entries_code,
							"name": entries_name}


class Bans:


	def __init__(self, bans_file):
		self.bans_file = bans_file

	def openfile(self):
		self.f_bans = open(self.bans_file, "a")

	def closefile(self):
		self.f_bans.close()

	def addban(self, guid_ip, time, reason):
		self.f_bans.write(guid_ip + " " + time + " " + reason + "\n")

	def removeban(self, guid, time, reason):
		pass

class Kicks:

	def __init__(self, logfile):
		self.kicks_file = logfile

	def openfile(self):
		self.f_kicks = open(self.kicks_file, "a")

	def closefile(self):
		self.f_kicks.close()

	def addkick(self, playername, reason):
		self.f_kicks.write(playername + "\n")
		#self.f_bans.write(guid_ip + " " + time + " " + reason + "\n")

	def removekick(self, guid, time, reason):
		pass

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
		self.rules = {} # {Regrex rule:[[triggers][actions], [triggers2][actions2]]}

		self.hackers = {}
		self.decoder = Decoder()

	def add_data(self, entries_date, entries_guid, entries_ip, entries_port, entries_code, entries_name):
		# Loop through entries
		for x in range(len(entries_date)):
			# Loop through self.filters & check if entries_code[x] is a match
			for rule in self.rules.keys():
				if re.search(rule, entries_code[x]) or re.search(rule, self.decoder.decode_string(entries_code[x])):
					if entries_guid[x] not in self.players: # Check if Player GUID exists in data
						self.players[entries_guid[x]] = {"name": entries_name[x], "ip":entries_ip[x], "port":entries_port[x], "rules":{}}  # Add GUID + Player Name
					time_stamp = time.mktime((time.strptime(entries_date[x], "%d.%m.%Y %H:%M:%S")))
					data = self.players[entries_guid[x]]["rules"].get(rule, [])
					data.append([time_stamp, entries_code[x]])
					self.players[entries_guid[x]]["rules"][rule] = data


	def scan(self, scan_time):
		# Loop through Players (unique id = GUID)
		player_guid_list = self.players.keys()
		for guid in player_guid_list: # Loop through PLAYERS
			player_logged_rules = self.players[guid]["rules"].keys()
			for rule in player_logged_rules: # Loop Logged Rules Detection
				if rule not in self.rules.keys(): # Check if old rule logged
					del self.players[guid]["rules"][rule] # Remove Old Rule
				else:
					#[[Timestamp][Code]] = self.players[entries_guid[x]][Rules][filter]
					data = self.players[guid]["rules"][rule] # Current logged rule data = [[Timestamp, Code], [T2,C2]]
					x = 0
					ignore_count = 0
					while x < len(data):
						max_count = int(self.rules[rule][0])
						max_time =  int(self.rules[rule][1])
						action = self.rules[rule][2]
						if ignore_count != 0:
							ignore_count = ignore_count - 1
						if (x + max_count) < len(data):
							if (data[x + max_count - 1][0] - data[x][0]) <= max_time:
								for y in range((x + ignore_count), (x + max_count)):
									self.addHacker(guid, action, time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(data[y][0])), data[y][1])
								ignore_count = max_count
						if (scan_time - data[x][0]) > max_time:
							self.players[guid]["rules"][rule].pop(0)   # Remove old entry
						else:
							x = x + 1
					if self.players[guid]["rules"][rule] == []:
						del self.players[guid]["rules"][rule]  # Remove Rule if no-more logged entries present
			if self.players[guid]["rules"] == {}:
				del self.players[guid] # Remove Player Info if no-more logged entries present

	def load(self):
			# GUID : Player Info Dict{}
				#{GUID: PlayerInfo{}}
					#{Name: Player Name}
					#{IP: Player IP}
					#{Rules: Regrex Filters{}}
						# regrex-filter1: [Timestamp][Code]
						# regrex-filter2: [Timestamp][Code]
						# regrex-filter3: [Timestamp][Code]
		if os.path.isfile(self.spam_data_file) is True:
			with open(self.spam_data_file, 'rb') as f_spam_data_file:
				f_spam_data_file = open(self.spam_data_file, 'rb')
			self.players = pickle.load(f_spam_data_file)
		else:
			self.players = {}


			# self.rules = {}
				# Regrex Rule: [[count, time elapsed, action], [2x]]
		for spam_rules_file in self.spam_rules_files:
			if os.path.isfile(spam_rules_file) is True:
				with open(spam_rules_file) as f:
					for line in f:
						# data = [0-max_count, 1-time elapsed, 2-action, 3-regrex rule]
						data = re.split(" ", line.strip(), 4)
						self.rules[data[3]] = [float(data[0]), data[1], data[2]]
			else:
				open(spam_rules_file, 'w').close()
				self.rules = {}

	def save(self):
		# Update players data
		with open(self.spam_data_file, 'wb') as f_spam_data_file:
			pickle.dump(self.players, f_spam_data_file)

	def addHacker(self, guid, action, code_time, code_entry):

		if guid not in self.hackers.keys():
			self.hackers[guid] = {"name": self.players[guid]["name"],
							"ip": self.players[guid]["ip"],
							"port": self.players[guid]["port"],
							"action": {}}
		if action not in self.hackers[guid]["action"].keys():
			self.hackers[guid]["action"][action] = [[code_time, code_entry]]
		else:
			temp = self.hackers[guid]["action"][action]
			temp.append([code_time, code_entry])
			self.hackers[guid]["action"][action] = temp

	def sync(self):
		if self.hackers != {}:
			banlist = {"date": [], "guid": [], "ip": [], "port": [], "code": [], "name": []}
			kicklist = {"date": [], "guid": [], "ip": [], "port": [], "code": [], "name": []}

			with open((os.path.join(self.parent.parent.backuplog_dir, self.logname + "-spam.txt")), "a") as f_log:
				for guid in self.hackers:
					name = self.hackers[guid]["name"]
					ip = self.hackers[guid]["ip"]
					port = self.hackers[guid]["port"]
					for action in self.hackers[guid]["action"]:
						f_log.write("\n")
						f_log.write("Player Name = " + name + "\n")
						f_log.write("\tAction = " + action + "\n")
						data = self.hackers[guid]["action"][action]
						for x in range(len(data)):
							f_log.write("\t\t" + str(data[x][0]) + ": " + str(name) + " " + str(ip) + ":" + str(port) + " " + str(guid) + " - " + str(data[x][1]) + "\n")
						if action == "BAN":
							banlist["date"].append(data[x][0])
							banlist["guid"].append(guid)
							banlist["ip"].append(ip)
							banlist["port"].append(port)
							banlist["code"].append(data[x][1])
							banlist["name"].append(name)
						elif action == "KICK":
							kicklist["date"].append(data[x][0])
							kicklist["guid"].append(guid)
							kicklist["ip"].append(ip)
							kicklist["port"].append(port)
							kicklist["code"].append(data[x][1])
							kicklist["name"].append(name)
				self.hackers = {}
				self.parent.parent.update_bans(self.logname, banlist, update=True)
				self.parent.parent.update_kicks(self.logname, kicklist, update=True)
