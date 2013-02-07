# Filename: settings.py
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

import ConfigParser
import copy
import os
import re
import sys

from modules import bans


class Settings:
    def __init__(self, bans_deamon=True):
        
        self.bans_deamon = bans_deamon

        self.main_dir = os.getcwd()
        conf_dir = os.path.join(self.main_dir, 'conf')
        logs_dir = os.path.join(self.main_dir, "logs")
        temp_dir = os.path.join(self.main_dir, "temp")

        self.conf_file = os.path.join(self.main_dir, 'conf', 'conf.ini')
        
        if not os.path.isfile(os.path.join(self.main_dir, 'pyBEscanner.py')):
            print "Wrong working Directory"
            sys.exit()
        else:
            if not os.path.exists(conf_dir):
                print "Missing Conf Directory @ " + self.conf_dir
                sys.exit()
            else:
                if not os.path.isfile(self.conf_file):
                    print "Missing Server Configs @ " + self.conf_file
                    sys.exit()

        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
            
        if not os.path.exists(logs_dir):
            os.mkdir(logs_dir)


        config = ConfigParser.ConfigParser()
        config.read(self.conf_file)

        if config.has_option("Default", "Version"):
            if config.get("Default", "Version") != "18":
                print "-------------------------------------------------"
                print "ERROR: Bad conf/servers.ini version"
                print "-------------------------------------------------"
                print "Read Changes.txt for more info"
                print "Old version = " + config.get("Default", "Version")
                sys.exit()
        else:
            print "-------------------------------------------------"
            print "ERROR: No servers.ini version found"
            print "-------------------------------------------------"
            print "This either means a mistake in your servers.ini file,"
            print "Look @ servers-example.ini"
            print
            print "Or if u haven't updated in awhile"
            print "Recommend u delete pyBEscanner temp folders & read Changes.txt for update changes"
            sys.exit()
            
    def get_config_file(self):
        return self.conf_file

    def load_config(self):

        settings = []

        config = ConfigParser.ConfigParser()
        config.read(self.conf_file)
        config_sections= config.sections()
        config_sections.remove("Default")

        default = {    "pyBEscanner Directory": self.main_dir}
        default["Scan Server Logs"] = config.get("Default", "Scan Server Logs")
        
        if config.has_option("Default", "Bans Symlinked Location"):
            default["Bans Symlinked Location"] = config.get("Default", "Bans Symlinked Location")            
        else:
            default["Bans Symlinked Location"] = None

        options = [["Scan Addbackpackcargo", "addbackpackcargo"],
                    ["Scan Addmagazinecargo", "addmagazinecargo"],
                    ["Scan Addweaponcargo", "addweaponcargo"],
                    ["Scan Attachto", "attachto"],
                    ["Scan Createvehicle", "createvehicle"],
                    ["Scan Deletevehicle", "deletevehicle"],
                    ["Scan Mpeventhandler", "mpeventhandler"],
                    ["Scan Publicvariable", "publicvariable"],
                    ["Scan Remotecontrol", "remotecontrol"],
                    ["Scan Remoteexec", "remoteexec"],
                    ["Scan Scripts", "scripts"],
                    ["Scan Setdamage", "setdamage"],
                    ["Scan Selectplayer", "selectplayer"],
                    ["Scan Setpos", "setpos"],
                    ["Scan Setvariable", "setvariable"],
                    ["Scan Teamswitch", "teamswitch"],
                    ["OffSet", "OffSet"],
                    ["Ban Message", "Ban Message"],
                    ["Kick Message", "Kick Message"],
                    ["Report Message", "Report Message"],
                    ["Ban IP", "Ban IP"],
                    ["Ban IP Time", "Ban IP Time"],
                    ["Rules", "Rules"],
                    ["Bans Symlinked", "Bans Symlinked"],
                    ["Bans Shared", "Bans Shared"]]

        ## Scan Settings -- Default
        interval = int(config.get("Default", "interval"))

        for x in range(len(options)):
            default[options[x][1]] = config.get("Default", options[x][0])
            
        if self.bans_deamon:
            server_ban_deamon = bans.BansDeamon(default["Bans Symlinked Location"], default["Ban IP Time"])
        else:
            server_ban_deamon = None

        for section in config_sections:
            server = copy.copy(default)

            ## Server Info
            server["Server ID"] = section
            server["ServerName"] = config.get(section, "ServerName")
            server["ServerIP"] = config.get(section, "ServerIP")
            server["ServerPort"] = config.get(section, "ServerPort")
            server["RconPassword"] = config.get(section, "RconPassword")
            server["BattlEye Directory"] = config.get(section, "BattlEye Directory")
            server["Server Console Log"] = config.get(section, "Server Console Log")
            server["Server RPT Log"] = config.get(section, "Server RPT Log")

            if config.has_option(section, "Temp Directory"):
                server["Temp Directory"] = os.path.join(config.get(section, "Temp Directory"), section)
            else:
                server["Temp Directory"] = os.path.join(self.main_dir, "temp", section)

            if config.has_option(section, "Logs Directory"):
                server["Logs Directory"] = os.path.join(config.get(section, "Logs Directory"), section)
            else:
                server["Logs Directory"] = os.path.join(self.main_dir, "logs", section)

            server["LockFile"] = os.path.join(server["Temp Directory"], "scan-stopped.lockfile")
            server["LockFile-Ask"] = os.path.join(server["Temp Directory"], "scan-stop-ask.lockfile")

            for y in range(len(options)):
                if config.has_option(section, options[y][0]):
                    server[options[y][1]] = config.get(section, options[y][0])

            server["Rules"] = re.sub(",\s*", ",", server["Rules"])
            temp_rules = server["Rules"].split(",")
            server["Rules"] = []
            for rules in temp_rules:
                if rules == "Custom":
                    server["Rules"].append(os.path.join(server["BattlEye Directory"], "pyBEscanner", "rules"))
                else:
                    server["Rules"].append(os.path.join(self.main_dir, "rules", rules))

            if self.bans_deamon:
                server_ban_deamon.addServer(section, server["BattlEye Directory"], server["Bans Shared"], server["Bans Symlinked"], server["Ban IP Time"])


            # Generated Settings
            server["Battleye Logs"] = ["addbackpackcargo",
                                            "addmagazinecargo",
                                            "addweaponcargo",
                                            "attachto",
                                            "createvehicle",
                                            "deletevehicle",
                                            "mpeventhandler",
                                            "publicvariable",
                                            "remotecontrol",
                                            "remoteexec",
                                            "selectplayer",
                                            "scripts",
                                            "setdamage",
                                            "setpos",
                                            "setvariable",
                                            "teamswitch"]

            server["Battleye Logs Location"] = {}
            server["Battleye Temp Logs"] = {}
            server["Battleye Backup Logs"] = {}

            server["Banlist Rules"] = {}
            server["Kicklist Rules"] = {}
            server["Whitelist Rules"] = {}
            server["Spamlist Rules"] = {}


            for be_log in server["Battleye Logs"]:
                server["Battleye Logs Location"][be_log] = os.path.join(server["BattlEye Directory"], (be_log + ".log"))
                server["Battleye Temp Logs"][be_log] = os.path.join(server["Temp Directory"], (be_log + ".log"))

                server["Banlist Rules"][be_log] = []
                server["Kicklist Rules"][be_log] = []
                server["Whitelist Rules"][be_log] = []
                server["Spamlist Rules"][be_log] = []

                for rules in server["Rules"]:
                    server["Banlist Rules"][be_log].append(os.path.join(rules, be_log + ".banlist"))
                    server["Kicklist Rules"][be_log].append(os.path.join(rules, be_log + ".kicklist"))
                    server["Whitelist Rules"][be_log].append(os.path.join(rules, be_log + ".whitelist"))
                    server["Spamlist Rules"][be_log].append(os.path.join(rules, be_log + ".spamlist"))
            settings.append(server)
            
        return interval, server_ban_deamon, settings