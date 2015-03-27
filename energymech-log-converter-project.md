Energymech Log Converter:
=========================

Format selection:
-----------------

Format selection works off of modules which are imported into the main wrapper 
program as the name of the format given with the --format option. 

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

Lines from a channel logged in energymech format can be split into three categories:

1. Normal PRIVMSG's sent to channel.

2. Notices sent to channel.

3. Everything else.


Since the former dominates the vast majority of lines in the log, it makes the 
most sense to determine that something is not in the second category before employing 
more complex methods.

If we split the string representing a line into elements of a list along the 
seperator " " (space) the second element should always be "***" for the third 
category above. This means that if something does not have three astericks as its
second split element it is a PRIVMSG. 

The first part of the algorithm is to split the IRC line twice, so that you have three elements:

[timestamp, username or "***", the rest of the line]

Lines where the second element is a username are PRIVMSG's, and are stored as such.

Message Types:

PRIVMSG, NOTICE, JOIN, PART, QUIT, KICK, NICK, SETMODE, TOPIC

PRIVMSG: [line_id, "PRIVMSG", timestamp in seconds, nickname, message]

NOTICE: [line_id, "NOTICE", timestamp in seconds, nickname, message]

JOIN: [line_id, "JOIN", timestamp in seconds, nickname, hostname]

PART: [line_id, "PART", timestamp in seconds, nickname, hostname, part_message]

QUIT: [line_id, "QUIT", timestamp in seconds, nickname, hostname, quit_message]

KICK: [line_id, "KICK", timestamp in seconds, nick_kicked, kicked_by, kick_message]

NICK: [line_id, "NICK", timestamp in seconds, nick_before, nick_after]

SETMODE: [line_id, "SETMODE", timestamp, set_by, mode_string]

TOPIC: [line_id, "TOPIC", timestamp in seconds, changed_by, topic]

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

