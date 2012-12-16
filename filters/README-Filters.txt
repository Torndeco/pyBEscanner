Subject to change, 
I believe the standard layout of filters should be something like the following....

dayz-default = Filters for standard dayz code (i.e from offical community builds)
dayz-<additional features> = Filters for addition features i.e gcam etc...

dayz-default-2017 = Filters for just dayz-2017 build 

dayz-weapons-default = Standard set of Filters for Dayz Weapons, so easier for admins to maintain a set of filters if they are custom weapons.
dayz-weapons-<map name / version> = Set of Filters for Dayz Weapons for that specfic map version...


Ideally the user to only need to pick
1) map/mod filter
2) single set of weapons filters
3) any additional features they have enabled...
4) custom built filters they might have made themselves...

i.e  dayz-default-2017, dayz-weapons-2017, dayz-optional-gcam
or 
dayz-default, dayz-weapons-chernarus
or
dayz-default, dayz-weapons-default


Note:-
Want to try and keep dayz weapons as whole seperate pacakge of filters.
Mainly due to inability to whitelist a previously blacklisted publicvarible value.
Otherwise the weapons-default will risk get watered down to much & not been useful on its own...

---------------------
---------------------

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
4 1 KICK ..
