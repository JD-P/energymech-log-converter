# Converts sample #lesswrong IRC logs to JSON and SQLite formats.

"""

energymech-log-converter - A utility to convert energymech logs to JSON or SQLite

usage: energymech-log-converter.py [Logs] [Options]

Convert the logs (file or a directory) to a JSON (default) or SQLite database.

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
    
  def write_day(self,day):
    pass

  def close(self):
    pass


class BufferedSqliteOutputHandler(BufferedOutputHandler):
  """ To be implemented.. """
  
  def __init__(self,filepath):
    self.conn = sqlite3.connect(filepath)

  def create_table(cur,table_def):
    self.conn.cursor().execute("CREATE TABLE IF NOT EXISTS {}")

  def get_id(self, string, colname, table):
    """ Retrieve the ID for a string from the table and column.
        If the string does not yet exist, create it. """
    cur = self.conn.cursor()
    cur.execute("SELECT id FROM {} WHERE {} = '{}'".format(table,colname,string))
    rows = cur.fetchall()
    if len(rows) == 1:
      id = rows[0][0]
    else:
      cur.execute("INSERT INTO {} VALUES('{}')".format(table,string))
      id = cur.lastrowid
    return id

  def begin(self):
    cur = self.conn.cursor()

    self.create_table("nicks(id INTEGER PRIMARY KEY, nickname TEXT)")
    self.create_table("users(id INTEGER PRIMARY KEY, username TEXT)")
    self.create_table("hosts(id INTEGER PRIMARY KEY, hostname TEXT)")
    self.create_table("modes(id INTEGER PRIMARY KEY, mode TEXT)")
    self.create_table("servs(id INTEGER PRIMARY KEY, server TEXT)")
    self.create_table("chans(id INTEGER PRIMARY KEY, channel TEXT)")

    self.create_table("hostmasks(nid INTEGER, uid INTEGER, hid INTEGER)")
    self.create_table("registered(nid INTEGER, registered TEXT, account TEXT)")
    self.create_table("privmsgs(id INTEGER, nid INTEGER, message TEXT)") 
    self.create_table("notices(id INTEGER, nid INTEGER, message TEXT)") 
    self.create_table("joins(id INTEGER, nid INTEGER, uid INTEGER, hid INTEGER)") 
    self.create_table("parts(id INTEGER, nid INTEGER, uid INTEGER, hid INTEGER, part_message TEXT)")
    self.create_table("quits(id INTEGER, nid INTEGER, uid INTEGER, hid INTEGER, quit_message TEXT)")
    self.create_table("kicks(id INTEGER, nid_kicked INTEGER, nid_kicked_by INTEGER, kick_message TEXT)")
    self.create_table("nick_changes(id INTEGER, nid_before INTEGER, nid_after INTEGER)")
    self.create_table("set_modes(id INTEGER, nid_set_by INTEGER, mid INTEGER)")
    self.create_table("set_topic(id INTEGER, nid_set_by INTEGER, topic TEXT)")

    #Some work required.
    self.create_table("messages(id INTEGER, time TEXT, type TEXT, origin_id INTEGER)")

    
  def write_day(self,day):
    cur = self.conn.cursor()
    date = day.keys()[0]
    messages = day[date]
    for message in messages:
      line_id = message[0]
      line_type = message[1]
      time = message[2]
      #Somewhat of a reversal of the input string parsing here.
      if line_type == "SETMODE":
        nid_set_by = get_id(message[3], 'nickname','nicks')
        mode_id = get_id(message[4], 'mode', 'modes')
        cur.execute("INSERT INTO set_modes VALUES({},{},{})".format(line_id, nid_set_by, mode_id))


  def close(self):
    self.conn.close()


class BufferedJSONOutputHandler(BufferedOutputHandler):
  """ Implements buffered output to JSON of logs being read. """

  def __init__(self, filepath):
    """ Configure the class with output format, path, etc.
        Should probably refactor so that format is handled by subclasses
        implementing this interface rather than internal logic. """
    if isinstance(filepath,str):
      self.outfile = open(filepath,'w',encoding='utf-8')
    else:
      self.outfile = filepath
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
