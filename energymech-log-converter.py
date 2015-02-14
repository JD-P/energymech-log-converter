# Converts sample #lesswrong IRC logs to JSON and SQLite formats.

"""

energymech-log-converter - A utility to convert energymech logs to JSON or SQLite

usage: energymech-log-converter.py [Logs Directory] [Options]

Convert the Logs Direcotry to a JSON (default) or SQLite database.

----

Options 

-h --help Show this help dialog.

-o --output The filepath to write output to, '-' for standard output.

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
  parser.add_argument("--output", "-o", help="Filepath to store output at.")
  parser.add_argument("--json", action="store_true", help="Output as a JSON archive.")
  parser.add_argument("--sqlite", action="store_true", help="Output as a SQLite database.")

  arguments = parser.parse_args()
  if arguments.json and arguments.sqlite:
    raise ValueError("Tried to output json and sqlite logs at the same time. Use one or the other.")
  elif 
  arguments.

def energymech_conv(directory, log_format):
  """Convert a set of log files in energymech format to JSON or SQLite."""
  if os.path.isdir(directory): 
    files = os.listdir(directory) 
    files.sort()
    for filename in files:
      datestring = filename.split("_")[2].split(".")[0] #See "Misc 0" in project file.
      datevalues = [int(datestring[0:4]), int(datestring[4:6]), int(datestring[6:])]
      logdate = datetime.date(year=datevalues[0],month=datevalues[1],day=datevalues[2])
      date_timestamp = time.mktime(logdate.timetuple())
    raise ValueError(directory + " is not a directory.")
  elif 
