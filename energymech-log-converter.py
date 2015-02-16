# Converts sample #lesswrong IRC logs to JSON and SQLite formats.

"""

energymech-log-converter - A utility to convert energymech logs to JSON or SQLite

usage: energymech-log-converter.py [Logs Directory] [Options]

Convert the Logs Direcotry to a JSON (default) or SQLite database.

----

Options 

-h --help Show this help dialog.

-o --output The filepath to write output to, default is standard output.

--json Output as a JSON archive.

--sqlite Output as a SQLite database.

"""

import argparse

import json

import sqlite

import os

import time

import datetime

import string

def main():
  """Implement command line interface and call subroutines to handle conversions."""
  parser = argparse.ArgumentParser()
  parser.add_argument("Directory", help="The directory in which the log files reside.")
  parser.add_argument("--output", "-o", help="Filepath to store output at, default is standard output.")
  parser.add_argument("--json", action="store_true", help="Output as a JSON archive.")
  parser.add_argument("--sqlite", action="store_true", help="Output as a SQLite database.")
  parser.add_argument("--timezone", "-t", help="Specify the timezone as a UTC offset. (Not implemented.)")

  arguments = parser.parse_args()
  if arguments.json and arguments.sqlite:
    raise ValueError("Tried to output json and sqlite logs at the same time. Use one or the other.") 
  elif arguments.sqlite:
    if arguments.output:
      # To be implemented later
      raise ValueError("SQL formatting not implemented at this time. Check back for further updates to this software.")
    else:
      raise ValueError("SQL formatting not implemented at this time. Check back for further updates to this software.")
  else:
    if arguments.output:
      jsondump = open(arguments.output, 'w')
      json.dump(jsondump, energymech_conv(arguments.Directory, "json"), indent=2)
    else:
      print(json.dumps(jsondump, energymech_conv(arguments.Directory, "json", indent=2)))

def energymech_conv(directory, log_format):
  """Convert a set of log files in energymech format to JSON or SQLite."""
  if os.path.isdir(directory): 
    files = os.listdir(directory) 
    files.sort()
    logs = {}
    line_id = 0
    for filename in files:
      datestring = filename.split("_")[2].split(".")[0] #See "Misc 0" in project file.
      logdate = time.strptime(datestring, "%Y%m%d")
      date_timestamp = time.mktime(logdate)
      logpath = os.path.join(directory, filename)
      log_lines = energymech_parse(logpath, line_id)
      logs[date_timestamp] = log_lines[1]
      line_id += log_lines[0]
    return (logs)
  else:
    raise ValueError(directory + " is not a directory.")

def energymech_parse(filepath, line_id):
  """Take a single log file in energymech format and parse it into a python datastructure."""
  log = open(filepath, 'r', encoding="latin-1")
  lines = log.readlines()
  tokenlist = []
  for line in lines:
    type_parse = line.split(" ", 2) # Temporary three token space parse to determine type of line.
    space_parse = line.split(" ") # Turns every space seperation into a token, doesn't handle closures such as closed parentheses intelligently.
    timestamp = time2seconds(type_parse[0][1:-1])
    if type_parse[1] != "***" and type_parse[1][0] == "<":
      tokenlist.append([line_id, "PRIVMSG", timestamp].extend(type_parse[1:])) #See "JSON line formats" in project file.
    elif type_parse[1] == "*":
      me_elements = line.split(" ", 3)
      tokenlist.append([line_id, "PRIVMSG", timestamp, me_elements[2], me_elements[3]]) 
    elif ''.join((type_parse[1][0], type_parse[1][-1])) == "--":
      tokenlist.append([line_id, "NOTICE", timestamp].extend(type_parse[1:]))
    elif space_parse[2] == "Joins:":
      tokenlist.append([line_id, "JOIN", timestamp, space_parse[3], space_parse[4][:-1]])
    elif space_parse[2] == "Parts:":
      part_elements = line.split(" ", 5)[3:]
      tokenlist.append([line_id, "PART", timestamp].extend(part_elements))
    elif space_parse[2] == "Quits:":
      quit_elements = line.split(" ", 5)[3:]
      tokenlist.append([line_id, "QUIT", timestamp].extend(quit_elements))
    elif space_parse[2]
    elif ''.join(space_parse[3:5]) == "waskicked":
      tokenlist.append([line_id, "KICK", timestamp, space_parse[2], space_parse[6], space_parse[7][:-1]])
    elif ''.join(space_parse[4:7]) == "nowknownas":
      tokenlist.append([line_id, "NICK", timestamp, space_parse[2], space_parse[-1:][0][:-1]])
    elif ''.join(space_parse[3:5]) == "setsmode:":
      setmode_elements = line.split(" ", 5)
      tokenlist.append([line_id, "SETMODE", timestamp, setmode_elements[2], setmode_elements[5][:-1]])
    elif ''.join(space_parse[3:5]) == "changestopic":
      topic_element = line.split(" ", 6)[6]
      tokenlist.append([line_id, "TOPIC", timestamp, space_parse[2], topic_element])
    line_id += 1
  return (line_id, tokenlist)

def time2seconds(time_string):
  """Convert a time string of the format HH:MM:SS or HH:MM to a timestamp in seconds."""
  if len(time_string) != 8 and len(time_string) != 5: # Check if length is consistent with HH:MM:SS or HH:MM respectively.
    raise ValueError("Time given to time2seconds() was not a time_string.")
  for character in time_string:
    if character in string.ascii_letters:
      raise ValueError("Time given to time2seconds() was not a time_string.")
  if len(time_string) == 8:
    time_elements = time.strptime(time_string,"%H:%M:%S")
    hours2minutes = time_elements.tm_hour * 60
    minutes2seconds = hours2minutes + time_elements.tm_min
    seconds = (minutes2seconds * 60) + time_elements.tm_sec
    return seconds
  elif len(time_string) == 5:
    time_elements = time.strptime(time_string, "%H:%M")
    hours2minutes = time.elements.tm_hour * 60
    minutes2seconds = hours2minutes + time_elements.tm_min
    seconds = minutes2seconds * 60
    return seconds
  else:
    raise ValueError("'time_string' was proper length and contained no alphanumeric characters, but was somehow not the proper length when it is checked again to determine which routine should be used to process the string.")
  
