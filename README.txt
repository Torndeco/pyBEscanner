README

pyBEscanner

A simple python application with goal of scanning arma2 + battlelog files.
This this not protect against people using a battleye bypass


Features (assuming not bugged)

	* Multiple Servers ( No multi-threading support, it scans 1 at a time )
	* Scans battlelogs
	* Whitelist + Blacklist filters with regrex features
		http://docs.python.org/2/library/re.html
	* Auto-purges logs as it scans, reduces need to re-scan
	* Makes backup logs files & splits them up into folders based on date
	* Makes actions logs i.e 
		createvehicle-bans.txt / createvehicle-kicks.txt / createvehicle-unknown-kicks.txt.
	* Ability to pick per file different scan settings / disable
		Ban only for blacklisted code...
		Ban only for blacklisted code + kick for unknown code entries... (dont recommend atm)
		Ban for all logged code that isnt in whitelist (dont recommend atm)


Directory Layout
	<pyBEscanner install directory>pyBEscanner.py                 
		[Main Python Script....   This is what u run]
	<pyBEscanner install directory>/conf/servers.ini              
		[Settings File,  settings are reloaded everytime before a log scan]
	<pyBEscanner install directory>/rcon/                         
		[Temp workaround, using ziello2k C# Battlenet library as workaround for reloading bans see note below]

	<server battleye directory>/pyBEscanner                       
		[Location of whitelist / blacklist filters]
	<server battleye directory>/Battle Logs - %Year-%Month-%Day   
		[Location of archived battleye logs, also contains any bans/kicks/unknown logs]
	
	
Requirements
	Python 2.7
	C# Compiler
	

Known Issues
	* No python rcon networking code
	* No / very little exception handling code...  If there is a typo in filter files will cause app to exit out with error message...
	* If logged code entry contains more than one line, possible for app to read file before battleye gets a chance to finish updating the files with line 2+. 
	* Health may cause Dementia, Hair Loss, Loss of Life


Notes:-  
	* Havent written any rcon code written for python yet...
	* So Temp workaround till i get around to creating rcon networking code...
		Using ziello2k https://github.com/ziellos2k/BattleNET to create an exe file to connect to server & issue reloadbans / kickplayers command
		Edit the source *.cs and enter in your server ip / port / password & compile into an exe. 
		I used http://www.csscript.net/ to create executables
