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

import argparse

import json

import sqlite3

import importlib

class conversion_wrapper():
  """Wraps the various converters and imports them all into one unified interface."""
  def main():
    """Implement command line interface and call subroutines to handle conversions."""
    parser = argparse.ArgumentParser()
    parser.add_argument("Directory", help="The directory in which the log files reside.")
    parser.add_argument("--output", "-o", help="Filepath to store output at, default is standard output.")
    formats_help = """\n\nValid formats are:\n\n\tjson\n\tsqlite"""
    parser.add_argument("--oformat", help="The format to output." + formats_help)
    parser.add_argument("--timezone", "-t", help="Specify the timezone as a UTC offset. (Not implemented.)")
    parser.add_argument("--format", "-f", help="Convert log as <FORMAT>.")

    arguments = parser.parse_args()

    if arguments.oformat:
      try:
        converter = importlib.import_module("converters." + arguments.format)
      except ImportError:
        raise ValueError("Given format " + arguments.format.upper() + " has no valid converter.")
      if arguments.oformat == "sqlite":
        if arguments.output:
          # To be implemented later
          raise ValueError("SQL formatting not implemented at this time. Check back for further updates to this software.")
        else:
          raise ValueError("SQL formatting not implemented at this time. Check back for further updates to this software.")
      else:
        if arguments.output:
          jsondump = open(arguments.output, 'w')

          json.dump(converter.convert(arguments.Directory, "json"), jsondump, indent=2)
        else:
          print(json.dumps(converter.convert(arguments.Directory, "json"), indent=2))
    else:
      raise ValueError("Did not specify an output format.")
  
conversion_wrapper.main()
