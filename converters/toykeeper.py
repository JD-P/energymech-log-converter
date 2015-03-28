import time

import datetime

def convert(filepath, log_format):
  """Run toykeeper_converter's conversion function and return the result."""
  return toykeeper_converter.toykeeper_conv(directory, log_format)

class toykeeper_converter():
  """Converts a custom log format of the form iso standard date, nick and message to json or sqlite."""
  def toykeeper_conv(filepath, log_format):
    logfile = open(filepath, 'r', encoding='latin-1')
    loglines = logfile.readlines()
    dates = {}
    timestamps = {}
    hostmasks = {}
    contents = {}
    line_id = 0    
    for line in loglines:
      components = (lambda space_split : (space_split[0], space_split[1], space_split[2].split("\t")[0], space_split[2].split("\t")[1]))(line.split(" ", 2))
      dates[line_id] = components[0]
      timestamps[line_id] = components[1] 
      hostmasks[line_id] = components[2]
      contents[line_id] = components[3]
      line_id += 1
  def toykeeper_json(hostmasks_dict, contents_dict):
    """Classify lines according to their contents and return a dictionary of the form {line_id:line_type...}
    
    Keyword arguments:
      hostmasks_dict | A dictionary of the form {line_id:hostmask, line_id:hostmask...}
      contents_dict | A dictionary of the form {line_id:contents, line_id:contents...}
    """
    line_types = {}
    for line in contents_dict:
      hostmask = hostmasks_dict[line]
      contents = contents_dict[line]
      if hostmask[0] + hostmask[-1] == "<>":
        line_types[line] = "PRIVMSG"
      elif hostmask[0] + hostmask[-1] == "[]" and contents[0:6] == "ACTION":
        line_types[line] = "ACTION"
        
# Infrastructure for actually producing the python objects representing the log file.
current_date = None
if current_date != time.strptime(components[0], "%Y-%m-%d"):
        current_date = time.strptime(components[0], "%Y-%m-%d")
lines_today = []
