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


Spam Filters are slighty different beast, while they are essential just regrex expressions.
There is a slighty different format

<Number of detections> <elapsed time in seconds> <action values = BAN / KICK / LOG / DELETE> <regrex rule>

For example
10 15 BAN .

10 detections within 15 seconds regrex rule . (basicly matches everything) results in a player ban...

Now lets say u wanted 2 different rules but with the same regrex rule...
Just alter the regrex slighty so it still catches what u want

10 15 BAN .
4 1 KICK ..


Note:- 
Lets say u are loading a filter set, but u want to disable a spam rule.
Plus u are feeling lazy & don't want to manually keep the altering the filters everytime they are updated.
U can just create a new filter set + have it loaded last in servers.ini

So if u original had
10 15 BAN .
4 1 KICK ..

And in your custom filter u added the line
4 1 DELETE ..

This will remove the filters with regrex rule ..




