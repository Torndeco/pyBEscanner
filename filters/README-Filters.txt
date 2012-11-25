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

For example the spam rule
10 15 BAN .

10 detections within 15 seconds regrex rule . (basicly matches everything) results in a player ban...

Possible <action> values are just KICK or BAN atm...

Note:- Spam Filters are not funcitonal just yet...
Will be ready do soon...