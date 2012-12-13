README

pyBEscanner

A simple python application with goal of scanning arma2 + battlelog files.
This this not protect against people using a battleye bypass


Features:

	* Multiple Servers ( No multi-threading support, it scans 1 server at a time )
	* Scans battlelogs
	* Whitelist + Blanlist + Kicklist filters with regrex features
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

	<pyBEscanner install directory>/filters>
		[Filter file directorys, were filters are located.
		If u arent using Custom Filter Setting]

	<pyBEscanner install directory>/rcon/
		[Source code available for exe's in src directorys, read the readme.txts]

	<server battleye directory>/pyBEscanner/filters
		[Location of whitelist / kicklist / blacklist / spamlist filters]

	<server battleye directory>/Logs/Battle Logs - %Year-%Month-%Day
		[Location of archived battleye logs,
		also contains any bans/kicks/unknown logs]


Installation
	Copy conf/servers-example.ini -> conf/servers.ini
	Edit conf/servers.ini
	Start pyBEscanner.py


Requirements
	Python 2.7


Known Issues
	* No python rcon networking code
	* There is no to very little exception handling code...
		So if u make a typo in filter files will cause app to crash

Notes:-
	* U can alter the settings & pyBEscanner filters & settings, while the
		program is running. Just avoid making any typo mistakes


---------------------------
---------------------------

Thx for the following people for helping out with this project

Nanomo for creating the c# app for kicking players
K4n30 for updating the filters & finding my mistakes
ziellos2k for creating the BattleNET C# library

and everyone else that i forgot....

