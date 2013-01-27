---------------------
---------------------

This is just a basic primer for Filters...

Note very important to make a note off..
pyBEscanner will not create the filters for a log file until it detects a battleye log for it


The Filters are really just exposing the user to python regrex module...
Have a look @
http://docs.python.org/2/library/re.html

Also very handy webapp for testing out your regrex expressions @
http://www.pythonregex.com/


-------------------
-------------------
Whitelist / Kicklist / Banlist Filters

#
# Random Comments
#
Rule = Some Random Regrex Rule
   Exception =
   Exception = 
Rule = X
Rule = Y

Rule = Z
  Exception:
# More Random Info
Rule:A
  Action = DELETE  (only valid option)

-------------------
-------------------
Spam Filters

Rule = Some Random Regrex Rule
    Exception = 
    Exception =
    Time = 
    Count = 
    Action = BAN/KICK/LOG
	
Rule = Some Random Regrex Rule
    Exception = 
    Exception =
    Time = 
    Count = 
    Action = BAN/KICK/LOG