Energymech Log Converter:
------------------------

Essential features of every message from an IRC server:

Time Handling:
--------------

With the energymech logs we count days and timestamps by the dates of the filenames.
This is done because it is impossible to determine from the logs alone whether a
given message that is a day ahead of the last message is one day ahead or X days
ahead. Further one cannot tell when the logger was started and when the logger 
was stopped, meaninging that the user could have started logging on the 3rd of
June, took a two week hiatus and started logging again.

Parsing:
--------

Lines from a channel logged in energymech format can be split into two categories:

1. Normal PRIVMSG's sent to channel.

2. Everything else.

Since the former dominates the vast majority of lines in the log, it makes the 
most sense to determine that something is not in the second category before employing 
more complex methods.

If we split the string representing a line into elements of a list along the 
seperator " " (space) the second element should always be "***" for the second 
category above. This means that if something does not have three astericks as its
second split element it is a PRIVMSG. 

The first part of the algorithm is to split the IRC line twice, so that you have three elements:

[timestamp, username or "***", the rest of the line]

Misc:
-----

0: This line splits a filename of the format:

servername_#channel_datestring.log

By first splitting into three parts along the underscores.

['servername', '#channel', 'datestring.log']

Then grabs the 3rd (starting from zero) element of the resulting list and splits
it along the dot.

["datestring", "log"]

From this list the first element is grabbed and then parsed as the datestring.

