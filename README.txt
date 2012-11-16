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

	<server battleye directory>/pyBEscanner/filters                     
		[Location of whitelist / blacklist filters]

	<server battleye directory>/Logs/Battle Logs - %Year-%Month-%Day   
		[Location of archived battleye logs, 
		also contains any bans/kicks/unknown logs]
	
	
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