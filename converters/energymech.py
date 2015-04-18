import os

import time

import datetime

import string

from utilities.time2seconds import time2seconds

def convert(directory, output_handler=None, utc_offset=None):
  """Run the energymech log converters conversion function."""
  return energymech_converter.energymech_conv(directory, output_handler)

class energymech_converter():
  """Convert an energymech log file to python datastructures."""
  def energymech_conv(directory, output_handler):
    """Convert a set of log files in energymech format to JSON or SQLite."""
    if not os.path.isdir(directory): 
      raise ValueError(directory + " is not a directory.")
    files = os.listdir(directory) 
    files.sort()

    if output_handler:
      output_handler.begin()
    else:
      logs = {}
      
    day = []
    total_lines = 0
    for filename in files:
      datestring = filename.split("_")[2].split(".")[0] #See "Misc 0" in project file.
      logdate = time.strptime(datestring, "%Y%m%d")
      date_timestamp = int(time.mktime(logdate))
      logpath = os.path.join(directory, filename)
      log_lines = energymech_converter.energymech_parse(logpath, total_lines)
      if output_handler:
        output_handler.write_day({date_timestamp:log_lines[1]})
      else:
        logs[date_timestamp] = log_lines[1]
      total_lines += log_lines[0]
    if output_handler:
      output_handler.close()
    else:
      return (logs)

  def energymech_parse(filepath, total_lines):
    """Take a single log file in energymech format and parse it into a python datastructure."""
    log = open(filepath, 'r', encoding="latin-1")
    lines = log.readlines()
    tokenlist = []
    lines_in_file = 0
    for line in lines:
      type_parse = line.split(" ", 2) # Temporary three token space parse to determine type of line.
      space_parse = line.split(" ") # Turns every space seperation into a token, doesn't handle closures such as closed parentheses intelligently.
      timestamp = time2seconds(type_parse[0][1:-1])
      line_id = total_lines + lines_in_file
      if type_parse[1] != "***" and type_parse[1][0] == "<":
        (nickname, message) = (type_parse[1][1:-1], type_parse[2][:-1])
        tokenlist.append([line_id, "PRIVMSG", timestamp, nickname, message])
      elif type_parse[1] == "*":
        me_elements = line.split(" ", 3)
        (nickname, message) = (me_elements[2], "/me " + me_elements[3][:-1])
        tokenlist.append([line_id, "PRIVMSG", timestamp, nickname, message]) 
      elif ''.join((type_parse[1][0], type_parse[1][-1])) == "--":
        (nickname, message) = (type_parse[1][1:-1], type_parse[2][:-1])
        tokenlist.append([line_id, "NOTICE", timestamp, nickname, message])
      elif space_parse[2] == "Joins:":
        (nickname, hostname) = (space_parse[3], space_parse[4][1:-2])
        tokenlist.append([line_id, "JOIN", timestamp, nickname, hostname])
      elif space_parse[2] == "Parts:":
        part_elements = line.split(" ", 5)[3:]
        (nickname, hostname, part_message) = (part_elements[0], part_elements[1][1:-1], part_elements[2][1:-2])
        tokenlist.append([line_id, "PART", timestamp, nickname, hostname, part_message])
      elif space_parse[2] == "Quits:":
        quit_elements = line.split(" ", 5)[3:]
        (nickname, hostname, quit_message) = (quit_elements[0], quit_elements[1][1:-1], quit_elements[2][1:-2])
        tokenlist.append([line_id, "QUIT", timestamp, nickname, hostname, quit_message])
      elif ''.join(space_parse[3:5]) == "waskicked":
        (nick_kicked, kicked_by, kick_message) = (space_parse[2], space_parse[6], space_parse[7][1:-2])
        tokenlist.append([line_id, "KICK", timestamp, nick_kicked, kicked_by, kick_message])
      elif ''.join(space_parse[4:7]) == "nowknownas":
        (nick_before, nick_after) = (space_parse[2], space_parse[-1][:-1])
        tokenlist.append([line_id, "NICK", timestamp, nick_before, nick_after])
      elif ''.join(space_parse[3:5]) == "setsmode:":
        setmode_elements = line.split(" ", 5)
        (set_by, mode_string) = (setmode_elements[2], setmode_elements[5][:-1])
        tokenlist.append([line_id, "SETMODE", timestamp, set_by, mode_string])
      elif ''.join(space_parse[3:5]) == "changestopic":
        topic_element = line.split(" ", 6)[6]
        (changed_by, topic) = (space_parse[2], topic_element[:-1])
        tokenlist.append([line_id, "TOPIC", timestamp, changed_by, topic])
      lines_in_file += 1
    return (lines_in_file, tokenlist)
