README

pyBEscanner

A simple python application with goal of scanning arma2 + battlelog files.
This this not protect against people using a battleye bypass


Features:

	* Multiple Servers ( No multi-threading support, it scans 1 server at a time )
	* Scans battlelogs
	* Whitelist + Blanlist + Kicklist rules with regrex features
		http://docs.python.org/2/library/re.html
	* Auto-purges logs as it scans, reduces need to re-scan
	* Makes backup logs files & splits them up into folders based on date
	* Makes actions logs i.e
		scripts-bans.txt /
		scripts-kicks.txt /
		scripts-unknown.txt.
	* Ability to pick per file different scan settings
		Standard       - Ban only for blanlisted code...
		Standard+Kick  - Ban only for blacklisted code
					   + kick for unknown code entries...
		Strict         - Ban for everything not in
						whitelist filter
	* Ability to detect multiple attempts i.e user spamming an logfile
		i.e
			If u could ban a player than appears in setpos.log
			10 times in 5 seconds if u wanted to...
		Or
			U can also add in different triggers i.e different triggers for
			pipebombs / grenades etc...

			
Directory Layout
	<pyBEscanner install directory>pyBEscanner.py
		[Main Python Script....   This is what u run]

	<pyBEscanner install directory>/conf/servers.ini
		[Settings File, reloaded everytime before a log scan]

	<pyBEscanner install directory>/rules>
		[Filter file directorys, were rules are located.
		If u arent using Custom Filter Setting]

	<pyBEscanner install directory>/tools/rcon/
		[Source code available for exe's in src directorys, read the readme.txts]

	<server battleye directory>/pyBEscanner/rules
		[Location of whitelist / kicklist / blacklist / spamlist rules]

	<server battleye directory>/Logs/Battle Logs - %Year-%Month-%Day
		[Location of archived battleye logs,
		also contains any bans/kicks/unknown logs]


Installation
	Copy conf/conf-example.ini -> conf/conf.ini
	Edit conf/conf.ini
	python pyBEscanner.py

	
Extras
	python pyBEutility.pl --download-bans
		After u have pyBEscanner configured... U can set to run this command once a day/week if u want.
		It will download cblbans / dwbans & banzunion bans + add any missing bans to your servers bans.txt for u.
		U can run this command while pyBEscanner is running.

	python pyBEutility.pl --pause-scan
		If u are paranoid of open file locks, while rotating server console / rpt logs.
		Add this to your script / bat file.. to pause server scanning...
		
	python pyBEutility.pl --resume-scan
		This re-enables server log scanning
	

Requirements
	Python 2.7
	Mono + Wine (Only for Linux / Unix / BSD etc)

Known Issues
	* No python rcon networking code
	* There is no to very little exception handling code...
		So if u make a typo in filter files will cause app to crash

Notes:-
	* U can alter the settings & pyBEscanner rules & settings, while the
		program is running. Just avoid making any typo mistakes
	* When using multiple rules, if u load up multiple spam filter with same
		regrex rule, the last one loaded is used.
	* Don't forget u can add exceptions when making a spam rule

---------------------------
---------------------------

Thx for the following people for helping out with this project

Nanomo for creating the c# app for kicking players
k4n30 for updating the rules & finding my mistakes
ziellos2k for creating the BattleNET C# library

and everyone else that i forgot....

