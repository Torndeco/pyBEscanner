README

pyBEscanner

A simple python application with goal of scanning arma2 + battlelog files.
This this not protect against people using a battleye bypass


Features (assuming not bugged)

	* Multiple Servers ( No multi-threading support, it scans 1 at a time )
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


Directory Layout
	<pyBEscanner install directory>pyBEscanner.py                 
		[Main Python Script....   This is what u run]
	<pyBEscanner install directory>/conf/servers.ini              
		[Settings File, reloaded everytime before a log scan]
	<pyBEscanner install directory>/rcon/                         
		[Using ziello2k C# Battlenet library, see note below]

	<server battleye directory>/pyBEscanner                       
		[Location of whitelist / blacklist filters]
	<server battleye directory>/Battle Logs - %Year-%Month-%Day   
		[Location of archived battleye logs, 
		also contains any bans/kicks/unknown logs]
		

Basic Usage Instructions

	If u are using multiple servers, recommend u hardlink the bans.txt.
	If byBEscanner detects bans.txt modified timestamp has changed it 
	issues reloadbans via rcon

	In pyBEscanner/doc/examples of filters are examples of filters u can use....
	Plz note these are just to help u get started + arent anyway complete.
	
	The basic idea is you use the whitelisted filter
	to filter out out normal ingame logs from battleye i.e
		Value Restriction #21 "remExField" = \[<NULL-object>,<NULL-object>,"playmove","ZombieFeed[0-9]"\]
	note:- the use of [0-9] so dont need to add in 10 different entries, 
	while still beening strict in what it filters out
		
	This way u are left with smaller logs to look over
	Then as u encounter new hacks u add them to the banlist filters
	Basicly teaching the tool to ban for them the next time around..
	
	

Requirements
	Python 2.7
	

Known Issues
	* No python rcon networking code
	* No / very little exception handling code...  
		If there is a typo in filter files will cause app to crash


Notes:-  
	* Havent written any rcon code written for python yet...
	* So Temp workaround till i get around to creating rcon networking code...
		Using ziello2k https://github.com/ziellos2k/BattleNET 
		Source file is included for the paranoid people out there...