# Filename: pyBEutility.py
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

#!/usr/bin/python

import argparse
import ConfigParser
import os
import sys
import time
import urllib

from modules import bans

class pyBE:
    def __init__(self):
        main_dir = os.getcwd()
        conf_dir = os.path.join(main_dir, 'conf')
        self.temp_dir = os.path.join(main_dir, "temp")
        self.pyBEscanner_lockfile = os.path.join(self.temp_dir, "pyBEscanner.lockfile")
        conf_file = os.path.join(main_dir, 'conf', 'servers.ini')

        if not os.path.isfile(os.path.join(main_dir, 'pyBEscanner.py')):
            print()
            print("Wrong working Directory")
            sys.exit()
        else:
            print()
            if not os.path.exists(conf_dir):
                print("Missing Conf Directory @ " + conf_dir)
                sys.exit()
            else:
                if not os.path.isfile(conf_file):
                    print("Missing Server Configs @ " + self.conf_file)
                    sys.exit()
                    
        config = configparser.ConfigParser()
        config.read(conf_file)
        
        if config.has_option("Default", "Version"):
            if config.get("Default", "Version") != "16":
                print("-------------------------------------------------")
                print("ERROR: Bad conf/servers.ini version")
                print("-------------------------------------------------")
                print("Read Changes.txt for more info")
                print("Old version = " + config.get("Default", "Version"))
                sys.exit()
        else:
            print("-------------------------------------------------")
            print("ERROR: No servers.ini version found")
            print("-------------------------------------------------")
            print("This either means a mistake in your servers.ini file,")
            print("Look @ servers-example.ini")
            print()
            print("Or if u haven't updated in awhile")
            print("Recommend u delete pyBEscanner temp folders & read Changes.txt for update changes")
            sys.exit()
            
        config = configparser.ConfigParser()
        config.read(conf_file)
        config_sections = config.sections()
        config_sections.remove("Default")

        self.section_list = config_sections
        self.server_list = {}
        for section in list(config_sections):
            self.server_list[section] = {"ServerName": config[section]["ServerName"],
                                         "LockFile-Scan-Ask": os.path.join(self.temp_dir, section, "scan-stop-ask.lockfile"),
                                         "LockFile-Scan-Stopped": os.path.join(self.temp_dir, section, "scan-stopped.lockfile")}
 
    def start_scan(self, servers=None):
        if servers == None:
            servers = self.section_list
            
        for section in servers:
            if os.path.isfile(self.server_list[section]["LockFile-Scan-Ask"]):
                os.remove(self.server_list[section]["LockFile-Scan-Ask"])
            if os.path.isfile(self.server_list[section]["LockFile-Scan-Stopped"]):
                os.remove(self.server_list[section]["LockFile-Scan-Stopped"])
        print("Telling pyBEscanner to resume scanning on " + str(servers))
    
    def stop_scan(self, servers=None):
        if servers == None:
            servers = self.section_list
            
        for section in servers: 
            open(self.server_list[section]["LockFile-Scan-Ask"], 'w', encoding='utf8').close()
        print("Asking pyBEscanner to pause scanning on " + str(servers))
        
        while servers != []:
            print
            x = 0
            while x < len(servers):
                section = servers[x]
                if os.path.isfile(self.server_list[section]["LockFile-Scan-Stopped"]):
                    print("Scan Paused on Server " + str(servers[x]))
                    servers.pop(x)
                else:
                    x = x + 1
            print("Waiting...")
            if os.path.isfile(self.pyBEscanner_lockfile):
                time.sleep(5)
            else:
                print("pyBEscanner is not running")
                print("Removing lockfiles + exiting")
                self.start_scan()
                sys.exit()
        print("Scanning Paused")
		
	def download_bans(self):
		urllib.urlretrieve ("http://www.banzunion.com/downloads/?do=download", os.path.join(self.temp_dir, "banzunion.txt"))
		urllib.urlretrieve ("http://code.google.com/p/dayz-community-banlist/source/browse/bans/cblbans.txt", os.path.join(self.temp_dir, "cblbans.txt"))
		urllib.urlretrieve ("http://code.google.com/p/dayz-community-banlist/source/browse/bans/dwbans.txt", os.path.join(self.temp_dir, "dwbans.txt"))


class Main:
    def __init__(self, args):
        self.args = args
    
    def start(self):
        if (self.args.pause_scan and self.args.start_scan):
            print("Can't Start + Pause Scanning, make your mind up")
            sys.exit()

        if self.args.pause_scan:
            pyBE().stop_scan()
        elif self.args.start_scan:
            pyBE().start_scan()
        else:
            pass

        if self.args.download_bans:
			print("Work In Progress")


parser = argparse.ArgumentParser(description='pyBEscanner Utility...')
parser.add_argument('-s', '--start-scan', action='store_true')
parser.add_argument('-p', '--pause-scan', action='store_true')
parser.add_argument('-d', '--download-bans', action='store_true')
args = parser.parse_args()
main = Main(args)
main.start()