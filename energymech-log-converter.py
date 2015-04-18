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

--format Convert log as <FORMAT>

"""
import sys

import argparse

import json

import sqlite3

import importlib



class BufferedOutputHandler():
  """ Template output buffer.
    Implementations should all handle 'day' updates. """

  def __init__(self,filepath):
    raise NotImplementedError("Don't intialise the BufferedOutputHandler directly, but one of its implementations.") 

  def begin(self):
    pass
    
  def write_day(self):
    pass

  def close(self):
    pass


class BufferedSqliteOutputHandler(BufferedOutputHandler):
  """ To be implemented.. """
  pass


class BufferedJSONOutputHandler(BufferedOutputHandler):
  """ Implements buffered output to JSON of logs being read. """

  def __init__(self, filepath):
    """ Configure the class with output format, path, etc.
        Should probably refactor so that format is handled by subclasses
        implementing this interface rather than internal logic. """
    self.outfile = open(filepath,'w')
    self.prevday = False
    
  def begin(self):
    """ Handle any initial writes. """
    self.outfile.write("{\n")
  
  def write_day(self,day):
    """ Writes a day's entry.

    Arguments:
      day: a dict (usually of one entry) which has a 'datestring':array_of_lines format. """
    #strip the object braces.
    outstr = json.dumps(day,indent=2)[2:-2]
    if self.prevday:
      self.outfile.write(',\n')
    else:
      self.prevday = True
    self.outfile.write(outstr)

  def close(self):
    """ Close the log. """
    self.outfile.write("\n}\n")
    self.outfile.close()


class conversion_wrapper():
  """Wraps the various converters and imports them all into one unified interface."""


  def main():
    """Implement command line interface and call subroutines to handle conversions."""

    supported_formats = {'json':BufferedJSONOutputHandler,
                         'sqlite': BufferedSqliteOutputHandler}

    parser = argparse.ArgumentParser()
    parser.add_argument("logs", help="The logfile or the directory in which the log files reside.")
    parser.add_argument("--output", "-o", help="Filepath to store output at, default is standard output.")
    formats_help = """\n\nValid formats are:\n\n\tjson\n\tsqlite"""
    parser.add_argument("--oformat", help="The format to output." + formats_help)
    parser.add_argument("--timezone", "-t", help="Specify the timezone as a UTC offset. (Not implemented.)")
    parser.add_argument("--format", "-f", help="Convert log as <FORMAT>.")

    arguments = parser.parse_args()

    try:
      converter = importlib.import_module("converters." + arguments.format)
    except ImportError:
      raise ValueError("Given format " + arguments.format.upper() + " has no valid converter.")

    if not arguments.oformat:
      raise ValueError("Did not specify an output format.")
    elif arguments.oformat not in supported_formats:
      raise ValueError("Do not recognise output format '{}'".format(arguments.ofile))
    elif arguments.oformat == 'sqlite':
      raise ValueError("SQL formatting not implemented at this time. Check back for further updates to this software.")

    ofile = arguments.output if arguments.output else sys.stdout
    output_handler = BufferedJSONOutputHandler(ofile)

    try:
      converter.convert(arguments.logs, output_handler)
    except KeyboardInterrupt as ki:
      #Should mean we mostly get valid data out of truncated converts.
      output_handler.close()
  
conversion_wrapper.main()
