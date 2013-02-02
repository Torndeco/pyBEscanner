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
    def __init__(self, updatebans=False):
        main_dir = os.getcwd()
        conf_dir = os.path.join(main_dir, 'conf')
        self.temp_dir = os.path.join(main_dir, "temp")
        self.pyBEscanner_lockfile = os.path.join(self.temp_dir, "pyBEscanner.lockfile")
        conf_file = os.path.join(main_dir, 'conf', 'conf.ini')

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
                    print("Missing Server Configs @ " + conf_file)
                    sys.exit()
                    
        config = ConfigParser.ConfigParser()
        config.read(conf_file)
        
        if config.has_option("Default", "Version"):
            if config.get("Default", "Version") != "18":
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
            
        config_sections= config.sections()
        config_sections.remove("Default")

        if updatebans:
            self.server_ban_deamon = bans.BansDeamon(default["Bans Symlinked Location"], default["Ban IP Time"])

        self.section_list = config_sections
        self.server_list = {}
        for section in config_sections:
            if updatebans:
                self.server_ban_deamon.addServer(section, server["BattlEye Directory"], server["Bans Shared"], server["Bans Symlinked"], server["Ban IP Time"])
            self.server_list[section] = {"ServerName": config.get(section, "ServerName"),
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
        print("pyBEutility: Request Resume Scanning: " + str(servers))

    
    def stop_scan(self, servers=None):
        if os.path.isfile(self.pyBEscanner_lockfile):
            if servers is None:
                servers = self.section_list
            for section in servers: 
                open(self.server_list[section]["LockFile-Scan-Ask"], 'w').close()
                print("pyBEscanner: Request Stop Scanning: " + self.server_list[section]["ServerName"])
            
            print
            while servers != []:
                print("Waiting...")
                time.sleep(5)            
                x = 0
                while x < len(servers):
                    section = servers[x]
                    if os.path.isfile(self.server_list[section]["LockFile-Scan-Stopped"]):
                        print("pyBEscanner: Scan Stopped: " + self.server_list[section]["ServerName"])
                        servers.pop(x)
                    else:
                        time.sleep(5) 
                        x = x + 1
                if servers != []:
                    print("pyBEutility: Waiting for " + str(servers))
            print("Scanning Paused")
        else:
            print("pyBEscanner is not running")
            print("Removing lockfiles + Exiting")
            self.start_scan()
            sys.exit()


    def download_bans(self):
        ban_files = [(os.path.join(self.temp_dir, "banzunion.txt")), (os.path.join(self.temp_dir, "cblbans.txt")), (os.path.join(self.temp_dir, "dwbans.txt"))]
        urllib.urlretrieve ("http://www.banzunion.com/downloads/?do=download", ban_files[0])
        urllib.urlretrieve ("http://code.google.com/p/dayz-community-banlist/source/browse/bans/cblbans.txt", ban_files[1])
        urllib.urlretrieve ("http://code.google.com/p/dayz-community-banlist/source/browse/bans/dwbans.txt", ban_files[2])

        self.stop_scan()
        self.server_ban_deamon.updateBanFiles(ban_files)
        self.start_scan()
        
        
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
            if self.args.download_bans:    
                #pyBE(True).download_bans()
                print("Work In Progress")



parser = argparse.ArgumentParser(description='pyBEscanner Utility...')
parser.add_argument('--start-scan', action='store_true')
parser.add_argument('--pause-scan', action='store_true')
parser.add_argument('--download-bans', action='store_true')
parser.add_argument('--update-battleeye-filters', action='store_true')
args = parser.parse_args()
main = Main(args)
main.start()