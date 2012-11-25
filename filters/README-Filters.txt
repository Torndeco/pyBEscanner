This is just a basic primer for Filters...
Note:- It is still v.rough will add it to later on..


The Filters are really just exposing the user to python regrex module...
Have a look @
http://docs.python.org/2/library/re.html

Also very handy webapp for testing out your regrex expressions @
http://www.pythonregex.com/


--------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------


Spam Filters are slighty different beast, while they are essential just regrex expressions.
There is a slighty different format

<Number of detections> <elapsed time in seconds> <action> <regrex rule>
Possible <action> values are just KICK or BAN atm...

For example
10 15 BAN .

10 detections within 15 seconds regrex rule . (basicly matches everything) results in a player ban...


Now lets say u wanted 2 different rules but with the same regrex rule...
Just alter the regrex slighty so it still catches what u want

10 15 BAN .
4 1 BAN ..



Note:- Spam Filters are just logging atm, just be carefull