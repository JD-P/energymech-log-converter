# Converts various IRC logger formats to JSON and SQLite formats.

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
        """Performs a routine that starts the output process."""
        pass
        
    def write_day(self,day):
        """Writes a single days worth of logs to the output."""
        pass

    def close(self):
        """Properly exits and handles finishing touches."""
        pass


class BufferedSqliteOutputHandler(BufferedOutputHandler):
    """ To be implemented.. """
    
    def __init__(self, filepath):
        self.conn = sqlite3.connect(filepath)

    def create_table(cur, table_def):
        self.conn.cursor().execute("CREATE TABLE IF NOT EXISTS {}")

    def begin(self):
        cur = self.conn.cursor()
        # If two things are equivalent then they determine the same things.
        self.create_table("nicks(id INTEGER PRIMARY KEY, nickname TEXT UNIQUE)")
        self.create_table("users(id INTEGER PRIMARY KEY, username TEXT UNIQUE)")
        self.create_table("client_hosts(id INTEGER PRIMARY KEY, hostname TEXT UNIQUE)")
        self.create_table("servers(id INTEGER PRIMARY KEY, hostname TEXT UNIQUE)")
        self.create_table("channels(id INTEGER PRIMARY KEY, nwid INTEGER, channel"
                          " TEXT, FOREIGN KEY(nwid) REFERENCES networks(nwid),"
                          " UNIQUE (nwid, channel))")
        self.create_table("msg_types(id INTEGER PRIMARY KEY, type TEXT UNIQUE)")
        self.create_table("networks(server INTEGER PRIMARY KEY, nwid INTEGER"
                          " UNIQUE, nw_name TEXT UNIQUE, FOREIGN KEY(server)"
                          " REFERENCES servers(id))") 


        self.create_table("hostmasks(id INTEGER PRIMARY KEY, nwid INTEGER, nid INTEGER, uid INTEGER,"
                          " hid INTEGER, FOREIGN KEY(nwid) REFERENCES networks(nwid),"
                          " FOREIGN KEY(nid) REFERENCES nicks(id), FOREIGN KEY(uid)"
                          " REFERENCES users(id), FOREIGN KEY(hid) REFERENCES"
                          " client_hosts(id), UNIQUE (nwid, nid, uid, hid))")


        self.create_table("registered(nwid INTEGER, nid INTEGER, time_of INTEGER," 
                          " account INTEGER, FOREIGN KEY(nwid) REFERENCES networks(nwid),"
                          " FOREIGN KEY(nid) REFERENCES nicks(id), FOREIGN"
                          " KEY(account) REFERENCES nicks(id), PRIMARY KEY"
                          " (nwid, nid, time_of))")


        self.create_table("messages(id INTEGER PRIMARY KEY, timestamp TEXT, channel"
                          " INTEGER, type TEXT, FOREIGN KEY(channel) REFERENCES"
                          " channels(id), FOREIGN KEY(type) REFERENCES msg_types(id))")


        self.create_table("privmsgs(mid INTEGER PRIMARY KEY, nid INTEGER, message TEXT,"
                          " FOREIGN KEY(mid) REFERENCES messages(id), FOREIGN"
                          " KEY(nid) REFERENCES nicks(id))")
 
        self.create_table("notices(mid INTEGER PRIMARY KEY, nid INTEGER, message TEXT,"
                          " FOREIGN KEY(mid) REFERENCES messages(id), FOREIGN"
                          " KEY(nid) REFERENCES nicks(id))")
 
        self.create_table("joins(mid INTEGER PRIMARY KEY, hostmask INTEGER,"
                          " FOREIGN KEY(mid) REFERENCES messages(id), FOREIGN"
                          " KEY(hostmask) REFERENCES hostmasks(id))")
 
        self.create_table("parts(mid INTEGER PRIMARY KEY, hostmask INTEGER," 
                          " part_message TEXT, FOREIGN KEY(mid) REFERENCES"
                          " messages(id), FOREIGN KEY(hostmask) REFERENCES"
                          " hostmasks(id))")

        self.create_table("quits(mid INTEGER PRIMARY KEY, hostmask INTEGER,"
                          " quit_message TEXT, FOREIGN KEY(mid) REFERENCES"
                          " messages(id), FOREIGN KEY(hostmask) REFERENCES"
                          " hostmasks(id))")

        self.create_table("kicks(mid INTEGER PRIMARY KEY, nid_kicked INTEGER, nid_kicked_by" 
                          " INTEGER, kick_message TEXT, FOREIGN KEY(mid) REFERENCES"
                          " messages(id), FOREIGN KEY(nid_kicked) REFERENCES"
                          " nicks(id), FOREIGN KEY(nid_kicked_by) REFERENCES"
                          " nicks(id))")

        self.create_table("nick_changes(mid INTEGER PRIMARY KEY, nid_before INTEGER,"
                          " nid_after INTEGER, FOREIGN KEY(mid) REFERENCES messages(id),"
                          " FOREIGN KEY(nid_before) REFERENCES nicks(id), FOREIGN"
                          " KEY(nid_after) REFERENCES nicks(id))")

        self.create_table("set_modes(mid INTEGER PRIMARY KEY, nid_set_by INTEGER," 
                          " mode_string TEXT, FOREIGN KEY(mid) REFERENCES"
                          " messages(id), FOREIGN KEY(nid_set_by) REFERENCES"
                          " nicks(id))")

        self.create_table("set_topic(mid INTEGER PRIMARY KEY, nid_set_by INTEGER," 
                          " topic TEXT, FOREIGN KEY(mid) REFERENCES messages(id),"
                          " FOREIGN KEY(nid_set_by) REFERENCES nicks(id))")

    def write_day(self, day):
        """
        Accepts a day dictionary with predefined attributes.
        
        Keyword Arguments:
            day:
                A dictionary with different contents depending on its "type" attribute.
                Types:
                
                PRIVMSG:
                NOTICE:
                JOIN:
                    id: unique integer identifying the message
                    nickname: nickname of the person who joined
                    
                PART:
                QUIT:
                KICK:
                NICK:
                MODE:
                TOPIC: 
        cur = self.conn.cursor()
        date = day.keys()[0]
        messages = day[date]
        for message in messages:
            line_id = message[0]
            line_type = message[1]
            time = message[2]
            

    def close(self):
        self.conn.close()

    def insert(self, table, params):
        

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
