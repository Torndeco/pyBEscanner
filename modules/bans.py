# Filename: bans.py
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

import copy
import os
import pickle
import re
import time

pickleVersion = 4

class BansDeamon:
	def __init__(self, bans_symlink_directory, bans_ip_time):
		if bans_symlink_directory != None:
			self.bans_symlinked = Bans(bans_symlink_directory, bans_ip_time)
		
		# {ServerName: 
#			{"Bans":Bans,
#			 "Bans Shared":Bans_Shared}
#			}
		self.bans_server_list = {}
		
	def addServer(self, servername, bans_directory, bans_shared, bans_symlinked, bans_ip_time):
		if bans_symlinked == "on":
			self.bans_server_list[servername] = {"Bans": self.bans_symlinked, "Bans Shared": bans_shared}
		else:
			self.bans_server_list[servername] = {"Bans": Bans(bans_directory, bans_ip_time), "Bans Shared": bans_shared}


	def getStatus(self, servername):
		return self.bans_server_list[servername]["Bans"].getStatus()

	def updateStatus(self, servername, status):
		self.bans_server_list[servername]["Bans"].updateStatus(status)
	
	def addBan(self, servername, unique_id, info, logname, ban_template, report_template, time):
		if self.bans_server_list[servername]["Bans Shared"] == "on":
			for servername in self.bans_server_list:
				self.bans_server_list[servername]["Bans"].addBan(unique_id, info, logname, ban_template, report_template, time)
		else:
			self.bans_server_list[servername]["Bans"].addBan(unique_id, info, logname, ban_template, report_template, time)

	def writeBans(self, servername):
		self.bans_server_list[servername]["Bans"].writeBans()

	def checkBans(self, servername):
		self.bans_server_list[servername]["Bans"].checkBans()

class Bans:

	def __init__(self, bans_directory, bans_ip_time):
		self.bans_file = os.path.join(bans_directory, "bans.txt")
		self.bans_report_file = os.path.join(bans_directory, "bans-pyBEscanner-report.txt")
		
		self.data = {"Version":2, "Bans":set(), "Timestamp":{"Local":None}}
		self.data_file = os.path.join(bans_directory, "bans.data")
		
		self.bans_ip_time = bans_ip_time

		self.new_bans = {}
		self.updateStatus(False)
		
		if os.path.exists(bans_directory) is False:
			os.makedirs(bans_directory)
		if os.path.isfile(self.bans_file) is False:
			open(self.bans_file, 'w').close()

		self.loadBanInfo()
		self.checkBans()


	def loadBanInfo(self):

		self.data["Version"] = pickleVersion
		self.info = {}

		if os.path.isfile(self.data_file) is True:
			f_bans_data = open(self.data_file, 'rb')
			data = pickle.load(f_bans_data)
			if data["Version"] == pickleVersion:
				self.data = data
			else:
				self.data["Bans"] = set()
				self.data["Timestamp"] = {"Local": None}

	def saveBanInfo(self):
		f_bans_data = open(self.data_file, 'wb')
		pickle.dump(self.data, f_bans_data)
		f_bans_data.close()

		
	def checkBans(self):
		timestamp = os.path.getmtime(self.bans_file)	  
		if self.data["Timestamp"]["Local"] != timestamp:
			print
			self.data["Timestamp"]["Local"] = timestamp
			self.updateStatus(True)
			bans_compare = copy.deepcopy(self.data["Bans"])
			with open(self.bans_file) as b_file:
				for line in b_file:
					data = re.split(' ', line.rstrip(), 2)
					if len(data) == 3:
						if data[0] not in self.data["Bans"]:
							self.data["Bans"].add(data[0])
							print("Ban Added: " + data[0])
						else:
							if data[0] in bans_compare:
								bans_compare.remove(data[0])
			if len(bans_compare) > 0:
				for x in bans_compare:
					self.data["Bans"].remove(x)
					print("Ban Removed: " + x)
			self.saveBanInfo()
			
	def formatMessage(self, template, player_name, server_name, log_file, date_time, guid, ip):
		tmp = template.replace("LOG_FILE", log_file)
		tmp = tmp.replace("DATE_TIME", date_time)
		tmp = tmp.replace("SERVER_NAME", server_name)
		tmp = tmp.replace("PLAYER_NAME", player_name)
		tmp = tmp.replace("GUID", guid)
		tmp = tmp.replace("IP", ip)
		return tmp

	def addBan(self, unique_id, info, logname, ban_template, report_template, time): #{ID,Reason}
		if unique_id not in self.data["Bans"]:
			if unique_id not in self.new_bans:
				self.data["Bans"].add(unique_id)
				self.new_bans[unique_id] = info
				self.new_bans[unique_id]["logname"] = logname
				self.new_bans[unique_id]["Ban Template"] = ban_template
				self.new_bans[unique_id]["Report Template"] = report_template
			else:
				self.new_bans[unique_id]["logname"].append(logname)
		self.updateStatus(True)

	def writeBans(self):
		print
		current_time = time.mktime(time.localtime())
		if self.new_bans != {}:
			with open(self.bans_file, "a") as f_bans, open(self.bans_report_file, "a") as f_report:
				for unique_id in self.new_bans.keys():
					guid = self.new_bans[unique_id]["Guid"]
					ip = self.new_bans[unique_id]["IP"]
					server_name = self.new_bans[unique_id]["ServerName"]
					date_time = self.new_bans[unique_id]["Date"]
					player_name = self.new_bans[unique_id]["Name"]
					lognames = self.new_bans[unique_id]["logname"]
					bans_message_template = self.new_bans[unique_id]["Ban Template"]
					report_message_template = self.new_bans[unique_id]["Report Template"]
					if self.bans_ip_time == "-1":
						ban_time = "-1"
					else:
						ban_time = str(current_time + (int(ban_time) * 86400))
					f_bans.write(unique_id + " " + str(ban_time) + " " + self.formatMessage(bans_message_template, player_name, server_name, lognames, date_time, guid, ip) + "\n")
					f_report.write(unique_id + " " + str(ban_time) + " " + self.formatMessage(report_message_template, player_name, server_name, lognames, date_time, guid, ip) + "\n")
					print("Ban Added: " + unique_id)
			self.data["Timestamp"]["Local"] = os.path.getmtime(self.bans_file)
		self.new_bans = {}


	def getStatus(self):
		return self.update_status

	def updateStatus(self, status):
		self.update_status = status