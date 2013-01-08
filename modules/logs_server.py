# logs_server.py
#	 This file is part of pyBEscanner.
#
#	 pyBEscanner is free software: you can redistribute it and/or modify
#	 it under the terms of the GNU General Public License as published by
#	 the Free Software Foundation, either version 3 of the License, or
#	 (at your option) any later version.
#
#	 pyBEscanner is distributed in the hope that it will be useful,
#	 but WITHOUT ANY WARRANTY; without even the implied warranty of
#	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	 GNU General Public License for more details.
#
#	 You should have received a copy of the GNU General Public License
#	 along with pyBEscanner.  If not, see <http://www.gnu.org/licenses/>.


import datetime
import os
import locale
import pickle
import re

pickleVersion = 1


def scan(logfile, log_offset):
	if os.path.isfile(logfile) is True:
		with open(logfile, 'r') as f_log:
			f_log.seek(0,2)
			if f_log.tell() == log_offset:
				f_log_entries = []
				f_offset = log_offset
			else:
				f_log.seek(log_offset)
				f_log_entries = f_log.readlines()
				f_offset = f_log.tell()
	return f_log_entries, f_offset


def load_datafile(logfile, datafile):
	timestamp = os.path.getctime(logfile)
	if os.path.isfile(datafile) is True:
		with open(datafile, 'rb') as f_data_file:
			data = pickle.load(f_data_file)
		if (data["Version"] != pickleVersion) or (data["Timestamp"] != timestamp):
			data = {"Version": pickleVersion, "Offset":0, "Lastline":"", "Timestamp": timestamp}
	else:
		data = {"Version": pickleVersion, "Offset":0, "Lastline":"", "Timestamp": timestamp}
	return data
		
def save_datafile(data, datafile):
	# Update offset_data_file
	with open(datafile, 'wb') as f_datafile:
		pickle.dump(data, f_datafile)



class GUIDTracker:
	def __init__(self, server_settings):
		pass
	
	def addPlayer(self, playername):
		pass
	
	def updatePlayerInfo(self, info):
		pass
		
	def removePlayer(self, playername, endtime):
		pass


class RPTScanner:
	def __init__(self, server_settings):
		self.logfile = server_settings["Server RPT Log"]
		self.offset_data_file = os.path.join(server_settings["Temp Directory"], "server_rpt.offset")

		backup_dir = os.path.join(server_settings["Logs Directory"], datetime.datetime.now().strftime("%Y-%m-%d"))
		self.backup_rptlog = os.path.join(backup_dir, "server_rpt.log")

	def scan_log(self, lastline=1):
		if os.path.isfile(self.logfile) is False:
			print
			print("Warning -- Could Not Find " + self.logfile)
		else:
			self.offset_data = load_datafile(self.logfile, self.offset_data_file)
			self.entries, f_offset = scan(self.logfile, self.offset_data["Offset"])
			self.offset_data["Offset"] = f_offset
			if self.entries != []:
				with open(self.backup_rptlog, "a") as rptlog_backup:
					self.entries[0] = self.offset_data["Lastline"] + self.entries[0]
					x = 0
					while x < (len(self.entries) - lastline):
						rptlog_backup.write(self.entries[x])
						x = x + 1
				self.offset_data["Lastline"] = self.entries[x-1]
				self.entries = []
				save_datafile(self.offset_data, self.offset_data_file)

class ConsoleScanner:
	def __init__(self, server_settings):
		self.logfile = server_settings["Server Console Log"]
		self.offset_data_file = os.path.join(server_settings["Temp Directory"], "server_console.offset")
		
		backup_dir = os.path.join(server_settings["Logs Directory"], datetime.datetime.now().strftime("%Y-%m-%d"))
		self.backup_chatlog = os.path.join(backup_dir, "chat-logs.txt")
		self.backup_consolelog = os.path.join(backup_dir, "server_console.log")

	def scan_log(self, lastline=1):
		if os.path.isfile(self.logfile) is False:
			print()
			print("Warning -- Could Not Find " + self.logfile)
		else:
			self.offset_data = load_datafile(self.logfile, self.offset_data_file)
			self.entries, f_offset = scan(self.logfile, self.offset_data["Offset"])
			self.offset_data["Offset"] = f_offset
			if self.entries != []:
				with open(self.backup_chatlog, "a") as chatlog_backup, open(self.backup_consolelog, "a") as consolelog_backup:
					self.entries[0] = self.offset_data["Lastline"] + self.entries[0]
					x = 0
					while x < (len(self.entries) - lastline):
						consolelog_backup.write(self.entries[x])
						#time = self.entries[x][0:8]
						data = self.entries[x][9:]
						if len(data) > 2:
							if re.match("BattlEye Server: ", data):
								if re.match("BattlEye Server: \(.*\)", data):
									chatlog_backup.write(self.entries[x])
								elif re.match("BattlEye Server: Player #", data):
									pass
								elif re.match("BattlEye Server: Verified GUID", data):
									pass
						x = x + 1
				self.offset_data["Lastline"] = self.entries[x-1]
				self.entries = []
				save_datafile(self.offset_data, self.offset_data_file)