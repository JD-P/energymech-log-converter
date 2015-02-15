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

def main():
  """Implement command line interface and call subroutines to handle conversions."""
  parser = argparse.ArgumentParser()
  parser.add_argument("Directory", help="The directory in which the log files reside.")
  parser.add_argument("--output", "-o", help="Filepath to store output at, default is standard output.")
  parser.add_argument("--json", action="store_true", help="Output as a JSON archive.")
  parser.add_argument("--sqlite", action="store_true", help="Output as a SQLite database.")

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
      datevalues = [int(datestring[0:4]), int(datestring[4:6]), int(datestring[6:])]
      logdate = datetime.date(year=datevalues[0],month=datevalues[1],day=datevalues[2])
      date_timestamp = time.mktime(logdate.timetuple())
      logpath = os.path.join(directory, filename)
      log_lines = energymech_parse(logpath, line_id)
      logs.update(date_timestamp:log_lines[1])
      line_id += log_lines[0]
    return (logs)
  else:
    raise ValueError(directory + " is not a directory.")

def energymech_parse(filepath, line_id):
  """Take a single log file in energymech format and parse it into a python datastructure."""
  log = open(filepath, 'r')
  lines = log.readlines()
  tokenlist = []
  for line in lines:
    type_parse = line.split(" ", maxsplit=2) # Temporary three token space parse to determine type of line.
    if type_parse[1] != "***" and type_parse[1][0] == "<":
      tokenlist.append([line_id, "PRIVMSG"].extend(type_parse))
  return (line_id, tokenlist)

def time2nixtime(time_string):
  """Convert a time string of the format HH:MM:SS or HH:MM to a timestamp in seconds."""
  if len(time_string) != 8 and len(time_string) != 5:
    raise ValueError("Time given to time2nixtime() was not a time_string.")
  elif len(time_string) == 8:
    time.
  
