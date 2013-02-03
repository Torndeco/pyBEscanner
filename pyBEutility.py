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
import os
import sys
import time
import urllib

from modules import bans, settings

class pyBE:
    def __init__(self, bans_deamon=False):
        self.interval, self.server_ban_deamon, self.server_settings = settings.Settings(bans_deamon).load_config()
        
 
    def start_scan(self):

        for server in self.server_settings: 
            if os.path.isfile(server["LockFile-Ask"]):
                os.remove(server["LockFile-Ask"])
            if os.path.isfile(server["LockFile"]):
                os.remove(server["LockFile"])
            print("pyBEutility: Request Resume Scanning: " + str(server["ServerName"]))

    
    def stop_scan(self, timeout=None):
        print
        server_list = []
        server_lockfile_scan_stopped = []

        for server in self.server_settings: 
            open(server["LockFile-Ask"], 'w').close()
            print("pyBEscanner: Request Stop Scanning: " + server["ServerName"])
            server_list.append(server["ServerName"])
            server_lockfile_scan_stopped.append(server["LockFile"])

        print
        while server_list != []:
            print("Waiting...")
            time.sleep(5)            
            x = 0
            while x < len(server_list):
                server = server_list[x]
                if os.path.isfile(server_lockfile_scan_stopped[x]):
                    print("pyBEscanner: Scan Stopped: " + str(server_list[x]))
                    server_list.pop(x)
                else:
                    time.sleep(5) 
                    x = x + 1
            if server_list != []:
                print("pyBEutility: Waiting for " + str(server_list))
        print
        print("All Scanning Paused")


    def download_bans(self):
        temp_dir = os.path.join(os.getcwd(), "temp")
        ban_files = [(os.path.join(temp_dir, "banzunion.txt")), (os.path.join(temp_dir, "cblbans.txt")), (os.path.join(temp_dir, "dwbans.txt"))]
        print "Downloading BanZ Union Bans..."
        urllib.urlretrieve ("http://www.banzunion.com/downloads/?do=download", ban_files[0])
        print "Downloading CBL Bans..."
        urllib.urlretrieve ("http://dayz-community-banlist.googlecode.com/git/bans/bans.txt", ban_files[1])
        print "Downloading Dwarden Bans..."
        urllib.urlretrieve ("http://dayz-community-banlist.googlecode.com/git/bans/dwbans.txt", ban_files[2])
        self.stop_scan()
        self.server_ban_deamon.updateBanFiles(ban_files)
        print
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
                pyBE(bans_deamon=True).download_bans()
#                print("Work In Progress")


parser = argparse.ArgumentParser(description='pyBEscanner Utility...')
parser.add_argument('--start-scan', action='store_true')
parser.add_argument('--pause-scan', action='store_true')
parser.add_argument('--download-bans', action='store_true')
parser.add_argument('--update-battleeye-filters', action='store_true')
args = parser.parse_args()
main = Main(args)
main.start()